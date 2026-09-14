# -*- coding: utf-8 -*-
from pathlib import Path
import html
import math
import re

import pandas as pd
import streamlit as st

# Streamlit Cloud에서 named import가 이전 모듈 캐시와 충돌하는 경우를 피하기 위해
# 모듈 자체를 import하고 필요한 속성을 런타임에 안전하게 조회합니다.
import expression_tab as expression_module
import word_tab as word_module

WORDS_PER_DAY = 20
EXPRESSIONS_PER_DAY = 20


def _load_words(base_dir: Path) -> pd.DataFrame:
    """word_tab 버전에 관계없이 DAY 학습용 단어 데이터를 안전하게 불러옵니다."""
    loader = getattr(word_module, "load_word_data", None)
    if callable(loader):
        words, _ = loader(str(base_dir))
    else:
        path = base_dir / "conversation_words.csv"
        words = pd.read_csv(path) if path.exists() else pd.DataFrame()

    polish = getattr(word_module, "apply_conversation_polish", None)
    if callable(polish) and not words.empty:
        words = polish(words)
    return words


def _build_expression_frame(base_dir: Path) -> pd.DataFrame:
    loader = getattr(expression_module, "load_expression_data", None)
    if callable(loader):
        mined, core = loader(str(base_dir))
    else:
        mined_path = base_dir / "mined_phrases.csv"
        core_path = base_dir / "phrases.csv"
        mined = pd.read_csv(mined_path) if mined_path.exists() else pd.DataFrame()
        core = pd.read_csv(core_path) if core_path.exists() else pd.DataFrame()

    if mined.empty:
        return pd.DataFrame(columns=["expression", "meaning_ko", "example_en"])

    curated = getattr(expression_module, "CURATED", {})
    phrasal = getattr(expression_module, "PHRASAL", {})
    word_map = getattr(expression_module, "WORD", {})

    core_map = {}
    if not core.empty and "expression" in core.columns:
        for _, row in core.iterrows():
            key = str(row.get("expression", "")).strip().lower()
            if key:
                core_map[key] = row

    def meaning_for(exp):
        key = str(exp).strip().lower()
        if key in core_map:
            meaning = str(core_map[key].get("meaning", "")).strip()
            if meaning and meaning.lower() != "nan":
                return meaning
        if key in curated:
            return curated[key][0]
        if key in phrasal:
            return phrasal[key]

        patterns = [
            (r"^i want to\b", "나는 ~하고 싶어"), (r"^you want to\b", "너는 ~하고 싶어"),
            (r"^i need to\b", "나는 ~해야 해 / 필요해"), (r"^you need to\b", "너는 ~해야 해"),
            (r"^i have to\b", "나는 ~해야 해"), (r"^you have to\b", "너는 ~해야 해"),
            (r"^i don't\b", "나는 ~하지 않아"), (r"^you don't\b", "너는 ~하지 않아"),
            (r"^i can't\b", "나는 ~할 수 없어"), (r"^you can't\b", "너는 ~할 수 없어"),
            (r"^i didn't\b", "나는 ~하지 않았어"), (r"^you didn't\b", "너는 ~하지 않았어"),
            (r"^i'm\b", "나는 ~이야 / ~한 상태야"), (r"^you're\b", "너는 ~이야 / ~한 상태야"),
            (r"^what\b", "무엇 / 뭐"), (r"^why\b", "왜"), (r"^how\b", "어떻게"),
            (r"^where\b", "어디"), (r"^when\b", "언제"), (r"^who\b", "누구"),
            (r"^can you\b", "~해줄래?"), (r"^could you\b", "~해주시겠어요?"),
            (r"^would you\b", "~해주시겠어요? / ~할래?"),
            (r"^let me\b", "내가 ~할게 / ~하게 해줘"), (r"^don't\b", "~하지 마 / ~하지 않아"),
        ]
        for pattern, base in patterns:
            if re.search(pattern, key):
                tail = [word_map[w] for w in key.split() if w in word_map][-2:]
                return base + ((" · " + " / ".join(tail)) if tail else "")

        parts = [word_map[w] for w in key.split() if w in word_map]
        if parts:
            return " ".join(parts) + " · 문맥에 따라 자연스럽게 해석"
        return "일상 회화에서 문맥에 따라 뜻이 달라지는 표현"

    def example_for(exp):
        key = str(exp).strip().lower()
        if key in core_map:
            example = str(core_map[key].get("example_en", "")).strip()
            if example and example.lower() != "nan":
                return example
        if key in curated:
            return curated[key][1]
        if key.endswith(" to"):
            return f"I {key} go home."
        if re.match(r"^(what|why|how|where|when|who|are|do|did|can|could|would|will|is|isn't|aren't|don't|didn't)\b", key):
            return str(exp)[:1].upper() + str(exp)[1:].rstrip(".?!") + "?"
        if re.match(r"^(come|go|get|take|give|look|hold|wait|tell|call|try|keep|stop|let|remember|forget|listen|watch|check|help|follow)\b", key):
            return str(exp)[:1].upper() + str(exp)[1:].rstrip(".?!") + "."
        if re.match(r"^(i|you|we|they|he|she|it)\b", key):
            return str(exp)[:1].upper() + str(exp)[1:].rstrip(".?!") + "."
        return f"You'll hear ‘{exp}’ a lot in everyday conversation."

    frame = mined.copy()
    frame["expression"] = frame["expression"].astype(str).str.strip()
    frame["meaning_ko"] = frame["expression"].apply(meaning_for)
    frame["example_en"] = frame["expression"].apply(example_for)
    return frame


