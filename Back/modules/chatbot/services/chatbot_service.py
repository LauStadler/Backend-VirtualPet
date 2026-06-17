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
                "Luego usa la función 'solicitar_facturacion'."
            )
        )

    def solicitar_facturacion(self, pedido_id: int, cuit: str) -> str:
        """
        Registra la solicitud de facturación para un pedido específico con un CUIT dado.
        """
        order = self.db.query(Order).filter(Order.id == pedido_id).first()
        
        if not order:
            return f"No encontré el pedido con ID {pedido_id}."
        
        if order.estado == OrderEstado.CANCELADO:
            return f"El pedido {pedido_id} está cancelado y no puede ser facturado."
        
        # Validación de rango de 30 días
        from datetime import timedelta
        ahora = datetime.now()
        fecha_limite = order.created_at + timedelta(days=30)
        
        if ahora > fecha_limite:
            return f"Lo siento, el pedido {pedido_id} fue realizado hace más de 30 días ({order.created_at.strftime('%d/%m/%Y')}) y ya no puede ser facturado por este medio."
        
        # Registro de facturación
        order.billing_cuit = cuit
        order.billing_requested_at = ahora
        self.db.commit()
        
        return f"¡Perfecto! He registrado la solicitud de factura para el pedido {pedido_id} con el CUIT {cuit}. El equipo de backoffice se encargará del resto."

    async def generate_response(self, message: str, user_id: int = None, history: list = None) -> str:
        if not GEMINI_API_KEY:
            return "Lo siento, el servicio de Chatbot no está configurado (falta API Key)."

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
            import traceback
            error_msg = f"Error en ChatbotService: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return f"Lo siento, tuve un problema interno. Error técnico: {str(e)}"
