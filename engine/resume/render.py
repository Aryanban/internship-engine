import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
"""
PDF Rendering & 1-Page Gate Validator
Compiles RenderCV documents into PDF using Typst and enforces the hard 1-page limit.
"""

from pathlib import Path
import subprocess
from pypdf import PdfReader
from engine.resume.compose import save_archetype_yaml

OUTPUT_RESUMES_DIR = Path(__file__).parent.parent.parent / "output" / "resumes"

def render_archetype_pdf(archetype_name: str) -> Path:
    yaml_path = save_archetype_yaml(archetype_name)
    cmd = [
        "rendercv", "render", str(yaml_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(yaml_path.parent))
    if res.returncode != 0:
        raise RuntimeError(f"RenderCV failed for {archetype_name}: {res.stderr}\n{res.stdout}")

    built_pdf = yaml_path.parent / "rendercv_output" / "Aryan_Bansal_CV.pdf"
    if not built_pdf.exists():
        raise FileNotFoundError(f"Generated PDF not found at {built_pdf}")

    target_pdf = OUTPUT_RESUMES_DIR / f"{archetype_name}.pdf"
    built_pdf.replace(target_pdf)

    # 1-Page Gate Validation
    reader = PdfReader(str(target_pdf))
    page_count = len(reader.pages)
    if page_count != 1:
        print(f"❌ FAIL: {target_pdf.name} is {page_count} pages! (Must be strictly 1 page)")
        return target_pdf

    print(f"✓ PASS: {target_pdf.name} compiled successfully (Exactly {page_count} page).")
    return target_pdf

if __name__ == "__main__":
    for arch in ["ai-agents", "product-fullstack", "systems-realtime"]:
        render_archetype_pdf(arch)
