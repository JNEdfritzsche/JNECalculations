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


def _resolve_image_paths(md: str, md_dir: Path) -> str:
    """
    Convert relative image paths in markdown to absolute paths.
    This fixes image rendering in Streamlit by converting:
      ![alt](image.jpg) -> ![alt](/absolute/path/to/image.jpg)
    """
    def replace_image_path(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Skip if already absolute or a URL
        if image_path.startswith(('/', 'http://', 'https://')):
            return match.group(0)
        
        # Resolve relative path
        resolved_path = (md_dir / image_path).resolve()
        return f"![{alt_text}]({resolved_path})"
    
    # Match ![alt](path) pattern
    md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_path, md)
    return md


def _extract_and_render_images(md: str, md_dir: Path) -> str:
    """
    Extract image markdown syntax and return markdown without images.
    Images will be rendered separately using st.image().
    """
    def replace_with_marker(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Skip if already absolute or a URL
        if not image_path.startswith(('/', 'http://', 'https://')):
            image_path = str((md_dir / image_path).resolve())
        
        # Create a marker to know where images should be placed
        # Use || as delimiter to avoid issues with colons in paths
        return f"\n<!-- IMAGE_MARKER||{image_path}||{alt_text} -->\n"
    
    # Match ![alt](path) pattern and replace with markers
    md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_with_marker, md)
    return md


def _render_markdown_with_images(md: str, md_dir: Path, wrap: bool = True):
    """
    Render markdown with embedded images using st.image() for image display.
    """
    # Extract images and get markdown without image syntax
    md = _extract_and_render_images(md, md_dir)
    
    # Split by image markers using || delimiter
    parts = re.split(r'<!-- IMAGE_MARKER\|\|(.+?)\|\|(.+?) -->', md)
    
    if wrap:
        st.markdown("<div class='jne-theory-wrap'>", unsafe_allow_html=True)
    
    # Process parts: alternates between markdown and image markers
    for i, part in enumerate(parts):
        if i % 3 == 0:
            # Markdown content
            if part.strip():
                st.markdown(part, unsafe_allow_html=True)
        elif i % 3 == 1:
            # Image path
            image_path = part
            if i + 1 < len(parts):
                alt_text = parts[i + 1]
                try:
                    # Center images by rendering inside a centered column
                    left, center, right = st.columns([1, 2, 1], gap="small")
                    with center:
                        # Pass the path directly; Streamlit handles local files reliably
                        st.image(
                            image_path,
                            caption=alt_text if alt_text else None,
                            width="stretch",
                        )
                except Exception as e:
                    st.warning(f"Failed to load image: {image_path}\n\n{e}")
    
    if wrap:
        st.markdown("</div>", unsafe_allow_html=True)


def render_md(md_path: str | Path, *, wrap: bool = True):
    """
    Render a markdown file into Streamlit with light CSS + LaTeX normalization.

    - Supports $$...$$ blocks and $...$ inline
    - Converts \\[...\\] and \\(...\\) into $$...$$ / $...$
    - Uses st.image() for image rendering for better compatibility
    """
    p = Path(md_path)
    if not p.exists():
        st.error(f"Markdown file not found: {p}")
        return

    _inject_css()

    md = p.read_text(encoding="utf-8")
    md = _normalize_latex(md)
    _render_markdown_with_images(md, p.parent, wrap=wrap)
