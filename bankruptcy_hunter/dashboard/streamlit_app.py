"""Streamlit dashboard for BankruptcyHunter analyst workflows."""

from __future__ import annotations

import streamlit as st

from app.ml.classifier import RuleBasedClassifier
from app.scoring import ScoringEngine

st.set_page_config(page_title="BankruptcyHunter", layout="wide")
st.title("BankruptcyHunter")
st.caption("Multilingual bankruptcy and financial distress discovery dashboard")

text = st.text_area("Paste article text or a news snippet", height=220)
if st.button("Analyze text", type="primary"):
    if not text.strip():
        st.warning("Paste text before analyzing.")
    else:
        classification = RuleBasedClassifier().classify(text)
        score = ScoringEngine().score(classification)
        st.metric("Priority", score.priority.upper(), f"{score.score}/100")
        st.write("Classification", classification.label)
        st.write("Confidence", classification.confidence)
        st.write("Keyword hits", [hit.__dict__ for hit in classification.keyword_hits])

st.sidebar.header("External provider setup")
st.sidebar.info("TODO: Add search and translation API keys in .env before enabling live provider adapters.")
