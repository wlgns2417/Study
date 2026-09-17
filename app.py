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
DATA_VERSION = "travel-japanese-2026-09-17-v3"

st.markdown("""
<style>
.block-container{max-width:1600px;padding-top:1rem;padding-bottom:2rem}
.card{border:1px solid rgba(120,120,120,.28);border-radius:14px;padding:14px 15px;min-height:155px;margin-bottom:10px}
.card .meaning{font-size:19px;font-weight:850;line-height:1.35;margin-top:4px}
.card .reading-label{font-size:10px;opacity:.50;font-weight:800;margin-top:14px;letter-spacing:.06em}
.card .reading{font-size:20px;font-weight:900;margin-top:3px;color:#67c5ff;line-height:1.35}
.card .meta{display:inline-block;font-size:10px;opacity:.72;margin-top:12px;padding:3px 8px;border:1px solid rgba(120,120,120,.22);border-radius:999px}
.card .study-no{font-size:10px;font-weight:800;opacity:.43;margin-bottom:7px;letter-spacing:.08em}
.word-card{min-height:155px}
.page-caption{opacity:.72;font-size:13px;margin:8px 0 12px 0}
.day-hero{border:1px solid rgba(120,120,120,.25);border-radius:18px;padding:18px 22px;margin:10px 0 18px 0;background:rgba(120,120,120,.05)}
.day-title{font-size:30px;font-weight:900;line-height:1.1}
.day-sub{font-size:14px;opacity:.78;margin-top:8px}
.travel-note{border:1px solid rgba(103,197,255,.25);border-radius:14px;padding:12px 15px;background:rgba(103,197,255,.05);margin:4px 0 15px 0;font-size:13px}
div[data-baseweb="tab-list"]{gap:10px}
button[data-baseweb="tab"]{font-size:16px;font-weight:750}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(data_version: str):
    # data_version을 인자로 받아 CSV가 갱신될 때 기존 Streamlit 캐시를 사용하지 않는다.
    words = pd.read_csv(BASE / "japanese_words.csv")
    phrases = pd.read_csv(BASE / "japanese_phrases.csv")
    required = {"rank", "reading_ko", "meaning_ko", "category"}
    for name, df in (("단어", words), ("표현", phrases)):
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{name} 데이터에 필요한 컬럼이 없습니다: {sorted(missing)}")
        df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
        df.dropna(subset=["rank"], inplace=True)
        df.sort_values("rank", inplace=True, kind="stable")
        df.reset_index(drop=True, inplace=True)
    words["fixed_day"] = ((words["rank"] - 1) // WORDS_PER_DAY + 1).astype(int)
    phrases["fixed_day"] = ((phrases["rank"] - 1) // PHRASES_PER_DAY + 1).astype(int)
    return words, phrases


def card_html(row, number, label):
    reading = html.escape(str(row.get("reading_ko", "")))
    meaning = html.escape(str(row.get("meaning_ko", "")))
    cat = html.escape(str(row.get("category", "")))
    return (
        f'<div class="card {"word-card" if label == "WORD" else ""}">'
        f'<div class="study-no">{label} {number:02d}</div>'
        f'<div class="meaning">{meaning}</div>'
        f'<div class="reading-label">이렇게 읽으세요</div>'
        f'<div class="reading">{reading}</div>'
        f'<div class="meta">{cat}</div></div>'
    )


def render_cards(df, label, start_number=1):
    if df.empty:
        st.info("표시할 항목이 없습니다.")
        return
    cols = st.columns(5)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 5]:
            st.markdown(card_html(row, start_number + i, label), unsafe_allow_html=True)


def day_theme(day):
    themes = {
        1: "기본 생존 일본어",
        2: "공항 체크인 · 출국",
        3: "공항 · 기내 · 입국심사",
        4: "입국심사 · 전철 · 버스",
        5: "교통 · 택시 · 호텔",
        6: "호텔 · 식당 주문",
        7: "식당 · 술집 · 쇼핑",
        8: "쇼핑 · 편의점 · 긴급상황",
    }
    return themes.get(day, "여행 실전 일본어")


def render_daily(words, phrases):
    total_days = max(int(words.fixed_day.max()), int(phrases.fixed_day.max()))
    top1, top2, top3 = st.columns([1.2, 2.2, 2.2])
    day = top1.selectbox(
        "학습 DAY", list(range(1, total_days + 1)),
        format_func=lambda x: f"DAY {x}", key="jp_daily_day"
    )
    top2.metric("오늘의 목표", "40개", "단어 20 + 표현 20")
    learned = len(words[words.fixed_day <= day]) + len(phrases[phrases.fixed_day <= day])
    total = len(words) + len(phrases)
    top3.metric("여기까지 학습량", f"{learned:,}개", f"전체 {total:,}개")
    st.progress(min(learned / max(1, total), 1.0), text=f"DAY {day} · 전체 커리큘럼 {learned / max(1,total) * 100:.1f}%")
    st.markdown(
        f'<div class="day-hero"><div class="day-title">DAY {day} · {day_theme(day)}</div>'
        '<div class="day-sub">히라가나 암기 없이 여행에서 바로 말하기 · 모든 읽는 법을 한글 발음으로 표시합니다.</div></div>',
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
    st.info("한국어 뜻을 보고 일본어를 떠올린 뒤, 파란색 한글 발음을 소리 내어 2~3번 읽어보세요. DAY별 항목은 고정되어 있습니다.")


def render_all(df, label, search_key):
    f = df.copy()
    c1, c2, c3 = st.columns([3, 1, 1])
    q = c1.text_input("검색", placeholder="한국어 뜻 또는 한글 발음 검색", key=search_key)
    per = c2.selectbox("한 화면", [20, 30, 40, 50], index=3, key=f"{search_key}_per")
    categories = ["전체"] + sorted(f["category"].dropna().astype(str).unique().tolist())
    cat = c3.selectbox("상황", categories, key=f"{search_key}_cat")
    if q:
        qq = q.strip().lower()
        mask = (
            f["reading_ko"].fillna("").astype(str).str.lower().str.contains(qq, regex=False)
            | f["meaning_ko"].fillna("").astype(str).str.lower().str.contains(qq, regex=False)
        )
        f = f[mask]
    if cat != "전체":
        f = f[f["category"].astype(str) == cat]
    pages = max(1, math.ceil(len(f) / per))
    page = st.number_input("페이지 직접 이동", 1, pages, 1, key=f"{search_key}_page")
    view = f.iloc[(int(page)-1)*per:int(page)*per]
    st.markdown(
        f'<div class="page-caption">전체 {len(f):,}개 · 현재 {len(view)}개 표시 · {int(page)}/{pages} 페이지</div>',
        unsafe_allow_html=True,
    )
    render_cards(view, label, (int(page)-1)*per + 1)


words, phrases = load_data(DATA_VERSION)

st.title("🇯🇵 Speak Japanese")
st.caption("히라가나 몰라도 OK · 여행에서 바로 말하는 일본어 · 하루 단어 20개 + 표현 20개")
st.markdown(
    f'<div class="travel-note">✈️ 현재 여행 일본어 <b>{len(words):,}개 단어 + {len(phrases):,}개 표현 = 총 {len(words)+len(phrases):,}개</b> · '
    '공항 · 기내 · 입국심사 · 교통 · 택시 · 호텔 · 식당 · 술집 · 쇼핑 · 편의점 · 긴급상황 중심</div>',
    unsafe_allow_html=True,
)

day_tab, phrase_tab, word_tab = st.tabs(["🔥 DAY 학습", "💬 전체 여행 표현", "📚 전체 여행 단어"])
with day_tab:
    render_daily(words, phrases)
with phrase_tab:
    st.caption("상황별로 바로 꺼내 말할 수 있는 여행 일본어 표현 · 한글 발음 제공")
    render_all(phrases, "PHRASE", "phrase_search")
with word_tab:
    st.caption("공항·기내·식당·호텔·쇼핑 등 여행 중 자주 만나는 핵심 단어 · 한글 발음 제공")
    render_all(words, "WORD", "word_search")
