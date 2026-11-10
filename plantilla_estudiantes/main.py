"""
Punto de Entrada Principal (FastAPI) - Chatbot de Voz de Admisiones ETITC.
VERSIÓN PLANTILLA PARA ESTUDIANTES.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import AudioConsultationRequest, VoiceChatResponse
from services.intent_service import IntentService
from services.stt_service import BANCO_AUDIOS_SIMULADOS, STTService
from services.tts_service import TTSService


app = FastAPI(
    title="ETITC - Chatbot de Voz para Admisiones (Plantilla Estudiantes)",
    description=(
        "Plantilla de trabajo colaborativo para el Proyecto Integrador de Ingeniería. "
        "Completa los bloques # TODO asignados a cada estudiante."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stt_service = STTService()
intent_service = IntentService(BASE_DIR / "data" / "faqs_admisiones_etitc.json")
tts_service = TTSService(intent_service.kb_data.get("perfil_voz_estudiante", {}))


@app.get("/health", tags=["Diagnóstico"])
def verificar_estado() -> dict:
    """
    Endpoint de diagnóstico para comprobar que la API y el JSON institucional están activos.
    """
    # TODO: [Estudiante 1] - Implementar la respuesta del endpoint `/health`.
    # Debe retornar un diccionario JSON con las siguientes llaves:
    # - `"status"`: `"ok"`
    # - `"institucion"`: nombre de la institución leído desde `intent_service.kb_data`
    # - `"departamento"`: nombre del departamento leído desde `intent_service.kb_data`
    # - `"intenciones_cargadas"`: cantidad total de intenciones en `intent_service.kb_data["intenciones"]`
    # - `"monitor_activo"`: nombre del estudiante monitor desde `tts_service.nombre_guia`
    raise NotImplementedError("TODO: [Estudiante 1] Debe implementar el endpoint /health")


@app.get("/api/v1/admisiones/catalogo", tags=["Base de Conocimiento"])
def listar_catalogo_admisiones() -> dict:
    """Lista las categorías oficiales y preguntas ejemplo soportadas por el bot de la ETITC."""
    return {
        "institucion": intent_service.kb_data.get("institucion"),
        "total_intenciones": len(intent_service.kb_data.get("intenciones", [])),
        "intenciones": intent_service.obtener_catalogo_intenciones(),
    }


@app.get("/api/v1/admisiones/audios-simulados", tags=["Laboratorio STT"])
def listar_audios_simulados() -> dict:
    """Retorna el banco de pistas de audio pregrabadas disponibles para pruebas de laboratorio."""
    return {
        "descripcion": "Identificadores de audio simulados para probar el pipeline STT sin micrófono físico.",
        "pistas_disponibles": BANCO_AUDIOS_SIMULADOS,
    }


@app.post(
    "/api/v1/chat/voz",
    response_model=VoiceChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Interacción por Voz"],
)
def procesar_consulta_voz(request: AudioConsultationRequest) -> VoiceChatResponse:
    """
    Orquesta el flujo extremo a extremo del Chatbot de Voz conectando STT, Intenciones y TTS.
    """
    # TODO: [Estudiante 5] - Orquestar el pipeline principal de voz en `/api/v1/chat/voz`.
    # Pasos que debes programar aquí para integrar el trabajo de tus compañeros:
    # 1. Invocar `stt_service.transcribir(request)` dentro de un bloque `try / except ValueError as err:`.
    #    Si ocurre un `ValueError`, lanzar `HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))`.
    # 2. Pasar el texto normalizado (`resultado_stt.texto_normalizado`) al método
    #    `intent_service.resolver_intencion(...)` para obtener `resultado_intencion`.
    # 3. Invocar `tts_service.sintetizar_respuesta_estudiante(...)` pasándole `resultado_intencion`
    #    y el flag `incluir_saludo=request.incluir_saludo_inicial`.
    # 4. Construir y retornar la instancia de `VoiceChatResponse` con todos los resultados integrados.
    raise NotImplementedError(
        "TODO: [Estudiante 5] Debe implementar la orquestación en procesar_consulta_voz()"
    )
