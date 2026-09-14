# -*- coding: utf-8 -*-
from pathlib import Path

import streamlit as st

# 기존 탭 모듈을 먼저 초기화한 뒤 DAY 모듈을 불러와 Streamlit Cloud의
# 모듈 캐시/배포 시점에 따른 import 충돌을 방지합니다.
from expression_tab import render_expression_tab
from word_tab import render_word_tab
from daily_study import render_daily_study

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
.card .study-no{font-size:10px;font-weight:800;opacity:.48;margin-bottom:7px;letter-spacing:.08em}
.word-card{min-height:165px}
.page-caption{opacity:.72;font-size:13px;margin:8px 0 12px 0}
.day-hero{border:1px solid rgba(120,120,120,.25);border-radius:18px;padding:18px 22px;margin:10px 0 18px 0;background:rgba(120,120,120,.05)}
.day-title{font-size:30px;font-weight:900;line-height:1.1}
.day-sub{font-size:14px;opacity:.78;margin-top:8px}
div[data-baseweb="tab-list"]{gap:10px}
button[data-baseweb="tab"]{font-size:16px;font-weight:750}
</style>
""", unsafe_allow_html=True)

st.title("🗣️ Speak English")
st.caption("DAY 1부터 하루 40개씩 · 회화 단어 20개 + 회화 표현 20개")

day_tab, phrase_tab, word_tab = st.tabs(["🔥 DAY 학습", "💬 전체 회화 표현", "📚 전체 회화 단어"])

with day_tab:
    render_daily_study(BASE)

with phrase_tab:
    st.caption("OpenSubtitles에서 발굴한 자주 쓰는 구어체 표현 · 한국어 뜻 · 실제 사용 예문")
    render_expression_tab(BASE)

with word_tab:
    render_word_tab(BASE)
