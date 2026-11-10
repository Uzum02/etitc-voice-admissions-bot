"""
Servicio de Síntesis de Voz (Text-to-Speech - TTS) con Perfil de Estudiante Guía ETITC.
Construye la locución empática de un estudiante monitor respetando palabra por palabra
la respuesta oficial verificada, genera marcado SSML y sintetiza un contenedor WAV en Base64.
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
        self.muletillas: list[str] = perfil_voz_config.get(
            "muletillas_permitidas",
            [
                "¡Con mucho gusto compañero!",
                "Mira, según la resolución oficial de admisiones de la Escuela:",
                "Recuerda que puedes acercarte a la oficina en el centro o escribirnos si tienes otra duda."
            ]
        )
        self.velocidad_wpm: int = int(perfil_voz_config.get("velocidad_wpm", 145))
        self.idioma_codigo: str = perfil_voz_config.get("idioma_codigo", "es-CO")

    @staticmethod
    def _generar_wav_sintetico_base64(duracion_seg: float = 0.35, frecuencia_hz: float = 440.0) -> str:
        """
        Genera un archivo de audio RIFF WAV PCM mono de 16-bit válido en memoria
        y lo retorna codificado en Base64 para pruebas de reproducción en clientes HTTP/Web.
        """
        sample_rate = 8000
        num_samples = max(int(sample_rate * min(duracion_seg, 0.5)), 800)
        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)       # Mono
            wav_file.setsampwidth(2)       # 16 bits por muestra
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            for i in range(num_samples):
                # Envolvente suave para evitar clics al inicio y al final
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
        Ensambla el guion hablado del estudiante monitor sin modificar la respuesta institucional,
        construye el documento SSML y calcula la duración estimada de locución.
        """
        partes_guion: list[str] = []

        if incluir_saludo:
            partes_guion.append(self.saludo_inicial)

        if not resultado_intencion.es_fallback and len(self.muletillas) >= 2:
            partes_guion.append(self.muletillas[0])
            partes_guion.append(self.muletillas[1])

        # Se inserta de forma íntegra e inalterada la respuesta oficial de la ETITC
        partes_guion.append(resultado_intencion.respuesta_institucional_exacta)

        if not resultado_intencion.es_fallback and len(self.muletillas) >= 3:
            partes_guion.append(self.muletillas[2])

        guion_completo = " ".join(partes_guion)

        # Cálculo de duración estimada según palabras por minuto (WPM)
        total_palabras = len(guion_completo.split())
        duracion_segundos = round((total_palabras / max(self.velocidad_wpm, 80)) * 60.0, 2)

        # Generación de marcado SSML con pausas naturales de estudiante
        ssml = (
            f'<speak version="1.1" xml:lang="{self.idioma_codigo}">'
            f'<voice name="{self.idioma_codigo}-Standard-A">'
            f'<prosody rate="103%" pitch="+2st">'
            f'{guion_completo}'
            f'</prosody>'
            f'</voice>'
            f'</speak>'
        )

        # Tono más agudo (523.25 Hz - Do5) para respuestas exitosas y 330 Hz para derivación/fallback
        frecuencia_tono = 330.0 if resultado_intencion.es_fallback else 523.25
        wav_base64 = self._generar_wav_sintetico_base64(frecuencia_hz=frecuencia_tono)

        return TTSOutput(
            guion_hablado_estudiante=guion_completo,
            ssml_generado=ssml,
            audio_wav_base64=wav_base64,
            duracion_estimada_segundos=duracion_segundos,
            perfil_voz=self.nombre_guia
        )
