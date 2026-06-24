import pytest
from unittest.mock import MagicMock, patch
from fastapi import status

@pytest.fixture
def mock_genai():
    with patch("modules.chatbot.services.chatbot_service.genai") as mock:
        # Configurar el mock de la API key
        mock.GenerativeModel.return_value = MagicMock()
        with patch("modules.chatbot.services.chatbot_service.GEMINI_API_KEY", "test_key"):
            yield mock

def test_chatbot_query_success(client, mock_genai):
    # Mockear la respuesta del chatbot
    mock_model = mock_genai.GenerativeModel.return_value
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hola, soy tu asistente de Virtual Pet. ¿En qué te puedo ayudar hoy?"
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat

    # Hacemos una llamada válida
    response = client.post(
        "/chatbot/query",
        json={"message": "Hola, cuáles son los horarios de entrega?"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "response" in data
    assert "Virtual Pet" in data["response"]

def test_chatbot_no_api_key(client):
    # Probar el comportamiento cuando no hay API Key configurada
    with patch("modules.chatbot.services.chatbot_service.GEMINI_API_KEY", None):
        response = client.post(
            "/chatbot/query",
            json={"message": "Hola"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "no está configurado" in response.json()["response"]

def test_chatbot_billing_flow_requires_login(client, mock_genai):
    # Si el usuario no ha iniciado sesión, no debería poder facturar
    # Mockear la respuesta de Gemini para que intente llamar a la función
    mock_model = mock_genai.GenerativeModel.return_value
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Para solicitar una factura, debes iniciar sesión en tu cuenta primero."
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat

    response = client.post(
        "/chatbot/query",
        json={"message": "Quiero facturar mi pedido 123", "user_id": None}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "iniciar sesión" in response.json()["response"]
