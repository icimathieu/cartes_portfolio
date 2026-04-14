import base64
from pathlib import Path
import streamlit as st


def _logo_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def render_footer():
    logos_dir = Path("assets/logos")
    logo_chartes  = _logo_base64(logos_dir / "logo-chartes-psl-coul_0.png")
    logo_carta    = _logo_base64(logos_dir / "20250115_logo_cartadata.png")
    logo_vaucluse = _logo_base64(logos_dir / "logo-dept-vaucluse-2025.svg_.png")

    st.markdown("---")
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:center;
                    gap:48px; padding:16px 0 8px 0;">
            <img src="data:image/png;base64,{logo_chartes}"
                 style="height:52px; object-fit:contain;">
            <img src="data:image/png;base64,{logo_carta}"
                 style="height:64px; object-fit:contain;">
            <img src="data:image/png;base64,{logo_vaucluse}"
                 style="height:52px; object-fit:contain;">
        </div>
        """,
        unsafe_allow_html=True,
    )
