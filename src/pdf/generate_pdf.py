from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML
from pathlib import Path


def get_html():
    fp = open("digest.html", "r", encoding="utf-8")
    return fp.read()

def generate_pdf():
    css = CSS('styles.css')
    html = HTML(string=get_html())
    out_path = Path("output/digest.pdf")
    html.write_pdf(out_path, stylesheets=[css])
    return out_path
