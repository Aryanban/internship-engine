import pytest
from pathlib import Path
from pypdf import PdfReader

OUTPUT_RESUMES_DIR = Path(__file__).parent.parent / "output" / "resumes"

@pytest.mark.parametrize("archetype", ["ai-agents", "product-fullstack", "systems-realtime"])
def test_resume_pdf_strictly_one_page(archetype):
    pdf_path = OUTPUT_RESUMES_DIR / f"{archetype}.pdf"
    assert pdf_path.exists(), f"Resume PDF {archetype}.pdf not generated"
    
    reader = PdfReader(str(pdf_path))
    assert len(reader.pages) == 1, f"Resume {archetype}.pdf exceeded 1 page limit (Found {len(reader.pages)} pages)"
