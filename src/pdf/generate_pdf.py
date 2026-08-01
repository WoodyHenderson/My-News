from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML
from pathlib import Path


def get_html():
    fp = open("digest.html", "r", encoding="utf-8")
    return fp.read()

def generate_pdf(ranked_articles, output_path: Path | None = None) -> Path:
    css = CSS('styles.css')
    html = HTML(string=get_html())
    if output_path is None:
        output_path = Path("output/digest.pdf")
    html.write_pdf(output_path, stylesheets=[css])
    return output_path
