import itertools
import os
import logging
from typing import Set

logger = logging.getLogger(__name__)

class KeyPool:
    def __init__(self, env_name: str = "GEMINI_API_KEYS"):
        self.env_name = env_name
        self.raw_val = os.getenv(env_name, "")
        self._keys = [k.strip() for k in self.raw_val.split(",") if k.strip() and not k.strip().startswith("your_")]
        self._invalid_keys: Set[str] = set()
        self._cycle = itertools.cycle(self._keys) if self._keys else None
        self._size = len(self._keys)

    def reload(self):
        self.raw_val = os.getenv(self.env_name, "")
        self._keys = [k.strip() for k in self.raw_val.split(",") if k.strip() and not k.strip().startswith("your_")]
        self._cycle = itertools.cycle(self._keys) if self._keys else None
        self._size = len(self._keys)

    @property
    def has_keys(self) -> bool:
        return len(self._keys) > 0

    @property
    def size(self) -> int:
        return len(self._keys)

    def next(self) -> str:
        if not self._keys:
            # Try reloading from env once
            self.reload()
        if not self._keys:
            raise RuntimeError(f"{self.env_name} is empty or has no valid keys")
        
        # Find next valid key
        attempts = 0
        while attempts < len(self._keys):
            key = next(self._cycle)
            attempts += 1
            if key not in self._invalid_keys:
                return key
        
        # If all were marked invalid, reset invalid list once and return
        self._invalid_keys.clear()
        return next(self._cycle)

    def mark_invalid(self, key: str):
        logger.warning(f"Key marked invalid or quota exceeded in {self.env_name} pool")
        self._invalid_keys.add(key)

gemini_key_pool = KeyPool("GEMINI_API_KEYS")
