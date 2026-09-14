# -*- coding: utf-8 -*-
from pathlib import Path
import html
import math

import pandas as pd
import streamlit as st

WORD_DATA = "conversation_words.csv"

# 앱에서 데이터 생성 전에도 바로 확인할 수 있는 소규모 미리보기입니다.
# collect_words.py 실행 후에는 실제 코퍼스 기반 conversation_words.csv가 우선 사용됩니다.
SEED_WORDS = [
    ("actually", "사실은 / 실제로", "Actually, I changed my mind.", "adverb", "A2"),
    ("probably", "아마 / 아마도", "I'll probably stay home tonight.", "adverb", "A2"),
    ("realize", "깨닫다 / 알아차리다", "I didn't realize that.", "verb", "B1"),
    ("instead", "대신에", "Let's stay home instead.", "adverb", "A2"),
    ("supposed", "~하기로 되어 있는", "I'm supposed to meet him at six.", "adjective", "B1"),
    ("matter", "중요하다 / 문제", "It doesn't really matter.", "verb", "A2"),
    ("apparently", "듣자 하니 / 보아하니", "Apparently, he's already left.", "adverb", "B2"),
    ("basically", "기본적으로 / 쉽게 말하면", "Basically, we need more time.", "adverb", "B1"),
    ("definitely", "확실히 / 분명히", "I'll definitely call you later.", "adverb", "B1"),
    ("exactly", "정확히 / 바로 그거야", "That's exactly what I mean.", "adverb", "A2"),
    ("seriously", "진심으로 / 정말", "Are you seriously doing this now?", "adverb", "B1"),
    ("obviously", "분명히 / 당연히", "Obviously, we need a better plan.", "adverb", "B1"),
    ("eventually", "결국 / 마침내", "We'll figure it out eventually.", "adverb", "B2"),
    ("honestly", "솔직히", "Honestly, I don't know what to say.", "adverb", "B1"),
    ("literally", "말 그대로 / 정말", "I literally just got here.", "adverb", "B2"),
    ("otherwise", "그렇지 않으면 / 그 외에는", "Hurry up, otherwise we'll be late.", "adverb", "B1"),
    ("somehow", "어떻게든 / 어쩐지", "We'll make it work somehow.", "adverb", "B1"),
    ("anyway", "어쨌든", "Anyway, what were you saying?", "adverb", "A2"),
    ("perhaps", "아마 / 어쩌면", "Perhaps we should try again.", "adverb", "B1"),
    ("probably", "아마도", "She's probably still at work.", "adverb", "A2"),
    ("prefer", "더 좋아하다 / 선호하다", "I'd prefer to stay here.", "verb", "A2"),
    ("afford", "~할 여유가 되다", "I can't afford to buy it right now.", "verb", "B1"),
    ("avoid", "피하다", "I'm trying to avoid traffic.", "verb", "B1"),
    ("bother", "귀찮게 하다 / 신경 쓰이게 하다", "Sorry to bother you.", "verb", "B1"),
    ("complain", "불평하다", "I'm not trying to complain.", "verb", "B1"),
    ("consider", "고려하다 / 생각해 보다", "Have you considered moving closer?", "verb", "B1"),
    ("depend", "달려 있다 / 의존하다", "It depends on what you want.", "verb", "B1"),
    ("deserve", "~할 자격이 있다 / 마땅히 받다", "You deserve a break.", "verb", "B2"),
    ("expect", "예상하다 / 기대하다", "I didn't expect that at all.", "verb", "A2"),
    ("explain", "설명하다", "Let me explain what happened.", "verb", "A2"),
    ("imagine", "상상하다 / 생각해 보다", "Can you imagine living there?", "verb", "B1"),
    ("manage", "해내다 / 관리하다", "I managed to finish it on time.", "verb", "B1"),
    ("mention", "언급하다", "Did she mention my name?", "verb", "B1"),
    ("notice", "알아차리다 / 눈치채다", "Did you notice anything different?", "verb", "A2"),
    ("pretend", "~인 척하다", "Don't pretend you didn't know.", "verb", "B1"),
    ("promise", "약속하다", "I promise I won't tell anyone.", "verb", "A2"),
    ("remind", "상기시키다 / 알려주다", "Remind me to call him later.", "verb", "B1"),
    ("seem", "~처럼 보이다", "You seem a little tired today.", "verb", "A2"),
    ("suggest", "제안하다", "I suggest we leave early.", "verb", "B1"),
    ("wonder", "궁금하다 / ~일까 생각하다", "I wonder why he left.", "verb", "B1"),
    ("admit", "인정하다", "I have to admit, you were right.", "verb", "B1"),
    ("assume", "추정하다 / 당연하다고 생각하다", "I assumed you already knew.", "verb", "B2"),
    ("handle", "처리하다 / 감당하다", "Don't worry, I can handle it.", "verb", "B1"),
    ("ignore", "무시하다", "Just ignore what he said.", "verb", "B1"),
    ("regret", "후회하다", "I regret saying that.", "verb", "B2"),
    ("cancel", "취소하다", "We might have to cancel the plan.", "verb", "B1"),
    ("available", "시간이 되는 / 이용 가능한", "Are you available this afternoon?", "adjective", "A2"),
    ("awkward", "어색한 / 난처한", "That was a little awkward.", "adjective", "B2"),
    ("confused", "혼란스러운 / 헷갈리는", "I'm a little confused right now.", "adjective", "A2"),
    ("exhausted", "완전히 지친", "I'm exhausted after work.", "adjective", "B1"),
    ("familiar", "익숙한 / 낯익은", "That name sounds familiar.", "adjective", "B1"),
    ("frustrated", "답답한 / 좌절한", "I'm getting really frustrated.", "adjective", "B2"),
    ("likely", "가능성이 높은", "It's likely to rain later.", "adjective", "B1"),
    ("obvious", "분명한 / 뻔한", "The answer seems pretty obvious.", "adjective", "B1"),
    ("reasonable", "합리적인 / 적당한", "That sounds reasonable to me.", "adjective", "B2"),
    ("ridiculous", "말도 안 되는 / 터무니없는", "That's absolutely ridiculous.", "adjective", "B2"),
    ("specific", "구체적인 / 특정한", "Do you have a specific time in mind?", "adjective", "B1"),
    ("weird", "이상한 / 묘한", "That's kind of weird.", "adjective", "B1"),
    ("issue", "문제 / 쟁점", "There's one small issue we need to fix.", "noun", "B1"),
    ("point", "요점 / 의미", "I see your point.", "noun", "A2"),
    ("reason", "이유", "Is there a reason you're asking?", "noun", "A2"),
    ("situation", "상황", "It's a complicated situation.", "noun", "A2"),
    ("choice", "선택", "I don't think we have much choice.", "noun", "A2"),
    ("chance", "기회 / 가능성", "There's a good chance he'll come.", "noun", "A2"),
]


