"""
Suite de Pruebas de Integración Extremo a Extremo (E2E) - Versión de Referencia.
Verifica el contrato de API, la transcripción STT, el motor determinista anti-alucinaciones
y la síntesis de voz del estudiante monitor de la ETITC.
"""

import base64
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Verifica que el servicio inicie correctamente y cargue las 6 intenciones oficiales."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ETITC" in data["institucion"]
    assert data["intenciones_cargadas"] == 6


def test_consulta_por_audio_simulado_programas() -> None:
    """Verifica el flujo completo usando un ID de audio simulado sobre carreras e ingenierías."""
    payload = {
        "session_id": "test-aspirante-101",
        "audio_id_simulado": "audio_carreras_01",
        "incluir_saludo_inicial": True
    }
    response = client.post("/api/v1/chat/voz", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert body["transcripcion"]["fuente_reconocimiento"] == "audio_id_simulado"
    assert body["intencion"]["intent_id"] == "PROGRAMAS_ACADEMICOS"
    assert body["intencion"]["es_fallback"] is False
    # Verifica que la respuesta oficial exacta esté contenida íntegramente en la voz del estudiante
    respuesta_oficial = body["intencion"]["respuesta_institucional_exacta"]
    assert respuesta_oficial in body["voz_estudiante"]["guion_hablado_estudiante"]
    assert "Camila" in body["voz_estudiante"]["guion_hablado_estudiante"]
    # Verifica que el audio generado sea un contenedor RIFF WAV válido en Base64
    wav_bytes = base64.b64decode(body["voz_estudiante"]["audio_wav_base64"])
    assert wav_bytes.startswith(b"RIFF")


def test_consulta_por_texto_directo_homologacion_sena() -> None:
    """Verifica la normalización de tildes/signos y clasificación de homologaciones SENA."""
    payload = {
        "session_id": "test-aspirante-102",
        "texto_directo": "¡Hola! Soy egresado del SENA, ¿cómo hago para HOMOLOGAR materias?",
        "incluir_saludo_inicial": False
    }
    response = client.post("/api/v1/chat/voz", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert body["intencion"]["intent_id"] == "HOMOLOGACIONES_TRANSFERENCIAS"
    assert "sena" in body["intencion"]["keywords_detectadas"] or "homologar" in body["intencion"]["keywords_detectadas"]
    assert body["intencion"]["es_fallback"] is False


def test_proteccion_anti_alucinaciones_fallback() -> None:
    """
    Garantiza que ante preguntas ajenas a admisiones de la ETITC el bot NUNCA invente respuestas
    y active determinísticamente el Fallback Institucional.
    """
    payload = {
        "session_id": "test-aspirante-103",
        "audio_id_simulado": "audio_fuera_dominio_07"
    }
    response = client.post("/api/v1/chat/voz", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert body["intencion"]["intent_id"] == "FALLBACK_INSTITUCIONAL"
    assert body["intencion"]["es_fallback"] is True
    assert "admisiones@itc.edu.co" in body["intencion"]["respuesta_institucional_exacta"]
    assert body["garantia_no_alucinacion"] is True


def test_validacion_error_solicitud_vacia() -> None:
    """Verifica que enviar un payload sin audio ni texto retorne HTTP 400 Bad Request."""
    response = client.post("/api/v1/chat/voz", json={"session_id": "sesion-vacia"})
    assert response.status_code == 400
