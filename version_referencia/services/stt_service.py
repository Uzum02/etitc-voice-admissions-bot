"""
Servicio de Reconocimiento de Voz a Texto (Speech-to-Text - STT).
Proporciona transcripción estructurada/simulada para entornos académicos sin requerir
GPUs o llaves pagas en la nube, además de normalización lingüística para español.
"""

import base64
import re
import unicodedata
from typing import Dict
from models.schemas import AudioConsultationRequest, STTResult


# Banco de pistas de audio simuladas para pruebas reproducibles en laboratorio
BANCO_AUDIOS_SIMULADOS: Dict[str, str] = {
    "audio_carreras_01": "Hola, ¿qué ingenierías y programas por ciclos propedéuticos ofrecen en la ETITC?",
    "audio_requisitos_02": "Buenas tardes, ¿qué documentos y requisitos del ICFES necesito para inscribirme?",
    "audio_costos_03": "¿Cuánto vale el PIN de inscripción y cómo funciona la matrícula cero o beca?",
    "audio_fechas_04": "¿En qué fechas se abren las inscripciones y cuándo salen los admitidos?",
    "audio_horarios_05": "Yo trabajo en el día, ¿ustedes tienen jornada nocturna y dónde queda la sede?",
    "audio_sena_06": "Soy tecnólogo del SENA, ¿cómo puedo homologar mis materias por transferencia?",
    "audio_fuera_dominio_07": "¿Me puedes dar la receta para preparar un ajiaco santafereño?"
}


class STTService:
    """Servicio modular para transcribir entradas de voz y normalizar texto en español."""

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """
        Limpia y estandariza una cadena en español:
        1. Convierte a minúsculas.
        2. Elimina tildes/diacríticos (conservando caracteres alfanuméricos).
        3. Elimina signos de puntuación e interrogación.
        4. Colapsa espacios múltiples.
        """
        if not texto or not texto.strip():
            return ""

        texto_minusculas = texto.lower().strip()
        # Descomposición Unicode NFD para separar letras de sus tildes
        texto_sin_tildes = "".join(
            char for char in unicodedata.normalize("NFD", texto_minusculas)
            if unicodedata.category(char) != "Mn"
        )
        # Conservar únicamente letras, números y espacios
        texto_limpio = re.sub(r"[^a-z0-9\s]", " ", texto_sin_tildes)
        return re.sub(r"\s+", " ", texto_limpio).strip()

    def transcribir(self, request: AudioConsultationRequest) -> STTResult:
        """
        Procesa la solicitud entrante priorizando:
        1. `audio_id_simulado` (pista pregrabada del banco de laboratorio)
        2. `audio_base64` (bytes de audio codificados en Base64)
        3. `texto_directo` (consulta textual directa)
        Lanza ValueError si no se proporciona ninguna fuente válida.
        """
        texto_crudo = ""
        fuente = ""
        confianza = 0.0

        if request.audio_id_simulado:
            if request.audio_id_simulado not in BANCO_AUDIOS_SIMULADOS:
                pistas_validas = ", ".join(BANCO_AUDIOS_SIMULADOS.keys())
                raise ValueError(
                    f"El audio_id_simulado '{request.audio_id_simulado}' no existe. "
                    f"Opciones válidas: {pistas_validas}"
                )
            texto_crudo = BANCO_AUDIOS_SIMULADOS[request.audio_id_simulado]
            fuente = "audio_id_simulado"
            confianza = 0.98

        elif request.audio_base64:
            try:
                raw_bytes = base64.b64decode(request.audio_base64, validate=True)
            except Exception as exc:
                raise ValueError("El campo 'audio_base64' no contiene una cadena Base64 válida.") from exc

            if len(raw_bytes) < 4:
                raise ValueError("El payload de audio Base64 es demasiado corto o está vacío.")

            # Si el cliente envía texto UTF-8 simulado dentro del Base64 o cabecera WAV con metadato
            texto_decodificado = raw_bytes.decode("utf-8", errors="ignore").strip()
            if texto_decodificado and not texto_decodificado.startswith("RIFF"):
                texto_crudo = texto_decodificado
            else:
                # Si es un contenedor RIFF/WAV binario estándar sin motor ASR externo conectado,
                # se mapea a la consulta por defecto de oferta académica para demostración.
                texto_crudo = BANCO_AUDIOS_SIMULADOS["audio_carreras_01"]

            fuente = "audio_base64"
            confianza = 0.92

        elif request.texto_directo and request.texto_directo.strip():
            texto_crudo = request.texto_directo.strip()
            fuente = "texto_directo"
            confianza = 1.0

        else:
            raise ValueError(
                "Debe enviar al menos una fuente de entrada: 'audio_id_simulado', "
                "'audio_base64' o 'texto_directo'."
            )

        texto_normalizado = self.normalizar_texto(texto_crudo)
        if not texto_normalizado:
            raise ValueError("La transcripción resultante está vacía tras la normalización.")

        return STTResult(
            texto_original=texto_crudo,
            texto_normalizado=texto_normalizado,
            fuente_reconocimiento=fuente,
            confianza_stt=confianza
        )
