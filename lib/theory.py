# lib/theory.py
from __future__ import annotations

import re
from pathlib import Path
import streamlit as st

# Optional: Graphviz for embedded flowcharts in markdown
try:
    import graphviz  # type: ignore
    _GRAPHVIZ_IMPORT_ERROR = None
except Exception as e:
    graphviz = None  # type: ignore
    _GRAPHVIZ_IMPORT_ERROR = str(e)


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

    # Match either image markers or flowchart markers
    marker_rx = re.compile(
        r"<!-- IMAGE_MARKER\|\|(.+?)\|\|(.+?) -->|<!-- FLOWCHART_([A-Z0-9_]+) -->",
        flags=re.DOTALL,
    )

    if wrap:
        st.markdown("<div class='jne-theory-wrap'>", unsafe_allow_html=True)

    cursor = 0
    for match in marker_rx.finditer(md):
        # Render markdown chunk before marker
        chunk = md[cursor:match.start()]
        if chunk.strip():
            st.markdown(chunk, unsafe_allow_html=True)

        image_path, alt_text, flow_id = match.groups()
        if image_path is not None:
            try:
                left, center, right = st.columns([1, 2, 1], gap="small")
                with center:
                    st.image(
                        image_path,
                        caption=alt_text if alt_text else None,
                        width="stretch",
                    )
            except Exception as e:
                st.warning(f"Failed to load image: {image_path}\n\n{e}")
        elif flow_id is not None:
            _render_flowchart(flow_id)

        cursor = match.end()

    # Render remaining markdown
    tail = md[cursor:]
    if tail.strip():
        st.markdown(tail, unsafe_allow_html=True)

    if wrap:
        st.markdown("</div>", unsafe_allow_html=True)


def _render_flowchart(flow_id: str):
    flowcharts = {
        "MOTOR_PROTECTION": """
digraph G {
  rankdir=TB;
 
  node [shape=box, style=rounded];
 
  d1 [label="Gather all \n information available"];
  d2 [label="Table 29 Row 1"];
  d1 -> d2 [label="1Φ AC"];
 
  d3 [label="Motor \n Type", shape=diamond];
  d4 [label="Starter or \n controller type", shape=diamond];
  d5 [label="Table 29 Row 5"];
  d6 [label="FLC > 30A?", shape=diamond];
  d7 [label="Table 29 Row 2"];
  d8 [label="Table 29 Row 4"];
  d9 [label="Table 29 Row 3"];
  d1 -> d3 [label="3Φ AC"];
  d3 -> d4 [label="Squirrel-cage or Synchronous"];
  d3 -> d5 [label="Wound Rotor"];
  d4 -> d6 [label="Auto-tx or \n star delta"];
  d4 -> d7 [label="FV&R"];
  d6 -> d8 [label="Yes"];
  d6 -> d9 [label="No"];
 
  d10 [label="Table 29 Row 6"];
  d1 -> d10 [label="DC"];
}
""",
    }

    dot = flowcharts.get(flow_id)
    if dot is None:
        st.warning(f"Unknown flowchart marker: {flow_id}")
        return

    if graphviz is None:
        st.warning(
            "Graphviz isn't available in this environment, so the flowchart can't render yet. "
            "Install the `graphviz` Python package (and system Graphviz if required), then reload."
        )
        if _GRAPHVIZ_IMPORT_ERROR is not None:
            with st.expander("Import error details"):
                st.exception(_GRAPHVIZ_IMPORT_ERROR)
        return

    # Keep flowcharts a bit smaller and centered for readability.
    left, center, right = st.columns([1, 2, 1], gap="small")
    with center:
        st.graphviz_chart(dot, width=600)


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
