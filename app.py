# -*- coding: utf-8 -*-
from pathlib import Path

import streamlit as st

from expression_tab import render_expression_tab
from word_tab import render_word_tab

st.set_page_config(page_title="Speak English", page_icon="🗣️", layout="wide")
BASE = Path(__file__).resolve().parent

st.markdown("""
<style>
.block-container{max-width:1600px;padding-top:1rem;padding-bottom:2rem}
.card{border:1px solid rgba(120,120,120,.28);border-radius:14px;padding:13px 15px;min-height:145px;margin-bottom:10px}
.card .e{font-size:20px;font-weight:800;line-height:1.25}
.card .ko{font-size:14px;font-weight:750;margin-top:8px;color:#67c5ff;line-height:1.35}
.card .ex{font-size:12px;opacity:.84;margin-top:12px;line-height:1.5}
.card .meta{font-size:11px;opacity:.58;margin-top:5px;text-transform:uppercase;letter-spacing:.03em}
.word-card{min-height:165px}
.page-caption{opacity:.72;font-size:13px;margin:8px 0 12px 0}
div[data-baseweb="tab-list"]{gap:10px}
button[data-baseweb="tab"]{font-size:16px;font-weight:750}
</style>
""", unsafe_allow_html=True)

st.title("🗣️ Speak English")
st.caption("실제 영어 회화에서 자주 쓰이는 표현과 단어를 빈도 기반으로 학습합니다.")

phrase_tab, word_tab = st.tabs(["💬 회화 표현", "📚 회화 단어"])

with phrase_tab:
    st.caption("OpenSubtitles에서 발굴한 자주 쓰는 구어체 표현 · 한국어 뜻 · 실제 사용 예문")
    render_expression_tab(BASE)

with word_tab:
    render_word_tab(BASE)
