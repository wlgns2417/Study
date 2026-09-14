# -*- coding: utf-8 -*-
from pathlib import Path
import math
import html
import re
import time
import pandas as pd
import streamlit as st
from deep_translator import GoogleTranslator

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

core_map = {}
if not core.empty and "expression" in core.columns:
    for _, r in core.iterrows():
        core_map[str(r["expression"]).strip().lower()] = r

# 자주 쓰는 표현은 자동 번역보다 자연스러운 뜻/예문을 우선 사용합니다.
CURATED = {
    "i don't": ("나는 ~하지 않아", "I don't think so.", "난 그렇게 생각하지 않아."),
    "you know": ("알잖아 / 있잖아", "You know what I mean.", "내 말 무슨 뜻인지 알잖아."),
    "all right": ("알았어 / 좋아 / 괜찮아", "All right, let's go.", "좋아, 가자."),
    "thank you": ("고마워요", "Thank you for your help.", "도와줘서 고마워요."),
    "want to": ("~하고 싶다", "I want to go home.", "집에 가고 싶어."),
    "come on": ("에이 / 제발 / 빨리", "Come on, we're late.", "빨리, 우리 늦었어."),
    "i know": ("알아", "I know how you feel.", "네 기분이 어떤지 알아."),
    "don't know": ("모르겠어", "I don't know yet.", "아직 모르겠어."),
    "i think": ("내 생각엔 / ~인 것 같아", "I think you're right.", "네 말이 맞는 것 같아."),
    "don't you": ("~하지 않아? / 그렇지?", "Don't you remember?", "기억 안 나?"),
    "i'm not": ("나는 ~이 아니야 / ~하지 않아", "I'm not ready yet.", "난 아직 준비 안 됐어."),
    "i can't": ("나는 ~할 수 없어", "I can't do this alone.", "이건 혼자 못 하겠어."),
    "let me": ("내가 ~하게 해줘 / 내가 ~할게", "Let me check.", "내가 확인해볼게."),
    "don't want to": ("~하고 싶지 않아", "I don't want to leave.", "나 가고 싶지 않아."),
    "come here": ("이리 와", "Come here for a second.", "잠깐 이리 와봐."),
    "that's right": ("맞아 / 그래", "That's right. I remember now.", "맞아. 이제 기억나."),
    "what's the matter": ("무슨 일이야? / 왜 그래?", "What's the matter with you?", "너 왜 그래?"),
    "don't worry": ("걱정하지 마", "Don't worry about it.", "그건 걱정하지 마."),
    "that's why": ("그래서 그런 거야", "That's why I called you.", "그래서 너한테 전화한 거야."),
    "figure out": ("알아내다 / 이해하다", "We'll figure it out.", "우리가 방법을 찾아낼 거야."),
    "let me know": ("알려줘", "Let me know when you're ready.", "준비되면 알려줘."),
    "hold on": ("잠깐만", "Hold on a second.", "잠깐만."),
    "fair enough": ("그건 인정 / 일리 있네", "Fair enough. I see your point.", "그건 인정. 네 말이 이해돼."),
    "sounds good": ("좋아 / 괜찮네", "Sounds good to me.", "난 좋아."),
    "my bad": ("내 실수야 / 미안", "My bad, I forgot.", "내 실수야, 깜빡했어."),
    "no worries": ("괜찮아 / 신경 쓰지 마", "No worries, it's fine.", "괜찮아, 문제 없어."),
    "give it a shot": ("한번 해봐", "Give it a shot.", "한번 해봐."),
    "i'm on my way": ("지금 가는 중이야", "I'm on my way now.", "지금 가는 중이야."),
    "of course": ("물론이지", "Of course I remember.", "물론 기억하지."),
    "what do you mean": ("무슨 뜻이야?", "What do you mean by that?", "그게 무슨 뜻이야?"),
    "what's going on": ("무슨 일이야? / 어떻게 된 거야?", "What's going on here?", "여기 무슨 일이야?"),
    "i mean": ("내 말은 / 그러니까", "I mean, it's not that bad.", "내 말은, 그렇게 나쁘진 않다는 거야."),
    "i guess": ("그런 것 같아 / 아마", "I guess you're right.", "네 말이 맞는 것 같아."),
    "have to": ("~해야 한다", "I have to go now.", "나 이제 가야 해."),
    "gotta go": ("가봐야 해", "Sorry, I gotta go.", "미안, 나 가봐야 해."),
    "let's go": ("가자", "Let's go home.", "집에 가자."),
    "get out": ("나가 / 빠져나가다", "Get out of here.", "여기서 나가."),
    "calm down": ("진정해", "Calm down and listen to me.", "진정하고 내 말 들어."),
    "hurry up": ("서둘러", "Hurry up or we'll miss it.", "서둘러, 안 그러면 놓쳐."),
    "hang on": ("잠깐만", "Hang on, I'm coming.", "잠깐만, 지금 가."),
    "find out": ("알아내다", "I'll find out what happened.", "무슨 일이 있었는지 알아볼게."),
    "work out": ("잘 풀리다 / 운동하다", "It'll work out somehow.", "어떻게든 잘 풀릴 거야."),
    "pick up": ("집다 / 데리러 가다 / 전화를 받다", "I'll pick you up at six.", "6시에 데리러 갈게."),
    "give up": ("포기하다", "Don't give up now.", "지금 포기하지 마."),
    "come back": ("돌아오다", "Come back soon.", "곧 돌아와."),
    "take care": ("잘 지내 / 몸조심해", "Take care of yourself.", "몸 잘 챙겨."),
    "never mind": ("신경 쓰지 마 / 됐어", "Never mind. It's okay.", "신경 쓰지 마. 괜찮아."),
    "no way": ("말도 안 돼 / 절대 안 돼", "No way! Are you serious?", "말도 안 돼! 진짜야?"),
    "not really": ("별로 / 꼭 그렇진 않아", "Not really. I'm just tired.", "별로. 그냥 피곤해."),
    "why not": ("왜 안 돼? / 그러지 뭐", "Why not give it a try?", "한번 해보는 게 어때?"),
    "makes sense": ("말이 되네 / 이해돼", "That makes sense.", "그거 말이 되네."),
    "i see": ("알겠어 / 그렇구나", "I see what you mean.", "무슨 말인지 알겠어."),
    "got it": ("알겠어", "Got it. I'll do it now.", "알겠어. 지금 할게."),
    "just kidding": ("농담이야", "Relax, I'm just kidding.", "진정해, 그냥 농담이야."),
    "are you serious": ("진심이야?", "Are you serious right now?", "너 지금 진심이야?"),
    "trust me": ("날 믿어", "Trust me, it'll be fine.", "날 믿어, 괜찮을 거야."),
    "excuse me": ("실례합니다 / 저기요", "Excuse me, is this seat taken?", "실례합니다, 여기 자리 있나요?"),
    "how come": ("왜? / 어째서?", "How come you didn't call?", "왜 전화 안 했어?"),
    "can you": ("~해줄래?", "Can you help me?", "나 좀 도와줄래?"),
    "could you": ("~해주시겠어요?", "Could you say that again?", "다시 말씀해주시겠어요?"),
}

