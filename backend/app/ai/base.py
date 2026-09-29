from abc import ABC, abstractmethod
from typing import Optional, List

class ImageProvider(ABC):
    @abstractmethod
    async def edit(
        self,
        user_image: bytes,
        prompt: str,
        reference_images: Optional[List[bytes]] = None
    ) -> bytes:
        """
        Executes an AI image modification on user_image based on prompt and optional references.
        Returns the output image bytes (JPEG format).
        """
        pass
