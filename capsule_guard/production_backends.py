from __future__ import annotations

from importlib.util import find_spec


def detect_vector_backend_support() -> dict[str, dict[str, object]]:
    backends = {
        "faiss": "faiss",
        "chromadb": "chromadb",
        "lancedb": "lancedb",
    }
    return {
        name: {
            "installed": find_spec(module_name) is not None,
            "module": module_name,
            "integration": "optional_external_vector_backend",
        }
        for name, module_name in backends.items()
    }