def _seed_dataframe():
    rows = []
    seen = set()
    for rank, (word, meaning, example, pos, cefr) in enumerate(SEED_WORDS, 1):
        if word in seen:
            continue
        seen.add(word)
        rows.append({
            "rank": len(rows) + 1,
            "word": word,
            "meaning_ko": meaning,
            "example_en": example,
            "pos": pos,
            "cefr": cefr,
            "score": "preview",
            "source": "starter preview",
        })
    return pd.DataFrame(rows)


@st.cache_data
def load_word_data(base_dir: str):
    path = Path(base_dir) / WORD_DATA
    if path.exists():
        df = pd.read_csv(path)
        required = {"word", "meaning_ko", "example_en"}
        if required.issubset(df.columns):
            return df, True
    return _seed_dataframe(), False


def render_word_tab(base_dir: Path):
    words, generated = load_word_data(str(base_dir))

    if generated:
        st.caption("SUBTLEX-US + OpenSubtitles 실사용 빈도 · 기능어/초급어 제거 · 회화 활용도/학습가치 보정")
    else:
        st.info("현재는 회화 단어 탭 미리보기입니다. `python collect_words.py` 실행 후 실제 코퍼스 기반 2,000~5,000개 데이터로 자동 전환됩니다.")

    f = words.copy()
    f["word"] = f["word"].astype(str).str.strip()
    f["meaning_ko"] = f["meaning_ko"].fillna("").astype(str)
    f["example_en"] = f["example_en"].fillna("").astype(str)

    c1, c2, c3 = st.columns([3, 1, 1])
    q = c1.text_input("단어 검색", placeholder="actually / 사실은", key="word_search")
    per = c2.selectbox("한 화면", [20, 30, 40, 50], index=3, key="word_per")

    levels = ["전체"]
    if "cefr" in f.columns:
        levels += [x for x in ["A2", "B1", "B2", "C1", "C2"] if x in set(f["cefr"].dropna().astype(str))]
    level = c3.selectbox("난이도", levels, key="word_level")

    if q:
        qq = q.strip().lower()
        f = f[
            f["word"].str.lower().str.contains(qq, regex=False)
            | f["meaning_ko"].str.lower().str.contains(qq, regex=False)
        ]
    if level != "전체" and "cefr" in f.columns:
        f = f[f["cefr"].astype(str) == level]

    pages = max(1, math.ceil(len(f) / per))
    if "word_page" not in st.session_state:
        st.session_state.word_page = 1
    st.session_state.word_page = max(1, min(int(st.session_state.word_page), pages))

    page_input = st.number_input(
        "단어 페이지 직접 이동",
        min_value=1,
        max_value=pages,
        value=st.session_state.word_page,
        step=1,
        key="word_page_input",
    )
    if int(page_input) != st.session_state.word_page:
        st.session_state.word_page = int(page_input)
        st.rerun()

    page = st.session_state.word_page
    view = f.iloc[(page - 1) * per:page * per]
    label = "코퍼스 선별 단어" if generated else "미리보기 단어"
    st.markdown(
        f'<div class="page-caption">전체 {len(f):,}개 {label} · 현재 {len(view)}개 표시 · {page}/{pages} 페이지</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    for i, (_, r) in enumerate(view.iterrows()):
        word = html.escape(str(r["word"]))
        ko = html.escape(str(r["meaning_ko"]))
        ex = html.escape(str(r["example_en"]))
        meta_parts = []
        if "pos" in r and pd.notna(r.get("pos")):
            meta_parts.append(str(r.get("pos")))
        if "cefr" in r and pd.notna(r.get("cefr")):
            meta_parts.append(str(r.get("cefr")))
        meta = " · ".join(meta_parts)
        meta_html = f'<div class="meta">{html.escape(meta)}</div>' if meta else ""
        card = (
            '<div class="card word-card"><div class="e">' + word + '</div>'
            + meta_html
            + '<div class="ko">' + ko + '</div>'
            + '<div class="ex">💬 ' + ex + '</div></div>'
        )
        with cols[i % 5]:
            st.markdown(card, unsafe_allow_html=True)

    st.divider()
    block_start = ((page - 1) // 5) * 5 + 1
    block_end = min(block_start + 4, pages)
    btns = st.columns(7)
    with btns[0]:
        if st.button("◀ 이전", key="word_prev", use_container_width=True, disabled=(page <= 1)):
            st.session_state.word_page = page - 1
            st.rerun()

    for idx, p in enumerate(range(block_start, block_end + 1), start=1):
        with btns[idx]:
            if st.button(("● " + str(p)) if p == page else str(p), key=f"word_page_{p}", use_container_width=True):
                st.session_state.word_page = p
                st.rerun()

    with btns[6]:
        if st.button("다음 ▶", key="word_next", use_container_width=True, disabled=(page >= pages)):
            st.session_state.word_page = page + 1
            st.rerun()
