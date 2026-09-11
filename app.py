# -*- coding: utf-8 -*-
from pathlib import Path
import math
import html
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

# 자주 등장하는 회화 청크의 자연스러운 한국어 뜻 + 짧은 예문.
# phrases.csv에 더 좋은 해설이 있으면 그 데이터를 우선 사용합니다.
PHRASE_DATA = {
    "i don't": ("나는 ~하지 않아", "I don't think so.", "난 그렇게 생각하지 않아."),
    "you know": ("알잖아 / 있잖아", "You know what I mean.", "내 말 무슨 뜻인지 알잖아."),
    "all right": ("알았어 / 좋아 / 괜찮아", "All right, let's go.", "좋아, 가자."),
    "thank you": ("고마워요", "Thank you for your help.", "도와줘서 고마워요."),
    "want to": ("~하고 싶다", "I want to go home.", "집에 가고 싶어."),
    "come on": ("에이 / 제발 / 빨리", "Come on, we're late.", "빨리, 우리 늦었어."),
    "i know": ("알아", "I know how you feel.", "네 기분이 어떤지 알아."),
    "out of": ("~이 떨어진 / ~밖으로", "We're out of time.", "우리 시간이 다 됐어."),
    "don't know": ("모르겠어", "I don't know yet.", "아직 모르겠어."),
    "you want": ("너는 ~을 원해 / ~하고 싶어", "You want to try it?", "이거 해보고 싶어?"),
    "i think": ("내 생각엔 / ~인 것 같아", "I think you're right.", "네 말이 맞는 것 같아."),
    "you don't": ("너는 ~하지 않아", "You don't have to go.", "너 갈 필요 없어."),
    "to get": ("~을 얻으려고 / ~하게 되다", "I need to get some sleep.", "나 좀 자야 해."),
    "don't you": ("~하지 않아? / 그렇지?", "Don't you remember?", "기억 안 나?"),
    "i'm not": ("나는 ~이 아니야 / ~하지 않아", "I'm not ready yet.", "난 아직 준비 안 됐어."),
    "i want": ("나는 원해 / ~하고 싶어", "I want some coffee.", "커피 좀 마시고 싶어."),
    "you think": ("너는 ~라고 생각해", "You think so?", "그렇게 생각해?"),
    "i didn't": ("나는 ~하지 않았어", "I didn't mean that.", "그런 뜻은 아니었어."),
    "i can't": ("나는 ~할 수 없어", "I can't do this alone.", "이건 혼자 못 하겠어."),
    "let me": ("내가 ~하게 해줘 / 내가 ~할게", "Let me check.", "내가 확인해볼게."),
    "don't want to": ("~하고 싶지 않아", "I don't want to leave.", "나 가고 싶지 않아."),
    "i love": ("나는 ~을 정말 좋아해", "I love this song.", "나 이 노래 정말 좋아해."),
    "come here": ("이리 와", "Come here for a second.", "잠깐 이리 와봐."),
    "to work": ("일하러 / 작동하도록", "I have to go to work.", "나 일하러 가야 해."),
    "don't be": ("~하지 마 / ~이지 마", "Don't be afraid.", "무서워하지 마."),
    "try to": ("~하려고 하다 / ~해보다", "Try to stay calm.", "침착하려고 해봐."),
    "that's right": ("맞아 / 그래", "That's right. I remember now.", "맞아. 이제 기억나."),
    "what's the matter": ("무슨 일이야? / 왜 그래?", "What's the matter with you?", "너 왜 그래?"),
    "i wouldn't": ("나라면 ~하지 않을 거야", "I wouldn't do that.", "나라면 그렇게 안 할 거야."),
    "you won't": ("너는 ~하지 않을 거야", "You won't regret it.", "후회하지 않을 거야."),
    "tell him": ("그에게 말해", "Tell him I'm here.", "내가 여기 있다고 그에게 말해."),
    "that's why": ("그래서 그런 거야", "That's why I called you.", "그래서 너한테 전화한 거야."),
    "aren't you": ("~아니야? / 그렇지?", "Aren't you tired?", "너 피곤하지 않아?"),
    "don't worry": ("걱정하지 마", "Don't worry about it.", "그건 걱정하지 마."),
    "i haven't": ("나는 아직 ~하지 않았어", "I haven't decided yet.", "아직 결정하지 않았어."),
    "don't think": ("~라고 생각하지 않아", "I don't think it's a good idea.", "좋은 생각은 아닌 것 같아."),
    "didn't you": ("너 ~하지 않았어?", "Didn't you call me?", "너 나한테 전화하지 않았어?"),
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
    "right now": ("지금 당장", "I need it right now.", "나 지금 당장 그게 필요해."),
    "what happened": ("무슨 일이 있었어?", "What happened last night?", "어젯밤에 무슨 일이 있었어?"),
    "what do you mean": ("무슨 뜻이야?", "What do you mean by that?", "그게 무슨 뜻이야?"),
    "what's going on": ("무슨 일이야? / 어떻게 된 거야?", "What's going on here?", "여기 무슨 일이야?"),
    "i mean": ("내 말은 / 그러니까", "I mean, it's not that bad.", "내 말은, 그렇게 나쁘진 않다는 거야."),
    "i guess": ("그런 것 같아 / 아마", "I guess you're right.", "네 말이 맞는 것 같아."),
    "i need to": ("나는 ~해야 해", "I need to talk to you.", "너랑 얘기해야 해."),
    "have to": ("~해야 한다", "I have to go now.", "나 이제 가야 해."),
    "gotta go": ("가봐야 해", "Sorry, I gotta go.", "미안, 나 가봐야 해."),
    "let's go": ("가자", "Let's go home.", "집에 가자."),
    "let's see": ("어디 보자 / 두고 보자", "Let's see what happens.", "어떻게 되는지 보자."),
    "get out": ("나가 / 빠져나가다", "Get out of here.", "여기서 나가."),
    "get back": ("돌아오다 / 되돌아가다", "When did you get back?", "언제 돌아왔어?"),
    "get up": ("일어나다", "Get up. We're late.", "일어나. 우리 늦었어."),
    "calm down": ("진정해", "Calm down and listen to me.", "진정하고 내 말 들어."),
    "hurry up": ("서둘러", "Hurry up or we'll miss it.", "서둘러, 안 그러면 놓쳐."),
    "hang on": ("잠깐만", "Hang on, I'm coming.", "잠깐만, 지금 가."),
    "look out": ("조심해", "Look out!", "조심해!"),
    "find out": ("알아내다", "I'll find out what happened.", "무슨 일이 있었는지 알아볼게."),
    "work out": ("잘 풀리다 / 운동하다", "It'll work out somehow.", "어떻게든 잘 풀릴 거야."),
    "pick up": ("집다 / 데리러 가다 / 전화를 받다", "I'll pick you up at six.", "6시에 데리러 갈게."),
    "give up": ("포기하다", "Don't give up now.", "지금 포기하지 마."),
    "come back": ("돌아오다", "Come back soon.", "곧 돌아와."),
    "take care": ("잘 지내 / 몸조심해", "Take care of yourself.", "몸 잘 챙겨."),
    "take it easy": ("진정해 / 무리하지 마", "Take it easy today.", "오늘은 무리하지 마."),
    "never mind": ("신경 쓰지 마 / 됐어", "Never mind. It's okay.", "신경 쓰지 마. 괜찮아."),
    "no way": ("말도 안 돼 / 절대 안 돼", "No way! Are you serious?", "말도 안 돼! 진짜야?"),
    "not really": ("별로 / 꼭 그렇진 않아", "Not really. I'm just tired.", "별로. 그냥 피곤해."),
    "why not": ("왜 안 돼? / 그러지 뭐", "Why not give it a try?", "한번 해보는 게 어때?"),
    "that's okay": ("괜찮아", "That's okay. Don't worry.", "괜찮아. 걱정하지 마."),
    "it's okay": ("괜찮아", "It's okay to be nervous.", "긴장해도 괜찮아."),
    "makes sense": ("말이 되네 / 이해돼", "That makes sense.", "그거 말이 되네."),
    "i see": ("알겠어 / 그렇구나", "I see what you mean.", "무슨 말인지 알겠어."),
    "got it": ("알겠어", "Got it. I'll do it now.", "알겠어. 지금 할게."),
    "here we go": ("자, 시작한다 / 또 시작이네", "Here we go again.", "또 시작이네."),
    "there you go": ("자, 여기 있어 / 그렇지", "There you go. Much better.", "그렇지. 훨씬 낫네."),
    "i'm ready": ("준비됐어", "I'm ready when you are.", "너 준비되면 나도 준비됐어."),
    "i'm fine": ("난 괜찮아", "I'm fine, thanks.", "난 괜찮아, 고마워."),
    "just kidding": ("농담이야", "Relax, I'm just kidding.", "진정해, 그냥 농담이야."),
    "are you serious": ("진심이야?", "Are you serious right now?", "너 지금 진심이야?"),
    "trust me": ("날 믿어", "Trust me, it'll be fine.", "날 믿어, 괜찮을 거야."),
    "excuse me": ("실례합니다 / 저기요", "Excuse me, is this seat taken?", "실례합니다, 여기 자리 있나요?"),
    "how come": ("왜? / 어째서?", "How come you didn't call?", "왜 전화 안 했어?"),
    "can you": ("~해줄래?", "Can you help me?", "나 좀 도와줄래?"),
    "could you": ("~해주시겠어요?", "Could you say that again?", "다시 말씀해주시겠어요?"),
}

