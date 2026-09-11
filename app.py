# -*- coding: utf-8 -*-
from pathlib import Path
import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Speak English", page_icon="🗣️", layout="wide")

BASE = Path(__file__).resolve().parent
CORE = BASE / "phrases.csv"
MINED = BASE / "mined_phrases.csv"

@st.cache_data
def load_data():
    core = pd.read_csv(CORE) if CORE.exists() else pd.DataFrame()
    mined = pd.read_csv(MINED) if MINED.exists() else pd.DataFrame()
    return core, mined

core, mined = load_data()

st.markdown("""
<style>
.block-container{max-width:1600px;padding-top:1rem}
.card{border:1px solid rgba(120,120,120,.28);border-radius:13px;padding:11px 13px;min-height:118px;margin-bottom:9px}
.card .e{font-size:18px;font-weight:800;line-height:1.2}
.card .meta{font-size:12px;opacity:.72;margin-top:7px;line-height:1.35}
.card .meaning{font-size:13px;font-weight:700;margin-top:6px}
.card .nuance{font-size:12px;opacity:.76;margin-top:5px;line-height:1.3}
.card .example{font-size:12px;opacity:.82;margin-top:6px;line-height:1.3}
</style>
""", unsafe_allow_html=True)

st.title("🗣️ Speak English")
st.caption("OpenSubtitles 실사용 표현을 한 화면에 최대 50개씩 보기")

tab1, tab2, tab3 = st.tabs(["🔥 실사용 표현 50개씩", "📚 해설 카드", "📊 빈도표"])

# ---------- 실사용 표현 50개씩 ----------
with tab1:
    if mined.empty:
        st.info("아직 mined_phrases.csv가 없습니다. 먼저 `python collect_phrases.py`를 실행하세요.")
    else:
        c1, c2, c3 = st.columns([2.3,1,1])
        q = c1.text_input("표현 검색", placeholder="figure out / come on / let me know")
        per = c2.selectbox("한 화면", [20,30,40,50], index=3, key="mined_per")
        mincount = c3.number_input("최소 등장 횟수", min_value=1, value=2, key="mined_min")

        f = mined[mined["count"] >= mincount].copy()

        if q:
            f = f[f["expression"].astype(str).str.contains(q, case=False, regex=False)]

        pages = max(1, math.ceil(len(f) / per))
        page = st.number_input("페이지", 1, pages, 1, key="mined_page")
        view = f.iloc[(page-1)*per:page*per]

        st.caption(f"총 {len(f):,}개 표현 · 현재 {len(view)}개 표시 · {page}/{pages} 페이지")
        cols = st.columns(5)

        # curated Korean explanations if exact expression exists in core
        core_map = {}
        if not core.empty and "expression" in core.columns:
            for _, r in core.iterrows():
                core_map[str(r["expression"]).strip().lower()] = r

        for i, (_, r) in enumerate(view.iterrows()):
            exp = str(r["expression"])
            matched = core_map.get(exp.strip().lower())

            with cols[i % 5]:
                if matched is not None:
                    st.markdown(f"""
                    <div class="card">
                      <div class="e">{exp}</div>
                      <div class="meaning">{matched.get('meaning','')}</div>
                      <div class="nuance">{matched.get('nuance','')}</div>
                      <div class="example">💬 {matched.get('example_en','')}<br>{matched.get('example_ko','')}</div>
                      <div class="meta">#{int(r['rank'])} · 등장 {int(r['count']):,}회 · 빈도 {r['frequency_score']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="card">
                      <div class="e">{exp}</div>
                      <div class="meta">실사용 순위 #{int(r['rank'])}<br>
                      등장 {int(r['count']):,}회 · 빈도점수 {r['frequency_score']}<br>
                      {r.get('source','OpenSubtitles')}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ---------- 해설 카드 ----------
with tab2:
    if core.empty:
        st.warning("phrases.csv가 없습니다.")
    else:
        c1, c2, c3, c4 = st.columns([1.2,1,1,2])
        cats = ["전체"] + sorted(core["category"].dropna().astype(str).unique().tolist())
        levels = ["전체"] + sorted(core["level"].dropna().astype(str).unique().tolist())
        cat = c1.selectbox("카테고리", cats, key="core_cat")
        lev = c2.selectbox("난이도", levels, key="core_lev")
        per = c3.selectbox("한 화면", [20,30,40,50], index=3, key="core_per")
        q2 = c4.text_input("검색", key="core_q")

        f = core.copy()
        if cat != "전체":
            f = f[f["category"].astype(str) == cat]
        if lev != "전체":
            f = f[f["level"].astype(str) == lev]
        if q2:
            qq = q2.lower()
            f = f[
                f["expression"].fillna("").str.lower().str.contains(qq, regex=False) |
                f["meaning"].fillna("").str.lower().str.contains(qq, regex=False)
            ]

        pages = max(1, math.ceil(len(f) / per))
        page2 = st.number_input("페이지", 1, pages, 1, key="core_page")
        view = f.iloc[(page2-1)*per:page2*per]

        st.caption(f"{len(f):,}개 중 {len(view)}개 표시 · {page2}/{pages} 페이지")
        cols = st.columns(5)

        for i, (_, r) in enumerate(view.iterrows()):
            with cols[i % 5]:
                st.markdown(f"""
                <div class="card">
                  <div class="e">{r.get('expression','')}</div>
                  <div class="meaning">{r.get('meaning','')}</div>
                  <div class="nuance">{r.get('nuance','')}</div>
                  <div class="example">💬 {r.get('example_en','')}<br>{r.get('example_ko','')}</div>
                  <div class="meta">{r.get('category','')} · {r.get('level','')}</div>
                </div>
                """, unsafe_allow_html=True)

# ---------- 빈도표 ----------
with tab3:
    if mined.empty:
        st.info("mined_phrases.csv가 아직 없습니다.")
    else:
        st.dataframe(
            mined[["rank","expression","count","frequency_score","source"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "rank":"순위",
                "expression":"표현",
                "count":"등장 횟수",
                "frequency_score":"빈도 점수",
                "source":"출처",
            },
        )
