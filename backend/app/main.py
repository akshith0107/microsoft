from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import KiranaAPIException, kirana_exception_handler
from app.core.logging import setup_logging, logger
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Kirana AI Backend Server", env=settings.APP_ENV)
    try:
        from app.db.base import Base
        from app.db.session import async_engine
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.warning(f"Database table initialization warning: {str(e)}")
    yield
    logger.info("Shutting down Kirana AI Backend Server")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-grade AI-powered Kirana Retail Shop Operating System API",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan
    )

    # CORS configuration
    origins = settings.CORS_ORIGINS
    if isinstance(origins, str):
        origins = [i.strip() for i in origins.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(set(origins + [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:4000",
            "http://127.0.0.1:4000",
        ])),
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.vercel\.app)(:[0-9]+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Exception Handlers
    app.add_exception_handler(KiranaAPIException, kirana_exception_handler)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred while processing your request.",
                    "details": str(exc) if settings.APP_ENV != "production" else None
                }
            }
        )

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
