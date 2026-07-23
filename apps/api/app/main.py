from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core import audit  # noqa: F401 - import kaydi tetikler (mapper event listener'lari)
from app.core.config import get_settings
from app.core.exceptions import ConflictError, DomainError, NotFoundError
from app.core.request_context import current_user_id
from app.modules.animal.router import router as animal_router
from app.modules.audit.router import router as audit_router
from app.modules.auth.dependencies import extract_bearer_token, get_current_user
from app.modules.auth.router import router as auth_router
from app.modules.auth.security import decode_access_token
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


@app.middleware("http")
async def set_current_user_context(request: Request, call_next):
    """current_user_id contextvar'ini istegin EN DISINDAKI async baglamda
    (route/dependency'lerin calistigi threadpool'lardan ONCE) set eder.
    Boylece her run_in_threadpool cagrisi bu degeri iceren bir context
    kopyalar - get_current_user Depends'i icinde set etmeye calismak
    islemez (o zaten ayri bir threadpool cagrisidir, disariya yazamaz).
    Bu middleware sadece audit log icin gozlemseldir; yetkilendirmeyi
    hala get_current_user/require_admin (401/403) yapar."""
    token = extract_bearer_token(request)
    user_id = decode_access_token(token) if token else None
    reset_token = current_user_id.set(user_id)
    try:
        return await call_next(request)
    finally:
        current_user_id.reset(reset_token)


# /auth/login (ve /health, asagida) girissiz erisilebilen tek uc noktalar -
# geri kalan tum router'lar get_current_user'a bagimli, gecerli bir JWT
# (Authorization: Bearer ...) olmadan 401 doner.
app.include_router(auth_router)
app.include_router(audit_router)

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
    app.include_router(router, dependencies=[Depends(get_current_user)])


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
