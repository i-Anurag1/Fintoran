from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class Provenance:
    provider: str
    source: str
    retrieved_at: str
    dataset_date_range: str | None = None
    license_note: str | None = None
    cache_timestamp: str | None = None

    @classmethod
    def now(cls, provider: str, source: str, *, dataset_date_range=None, license_note=None, cache_timestamp=None):
        return cls(provider, source, datetime.now(timezone.utc).isoformat(), dataset_date_range, license_note, cache_timestamp)

    def as_dict(self):
        return {k: v for k, v in {
            'provider': self.provider,
            'source': self.source,
            'retrieved_at': self.retrieved_at,
            'dataset_date_range': self.dataset_date_range,
            'license_note': self.license_note,
            'cache_timestamp': self.cache_timestamp,
        }.items() if v is not None}
