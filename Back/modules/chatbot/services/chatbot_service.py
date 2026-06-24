import os
import google.generativeai as genai
from datetime import datetime
from sqlalchemy.orm import Session
from modules.orders.models.order import Order, OrderEstado
from fastapi import HTTPException
import json

# Configuración básica (Idealmente esto iría en un config.py)
# Por ahora lo dejamos aquí para simplificar la implementación inicial
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class ChatbotService:
    def __init__(self, db: Session):
        self.db = db
        # Definimos las herramientas (functions) que la IA puede usar
        self.tools = [self.solicitar_facturacion]
        self.model = genai.GenerativeModel(
            model_name='gemini-flash-lite-latest',
            tools=self.tools,
            system_instruction=(
                "Eres el asistente virtual de 'Virtual Pet', una tienda de productos para mascotas. "
                "Tus objetivos son responder consultas generales y ayudar con la facturación. "
                "\n\nINFORMACIÓN DE LA EMPRESA:"
                "\n- Horarios de entrega: Lunes a Viernes de 09:00 a 18:00 hs. Sábados de 09:00 a 13:00 hs."
                "\n- Costos de entrega: $500 en CABA, $1200 en GBA. Gratis en compras superiores a $15.000."
                "\n- Condiciones de entrega: Los pedidos se entregan dentro de las 48hs hábiles después de la confirmación."
                "\n- Política de facturación: Se puede solicitar factura indicando el CUIT. "
                "Condiciones: El pedido debe estar confirmado (no cancelado) y debe ser del mes actual. "
                "\n\nSi el usuario quiere facturar un pedido, pídele el ID del pedido y su CUIT. "
                "Luego usa la función 'solicitar_facturacion'. IMPORTANTE: El usuario debe haber iniciado sesión para facturar, si la función indica que debe iniciar sesión, indícaselo amablemente."
            )
        )

    def solicitar_facturacion(self, pedido_id: int, cuit: str) -> str:
        """
        Registra la solicitud de facturación para un pedido específico con un CUIT dado.
        """
        if getattr(self, 'current_user_id', None) is None:
            return "Para solicitar una factura, debes iniciar sesión en tu cuenta primero."

        # Limpiar el CUIT (quitar guiones, puntos, espacios y caracteres no numéricos)
        clean_cuit = "".join(c for c in cuit if c.isdigit())
        
        # Validar que tenga exactamente 11 dígitos
        if len(clean_cuit) != 11:
            return (
                f"El CUIT proporcionado ('{cuit}') no es válido. "
                "Debe contener exactamente 11 números (por ejemplo: 20123456789 o 20-12345678-9). "
                "Por favor, verifícalo y vuelve a indicármelo."
            )

        order = self.db.query(Order).filter(Order.id == pedido_id).first()
        
        if not order:
            return f"No encontré el pedido con ID {pedido_id}."

        # Verificar propiedad del pedido (Evitar vulnerabilidad IDOR de facturación cruzada)
        if order.user_id != self.current_user_id:
            return (
                f"El pedido con ID {pedido_id} no pertenece a tu cuenta de usuario. "
                "Solo puedes solicitar la facturación de tus propios pedidos. "
                "Por favor, verifica el número de pedido e intenta nuevamente."
            )
        
        if order.estado == OrderEstado.CANCELADO:
            return f"El pedido {pedido_id} está cancelado y no puede ser facturado."
        
        # Validación de rango de 30 días
        from datetime import timedelta
        ahora = datetime.now()
        fecha_limite = order.created_at + timedelta(days=30)
        
        if ahora > fecha_limite:
            return f"Lo siento, el pedido {pedido_id} fue realizado hace más de 30 días ({order.created_at.strftime('%d/%m/%Y')}) y ya no puede ser facturado por este medio."
        
        # Registro de facturación
        order.billing_cuit = clean_cuit
        order.billing_requested_at = ahora
        
        try:
            self.db.commit()
            
            # Notificar en tiempo real al Backoffice vía WebSocket (Usa el canal existente /backoffice/ws)
            try:
                import asyncio
                from shared.utils.websocket_manager import manager
                from modules.orders.services.order_service import OrderService
                
                # Utilizar el servicio de órdenes para obtener el pedido completamente hidratado
                # (con los datos del cliente y del repartidor) para evitar borrar info en el front
                order_service = OrderService(self.db)
                full_order = order_service.obtener_una_backoffice(pedido_id)
                order_data = full_order.model_dump(mode='json')
                
                # Obtener el bucle de eventos asíncronos activo de FastAPI y encolar el envío
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(manager.broadcast({
                        "type": "order_updated",
                        "order": order_data
                    }))
            except Exception as ws_err:
                # Evitar que fallos menores de red en sockets afecten el guardado exitoso en base de datos
                print(f"Advertencia: No se pudo despachar la notificación WebSocket de facturación: {ws_err}")
                
        except Exception as e:
            self.db.rollback()
            # Registrar el error técnico en los logs del servidor
            import traceback
            print(f"Error al guardar facturación en DB para pedido {pedido_id}: {str(e)}\n{traceback.format_exc()}")
            return "Hubo un problema interno al registrar los datos en nuestro sistema. Por favor, intenta nuevamente en unos minutos."
        
        return f"¡Perfecto! He registrado la solicitud de factura para el pedido {pedido_id} con el CUIT {clean_cuit}. El equipo de backoffice se encargará del resto."

    async def generate_response(self, message: str, user_id: int = None, history: list = None) -> str:
        if not GEMINI_API_KEY:
            return "Lo siento, el servicio de Chatbot no está configurado (falta API Key)."

        self.current_user_id = user_id

        # Formatear el historial para Gemini si existe
        gemini_history = []
        if history:
            for msg in history:
                gemini_history.append({
                    "role": msg.role,
                    "parts": msg.parts
                })

        chat = self.model.start_chat(
            history=gemini_history,
            enable_automatic_function_calling=True
        )
        try:
            response = chat.send_message(message)
            return response.text
        except Exception as e:
            # Registrar el traceback completo en los logs de Docker para el desarrollador
            import traceback
            error_msg = f"Error en ChatbotService: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            # Retornar un mensaje amigable y limpio al usuario final
            return "Lo siento, ocurrió un inconveniente interno al procesar tu solicitud. Por favor, intenta nuevamente en unos momentos."
