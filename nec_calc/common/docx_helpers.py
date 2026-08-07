from __future__ import annotations

from html import escape

from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


def omml_r(text: str) -> str:
    return f"<m:r><m:t>{escape(str(text))}</m:t></m:r>"


def omml_sub(base: str, sub: str) -> str:
    return (
        "<m:sSub>"
        f"<m:e>{omml_r(base)}</m:e>"
        f"<m:sub>{omml_r(sub)}</m:sub>"
        "</m:sSub>"
    )


def omml_frac(num_inner: str, den_inner: str) -> str:
    return (
        "<m:f>"
        f"<m:num>{num_inner}</m:num>"
        f"<m:den>{den_inner}</m:den>"
        "</m:f>"
    )


def omml_sqrt(inner: str) -> str:
    return f'<m:rad><m:degHide m:val="1"/><m:e>{inner}</m:e></m:rad>'


def add_omml_equation_to_paragraph(p, omml_inner: str) -> None:
    xml = f'<m:oMath {nsdecls("m")}>{omml_inner}</m:oMath>'
    p._p.append(parse_xml(xml))


def add_word_equation(doc, label: str, omml_inner: str) -> None:
    p = doc.add_paragraph()
    p.add_run(f"{label}: ").bold = True
    add_omml_equation_to_paragraph(p, omml_inner)


__all__ = [
    "omml_r",
    "omml_sub",
    "omml_frac",
    "omml_sqrt",
    "add_omml_equation_to_paragraph",
    "add_word_equation",
]