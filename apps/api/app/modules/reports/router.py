"""Raporlama uc noktalari: hepsi salt-okunur (GET), veri girisi yapmaz
(Anayasa m.2). Her endpoint app/modules/reports/service.py'deki turetme
mantigini cagirir; hicbir hesaplama burada yapilmaz."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.reports import service
from app.modules.reports.schemas import (
    AnimalEvaluationReportRead,
    AnimalMarketValueRead,
    AnimalProfitabilityRead,
    BredAnimalRead,
    BreedingCandidateRead,
    BreedingPerformanceRead,
    BreedingRecommendationRead,
    CalvingIntervalRead,
    CalvingRead,
    DashboardSummaryRead,
    DeathLossReportRead,
    FeedConsumptionRead,
    FeedStockStatusRead,
    HealthEventReportRead,
    HerdCostSummaryRead,
    HerdExitRead,
    HerdFlowReportRead,
    HerdInventoryRead,
    HerdStatusSummaryRead,
    MotherPerformanceRead,
    OffspringByMotherRead,
    OffspringBySireRead,
    PenEfficiencyRead,
    PenOccupancyRead,
    PregnancyCheckResultRead,
    SalesReportRead,
    SirePerformanceRead,
    WeightGainRead,
    WithdrawalPeriodRead,
    YoungAnimalRead,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/breeding-candidates", response_model=list[BreedingCandidateRead])
def breeding_candidates(db: Session = Depends(get_db)) -> list[BreedingCandidateRead]:
    return service.list_breeding_candidates(db)


@router.get("/bred-animals", response_model=list[BredAnimalRead])
def bred_animals(db: Session = Depends(get_db)) -> list[BredAnimalRead]:
    return service.list_bred_animals(db)


@router.get("/withdrawal-periods", response_model=list[WithdrawalPeriodRead])
def withdrawal_periods(db: Session = Depends(get_db)) -> list[WithdrawalPeriodRead]:
    return service.list_active_withdrawal_periods(db)


@router.get("/calving", response_model=list[CalvingRead])
def calving(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[CalvingRead]:
    return service.list_calvings(db, start_date, end_date)


@router.get("/offspring-by-mother", response_model=list[OffspringByMotherRead])
def offspring_by_mother(db: Session = Depends(get_db), q: str | None = Query(None)) -> list[OffspringByMotherRead]:
    return service.list_offspring_by_mother(db, q)


@router.get("/offspring-by-sire", response_model=list[OffspringBySireRead])
def offspring_by_sire(db: Session = Depends(get_db), q: str | None = Query(None)) -> list[OffspringBySireRead]:
    return service.list_offspring_by_sire(db, q)


@router.get("/mother-performance", response_model=list[MotherPerformanceRead])
def mother_performance(db: Session = Depends(get_db)) -> list[MotherPerformanceRead]:
    return service.list_mother_performance(db)


@router.get("/sire-performance", response_model=list[SirePerformanceRead])
def sire_performance(db: Session = Depends(get_db)) -> list[SirePerformanceRead]:
    return service.list_sire_performance(db)


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


@router.get("/health-events", response_model=list[HealthEventReportRead])
def health_events_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[HealthEventReportRead]:
    return service.list_health_events(db, start_date, end_date)


@router.get("/weight-gains", response_model=list[WeightGainRead])
def weight_gains(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[WeightGainRead]:
    return service.list_weight_gains(db, start_date, end_date)


@router.get("/sales", response_model=list[SalesReportRead])
def sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[SalesReportRead]:
    return service.list_sales_report(db, start_date, end_date)


@router.get("/deaths", response_model=list[DeathLossReportRead])
def death_losses(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[DeathLossReportRead]:
    return service.list_death_losses(db, start_date, end_date)


@router.get("/herd-flow", response_model=list[HerdFlowReportRead])
def herd_flow(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[HerdFlowReportRead]:
    return service.list_herd_flow(db, start_date, end_date)


@router.get("/feed-consumption", response_model=list[FeedConsumptionRead])
def feed_consumption(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[FeedConsumptionRead]:
    return service.list_feed_consumption(db, start_date, end_date)


@router.get("/feed-stock-status", response_model=list[FeedStockStatusRead])
def feed_stock_status(as_of_date: date | None = None, db: Session = Depends(get_db)) -> list[FeedStockStatusRead]:
    return service.list_feed_stock_status(db, as_of_date)


@router.get("/calving-intervals", response_model=list[CalvingIntervalRead])
def calving_intervals(db: Session = Depends(get_db)) -> list[CalvingIntervalRead]:
    return service.list_calving_intervals(db)


@router.get("/active-animals", response_model=list[YoungAnimalRead])
def active_animals(
    status_ids: list[int] = Query(default=[]), db: Session = Depends(get_db)
) -> list[YoungAnimalRead]:
    return service.list_animals_by_status(db, status_ids or None)


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


@router.get("/herd-status-summary", response_model=list[HerdStatusSummaryRead])
def herd_status_summary(db: Session = Depends(get_db)) -> list[HerdStatusSummaryRead]:
    return service.list_herd_status_summary(db)


@router.get("/dashboard-summary", response_model=DashboardSummaryRead)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummaryRead:
    return service.get_dashboard_summary(db)


@router.get("/pen-efficiency", response_model=list[PenEfficiencyRead])
def pen_efficiency(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[PenEfficiencyRead]:
    return service.list_pen_efficiency(db, start_date, end_date)


@router.get("/animal-profitability", response_model=list[AnimalProfitabilityRead])
def animal_profitability(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[AnimalProfitabilityRead]:
    return service.list_animal_profitability(db, start_date, end_date)


@router.get("/herd-cost-summary", response_model=list[HerdCostSummaryRead])
def herd_cost_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[HerdCostSummaryRead]:
    return service.list_herd_cost_summary(db, start_date, end_date)


@router.get("/herd-animal-market-values", response_model=list[AnimalMarketValueRead])
def herd_animal_market_values(
    as_of_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[AnimalMarketValueRead]:
    return service.list_herd_animal_market_values(db, as_of_date)


@router.get("/animal-evaluations", response_model=list[AnimalEvaluationReportRead])
def animal_evaluations_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[AnimalEvaluationReportRead]:
    return service.list_animal_evaluations_report(db, start_date, end_date)


@router.get("/breeding-recommendations", response_model=list[BreedingRecommendationRead])
def breeding_recommendations(db: Session = Depends(get_db)) -> list[BreedingRecommendationRead]:
    return service.list_breeding_recommendations(db)


@router.get("/herd-exits", response_model=list[HerdExitRead])
def herd_exits(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[HerdExitRead]:
    return service.list_herd_exits(db, start_date, end_date)
