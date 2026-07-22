"""Raporlama uc noktalari: hepsi salt-okunur (GET), veri girisi yapmaz
(Anayasa m.2). Her endpoint app/modules/reports/service.py'deki turetme
mantigini cagirir; hicbir hesaplama burada yapilmaz."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.reports import service
from app.modules.reports.schemas import (
    BredAnimalRead,
    BreedingCandidateRead,
    BreedingPerformanceRead,
    CalvingRead,
    DashboardSummaryRead,
    HerdInventoryRead,
    PenOccupancyRead,
    PregnancyCheckResultRead,
    PregnantAnimalRead,
    RepeatBreederRead,
    YoungAnimalRead,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/breeding-candidates", response_model=list[BreedingCandidateRead])
def breeding_candidates(db: Session = Depends(get_db)) -> list[BreedingCandidateRead]:
    return service.list_breeding_candidates(db)


@router.get("/bred-animals", response_model=list[BredAnimalRead])
def bred_animals(db: Session = Depends(get_db)) -> list[BredAnimalRead]:
    return service.list_bred_animals(db)


@router.get("/repeat-breeders", response_model=list[RepeatBreederRead])
def repeat_breeders(db: Session = Depends(get_db)) -> list[RepeatBreederRead]:
    return service.list_repeat_breeders(db)


@router.get("/pregnant-animals", response_model=list[PregnantAnimalRead])
def pregnant_animals(db: Session = Depends(get_db)) -> list[PregnantAnimalRead]:
    return service.list_pregnant_animals(db)


@router.get("/calving", response_model=list[CalvingRead])
def calving(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[CalvingRead]:
    return service.list_calvings(db, start_date, end_date)


@router.get("/breeding-performance", response_model=list[BreedingPerformanceRead])
def breeding_performance(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[BreedingPerformanceRead]:
    return service.list_breeding_performance(db, start_date, end_date)


@router.get("/pregnancy-check-results", response_model=list[PregnancyCheckResultRead])
def pregnancy_check_results(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[PregnancyCheckResultRead]:
    return service.list_pregnancy_check_results(db, start_date, end_date)


@router.get("/calves", response_model=list[YoungAnimalRead])
def calves(db: Session = Depends(get_db)) -> list[YoungAnimalRead]:
    return service.list_calves(db)


@router.get("/heifers-steers", response_model=list[YoungAnimalRead])
def heifers_steers(db: Session = Depends(get_db)) -> list[YoungAnimalRead]:
    return service.list_heifers_and_steers(db)


@router.get("/pen-occupancy", response_model=list[PenOccupancyRead])
def pen_occupancy(db: Session = Depends(get_db)) -> list[PenOccupancyRead]:
    return service.list_pen_occupancy(db)


@router.get("/herd-inventory", response_model=HerdInventoryRead)
def herd_inventory(db: Session = Depends(get_db)) -> HerdInventoryRead:
    return service.get_herd_inventory(db)


@router.get("/dashboard-summary", response_model=DashboardSummaryRead)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummaryRead:
    return service.get_dashboard_summary(db)
