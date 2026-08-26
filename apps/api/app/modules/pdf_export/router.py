from fastapi import APIRouter, Response

from app.modules.pdf_export import service
from app.modules.pdf_export.schemas import AnimalProfilePdfRequest, PdfTableRequest

router = APIRouter(prefix="/pdf-export", tags=["pdf-export"])


@router.post("/table")
def export_table_pdf(payload: PdfTableRequest) -> Response:
    pdf_bytes = service.render_table_pdf(payload)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.post("/animal-profile")
def export_animal_profile_pdf(payload: AnimalProfilePdfRequest) -> Response:
    pdf_bytes = service.render_animal_profile_pdf(payload)
    return Response(content=pdf_bytes, media_type="application/pdf")
