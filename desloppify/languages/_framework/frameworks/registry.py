"""Framework spec registry (analogous to tree-sitter spec registry)."""

from __future__ import annotations

from collections.abc import Iterable

from .types import FrameworkSpec

FRAMEWORK_SPECS: dict[str, FrameworkSpec] = {}


def register_framework_spec(spec: FrameworkSpec) -> None:
    """Register a framework spec by id."""
    key = str(spec.id or "").strip()
    if not key:
        raise ValueError("FrameworkSpec.id must be non-empty")
    FRAMEWORK_SPECS[key] = spec


def get_framework_spec(framework_id: str) -> FrameworkSpec | None:
    """Return a registered framework spec by id."""
    key = str(framework_id or "").strip()
    if not key:
        return None
    return FRAMEWORK_SPECS.get(key)


def list_framework_specs(*, ecosystem: str | None = None) -> dict[str, FrameworkSpec]:
    """Return a copy of the framework registry, optionally filtered by ecosystem."""
    if ecosystem is None:
        return dict(FRAMEWORK_SPECS)
    eco = str(ecosystem or "").strip().lower()
    if not eco:
        return dict(FRAMEWORK_SPECS)
    return {k: v for k, v in FRAMEWORK_SPECS.items() if str(v.ecosystem).lower() == eco}


def _register_builtin_specs() -> None:
    """Register built-in framework specs shipped with the repo."""
    if FRAMEWORK_SPECS:
        return
    from .specs.astro import ASTRO_SPEC
    from .specs.nextjs import NEXTJS_SPEC
    from .specs.svelte import SVELTE_SPEC
    from .specs.vue import VUE_SPEC

    register_framework_spec(NEXTJS_SPEC)
    register_framework_spec(ASTRO_SPEC)
    register_framework_spec(SVELTE_SPEC)
    register_framework_spec(VUE_SPEC)


def ensure_builtin_specs_loaded() -> None:
    """Idempotently load built-in framework specs."""
    _register_builtin_specs()


def framework_source_extensions(ecosystem: str | None = None) -> tuple[str, ...]:
    """Return the sorted, deduplicated source extensions across registered specs.

    Used by dep-graph builders to learn which non-host-language file types
    (e.g. ``.astro``, ``.svelte``, ``.vue``) should be scanned as importers
    of the host language's modules. Lookup is driven by the registry, so
    adding a new framework with ``source_extensions`` automatically extends
    every plugin that calls this — no infrastructure edits required.
    """
    ensure_builtin_specs_loaded()
    return tuple(
        sorted(
            {
                ext
                for spec in list_framework_specs(ecosystem=ecosystem).values()
                for ext in spec.source_extensions
            }
        )
    )


__all__ = [
    "FRAMEWORK_SPECS",
    "ensure_builtin_specs_loaded",
    "framework_source_extensions",
    "get_framework_spec",
    "list_framework_specs",
    "register_framework_spec",
]
