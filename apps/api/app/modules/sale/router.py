from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.sale import service
from app.modules.sale.lookups import SaleType
from app.modules.sale.schemas import BuyerCreate, BuyerRead, SaleCreate, SaleRead

router = APIRouter(prefix="/sales", tags=["sale"])


@router.post("/buyers", response_model=BuyerRead, status_code=201)
def create_buyer(payload: BuyerCreate, db: Session = Depends(get_db)) -> BuyerRead:
    return service.create_buyer(db, payload)


@router.get("/buyers", response_model=list[BuyerRead])
def list_buyers(db: Session = Depends(get_db)) -> list[BuyerRead]:
    return service.list_buyers(db)


@router.get("/buyers/{buyer_id}", response_model=BuyerRead)
def get_buyer(buyer_id: int, db: Session = Depends(get_db)) -> BuyerRead:
    try:
        return service.get_buyer(db, buyer_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/buyers/{buyer_id}", response_model=BuyerRead)
def update_buyer(buyer_id: int, payload: BuyerCreate, db: Session = Depends(get_db)) -> BuyerRead:
    try:
        return service.update_buyer(db, buyer_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/buyers/{buyer_id}", status_code=204)
def delete_buyer(buyer_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_buyer(db, buyer_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=SaleRead, status_code=201)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)) -> SaleRead:
    return service.create_sale(db, payload)


@router.get("", response_model=list[SaleRead])
def list_sales(db: Session = Depends(get_db)) -> list[SaleRead]:
    return service.list_sales(db)


router.include_router(build_lookup_router(SaleType, "/types", "sale-lookups", "satış tipi"))


# NOT: /{sale_id} (tek segment, wildcard), yukaridaki /buyers ve /types
# route'larindan SONRA tanimlanmalidir.
@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)) -> SaleRead:
    try:
        return service.get_sale(db, sale_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{sale_id}", response_model=SaleRead)
def update_sale(sale_id: int, payload: SaleCreate, db: Session = Depends(get_db)) -> SaleRead:
    try:
        return service.update_sale(db, sale_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{sale_id}", status_code=204)
def delete_sale(sale_id: int, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_sale(db, sale_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
