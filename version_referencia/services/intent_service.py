"""
Motor Determinista de Intenciones Institucionales (Cero Alucinaciones).
Clasifica la consulta normalizada del aspirante contra la base de conocimiento oficial
de Admisiones de la ETITC. Jamás genera texto libre fuera del JSON institucional.
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
        """Lee y valida la estructura del archivo JSON con las FAQs de Admisiones."""
        if not self.json_path.exists():
            raise FileNotFoundError(f"No se encontró la base de conocimiento en: {self.json_path}")

        with open(self.json_path, mode="r", encoding="utf-8") as file:
            data = json.load(file)

        if "intenciones" not in data or "respuesta_fallback" not in data:
            raise ValueError("El archivo JSON institucional no contiene las llaves obligatorias.")

        return data

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
        Evalúa determinísticamente qué intención institucional corresponde al texto normalizado.
        Si ninguna intención supera el umbral mínimo (al menos 1 keyword detectada),
        retorna obligatoriamente la respuesta institucional de Fallback para evitar alucinaciones.
        """
        tokens_consulta = set(texto_normalizado.split())
        mejor_intencion: Dict[str, Any] | None = None
        mejores_keywords: List[str] = []
        mejor_puntaje: float = 0.0

        for intencion in self.kb_data.get("intenciones", []):
            keywords_coincidentes: List[str] = []
            for kw in intencion.get("keywords", []):
                kw_norm = STTService.normalizar_texto(kw)
                # Verifica coincidencia exacta de frase o de palabra individual
                if (" " in kw_norm and kw_norm in texto_normalizado) or (
                    " " not in kw_norm and kw_norm in tokens_consulta
                ):
                    keywords_coincidentes.append(kw)

            if keywords_coincidentes:
                # Puntaje normalizado: 1 keyword = 0.55, 2 keywords = 0.80, 3+ keywords = 0.98
                cantidad = len(keywords_coincidentes)
                puntaje = min(0.35 + (cantidad * 0.22), 0.99)
                if puntaje > mejor_puntaje:
                    mejor_puntaje = round(puntaje, 2)
                    mejor_intencion = intencion
                    mejores_keywords = keywords_coincidentes

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

        return IntentMatchResult(
            intent_id=mejor_intencion["intent_id"],
            categoria=mejor_intencion["categoria"],
            puntaje_coincidencia=mejor_puntaje,
            keywords_detectadas=mejores_keywords,
            respuesta_institucional_exacta=mejor_intencion["respuesta_oficial"],
            enlaces_oficiales=mejor_intencion.get("enlaces_oficiales", []),
            es_fallback=False
        )
