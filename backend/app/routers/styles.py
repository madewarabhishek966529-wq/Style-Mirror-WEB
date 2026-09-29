from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Style
from app.schemas import StyleSchema

router = APIRouter(prefix="/v1", tags=["styles"])

@router.get("/styles", response_model=List[StyleSchema])
def get_styles(
    type: Optional[str] = Query(None, pattern="^(hair|beard)$"),
    db: Session = Depends(get_db)
):
    """
    Returns catalog of hairstyles and beard styles.
    Filter by ?type=hair or ?type=beard.
    """
    query = db.query(Style).filter(Style.is_active == True)
    if type:
        query = query.filter(Style.type == type)
    styles = query.order_by(Style.sort_order.asc()).all()
    return styles
