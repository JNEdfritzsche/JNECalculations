from __future__ import annotations

from pathlib import Path


PROJECT_NUMBER = ""
DESIGNER_NAME = ""
PANEL_TEMPLATE_PATH = Path("content/files/panel_schedule_template.xlsx")

def set_report_info(project_number="", designer_name=""):
    global PROJECT_NUMBER, DESIGNER_NAME
    PROJECT_NUMBER = project_number or ""
    DESIGNER_NAME = designer_name or ""

APP_DIR = Path(__file__).parent.parent
CONTENT_DIR = APP_DIR / "content"

__all__ = [
    "PROJECT_NUMBER", "DESIGNER_NAME", "PANEL_TEMPLATE_PATH", "set_report_info",
    "APP_DIR", "CONTENT_DIR",
]
