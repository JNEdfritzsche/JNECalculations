# lib/theory.py
from __future__ import annotations

import re
from pathlib import Path
import streamlit as st


# Convert common LaTeX wrappers often found in exported documents:
#   \[ ... \]  -> $$ ... $$
#   \( ... \)  -> $ ... $
_LATEX_BLOCK_PATTERNS = [
    (re.compile(r"\\\[(.*?)\\\]", flags=re.DOTALL), r"$$\1$$"),
]

_LATEX_INLINE_PATTERNS = [
    (re.compile(r"\\\((.*?)\\\)", flags=re.DOTALL), r"$\1$"),
]


def _normalize_latex(md: str) -> str:
    # Convert \[...\] to $$...$$
    for rx, repl in _LATEX_BLOCK_PATTERNS:
        md = rx.sub(repl, md)

    # Convert \(...\) to $...$
    for rx, repl in _LATEX_INLINE_PATTERNS:
        md = rx.sub(repl, md)

    return md


def _inject_css():
    # Minimal styling to make markdown read nicely while keeping Streamlit defaults.
    st.markdown(
        """
        <style>
          .jne-theory-wrap {
            line-height: 1.55;
            font-size: 0.98rem;
          }
          .jne-theory-wrap h1, .jne-theory-wrap h2, .jne-theory-wrap h3 {
            margin-top: 1.2rem;
            margin-bottom: 0.6rem;
          }
          .jne-theory-wrap p {
            margin: 0.45rem 0;
          }
          .jne-theory-wrap code {
            font-size: 0.92em;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_md(md_path: str | Path, *, wrap: bool = True):
    """
    Render a markdown file into Streamlit with light CSS + LaTeX normalization.

    - Supports $$...$$ blocks and $...$ inline
    - Converts \\[...\\] and \\(...\\) into $$...$$ / $...$
    """
    p = Path(md_path)
    if not p.exists():
        st.error(f"Markdown file not found: {p}")
        return

    _inject_css()

    md = p.read_text(encoding="utf-8")
    md = _normalize_latex(md)

    if wrap:
        st.markdown("<div class='jne-theory-wrap'>", unsafe_allow_html=True)
        st.markdown(md, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(md, unsafe_allow_html=True)