BLOCKED = {"of the", "in the", "to the", "and the", "for the", "on the", "at the", "from the"}


def core_info(key):
    if key not in core_map:
        return None
    r = core_map[key]
    meaning = str(r.get("meaning", "")).strip()
    ex_en = str(r.get("example_en", "")).strip()
    ex_ko = str(r.get("example_ko", "")).strip()
    nuance = str(r.get("nuance", "")).strip()
    similar = str(r.get("similar", "")).strip()
    if not meaning or meaning.lower() == "nan":
        return None
    return {
        "meaning": meaning,
        "example_en": "" if ex_en.lower() == "nan" else ex_en,
        "example_ko": "" if ex_ko.lower() == "nan" else ex_ko,
        "nuance": "" if nuance.lower() == "nan" else nuance,
        "similar": "" if similar.lower() == "nan" else similar,
    }


@st.cache_data(ttl=60*60*24*30, show_spinner=False)
def translate_one(text):
    text = str(text).strip()
    if not text:
        return ""
    # Google 번역을 여러 번 시도해 페이지 일부가 비는 문제를 줄입니다.
    for _ in range(3):
        try:
            result = GoogleTranslator(source="en", target="ko").translate(text)
            if result and str(result).strip():
                return str(result).strip()
        except Exception:
            time.sleep(0.25)
    return "번역을 다시 시도해 주세요"


@st.cache_data(ttl=60*60*24*30, show_spinner=False)
def translate_many(items_tuple):
    items = [str(x).strip() for x in items_tuple]
    if not items:
        return []
    results = [""] * len(items)
    # 먼저 batch 번역, 실패한 항목만 개별 재시도합니다.
    try:
        batch = GoogleTranslator(source="en", target="ko").translate_batch(items)
        if isinstance(batch, list):
            for i, val in enumerate(batch[:len(items)]):
                if val and str(val).strip():
                    results[i] = str(val).strip()
    except Exception:
        pass
    for i, item in enumerate(items):
        if not results[i]:
            results[i] = translate_one(item)
    return results


