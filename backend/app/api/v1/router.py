from fastapi import APIRouter

from .vlm.router import router as vlm_router
from .auth.router import router as auth_router
from .keys.router import router as keys_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(vlm_router)
router.include_router(auth_router)
router.include_router(keys_router)