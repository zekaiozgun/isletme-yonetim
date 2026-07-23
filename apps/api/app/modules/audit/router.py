from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogRead
from app.modules.auth.dependencies import require_admin

router = APIRouter(prefix="/audit-logs", tags=["audit"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(
    table_name: str | None = None,
    limit: int = 200,
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    stmt = select(AuditLog).options(joinedload(AuditLog.user)).order_by(AuditLog.created_at.desc())
    if table_name:
        stmt = stmt.where(AuditLog.table_name == table_name)
    stmt = stmt.limit(min(limit, 1000))
    return list(db.scalars(stmt).all())