# 잘린 조각 중 학습 가치가 특히 낮은 것만 제외합니다.
BLOCKED = {"wait a", "take the", "you're a", "a little", "of the", "in the", "to the", "and the", "for the"}

core_map = {}
if not core.empty and "expression" in core.columns:
    for _, r in core.iterrows():
        core_map[str(r["expression"]).strip().lower()] = r

def study_info(expression):
    key = str(expression).strip().lower()
    if key in core_map:
        r = core_map[key]
        meaning = str(r.get("meaning", "")).strip()
        ex_en = str(r.get("example_en", "")).strip()
        ex_ko = str(r.get("example_ko", "")).strip()
        if meaning and meaning.lower() != "nan":
            return meaning, ex_en if ex_en.lower() != "nan" else "", ex_ko if ex_ko.lower() != "nan" else ""
    return PHRASE_DATA.get(key, ("", "", ""))

st.markdown("""
<style>
.block-container{max-width:1600px;padding-top:1rem}
.card{border:1px solid rgba(120,120,120,.28);border-radius:14px;padding:13px 15px;min-height:150px;margin-bottom:10px}
.card .e{font-size:20px;font-weight:800;line-height:1.25}
.card .ko{font-size:14px;font-weight:750;margin-top:8px;color:#8fd3ff;line-height:1.35}
.card .ex{font-size:12px;opacity:.84;margin-top:12px;line-height:1.5}
.muted{opacity:.7}
</style>
""", unsafe_allow_html=True)

