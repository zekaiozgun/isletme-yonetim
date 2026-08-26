import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.lookup_router import build_lookup_router
from app.modules.animal import service
from app.modules.reports import service as reports_service
from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.auth.models import User
from app.modules.animal.lookups import (
    AnimalStatus,
    BirthType,
    Breed,
    DeathReason,
    EntrySource,
    Gender,
    HornStatus,
    LitterType,
    SourceFarm,
)
from app.modules.animal.schemas import (
    AnimalCancelEntry,
    AnimalCreate,
    AnimalRead,
    PedigreeNodeRead,
)

router = APIRouter(prefix="/animals", tags=["animals"])


@router.post("", response_model=AnimalRead, status_code=201)
def create_animal(
    payload: AnimalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> AnimalRead:
    try:
        return service.create_animal(db, payload, created_by_role=user.role)
    except NotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=list[AnimalRead])
def list_animals(status_id: int | None = None, db: Session = Depends(get_db)) -> list[AnimalRead]:
    return service.list_animals(db, status_id=status_id)


# Master Data listeleri (Anayasa m.6): arayuz dropdown'lari bunlardan beslenir.
# NOT: Bu literal-path lookup route'lari, asagidaki /{animal_id} route'undan
# ONCE kayit edilmelidir - Starlette rotalari kayit sirasina gore esler
# (en spesifik olana gore degil), aksi halde "/animals/breeds" gibi bir
# istek yanlislikla /{animal_id}'e (gecersiz UUID hatasiyla) duser.
lookup_routers = [
    build_lookup_router(Breed, "/breeds", "animal-lookups", "ırk"),
    build_lookup_router(Gender, "/genders", "animal-lookups", "cinsiyet"),
    build_lookup_router(BirthType, "/birth-types", "animal-lookups", "doğum şekli"),
    build_lookup_router(LitterType, "/litter-types", "animal-lookups", "doğum tipi"),
    build_lookup_router(HornStatus, "/horn-statuses", "animal-lookups", "boynuz durumu"),
    build_lookup_router(SourceFarm, "/source-farms", "animal-lookups", "kaynak işletme"),
    build_lookup_router(EntrySource, "/entry-sources", "animal-lookups", "giriş kaynağı"),
    build_lookup_router(AnimalStatus, "/statuses", "animal-lookups", "statü"),
    build_lookup_router(DeathReason, "/death-reasons", "animal-lookups", "ölüm nedeni"),
]
for lookup_router in lookup_routers:
    router.include_router(lookup_router)


@router.get("/{animal_id}", response_model=AnimalRead)
def get_animal(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> AnimalRead:
    try:
        return service.get_animal(db, animal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{animal_id}/age-days")
def get_animal_age(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> dict[str, int | None]:
    """Anayasa m.4/m.5: yas saklanmaz, istek aninda hesaplanir. Animal.age_days
    (bkz. models.py) satilmis/olmus bir hayvanda status_date'i referans alir -
    cikistan sonra yaslanmaya devam etmez."""
    try:
        animal = service.get_animal(db, animal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"age_days": animal.age_days}


@router.get("/{animal_id}/pedigree", response_model=PedigreeNodeRead)
def get_animal_pedigree(
    animal_id: uuid.UUID, generations: int = 4, db: Session = Depends(get_db)
) -> PedigreeNodeRead:
    """Anayasa m.4/m.5: soy agaci hicbir yerde saklanmaz, mother_id/
    father_sire_id zincirinden istek aninda kurulur (bkz. service.get_pedigree_tree)."""
    try:
        return service.get_pedigree_tree(db, animal_id, generations)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{animal_id}/genetic-composition")
def get_animal_genetic_composition(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> dict[str, str | None]:
    """Anayasa m.4/m.5: irk karmasi hicbir yerde saklanmaz, soy agacindan
    istek aninda turetilir (bkz. reports/service.py
    get_animal_genetic_composition_text) - orn. "Angus %75, Belirsiz %25"."""
    text = reports_service.get_animal_genetic_composition_text(db, animal_id)
    if text is None:
        raise HTTPException(status_code=404, detail=f"Animal bulunamadi: {animal_id}")
    return {"composition_text": text}


@router.put("/{animal_id}", response_model=AnimalRead)
def update_animal(
    animal_id: uuid.UUID,
    payload: AnimalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AnimalRead:
    try:
        return service.update_animal(db, animal_id, payload, requester_role=user.role)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{animal_id}/cancel-entry", response_model=AnimalRead)
def cancel_animal_entry(
    animal_id: uuid.UUID, payload: AnimalCancelEntry, db: Session = Depends(get_db)
) -> AnimalRead:
    """Hatalı Giriş İptali: hem Çalışan hem Yönetici kullanabilir, kilitli
    kayıtlar için BİLİNÇLİ istisna - düzeltmenin tek yolu budur."""
    try:
        return service.cancel_animal_entry(db, animal_id, payload.note)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{animal_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_animal(animal_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        service.delete_animal(db, animal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
