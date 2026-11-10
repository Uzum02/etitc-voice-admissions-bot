"""
Servicio de Síntesis de Voz (Text-to-Speech - TTS) con Perfil de Estudiante Guía ETITC.
VERSIÓN PLANTILLA PARA ESTUDIANTES.
"""

import base64
import io
import math
import struct
import wave
from typing import Any, Dict
from models.schemas import IntentMatchResult, TTSOutput


class TTSService:
    """Sintetiza la respuesta institucional con la identidad vocal de un estudiante de la ETITC."""

    def __init__(self, perfil_voz_config: Dict[str, Any]) -> None:
        self.nombre_guia: str = perfil_voz_config.get(
            "nombre_guia", "Estudiante Monitor ETITC"
        )
        self.saludo_inicial: str = perfil_voz_config.get(
            "saludo_inicial", "¡Hola! Hablas con el monitor estudiantil de la ETITC."
        )
        self.muletillas: list[str] = perfil_voz_config.get("muletillas_permitidas", [])
        self.velocidad_wpm: int = int(perfil_voz_config.get("velocidad_wpm", 145))
        self.idioma_codigo: str = perfil_voz_config.get("idioma_codigo", "es-CO")

    @staticmethod
    def _generar_wav_sintetico_base64(duracion_seg: float = 0.35, frecuencia_hz: float = 440.0) -> str:
        """
        Helper entregado: Genera un archivo RIFF WAV PCM mono válido en memoria codificado en Base64.
        """
        sample_rate = 8000
        num_samples = max(int(sample_rate * min(duracion_seg, 0.5)), 800)
        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            for i in range(num_samples):
                envolvente = math.sin(math.pi * i / num_samples)
                valor = int(12000 * envolvente * math.sin(2.0 * math.pi * frecuencia_hz * i / sample_rate))
                frames.extend(struct.pack("<h", valor))

            wav_file.writeframes(bytes(frames))

        return base64.b64encode(buffer.getvalue()).decode("ascii")

    def sintetizar_respuesta_estudiante(
        self,
        resultado_intencion: IntentMatchResult,
        incluir_saludo: bool = False
    ) -> TTSOutput:
        """
        Ensambla el guion hablado del estudiante monitor y genera la salida de audio y SSML.
        """
        # TODO: [Estudiante 4] - Implementar la síntesis de voz estudiantil en `sintetizar_respuesta_estudiante`.
        # Pasos que debes programar aquí:
        # 1. Crear una lista de fragmentos para el guion hablado:
        #    - Si `incluir_saludo` es `True`, agregar `self.saludo_inicial`.
        #    - Si `resultado_intencion.es_fallback` es `False` y existen elementos en `self.muletillas`,
        #      agregar las muletillas introductorias autorizadas (`self.muletillas[0]` y `self.muletillas[1]`).
        #    - Agregar SIEMPRE de manera íntegra `resultado_intencion.respuesta_institucional_exacta`
        #      (¡Nunca modifiques el texto oficial para no introducir alucinaciones!).
        #    - Si no es fallback y existe `self.muletillas[2]`, agregarla como cierre cordial.
        # 2. Unir los fragmentos con espacios en `guion_completo`.
        # 3. Calcular `duracion_segundos` dividiendo el número de palabras de `guion_completo`
        #    entre `self.velocidad_wpm` y multiplicando por 60.0 (redondeado a 2 decimales).
        # 4. Construir la cadena `ssml` envolviendo `guion_completo` en etiquetas `<speak>`, `<voice>` y `<prosody>`.
        # 5. Generar el audio WAV en Base64 invocando `self._generar_wav_sintetico_base64(...)`.
        # 6. Retornar el objeto `TTSOutput(...)` con todos sus campos completos.
        raise NotImplementedError(
            "TODO: [Estudiante 4] Debe implementar TTSService.sintetizar_respuesta_estudiante()"
        )
