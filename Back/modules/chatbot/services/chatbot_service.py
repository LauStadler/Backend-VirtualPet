import os
import google.generativeai as genai
from datetime import datetime
from sqlalchemy.orm import Session
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
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 400,
            },
            system_instruction=(
                "Eres el asistente virtual exclusivo de 'Virtual Pet', una tienda de productos para mascotas. "
                "Tus objetivos son responder exclusivamente a consultas sobre 'Virtual Pet', el cuidado de mascotas, "
                "nuestros productos, envíos, y asistir en la facturación de pedidos. "
                "\n\nPOLÍTICAS DE SEGURIDAD Y GUARDRAILS (ESTRICTAMENTE OBLIGATORIO):"
                "\n1. ALCANCE TEMÁTICO: Solo debes responder preguntas sobre la tienda 'Virtual Pet', mascotas, productos para mascotas, "
                "horarios de atención, costos y condiciones de entrega, y facturación."
                "\n2. RECHAZO DE TEMAS AJENOS: Si el usuario te realiza preguntas ajenas a estos temas (por ejemplo: programar en cualquier lenguaje, "
                "recetas de cocina, historia general, matemáticas avanzadas, traducción de textos ajenos a la tienda, redactar historias de ficción, "
                "o cualquier consulta de cultura general/asistencia técnica no relacionada con la tienda), debes responder con cortesía diciendo "
                "que solo estás capacitado para ayudar con temas relacionados a Virtual Pet, y rehusarte amablemente a contestar la consulta."
                "\n3. RESPUESTAS CONCISAS: Sé claro, conciso y directo para evitar el consumo innecesario de tokens. No te extiendas en explicaciones innecesarias."
                "\n4. CONTROL DE HERRAMIENTAS: No utilices herramientas ni realices acciones a menos que el usuario lo solicite expresamente."
                "\n\nINFORMACIÓN DE LA EMPRESA:"
                "\n- Horarios de entrega: Lunes a Viernes de 09:00 a 18:00 hs. Sábados de 09:00 a 13:00 hs."
                "\n- Costos de entrega: $500 en CABA, $1200 en GBA. Envío gratis en compras superiores a $15.000."
                "\n- Condiciones de entrega: Los pedidos se entregan dentro de las 48hs hábiles después de la confirmación."
                "\n- Política de facturación: Se puede solicitar factura indicando el CUIT. "
                "Condiciones: El pedido debe estar confirmado (no cancelado) y debe ser del mes actual (dentro de los 30 días)."
                "\n\nSi el usuario quiere facturar un pedido, pídele el ID del pedido y su CUIT. "
                "Luego usa la función 'solicitar_facturacion'. IMPORTANTE: El usuario debe haber iniciado sesión para facturar, si la función indica que debe iniciar sesión, indícaselo amablemente."
            )
        )

    def solicitar_facturacion(self, pedido_id: int, cuit: str) -> str:
        """
        Registra la solicitud de facturación delegando al OrderService,
        respetando las fronteras del monolito modular.
        """
        if getattr(self, 'current_user_id', None) is None:
            return "Para solicitar una factura, debes iniciar sesión en tu cuenta primero."

        from modules.orders.services.order_service import OrderService, OrdenNoEncontradaError

        try:
            order_service = OrderService(self.db)
            order_service.solicitar_facturacion(
                order_id=pedido_id,
                user_id=self.current_user_id,
                cuit=cuit
            )
        except (ValueError, OrdenNoEncontradaError, PermissionError) as domain_err:
            # Retornar el mensaje amigable de error del negocio directamente
            return str(domain_err)
        except Exception as e:
            # Registrar el error técnico en los logs del servidor
            import traceback
            print(f"Error al solicitar facturación en ChatbotService para pedido {pedido_id}: {str(e)}\n{traceback.format_exc()}")
            return "Hubo un problema interno al registrar los datos en nuestro sistema. Por favor, intenta nuevamente en unos minutos."

        clean_cuit = "".join(c for c in cuit if c.isdigit())
        return f"¡Perfecto! He registrado la solicitud de factura para el pedido {pedido_id} con el CUIT {clean_cuit}. El equipo de backoffice se encargará del resto."

    async def generate_response(self, message: str, user_id: int = None, history: list = None) -> str:
        if not GEMINI_API_KEY:
            return "Lo siento, el servicio de Chatbot no está configurado actualmente."

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
