from fastapi import APIRouter, HTTPException
from config.database import FEATURE_FLAGS

router = APIRouter(
    prefix="/feature-flags",
    tags=["feature-flags"]
)

@router.get("")
async def get_feature_flags():
    """
    Get the current state of feature flags.
    """
    return {
        "competitor_score": FEATURE_FLAGS.get('COMPETITOR_SCORING', False)
    }

@router.post("")
async def update_feature_flags(flags: dict):
    """
    Update feature flags state.
    """
    if "competitor_score" in flags:
        FEATURE_FLAGS['COMPETITOR_SCORING'] = flags["competitor_score"]
    return FEATURE_FLAGS 