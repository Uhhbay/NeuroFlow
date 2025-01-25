from .homepage import router as homepage_router
from .try_page import router as try_page_router

# Export all routers for easy import in main.py
__all__ = ["homepage_router", "try_page_router"]
