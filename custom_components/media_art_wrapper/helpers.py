from __future__ import annotations

import base64

# Shared fallback image (small PNG placeholder shown when no cover is available).
# Used by both the Image and Camera entities to avoid duplicating the binary blob.
FALLBACK_IMAGE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAABQUlEQVR42u3cMRGAMAAEwVeSGglowAqKcBY3QQAVM+l+izPAb8NAkvN6lnqLhwCABwGAABAAAkAACAABIAAEgAAQAAJAAAgAASAABIAAEAACQAAIAAEgAASAABAAAkAACAABIAAEgAAQAAJAAAgAASAABIAAEAACQAAIAAEgAASAABAAO1vz/h0ApcM3QYjhuyHE+N0IYvhuCDF+N4IYvxsBAAAYvxlBjN+NAAAAjN+MAAAAjN+MAAAAAAAAAADaABxjfAIAAAAAAAAAAAAAwFsAAAAAAAAAAAAAga+BAAAAgT+CAAAAAn8FQ+BcAAAAQOBsoNPBALgfAAA3hADgjiAA3BIGgAAQAAJAAAgAASAABIAAEAACQAAIAAEgAASAABAAAkAACAABIAAEgAAQAAJAAAgAASAABIAAEAACQNt6Adpn9COM5b1AAAAAAElFTkSuQmCC"
)


def source_name(source_entity_id: str) -> str:
    """Return a human-readable name derived from a media_player entity id."""
    object_id = source_entity_id.split(".", 1)[-1]
    return object_id.replace("_", " ").title()