st.title("🗣️ Speak English")
st.caption("자주 쓰는 영어 표현 · 한국어 뜻 · 실제 사용 예문")

if mined.empty:
    st.warning("mined_phrases.csv가 없습니다.")
else:
    c1, c2 = st.columns([3,1])
    q = c1.text_input("검색", placeholder="don't worry / 걱정하지 마")
    per = c2.selectbox("한 화면", [20,30,40,50], index=3)

    f = mined.copy()
    f["key"] = f["expression"].astype(str).str.strip().str.lower()
    f = f[~f["key"].isin(BLOCKED)]
    f[["meaning_ko", "example_en", "example_ko"]] = f["expression"].apply(lambda x: pd.Series(study_info(x)))

    # 번역/예문이 준비된 실제 학습 카드만 표시합니다.
    f = f[f["meaning_ko"].astype(str).str.len() > 0].copy()

    if q:
        qq = q.strip().lower()
        f = f[
            f["expression"].astype(str).str.lower().str.contains(qq, regex=False) |
            f["meaning_ko"].astype(str).str.lower().str.contains(qq, regex=False)
        ]

    pages = max(1, math.ceil(len(f) / per))
    page = st.number_input("페이지", min_value=1, max_value=pages, value=1)
    view = f.iloc[(page-1)*per:page*per]
    st.caption(f"학습 표현 {len(f):,}개 · 현재 {len(view)}개 표시 · {page}/{pages} 페이지")

    cols = st.columns(5)
    for i, (_, r) in enumerate(view.iterrows()):
        exp = html.escape(str(r["expression"]))
        ko = html.escape(str(r["meaning_ko"]))
        ex_en = html.escape(str(r["example_en"]))
        ex_ko = html.escape(str(r["example_ko"]))
        with cols[i % 5]:
            st.markdown(
                f'''<div class="card">
                <div class="e">{exp}</div>
                <div class="ko">{ko}</div>
                <div class="ex">💬 {ex_en}<br><span class="muted">{ex_ko}</span></div>
                </div>''',
                unsafe_allow_html=True,
            )
