"""
Motor Determinista de Intenciones Institucionales (Cero Alucinaciones).
VERSIÓN PLANTILLA PARA ESTUDIANTES.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from models.schemas import IntentMatchResult
from services.stt_service import STTService


class IntentService:
    """Gestiona la carga de la base de conocimiento y la búsqueda determinista de intenciones."""

    def __init__(self, json_path: Path | None = None) -> None:
        if json_path is None:
            json_path = Path(__file__).resolve().parent.parent / "data" / "faqs_admisiones_etitc.json"
        self.json_path = json_path
        self.kb_data: Dict[str, Any] = self._cargar_base_conocimiento()

    def _cargar_base_conocimiento(self) -> Dict[str, Any]:
        """Lee el archivo JSON con las preguntas frecuentes oficiales de la ETITC."""
        if not self.json_path.exists():
            raise FileNotFoundError(f"No se encontró la base de conocimiento en: {self.json_path}")

        with open(self.json_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    def obtener_catalogo_intenciones(self) -> List[Dict[str, Any]]:
        """Retorna el listado resumido de intenciones soportadas para consulta pública."""
        return [
            {
                "intent_id": item["intent_id"],
                "categoria": item["categoria"],
                "preguntas_ejemplo": item.get("preguntas_ejemplo", []),
                "keywords": item.get("keywords", [])
            }
            for item in self.kb_data.get("intenciones", [])
        ]

   
def resolver_intencion(self, texto_normalizado: str) -> IntentMatchResult:
    """
    Busca la intención institucional que mejor coincide con la consulta
    sin inventar ni modificar ninguna respuesta oficial.
    """

    # 1. Separar la consulta en palabras
    tokens_consulta = set(texto_normalizado.split())

    mejor_intencion = None
    mejores_coincidencias = []
    mejor_puntaje = 0.0

    # 2. Recorrer las intenciones disponibles en el JSON
    for intencion in self.kb_data.get("intenciones", []):

        coincidencias = []

        # 3. Comparar cada palabra clave
        for kw in intencion.get("keywords", []):

            keyword_normalizada = STTService.normalizar_texto(kw)

            if not keyword_normalizada:
                continue

            # Comprobar frases compuestas
            if " " in keyword_normalizada:
                coincide = keyword_normalizada in texto_normalizado

            # Comprobar palabras individuales
            else:
                coincide = keyword_normalizada in tokens_consulta

            if coincide:
                coincidencias.append(kw)

        # 4. Calcular el puntaje de coincidencia
        puntaje = min(0.35 + len(coincidencias) * 0.22, 0.99)

        # Conservar la intención con mayor puntaje
        if coincidencias and puntaje > mejor_puntaje:
            mejor_intencion = intencion
            mejores_coincidencias = coincidencias
            mejor_puntaje = puntaje

    # 5. Aplicar la regla anti-alucinaciones
    if mejor_intencion is None:

        fallback = self.kb_data["respuesta_fallback"]

        return IntentMatchResult(
            intent_id=fallback["intent_id"],
            categoria=fallback["categoria"],
            puntaje_coincidencia=0.0,
            keywords_detectadas=[],
            respuesta_institucional_exacta=fallback["respuesta_oficial"],
            enlaces_oficiales=fallback.get("enlaces_oficiales", []),
            es_fallback=True
        )

    # 6. Devolver la intención ganadora
    return IntentMatchResult(
        intent_id=mejor_intencion["intent_id"],
        categoria=mejor_intencion["categoria"],
        puntaje_coincidencia=mejor_puntaje,
        keywords_detectadas=mejores_coincidencias,
        respuesta_institucional_exacta=mejor_intencion["respuesta_oficial"],
        enlaces_oficiales=mejor_intencion.get("enlaces_oficiales", []),
        es_fallback=False
    )