def make_example(exp):
    k = str(exp).strip().lower()
    cap = str(exp).strip()[:1].upper() + str(exp).strip()[1:]
    if k in CURATED:
        return CURATED[k][1]
    if k.endswith(" to"):
        return cap + " go home."
    if re.match(r"^(what|why|how|where|when|who|are|do|did|can|could|would|will|is|isn't|aren't|don't|didn't)\b", k):
        return cap.rstrip("?.!") + "?"
    if re.match(r"^(come|go|get|take|give|look|hold|wait|tell|call|try|keep|stop|let|remember|forget|listen|watch|check|help|follow)\b", k):
        return cap.rstrip(".?!") + "."
    if re.match(r"^(i|you|we|they|he|she|it)\b", k):
        return cap.rstrip(".?!") + "."
    return f"People often say ‘{exp}’ in everyday conversation."


def phrase_data(exp):
    key = str(exp).strip().lower()
    ci = core_info(key)
    if ci:
        return ci
    if key in CURATED:
        m, ee, ek = CURATED[key]
        return {"meaning": m, "example_en": ee, "example_ko": ek, "nuance": "", "similar": ""}
    example = make_example(exp)
    meaning, example_ko = translate_many((str(exp), example))
    return {"meaning": meaning, "example_en": example, "example_ko": example_ko, "nuance": "", "similar": ""}


def generic_nuance(exp):
    k = str(exp).strip().lower()
    if "'" in k:
        return "축약형이 들어간 자연스러운 회화 표현입니다. 말할 때 매우 자주 들을 수 있습니다."
    if len(k.split()) <= 2:
        return "짧게 자주 쓰이는 회화 조합입니다. 문맥에 따라 한국어 뜻이 조금 달라질 수 있습니다."
    return "일상 대화에서 통째로 익혀 두면 듣기와 말하기에 도움이 되는 표현입니다."


