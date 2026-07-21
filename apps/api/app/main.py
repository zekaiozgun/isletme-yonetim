from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import ConflictError, DomainError, NotFoundError
from app.modules.animal.router import router as animal_router
from app.modules.breeding.router import router as breeding_router
from app.modules.death.router import router as death_router
from app.modules.feed.router import router as feed_router
from app.modules.genetic_resource.router import router as genetic_resource_router
from app.modules.health.router import router as health_router
from app.modules.pen.router import router as pen_router
from app.modules.reports.router import router as reports_router
from app.modules.sale.router import router as sale_router
from app.modules.weight.router import router as weight_router

settings = get_settings()

app = FastAPI(title="İşletme Yönetim API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    animal_router,
    pen_router,
    genetic_resource_router,
    weight_router,
    breeding_router,
    health_router,
    feed_router,
    sale_router,
    death_router,
    reports_router,
):
    app.include_router(router)


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DomainError)
def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.api_route("/health", methods=["GET", "HEAD"])
def health() -> dict[str, str]:
    return {"status": "ok"}