@st.cache_data
def _daily_frames(base_dir: str):
    base = Path(base_dir)
    words = _load_words(base)
    expressions = _build_expression_frame(base)
    return words, expressions


def _word_card(row, number):
    word = html.escape(str(row.get("word", "")))
    meaning = html.escape(str(row.get("meaning_ko", "")))
    example = html.escape(str(row.get("example_en", "")))
    meta = []
    pos = str(row.get("pos", "")).strip()
    cefr = str(row.get("cefr", "")).strip()
    if pos and pos.lower() not in {"nan", "other"}:
        meta.append(pos)
    if cefr and cefr.lower() != "nan":
        meta.append(cefr)
    meta_html = f'<div class="meta">{" · ".join(map(html.escape, meta))}</div>' if meta else ""
    return (
        f'<div class="card word-card"><div class="study-no">WORD {number:02d}</div>'
        f'<div class="e">{word}</div>{meta_html}<div class="ko">{meaning}</div>'
        f'<div class="ex">💬 {example}</div></div>'
    )


def _expression_card(row, number):
    expression = html.escape(str(row.get("expression", "")))
    meaning = html.escape(str(row.get("meaning_ko", "")))
    example = html.escape(str(row.get("example_en", "")))
    return (
        f'<div class="card"><div class="study-no">PHRASE {number:02d}</div>'
        f'<div class="e">{expression}</div><div class="ko">{meaning}</div>'
        f'<div class="ex">💬 {example}</div></div>'
    )


def render_daily_study(base_dir: Path):
    words, expressions = _daily_frames(str(base_dir))
    if words.empty or expressions.empty:
        st.warning("DAY 학습에 필요한 단어 또는 표현 데이터가 없습니다.")
        return

    word_days = math.ceil(len(words) / WORDS_PER_DAY)
    expression_days = math.ceil(len(expressions) / EXPRESSIONS_PER_DAY)
    total_days = max(word_days, expression_days)

    top1, top2, top3 = st.columns([1.2, 2.2, 2.2])
    day = top1.selectbox(
        "학습 DAY",
        options=list(range(1, total_days + 1)),
        format_func=lambda value: f"DAY {value}",
        key="daily_day",
    )
    top2.metric("오늘의 목표", "40개", "단어 20 + 표현 20")
    learned_now = len(words.iloc[:day * WORDS_PER_DAY]) + len(expressions.iloc[:day * EXPRESSIONS_PER_DAY])
    top3.metric("여기까지 학습량", f"{learned_now:,}개", f"전체 {len(words) + len(expressions):,}개")

    overall = min(learned_now / max(1, len(words) + len(expressions)), 1.0)
    st.progress(overall, text=f"DAY {day} · 전체 커리큘럼 {overall * 100:.1f}%")
    st.markdown(
        f'<div class="day-hero"><div class="day-title">DAY {day}</div>'
        '<div class="day-sub">오늘은 회화 단어 20개 + 회화 표현 20개, 총 40개를 익히는 날입니다.</div></div>',
        unsafe_allow_html=True,
    )

    word_start = (day - 1) * WORDS_PER_DAY
    phrase_start = (day - 1) * EXPRESSIONS_PER_DAY
    today_words = words.iloc[word_start:word_start + WORDS_PER_DAY]
    today_expressions = expressions.iloc[phrase_start:phrase_start + EXPRESSIONS_PER_DAY]

    word_tab, phrase_tab = st.tabs([f"📚 오늘의 단어 {len(today_words)}개", f"💬 오늘의 표현 {len(today_expressions)}개"])

    with word_tab:
        if today_words.empty:
            st.success("단어 커리큘럼은 모두 학습하셨습니다. 🎉")
        else:
            st.caption(f"단어 {word_start + 1:,} ~ {word_start + len(today_words):,} / 전체 {len(words):,}")
            cols = st.columns(5)
            for idx, (_, row) in enumerate(today_words.iterrows(), start=1):
                with cols[(idx - 1) % 5]:
                    st.markdown(_word_card(row, idx), unsafe_allow_html=True)

    with phrase_tab:
        if today_expressions.empty:
            st.success("회화 표현 커리큘럼은 모두 학습하셨습니다. 🎉")
        else:
            st.caption(f"표현 {phrase_start + 1:,} ~ {phrase_start + len(today_expressions):,} / 전체 {len(expressions):,}")
            cols = st.columns(5)
            for idx, (_, row) in enumerate(today_expressions.iterrows(), start=1):
                with cols[(idx - 1) % 5]:
                    st.markdown(_expression_card(row, idx), unsafe_allow_html=True)

    st.info("학습 방법: 영어를 먼저 보고 뜻을 떠올린 뒤 예문을 소리 내어 2~3번 읽어보세요. 다음 날은 DAY를 하나 올려서 새 40개를 학습하시면 됩니다.")