"""Streamlit web interface for the AI-Assisted Advertisement Generator."""
from pathlib import Path
import tempfile

import streamlit as st
from advertisement_generator import CATEGORY_RULES, render_ad

st.set_page_config(page_title="AI Advertisement Generator", page_icon="🎨", layout="wide")
st.title("AI-Assisted Advertisement Generator")
st.caption("Turn a product brief into a 1080 × 1080 PNG advertisement concept.")
st.info("This prototype uses a local, rule-based recommendation engine. It does not call an external generative-AI service.")

with st.sidebar:
    st.header("Advertisement brief")
    with st.form("ad_form"):
        product = st.text_input("Product or campaign", "PulseFit Protein", max_chars=90)
        audience = st.text_input("Target audience", "Gym Goers", max_chars=90)
        requirements = st.text_area("Design requirements", "bold, modern, energetic", max_chars=250)
        submitted = st.form_submit_button("Generate advertisement", type="primary", use_container_width=True)
    st.caption("Categories: " + ", ".join(x.title() for x in CATEGORY_RULES))

if "ad_png" not in st.session_state:
    st.session_state.ad_png = None
    st.session_state.plan = None

if submitted:
    if not product.strip() or not audience.strip():
        st.error("Enter both a product name and a target audience.")
    else:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "generated_ad.png"
                plan = render_ad(product.strip(), audience.strip(), requirements.strip(), path)
                st.session_state.ad_png = path.read_bytes()
                st.session_state.plan = plan
                st.session_state.product = product.strip()
        except Exception as exc:
            st.error(f"Could not generate the advertisement: {exc}")

if st.session_state.ad_png:
    plan = st.session_state.plan
    col1, col2 = st.columns([1.15, 1], gap="large")
    with col1:
        st.subheader("Generated advertisement")
        st.image(st.session_state.ad_png, use_container_width=True)
        safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in st.session_state.product).strip("_")
        st.download_button("Download PNG", st.session_state.ad_png, file_name=f"{safe or 'advertisement'}_ad.png",
                           mime="image/png", type="primary", use_container_width=True)
    with col2:
        st.subheader("Design recommendations")
        st.metric("Detected category", plan.category.title())
        st.metric("Heuristic design-strength score", f"{plan.confidence}%")
        st.caption("This score is not model accuracy or a statistical probability.")
        st.markdown(f"**Tagline:** {plan.tagline}")
        st.markdown(f"**Call to action:** {plan.cta}")
        st.markdown(f"**Typography:** {plan.typography}")
        st.markdown(f"**Layout:** {plan.layout}")
        st.markdown("**Matched signals:** " + (", ".join(plan.matched_keywords) or "No matching keyword; technology fallback used"))
        st.markdown("**Palette:**")
        swatches = st.columns(3)
        for col, rgb in zip(swatches, plan.palette):
            color = "#%02x%02x%02x" % rgb
            col.markdown(f"<div style='background:{color};height:44px;border-radius:8px;border:1px solid #888'></div><p style='text-align:center'>{color}</p>", unsafe_allow_html=True)
        st.warning("Review claims, spelling, pricing, trademarked assets, and brand guidelines before using an ad commercially.")
else:
    st.markdown("### How it works")
    steps = st.columns(4)
    for col, label, details in zip(steps, ["1 · Enter a brief", "2 · Analyze intent", "3 · Build a design", "4 · Export PNG"],
                                  ["Provide product, audience, and requirements", "Score categories using keywords", "Select a palette, tagline, CTA, and product motif", "Download the square advertisement"]):
        with col:
            st.subheader(label)
            st.write(details)
    st.write("Fill in the brief in the sidebar and click **Generate advertisement**.")
