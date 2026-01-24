"""
FastAPI application with vertical slicing architecture and dynamic router discovery
"""
import logging
import inspect
import sys
from importlib import import_module
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
from app.core.config import settings
from app.core.database import init_db, close_db

# Configure logging
output_dir = Path("logs")
output_dir.mkdir(exist_ok=True)

LOG_FILENAME = f"logs/logfile_{settings.environment}.log"

# Configure both file AND console logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler(sys.stdout)  # This prints to console
    ]
)
logger = logging.getLogger("resume_flow")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def discover_routers() -> List[APIRouter]:
    """
    Dynamically discover and return all APIRouter instances from feature modules.
    This function is separate to ensure it runs after all modules are importable.
    """
    routers = []
    
    # Get the absolute path to the features directory
    app_dir = Path(__file__).parent
    features_path = app_dir / "features"
    
    if not features_path.exists():
        logger.warning(f"Features directory not found: {features_path}")
        return routers
    
    logger.info(f"Scanning for routers in: {features_path.absolute()}")
    
    # Find all Python files in features directory
    python_files = list(features_path.rglob("*.py"))
    logger.info(f"Found {len(python_files)} Python files to scan")
    
    for file in python_files:
        # Skip __init__ and __pycache__
        if "__init__" in file.name or "__pycache__" in str(file):
            continue
        
        # Calculate module path relative to project root
        try:
            rel_path = file.relative_to(app_dir)
            module_parts = list(rel_path.with_suffix("").parts)
            module_name = "app." + ".".join(module_parts)
            
            logger.debug(f"Attempting to import: {module_name}")
            
            # Import the module
            module = import_module(module_name)
            
            # Find all APIRouter instances in the module
            found_routers = False
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, APIRouter):
                    # Avoid duplicates by checking if already in list
                    if obj not in routers:
                        routers.append(obj)
                        found_routers = True
                        prefix = obj.prefix or "/"
                        tags = ", ".join(obj.tags) if obj.tags else "no tags"
                        logger.info(f"✓ Discovered router: '{prefix}' ({tags}) from {module_name}")
            
            if not found_routers:
                logger.debug(f"  No routers found in {module_name}")
                
        except Exception as e:
            logger.error(f"✗ Failed to import {file.name}: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue
    
    logger.info(f"Router discovery complete. Found {len(routers)} total routers.")
    return routers


def setup_routers(app: FastAPI):
    """
    Discover and register all routers with the FastAPI app.
    Called during app initialization.
    """
    logger.info("=" * 70)
    logger.info("Starting dynamic router discovery...")
    logger.info("=" * 70)
    
    # Discover and include all routers
    discovered_routers = discover_routers()
    
    for router in discovered_routers:
        try:
            app.include_router(router)
            logger.info(f"✓ Registered router: {router.prefix or '/'}")
        except Exception as e:
            logger.error(f"✗ Failed to register router {router.prefix or '/'}: {e}")
    
    logger.info("=" * 70)
    logger.info(f"API ready with {len(discovered_routers)} routers")
    logger.info("=" * 70)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Resume Flow API...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    yield
    
    # Shutdown
    logger.info("Shutting down Resume Flow API...")
    
    # Close database connections
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")
    
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Resume Flow API",
    description="""
    AI-powered generator for:
    - Professional Cover Letters
    - Summary and Project Descriptions for CV
    - Create Resume using LaTeX
    - AI-Powered Interview System
    
    Built with FastAPI, Google's Gemini AI, Keycloak Authentication, and LaTeX.
    
    ## Authentication
    Protected endpoints require a Keycloak JWT token in the `Authorization: Bearer <token>` header.
    
    ## Getting Started
    1. Set up Keycloak and create a user
    2. Obtain a JWT token from Keycloak
    3. Include the token in the Authorization header for protected endpoints
    4. Beware of the rate limits
    """,
    version=settings.api_version,
    lifespan=lifespan,
    root_path="/api/resume-flow" if settings.environment == "production" else "",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# DYNAMIC ROUTER AUTO-DISCOVERY
# This runs immediately when the module is imported by uvicorn
# ============================================================================

setup_routers(app)

# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )