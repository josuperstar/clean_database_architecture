from __future__ import annotations

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


def canonical_shot_label(row: RawShotRow) -> str:
    """
    One studio-facing label for a shot.

    Trackers often expose both a ``name`` and a ``code``; in this app they are treated
    as the same concept: we pick a single non-empty string (prefer ``name``, else ``code``,
    else the external id).
    """
    name = (row.name or "").strip()
    code = (row.code or "").strip()
    label = name or code or str(row.external_id).strip()
    return label
