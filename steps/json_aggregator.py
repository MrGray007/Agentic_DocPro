"""
JSON aggregation strategies for document-level representation.

This module provides an abstract base class for aggregation strategies
and a concrete implementation that merges chunk-level JSON outputs into
a single aggregated document-level JSON, preserving sets, booleans, and
average confidence.
"""

from collections import defaultdict
from langchain_core.output_parsers import JsonOutputParser
from abc import ABC, abstractmethod


class JsonAggStrategy(ABC):
    """
    Abstract base class for strategies that aggregate chunk-level JSON outputs.
    """

    @abstractmethod
    def get_agg_json(self, chunk_jsons):
        """
        Aggregate multiple chunk-level JSON objects into a single document-level JSON.

        Args:
            chunk_jsons (list): List of chunk-level JSON strings or elements.

        Returns:
            dict: Aggregated document-level JSON.
        """
        pass


class AggJson(JsonAggStrategy):
    """
    Aggregates structured chunk-level JSON signals into a single document-level representation.
    """

    def get_agg_json(self, chunk_jsons):
        parser = JsonOutputParser()

        aggregated = {
            "document_signals": defaultdict(set),
            "entities": defaultdict(set),
            "dates": set(),
            "identifiers": set(),
            "monetary_values": set(),
            "pii_detected": False,
            "contains_signature": False,
            "contains_table": False,
            "avg_chunk_confidence": 0.0,
            "chunk_count": len(chunk_jsons)
        }

        total_confidence = 0.0

        for el in chunk_jsons:
            chunk = parser.parse(el.page_content)

            # Aggregate document signals
            for category, values in chunk.get("document_signals", {}).items():
                aggregated["document_signals"][category].update(values or [])

            # Aggregate entities
            for entity_type, values in chunk.get("entities", {}).items():
                aggregated["entities"][entity_type].update(values or [])

            # Aggregate simple lists
            aggregated["dates"].update(chunk.get("dates", []))
            aggregated["identifiers"].update(chunk.get("identifiers", []))
            aggregated["monetary_values"].update(chunk.get("monetary_values", []))

            # Boolean OR logic
            aggregated["pii_detected"] |= chunk.get("pii_detected", False)
            aggregated["contains_signature"] |= chunk.get("contains_signature", False)
            aggregated["contains_table"] |= chunk.get("contains_table", False)

            total_confidence += chunk.get("confidence", 0.0)

        # Convert sets to lists
        aggregated["document_signals"] = {k: list(v) for k, v in aggregated["document_signals"].items()}
        aggregated["entities"] = {k: list(v) for k, v in aggregated["entities"].items()}
        aggregated["dates"] = list(aggregated["dates"])
        aggregated["identifiers"] = list(aggregated["identifiers"])
        aggregated["monetary_values"] = list(aggregated["monetary_values"])

        # Average confidence
        if chunk_jsons:
            aggregated["avg_chunk_confidence"] = total_confidence / len(chunk_jsons)

        return aggregated


def json_aggregator(chunk_json):
    """
    Convenience function to aggregate chunk-level JSON into document-level JSON.

    Args:
        chunk_json (list): List of chunk-level JSON elements.

    Returns:
        dict: Aggregated document-level JSON.
    """
    aggregator = AggJson()
    agg_json = aggregator.get_agg_json(chunk_json)
    return agg_json