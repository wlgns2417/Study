# -*- coding: utf-8 -*-
from pathlib import Path
import html
import math

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Speak Japanese", page_icon="🇯🇵", layout="wide")
BASE = Path(__file__).resolve().parent
WORDS_PER_DAY = 20
PHRASES_PER_DAY = 20

st.markdown("""
<style>
.block-container{max-width:1600px;padding-top:1rem;padding-bottom:2rem}
.card{border:1px solid rgba(120,120,120,.28);border-radius:14px;padding:13px 15px;min-height:188px;margin-bottom:10px}
.card .e{font-size:22px;font-weight:800;line-height:1.25}
.card .reading{font-size:12px;font-weight:700;margin-top:5px;color:#a9a9ff;line-height:1.35}
.card .ko{font-size:14px;font-weight:750;margin-top:8px;color:#67c5ff;line-height:1.35}
.card .ex{font-size:12px;opacity:.88;margin-top:12px;line-height:1.5;border-top:1px solid rgba(120,120,120,.14);padding-top:9px}
.card .exko{font-size:11px;opacity:.62;margin-top:4px;line-height:1.4}
.card .meta{font-size:11px;opacity:.58;margin-top:5px;text-transform:uppercase;letter-spacing:.03em}
.card .study-no{font-size:10px;font-weight:800;opacity:.48;margin-bottom:7px;letter-spacing:.08em}
.word-card{min-height:208px}
.page-caption{opacity:.72;font-size:13px;margin:8px 0 12px 0}
.day-hero{border:1px solid rgba(120,120,120,.25);border-radius:18px;padding:18px 22px;margin:10px 0 18px 0;background:rgba(120,120,120,.05)}
.day-title{font-size:30px;font-weight:900;line-height:1.1}
.day-sub{font-size:14px;opacity:.78;margin-top:8px}
div[data-baseweb="tab-list"]{gap:10px}
button[data-baseweb="tab"]{font-size:16px;font-weight:750}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    words = pd.read_csv(BASE / "japanese_words.csv")
    phrases = pd.read_csv(BASE / "japanese_phrases.csv")
    for df in (words, phrases):
        df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
        df.sort_values("rank", inplace=True, kind="stable")
        df.reset_index(drop=True, inplace=True)
    words["fixed_day"] = ((words["rank"] - 1) // WORDS_PER_DAY + 1).astype(int)
    phrases["fixed_day"] = ((phrases["rank"] - 1) // PHRASES_PER_DAY + 1).astype(int)
    return words, phrases


def card_html(row, number, label):
    jp = html.escape(str(row.get("japanese", "")))
    reading = html.escape(str(row.get("reading", "")))
    ko = html.escape(str(row.get("meaning_ko", "")))
    exjp = html.escape(str(row.get("example_jp", "")))
    exko = html.escape(str(row.get("example_ko", "")))
    cat = html.escape(str(row.get("category", "")))
    return (
        f'<div class="card {"word-card" if label == "WORD" else ""}">'
        f'<div class="study-no">{label} {number:02d}</div>'
        f'<div class="e">{jp}</div><div class="reading">{reading}</div>'
        f'<div class="meta">{cat}</div><div class="ko">{ko}</div>'
        f'<div class="ex">💬 {exjp}</div><div class="exko">↳ {exko}</div></div>'
    )


def render_cards(df, label, start_number=1):
    if df.empty:
        st.info("표시할 항목이 없습니다.")
        return
    cols = st.columns(5)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 5]:
            st.markdown(card_html(row, start_number + i, label), unsafe_allow_html=True)


def render_daily(words, phrases):
    total_days = max(int(words.fixed_day.max()), int(phrases.fixed_day.max()))
    top1, top2, top3 = st.columns([1.2, 2.2, 2.2])
    day = top1.selectbox("학습 DAY", list(range(1, total_days + 1)), format_func=lambda x: f"DAY {x}")
    top2.metric("오늘의 목표", "40개", "단어 20 + 표현 20")
    learned = len(words[words.fixed_day <= day]) + len(phrases[phrases.fixed_day <= day])
    total = len(words) + len(phrases)
    top3.metric("여기까지 학습량", f"{learned:,}개", f"전체 {total:,}개")
    st.progress(min(learned / max(1, total), 1.0), text=f"DAY {day} · 전체 커리큘럼 {learned / max(1,total) * 100:.1f}%")
    st.markdown(
        f'<div class="day-hero"><div class="day-title">DAY {day}</div>'
        '<div class="day-sub">고정 커리큘럼 · 같은 DAY에는 언제 접속해도 같은 일본어 단어와 표현이 나옵니다.</div></div>',
        unsafe_allow_html=True,
    )
    w = words[words.fixed_day == day].copy()
    p = phrases[phrases.fixed_day == day].copy()
    wt, pt = st.tabs([f"📚 오늘의 단어 {len(w)}개", f"💬 오늘의 표현 {len(p)}개"])
    with wt:
        st.caption(f"고정 단어 {(day-1)*20+1} ~ {(day-1)*20+len(w)} / 전체 {len(words)}")
        render_cards(w, "WORD")
    with pt:
        st.caption(f"고정 표현 {(day-1)*20+1} ~ {(day-1)*20+len(p)} / 전체 {len(phrases)}")
        render_cards(p, "PHRASE")
    st.info("학습 방법: 일본어를 먼저 읽고 뜻을 떠올린 뒤, 읽는 법을 확인하고 예문을 소리 내어 2~3번 읽어보세요. DAY별 항목은 고정되어 있습니다.")


def render_all(df, label, search_key):
    f = df.copy()
    c1, c2, c3 = st.columns([3,1,1])
    q = c1.text_input("검색", placeholder="일본어 / 읽는 법 / 한국어 뜻", key=search_key)
    per = c2.selectbox("한 화면", [20,30,40,50], index=3, key=f"{search_key}_per")
    cats = ["전체"] + sorted(f["category"].dropna().astype(str).unique().tolist())
    cat = c3.selectbox("분류", cats, key=f"{search_key}_cat")
    if q:
        qq = q.strip().lower()
        mask = pd.Series(False, index=f.index)
        for col in ["japanese","reading","meaning_ko","example_jp","example_ko"]:
            mask |= f[col].fillna("").astype(str).str.lower().str.contains(qq, regex=False)
        f = f[mask]
    if cat != "전체":
        f = f[f.category.astype(str) == cat]
    pages = max(1, math.ceil(len(f) / per))
    page = st.number_input("페이지 직접 이동", 1, pages, 1, key=f"{search_key}_page")
    view = f.iloc[(int(page)-1)*per:int(page)*per]
    st.markdown(f'<div class="page-caption">전체 {len(f):,}개 · 현재 {len(view)}개 표시 · {int(page)}/{pages} 페이지</div>', unsafe_allow_html=True)
    render_cards(view, label, (int(page)-1)*per + 1)

words, phrases = load_data()

st.title("🇯🇵 Speak Japanese")
st.caption("DAY 1부터 하루 40개씩 · 회화 단어 20개 + 회화 표현 20개")

day_tab, phrase_tab, word_tab = st.tabs(["🔥 DAY 학습", "💬 전체 회화 표현", "📚 전체 회화 단어"])
with day_tab:
    render_daily(words, phrases)
with phrase_tab:
    st.caption("일본 여행과 일상 회화에서 바로 쓸 수 있는 표현 · 읽는 법 · 한국어 뜻 · 실제 예문")
    render_all(phrases, "PHRASE", "phrase_search")
with word_tab:
    st.caption("실전 일본어 회화에 자주 쓰는 핵심 단어 · 읽는 법 · 한국어 뜻 · 실제 예문")
    render_all(words, "WORD", "word_search")