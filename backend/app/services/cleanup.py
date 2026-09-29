import asyncio
import logging
from datetime import datetime, timezone
from app.db import SessionLocal
from app.models import Photo
from app.services.storage import delete_photo_storage

logger = logging.getLogger(__name__)

async def cleanup_expired_photos_loop(interval_seconds: int = 900):
    """
    Periodic worker running in background lifespan.
    Checks and removes photos and generated outputs older than their expiry time (24h).
    """
    logger.info("Started 24-hour photo TTL cleanup worker")
    while True:
        try:
            now = datetime.now(timezone.utc)
            db = SessionLocal()
            expired_photos = db.query(Photo).filter(Photo.expires_at < now).all()
            if expired_photos:
                logger.info(f"Found {len(expired_photos)} expired photo sessions to purge")
                for p in expired_photos:
                    try:
                        delete_photo_storage(p.id)
                    except Exception as fe:
                        logger.error(f"Error purging storage for photo {p.id}: {fe}")
                    db.delete(p)
                db.commit()
            db.close()
        except asyncio.CancelledError:
            logger.info("Cleanup worker task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in cleanup worker: {e}")

        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            break
