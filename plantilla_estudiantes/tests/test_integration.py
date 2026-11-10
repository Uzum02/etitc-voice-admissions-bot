"""
Suite de Pruebas de Integración Extremo a Extremo (E2E).
VERSIÓN PLANTILLA PARA ESTUDIANTES.
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
    """
    Prueba 1: Verificar que el endpoint `/health` responde HTTP 200 y carga las 6 intenciones.
    """
    # TODO: [Estudiante 6] - Programar la prueba de diagnóstico del endpoint `/health`.
    # Pasos que debes programar aquí:
    # 1. Realizar una petición `client.get("/health")`.
    # 2. Comprobar con `assert` que `response.status_code == 200`.
    # 3. Verificar que `response.json()["status"] == "ok"` y `response.json()["intenciones_cargadas"] == 6`.
    raise NotImplementedError("TODO: [Estudiante 6] Debe implementar test_health_endpoint()")


def test_consulta_por_audio_simulado_programas() -> None:
    """
    Prueba 2: Verificar el flujo completo enviando `audio_id_simulado="audio_carreras_01"`.
    """
    # TODO: [Estudiante 6] - Programar la prueba de integración E2E para consulta de programas académicos.
    # Pasos que debes programar aquí:
    # 1. Enviar un `client.post("/api/v1/chat/voz", json={...})` con `audio_id_simulado="audio_carreras_01"`
    #    e `incluir_saludo_inicial=True`.
    # 2. Verificar que el código de estado sea `200`.
    # 3. Comprobar que `body["intencion"]["intent_id"] == "PROGRAMAS_ACADEMICOS"` y `es_fallback` sea `False`.
    # 4. Comprobar que `body["intencion"]["respuesta_institucional_exacta"]` esté contenida sin alteraciones
    #    dentro de `body["voz_estudiante"]["guion_hablado_estudiante"]`.
    # 5. Decodificar `body["voz_estudiante"]["audio_wav_base64"]` con `base64.b64decode` y verificar
    #    que los bytes comiencen con la cabecera `b"RIFF"`.
    raise NotImplementedError(
        "TODO: [Estudiante 6] Debe implementar test_consulta_por_audio_simulado_programas()"
    )


def test_proteccion_anti_alucinaciones_fallback() -> None:
    """
    Prueba 3: Garantizar que preguntas fuera de dominio activen `FALLBACK_INSTITUCIONAL`.
    """
    # TODO: [Estudiante 6] - Programar la validación de seguridad anti-alucinaciones.
    # Pasos que debes programar aquí:
    # 1. Enviar un `client.post("/api/v1/chat/voz", json={"audio_id_simulado": "audio_fuera_dominio_07"})`.
    # 2. Verificar que `body["intencion"]["intent_id"] == "FALLBACK_INSTITUCIONAL"`.
    # 3. Verificar que `body["intencion"]["es_fallback"] is True` y que mencione el correo `admisiones@itc.edu.co`.
    raise NotImplementedError(
        "TODO: [Estudiante 6] Debe implementar test_proteccion_anti_alucinaciones_fallback()"
    )


def test_validacion_error_solicitud_vacia() -> None:
    """
    Prueba 4: Verificar que enviar un JSON sin audio ni texto retorne HTTP 400 Bad Request.
    """
    # TODO: [Estudiante 6] - Programar la prueba de manejo de errores HTTP 400.
    # 1. Enviar `client.post("/api/v1/chat/voz", json={"session_id": "vacia"})`.
    # 2. Comprobar con `assert response.status_code == 400`.
    raise NotImplementedError(
        "TODO: [Estudiante 6] Debe implementar test_validacion_error_solicitud_vacia()"
    )
