"""
Esquemas Pydantic para la validación de entradas y salidas del Chatbot de Voz ETITC.
Garantiza contratos de datos estrictos entre las capas de STT, Intenciones y TTS.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AudioConsultationRequest(BaseModel):
    """
    Representa una solicitud de consulta al chatbot de admisiones.
    En modo prototipo acepta tanto un payload de audio simulado (base64 o etiqueta de pista)
    como texto directo para facilitar pruebas unitarias y de integración.
    """
    session_id: str = Field(
        default="sesion-aspirante-001",
        description="Identificador único de la sesión del aspirante."
    )
    audio_id_simulado: Optional[str] = Field(
        default=None,
        description="Identificador de pista de audio pregrabada para simular STT (ej. 'audio_carreras_01')."
    )
    audio_base64: Optional[str] = Field(
        default=None,
        description="Cadena en Base64 que representa los bytes de un archivo WAV/MP3."
    )
    texto_directo: Optional[str] = Field(
        default=None,
        description="Texto opcional de respaldo cuando se prueba sin micrófono."
    )
    incluir_saludo_inicial: bool = Field(
        default=False,
        description="Si es True, antepone el saludo de bienvenida del estudiante monitor."
    )


class STTResult(BaseModel):
    """Resultado estructurado del servicio Speech-to-Text (STT)."""
    texto_original: str
    texto_normalizado: str
    fuente_reconocimiento: str = Field(
        description="Indica si provino de 'audio_id_simulado', 'audio_base64' o 'texto_directo'."
    )
    confianza_stt: float = Field(ge=0.0, le=1.0)


class IntentMatchResult(BaseModel):
    """Resultado del motor determinista de intenciones institucionales (Cero Alucinaciones)."""
    intent_id: str
    categoria: str
    puntaje_coincidencia: float = Field(ge=0.0, le=1.0)
    keywords_detectadas: List[str]
    respuesta_institucional_exacta: str
    enlaces_oficiales: List[str]
    es_fallback: bool


class TTSOutput(BaseModel):
    """Resultado del sintetizador de voz (TTS) con personalidad de estudiante ETITC."""
    guion_hablado_estudiante: str = Field(
        description="Guion enriquecido con el saludo/tono del estudiante monitor, sin alterar el dato oficial."
    )
    ssml_generado: str = Field(
        description="Marcado SSML estándar para motores de voz con prosodia estudiantil colombiana."
    )
    audio_wav_base64: str = Field(
        description="Audio WAV válido codificado en Base64 (onda sintetizada de demostración)."
    )
    duracion_estimada_segundos: float
    perfil_voz: str


class VoiceChatResponse(BaseModel):
    """Respuesta integral del endpoint principal del Chatbot de Voz de Admisiones."""
    session_id: str
    transcripcion: STTResult
    intencion: IntentMatchResult
    voz_estudiante: TTSOutput
    garantia_no_alucinacion: bool = True
