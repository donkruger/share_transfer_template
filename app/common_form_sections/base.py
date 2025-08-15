from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

class SectionComponent(ABC):
    """Interface for reusable UI sections."""

    @abstractmethod
    def render(self, *, ns: str, instance_id: str, **config) -> None:
        """Draw widgets. Persist via your persist_* helpers."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        """Return a list of human-readable error strings (empty if ok)."""
        raise NotImplementedError

    @abstractmethod
    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        """
        Return: (payload_dict, uploads_list)
        - payload_dict: JSON-safe summary
        - uploads_list: list of UploadedFiles to attach in submission email
        """
        raise NotImplementedError
