"""
Punto de Entrada Principal (FastAPI) - Chatbot de Voz de Admisiones ETITC (Versión Referencia).
Arquitectura limpia y determinista que orquesta:
1. Servicio STT (Transcripción y normalización de audio/texto).
2. Servicio de Intenciones (Búsqueda estricta sobre JSON oficial de la ETITC sin alucinaciones).
3. Servicio TTS (Síntesis con perfil vocal de estudiante monitor y salida WAV/SSML).
"""

import sys
from pathlib import Path

# Garantiza importaciones relativas limpias sin importar desde qué directorio se ejecute uvicorn o pytest
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
    title="ETITC - Chatbot de Voz para Admisiones (Referencia Docente)",
    description=(
        "Prototipo funcional de arquitectura de software para el Departamento de Admisiones "
        "de la Escuela Tecnológica Instituto Técnico Central (ETITC). "
        "Respuestas 100% deterministas libres de alucinaciones con voz simulada de estudiante monitor."
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

# Instanciación de servicios de dominio (Singleton a nivel de aplicación)
stt_service = STTService()
intent_service = IntentService(BASE_DIR / "data" / "faqs_admisiones_etitc.json")
tts_service = TTSService(intent_service.kb_data.get("perfil_voz_estudiante", {}))


@app.get("/health", tags=["Diagnóstico"])
def verificar_estado() -> dict:
    """Endpoint de diagnóstico para comprobar la disponibilidad del servicio y la base institucional."""
    return {
        "status": "ok",
        "institucion": intent_service.kb_data.get("institucion"),
        "departamento": intent_service.kb_data.get("departamento"),
        "version_base_conocimiento": intent_service.kb_data.get("version_base_conocimiento"),
        "intenciones_cargadas": len(intent_service.kb_data.get("intenciones", [])),
        "monitor_activo": tts_service.nombre_guia,
    }


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
    Orquesta el flujo extremo a extremo del Chatbot de Voz:
    1. Transcribe el audio o texto entrante y lo normaliza (`STTService`).
    2. Clasifica la intención contra el JSON oficial de la ETITC sin inventar datos (`IntentService`).
    3. Sintetiza el guion hablado del estudiante monitor y genera el audio WAV en Base64 (`TTSService`).
    """
    try:
        resultado_stt = stt_service.transcribir(request)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err

    resultado_intencion = intent_service.resolver_intencion(resultado_stt.texto_normalizado)
    resultado_tts = tts_service.sintetizar_respuesta_estudiante(
        resultado_intencion=resultado_intencion,
        incluir_saludo=request.incluir_saludo_inicial,
    )

    return VoiceChatResponse(
        session_id=request.session_id,
        transcripcion=resultado_stt,
        intencion=resultado_intencion,
        voz_estudiante=resultado_tts,
        garantia_no_alucinacion=True,
    )