st.markdown("""
<style>
.block-container{max-width:1600px;padding-top:1rem}
.card{border:1px solid rgba(120,120,120,.28);border-radius:14px;padding:13px 15px;min-height:150px;margin-bottom:8px}
.card .e{font-size:20px;font-weight:800;line-height:1.25}
.card .ko{font-size:14px;font-weight:750;margin-top:8px;color:#67c5ff;line-height:1.35}
.card .ex{font-size:12px;opacity:.86;margin-top:12px;line-height:1.5}
.card .exko{font-size:12px;opacity:.66;line-height:1.45;margin-top:2px}
.detail-box{border:1px solid rgba(120,120,120,.3);border-radius:16px;padding:22px;margin-top:10px}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = 1
if "selected_phrase" not in st.session_state:
    st.session_state.selected_phrase = None

# -------------------- 상세 페이지 --------------------
if st.session_state.selected_phrase:
    exp = st.session_state.selected_phrase
    data = phrase_data(exp)
    st.title(f"🗣️ {exp}")
    if st.button("← 목록으로 돌아가기", use_container_width=False):
        st.session_state.selected_phrase = None
        st.rerun()

    st.markdown(f"## 🇰🇷 {data['meaning']}")
    st.markdown("### 뉘앙스")
    st.write(data.get("nuance") or generic_nuance(exp))

    st.markdown("### 대표 예문")
    st.markdown(f"**{data['example_en']}**")
    st.write(data['example_ko'])

    # 추가 예문은 원 표현을 포함한 간단한 문장으로 2개 더 제공합니다.
    extra_en = [
        f"I often hear people say ‘{exp}’ in conversation.",
        f"You can use ‘{exp}’ naturally in the right situation.",
    ]
    extra_ko = translate_many(tuple(extra_en))
    for ee, ek in zip(extra_en, extra_ko):
        st.markdown(f"- **{ee}**  \n  {ek}")

    if data.get("similar"):
        st.markdown("### 비슷한 표현")
        st.write(data["similar"])

    st.markdown("### 학습 팁")
    st.write("뜻만 외우기보다 위 예문을 소리 내어 3번 읽고, 주어·목적어만 바꿔서 한 문장 더 만들어 보세요.")
    st.stop()

# -------------------- 목록 페이지 --------------------
st.title("🗣️ Speak English")
st.caption("자주 쓰는 영어 표현 · 한국어 뜻 · 실제 사용 예문")

if mined.empty:
    st.warning("mined_phrases.csv가 없습니다.")
    st.stop()

c1, c2 = st.columns([3,1])
q = c1.text_input("검색", placeholder="don't worry / 걱정하지 마")
per = c2.selectbox("한 화면", [20,30,40,50], index=3)

f = mined.copy()
f["key"] = f["expression"].astype(str).str.strip().str.lower()
f = f[~f["key"].isin(BLOCKED)].copy()

# 검색을 위해 현재 전체 표현의 한국어 뜻을 모두 미리 번역하지는 않습니다.
# 영어 검색은 즉시, 한국어 검색은 현재 준비된 curated/core 뜻에서 우선 처리합니다.
if q:
    qq = q.strip().lower()
    prepared_meaning = f["key"].map(lambda k: (core_info(k) or {}).get("meaning", CURATED.get(k, ("", "", ""))[0]))
    mask = f["expression"].astype(str).str.lower().str.contains(qq, regex=False) | prepared_meaning.astype(str).str.lower().str.contains(qq, regex=False)
    f = f[mask].copy()

pages = max(1, math.ceil(len(f) / per))
st.session_state.page = min(max(1, int(st.session_state.page)), pages)

# 숫자 직접 입력 기능 유지
page_input = st.number_input("페이지 직접 이동", min_value=1, max_value=pages, value=st.session_state.page, step=1)
if int(page_input) != st.session_state.page:
    st.session_state.page = int(page_input)
    st.rerun()

start = (st.session_state.page - 1) * per
view = f.iloc[start:start+per].copy()

# 현재 페이지 50개는 뜻/예문을 최대한 모두 채웁니다.
missing_exp = []
missing_example = []
row_data = []
for _, r in view.iterrows():
    exp = str(r["expression"]).strip()
    key = exp.lower()
    ci = core_info(key)
    if ci:
        row_data.append([exp, ci["meaning"], ci["example_en"] or make_example(exp), ci["example_ko"], ci.get("nuance", ""), ci.get("similar", "")])
    elif key in CURATED:
        m, ee, ek = CURATED[key]
        row_data.append([exp, m, ee, ek, "", ""])
    else:
        ee = make_example(exp)
        missing_exp.append(exp)
        missing_example.append(ee)
        row_data.append([exp, None, ee, None, "", ""])

if missing_exp:
    translations = translate_many(tuple(missing_exp + missing_example))
    n = len(missing_exp)
    meaning_map = dict(zip(missing_exp, translations[:n]))
    example_map = dict(zip(missing_exp, translations[n:]))
    for item in row_data:
        if item[1] is None:
            item[1] = meaning_map.get(item[0], "번역을 다시 시도해 주세요")
            item[3] = example_map.get(item[0], "번역을 다시 시도해 주세요")

st.caption(f"총 {len(f):,}개 표현 · 현재 {len(view)}개 표시 · {st.session_state.page}/{pages} 페이지")

cols = st.columns(5)
for i, item in enumerate(row_data):
    exp, meaning, ex_en, ex_ko, _, _ = item
    with cols[i % 5]:
        st.markdown(
            f'''<div class="card">
            <div class="e">{html.escape(exp)}</div>
            <div class="ko">{html.escape(str(meaning))}</div>
            <div class="ex">💬 {html.escape(str(ex_en))}</div>
            <div class="exko">{html.escape(str(ex_ko))}</div>
            </div>''',
            unsafe_allow_html=True,
        )
        if st.button("자세히 보기", key=f"detail_{st.session_state.page}_{i}_{exp}", use_container_width=True):
            st.session_state.selected_phrase = exp
            st.rerun()

# -------------------- 페이지 번호 네비게이션 --------------------
st.divider()
current = st.session_state.page
block_start = ((current - 1) // 5) * 5 + 1
nums = list(range(block_start, min(block_start + 5, pages + 1)))
nav_cols = st.columns(len(nums) + 2)

with nav_cols[0]:
    if st.button("◀ 이전", disabled=(current == 1), use_container_width=True):
        st.session_state.page = max(1, current - 1)
        st.rerun()

for idx, p in enumerate(nums, start=1):
    with nav_cols[idx]:
        label = f"● {p}" if p == current else str(p)
        if st.button(label, key=f"page_{p}", use_container_width=True):
            st.session_state.page = p
            st.rerun()

with nav_cols[-1]:
    if st.button("다음 ▶", disabled=(current == pages), use_container_width=True):
        st.session_state.page = min(pages, current + 1)
        st.rerun()
