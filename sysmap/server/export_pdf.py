"""PDF report generator for sysmap."""

import os
from typing import Optional

from .export_html import generate_html_report


def generate_pdf_report(output_path: str = "sysmap_report.pdf", html_path: Optional[str] = None) -> str:
    """Generate a PDF report from the HTML report."""
    if html_path is None:
        html_path = "sysmap_report.html"
        generate_html_report(output_path=html_path)

    try:
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(output_path)
        return output_path
    except ImportError:
        # Fallback: convert HTML to PDF using browser if available
        try:
            import subprocess
            result = subprocess.run(
                ['chromium', '--headless', '--print-to-pdf=' + output_path, html_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0:
                return output_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Last fallback: just return HTML path with note
        raise ImportError(
            "PDF generation requires 'weasyprint' (pip install sysmap[pdf]) "
            "or Chromium/Chrome browser. HTML report generated instead."
        )
