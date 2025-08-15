from __future__ import annotations
from typing import Dict
from app.common_form_sections.base import SectionComponent

# Simple in-process registry
_REGISTRY: Dict[str, SectionComponent] = {}

def register_component(name: str, component: SectionComponent):
    """Register a reusable section under a stable name."""
    _REGISTRY[name] = component

def get_component(name: str) -> SectionComponent | None:
    return _REGISTRY.get(name)

# Import modules that self-register here (add more as you create them)
from . import natural_persons  # noqa: F401  (triggers self-registration)
from . import address         # noqa: F401
from . import phone          # noqa: F401
