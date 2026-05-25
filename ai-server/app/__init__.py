__version__ = "1.0.0"
from .config import get_settings, Settings
from .chat.infrastructure.master import Master
from .chat.interface.router import router as chat_router
from .catalog.interface.router import router as catalog_router
from .auth.interface.router import router as auth_router
from .demo import depend, devtools, learn, path, tortoise_demo, ws
from .db.session import close_db_engine
from .db.tortoise_config import close_tortoise_orm, init_tortoise_orm
from .handlers import register_exception_handlers
from .middleware.response import UnifiedResponseMiddleware
from .middleware.response_cleanup import ResponseCleanupMiddleware
from .middleware.response_time import add_process_time_header
from .schemas.openapi import install_unified_openapi
