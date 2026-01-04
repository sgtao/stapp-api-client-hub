from fastapi import APIRouter

from .config_controller import router as config_router
from .hello import router as hello

from .action_controller import router as action_controller
from .message_controller import router as message_router
from .single_controller import router as single_router
from .echo_controller import router as echo_controller
from .search_controller import router as search_controller

router = APIRouter()
router.include_router(config_router)
router.include_router(hello)
router.include_router(message_router)
router.include_router(single_router)
router.include_router(echo_controller)
router.include_router(search_controller)
router.include_router(action_controller)
