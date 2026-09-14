# -*- coding: utf-8 -*-
from pathlib import Path
import html
import math
import re

import pandas as pd
import streamlit as st

CURATED = {
    "i don't":("나는 ~하지 않아","I don't think so."),
    "you know":("알잖아 / 있잖아","You know what I mean."),
    "all right":("알았어 / 좋아 / 괜찮아","All right, let's go."),
    "thank you":("고마워요","Thank you for your help."),
    "want to":("~하고 싶다","I want to go home."),
    "come on":("에이 / 제발 / 빨리","Come on, we're late."),
    "i know":("알아","I know how you feel."),
    "out of":("~이 떨어진 / ~밖으로","We're out of time."),
    "don't know":("모르겠어","I don't know yet."),
    "you want":("너는 ~을 원해 / ~하고 싶어","You want to try it?"),
    "i think":("내 생각엔 / ~인 것 같아","I think you're right."),
    "you don't":("너는 ~하지 않아","You don't have to go."),
    "to get":("~을 얻으려고 / ~하게 되다","I need to get some sleep."),
    "don't you":("~하지 않아? / 그렇지?","Don't you remember?"),
    "i'm not":("나는 ~이 아니야 / ~하지 않아","I'm not ready yet."),
    "i want":("나는 원해 / ~하고 싶어","I want some coffee."),
    "you think":("너는 ~라고 생각해","You think so?"),
    "i didn't":("나는 ~하지 않았어","I didn't mean that."),
    "i can't":("나는 ~할 수 없어","I can't do this alone."),
    "let me":("내가 ~하게 해줘 / 내가 ~할게","Let me check."),
    "don't want to":("~하고 싶지 않아","I don't want to leave."),
    "i love":("나는 ~을 정말 좋아해","I love this song."),
    "come here":("이리 와","Come here for a second."),
    "to work":("일하러 / 작동하도록","I have to go to work."),
    "don't be":("~하지 마 / ~이지 마","Don't be afraid."),
    "wait a":("잠깐 기다려 / 잠시","Wait a minute."),
    "try to":("~하려고 하다 / ~해보다","Try to stay calm."),
    "take the":("그 ~을 가져가 / 타다","Take the next train."),
    "you're a":("너는 ~이야","You're a good friend."),
    "that's right":("맞아 / 그래","That's right. I remember now."),
    "what's the matter":("무슨 일이야? / 왜 그래?","What's the matter with you?"),
    "don't worry":("걱정하지 마","Don't worry about it."),
    "that's why":("그래서 그런 거야","That's why I called you."),
    "know what":("뭔지 알아 / 있잖아","You know what? Let's go."),
    "a good":("좋은 ~","That's a good idea."),
    "i'm sorry":("미안해","I'm sorry I'm late."),
    "you get":("너는 얻어 / 이해하게 돼","You get what I mean."),
    "back to":("~로 돌아가 / 다시 ~로","Let's get back to work."),
    "you mean":("네 말은 ~라는 거지","You mean this one?"),
    "i've got":("나는 ~을 가지고 있어 / ~해야 해","I've got an idea."),
    "in this":("이 안에 / 이것에서","What's in this box?"),
    "you can't":("너는 ~할 수 없어 / ~하면 안 돼","You can't do that."),
    "don't want":("원하지 않아","I don't want that."),
    "it's a":("그건 ~이야","It's a good idea."),
    "tell you":("너에게 말해","Let me tell you something."),
    "the way":("방식 / 길 / ~하는 모습","I like the way you think."),
    "tell me":("말해줘","Tell me what happened."),
    "what do you mean":("무슨 뜻이야?","What do you mean by that?"),
    "what's going on":("무슨 일이야? / 어떻게 된 거야?","What's going on here?"),
    "i mean":("내 말은 / 그러니까","I mean, it's not that bad."),
    "i guess":("그런 것 같아 / 아마","I guess you're right."),
    "of course":("물론이지","Of course I remember."),
    "right now":("지금 당장","I need it right now."),
    "have to":("~해야 한다","I have to go now."),
    "gotta go":("가봐야 해","Sorry, I gotta go."),
    "let's go":("가자","Let's go home."),
    "get out":("나가 / 빠져나가다","Get out of here."),
    "calm down":("진정해","Calm down and listen to me."),
    "hurry up":("서둘러","Hurry up or we'll miss it."),
    "hang on":("잠깐만","Hang on, I'm coming."),
    "find out":("알아내다","I'll find out what happened."),
    "figure out":("알아내다 / 이해하다","We'll figure it out."),
    "work out":("잘 풀리다 / 운동하다","It'll work out somehow."),
    "pick up":("집다 / 데리러 가다 / 전화를 받다","I'll pick you up at six."),
    "give up":("포기하다","Don't give up now."),
    "come back":("돌아오다","Come back soon."),
    "take care":("잘 지내 / 몸조심해","Take care of yourself."),
    "never mind":("신경 쓰지 마 / 됐어","Never mind. It's okay."),
    "no way":("말도 안 돼 / 절대 안 돼","No way! Are you serious?"),
    "not really":("별로 / 꼭 그렇진 않아","Not really. I'm just tired."),
    "why not":("왜 안 돼? / 그러지 뭐","Why not give it a try?"),
    "sounds good":("좋아 / 괜찮네","Sounds good to me."),
    "fair enough":("그건 인정 / 일리 있네","Fair enough. I see your point."),
    "my bad":("내 실수야 / 미안","My bad, I forgot."),
    "no worries":("괜찮아 / 신경 쓰지 마","No worries, it's fine."),
    "give it a shot":("한번 해봐","Give it a shot."),
    "i'm on my way":("지금 가는 중이야","I'm on my way now."),
    "makes sense":("말이 되네 / 이해돼","That makes sense."),
    "i see":("알겠어 / 그렇구나","I see what you mean."),
    "got it":("알겠어","Got it. I'll do it now."),
    "just kidding":("농담이야","Relax, I'm just kidding."),
    "are you serious":("진심이야?","Are you serious right now?"),
    "trust me":("날 믿어","Trust me, it'll be fine."),
    "excuse me":("실례합니다 / 저기요","Excuse me, is this seat taken?"),
    "how come":("왜? / 어째서?","How come you didn't call?"),
    "can you":("~해줄래?","Can you help me?"),
    "could you":("~해주시겠어요?","Could you say that again?"),
    "let me know":("알려줘","Let me know when you're ready."),
    "hold on":("잠깐만","Hold on a second."),
}

WORD = {
    "i":"나","you":"너","we":"우리","they":"그들","he":"그","she":"그녀","it":"그것","me":"나를/나에게","him":"그에게","her":"그녀에게",
    "my":"내","your":"네","our":"우리의","their":"그들의","this":"이것/이","that":"그것/그","a":"하나의","an":"하나의","the":"그",
    "am":"~이다","is":"~이다","are":"~이다","was":"~였다","were":"~였다","be":"~이다","have":"가지다/~했다","has":"가지다/~했다","had":"가지고 있었다/~했다",
    "do":"하다","does":"하다","did":"했다","can":"~할 수 있다","could":"~할 수 있다","will":"~할 것이다","would":"~할 것이다","should":"~해야 한다","must":"반드시 ~해야 한다",
    "don't":"~하지 않아","doesn't":"~하지 않아","didn't":"~하지 않았어","can't":"~할 수 없어","won't":"~하지 않을 거야","wouldn't":"~하지 않을 거야",
    "isn't":"~이 아니야","aren't":"~이 아니야","haven't":"아직 ~하지 않았어","i'm":"나는 ~이야","you're":"너는 ~이야","we're":"우리는 ~이야","they're":"그들은 ~이야",
    "it's":"그건 ~이야","i've":"나는 ~했어/가지고 있어","what":"뭐","why":"왜","how":"어떻게","where":"어디","when":"언제","who":"누구",
    "want":"원하다","need":"필요하다","like":"좋아하다","love":"사랑하다/정말 좋아하다","hate":"싫어하다","know":"알다","think":"생각하다","mean":"뜻하다","guess":"~인 것 같다",
    "say":"말하다","tell":"말해주다","talk":"이야기하다","speak":"말하다","ask":"묻다","call":"전화하다/부르다","hear":"듣다","listen":"듣다","see":"보다/알다","look":"보다",
    "feel":"느끼다","remember":"기억하다","forget":"잊다","go":"가다","come":"오다","get":"얻다/되다","take":"가져가다/타다","give":"주다","put":"놓다","bring":"가져오다",
    "keep":"유지하다/계속하다","leave":"떠나다/두다","stay":"머무르다","wait":"기다리다","stop":"멈추다","start":"시작하다","try":"시도하다","help":"돕다","work":"일하다/작동하다",
    "find":"찾다","show":"보여주다","use":"사용하다","make":"만들다","let":"~하게 해주다","move":"움직이다","turn":"돌다/돌리다","run":"달리다/운영하다","happen":"일어나다",
    "good":"좋은","bad":"나쁜","great":"좋은/훌륭한","right":"맞는/오른쪽","wrong":"틀린","sure":"확실한","fine":"괜찮은","okay":"괜찮아","ready":"준비된","sorry":"미안해",
    "happy":"행복한","sad":"슬픈","tired":"피곤한","afraid":"두려운","big":"큰","small":"작은","little":"작은/조금","new":"새로운","old":"오래된/나이 든",
    "time":"시간","day":"날","night":"밤","today":"오늘","tomorrow":"내일","yesterday":"어제","now":"지금","later":"나중에","again":"다시","still":"여전히","already":"이미",
    "home":"집","house":"집","place":"장소","way":"길/방식","thing":"것","something":"무언가","nothing":"아무것도 없음","anything":"무엇이든","everything":"모든 것","people":"사람들",
    "man":"남자","woman":"여자","guy":"사람/남자","girl":"여자","boy":"남자아이","friend":"친구","family":"가족","mom":"엄마","dad":"아빠","name":"이름","money":"돈","job":"일/직업",
    "car":"차","phone":"전화","room":"방","world":"세상","life":"삶","problem":"문제","idea":"생각/아이디어",
    "to":"~에/~하기 위해","for":"~을 위해","from":"~에서","with":"~와 함께","without":"~없이","in":"~안에","on":"~위에/~에","at":"~에서","of":"~의","about":"~에 대해","by":"~에 의해/~옆에",
    "up":"위로","down":"아래로","out":"밖으로","back":"뒤로/다시","over":"너머로/끝난","off":"떨어져/꺼진","away":"멀리","around":"주변에","through":"통해서","before":"전에","after":"후에",
    "here":"여기","there":"거기","yes":"응/네","no":"아니","not":"아니다/~않다","really":"정말","just":"그냥/막","maybe":"아마","always":"항상","never":"절대 ~않다",
    "too":"너무/~도","very":"매우","so":"그래서/너무","more":"더","less":"덜","and":"그리고","or":"또는","but":"하지만","because":"왜냐하면","if":"만약","then":"그러면",
    "well":"음/잘","hey":"야/안녕","hi":"안녕","hello":"안녕하세요","thanks":"고마워","please":"제발/부탁해","yeah":"응","yep":"응","nope":"아니",
}

PHRASAL = {
    "get up":"일어나다","get out":"나가다","get back":"돌아오다","get in":"들어가다/타다","go back":"돌아가다","come back":"돌아오다",
    "come on":"어서/제발","hold on":"잠깐만","hang on":"잠깐만","find out":"알아내다","figure out":"알아내다/이해하다","work out":"잘 풀리다/운동하다",
    "give up":"포기하다","pick up":"집다/데리러 가다/전화 받다","look out":"조심하다","look for":"찾다","take care":"몸조심하다/돌보다",
    "calm down":"진정하다","hurry up":"서두르다","sit down":"앉다","wake up":"일어나다","shut up":"조용히 해","go away":"가버리다",
}


@st.cache_data
def load_expression_data(base_dir: str):
    base = Path(base_dir)
    mined_path = base / "mined_phrases.csv"
    core_path = base / "phrases.csv"
    mined = pd.read_csv(mined_path) if mined_path.exists() else pd.DataFrame()
    core = pd.read_csv(core_path) if core_path.exists() else pd.DataFrame()
    return mined, core


def render_expression_tab(base_dir: Path):
    mined, core = load_expression_data(str(base_dir))
    core_map = {}
    if not core.empty and "expression" in core.columns:
        for _, r in core.iterrows():
            key = str(r.get("expression", "")).strip().lower()
            if key:
                core_map[key] = r

    def offline_meaning(exp):
        k = exp.strip().lower()
        if k in core_map:
            m = str(core_map[k].get("meaning", "")).strip()
            if m and m.lower() != "nan":
                return m
        if k in CURATED:
            return CURATED[k][0]
        if k in PHRASAL:
            return PHRASAL[k]

        patterns = [
            (r"^i want to\b","나는 ~하고 싶어"),(r"^you want to\b","너는 ~하고 싶어"),
            (r"^i need to\b","나는 ~해야 해 / 필요해"),(r"^you need to\b","너는 ~해야 해"),
            (r"^i have to\b","나는 ~해야 해"),(r"^you have to\b","너는 ~해야 해"),
            (r"^i don't\b","나는 ~하지 않아"),(r"^you don't\b","너는 ~하지 않아"),
            (r"^i can't\b","나는 ~할 수 없어"),(r"^you can't\b","너는 ~할 수 없어"),
            (r"^i didn't\b","나는 ~하지 않았어"),(r"^you didn't\b","너는 ~하지 않았어"),
            (r"^i'm\b","나는 ~이야 / ~한 상태야"),(r"^you're\b","너는 ~이야 / ~한 상태야"),
            (r"^what\b","무엇 / 뭐"),(r"^why\b","왜"),(r"^how\b","어떻게"),(r"^where\b","어디"),(r"^when\b","언제"),(r"^who\b","누구"),
            (r"^can you\b","~해줄래?"),(r"^could you\b","~해주시겠어요?"),(r"^would you\b","~해주시겠어요? / ~할래?"),
            (r"^let me\b","내가 ~할게 / ~하게 해줘"),(r"^don't\b","~하지 마 / ~하지 않아"),
        ]
        for pat, base in patterns:
            if re.search(pat, k):
                tail = [WORD[w] for w in k.split() if w in WORD][-2:]
                return base + ((" · " + " / ".join(tail)) if tail else "")
        parts = [WORD[w] for w in k.split() if w in WORD]
        if parts:
            return " ".join(parts) + " · 문맥에 따라 자연스럽게 해석"
        return "일상 회화에서 문맥에 따라 뜻이 달라지는 표현"

    def example_for(exp):
        k = exp.strip().lower()
        if k in core_map:
            ex = str(core_map[k].get("example_en", "")).strip()
            if ex and ex.lower() != "nan":
                return ex
        if k in CURATED:
            return CURATED[k][1]
        if k.endswith(" to"):
            return f"I {k} go home."
        if re.match(r"^(what|why|how|where|when|who|are|do|did|can|could|would|will|is|isn't|aren't|don't|didn't)\b", k):
            return exp[:1].upper() + exp[1:].rstrip(".?!") + "?"
        if re.match(r"^(come|go|get|take|give|look|hold|wait|tell|call|try|keep|stop|let|remember|forget|listen|watch|check|help|follow)\b", k):
            return exp[:1].upper() + exp[1:].rstrip(".?!") + "."
        if re.match(r"^(i|you|we|they|he|she|it)\b", k):
            return exp[:1].upper() + exp[1:].rstrip(".?!") + "."
        return f"You'll hear “{exp}” a lot in everyday conversation."

    if mined.empty:
        st.warning("mined_phrases.csv가 없습니다.")
        return

    f = mined.copy()
    f["expression"] = f["expression"].astype(str).str.strip()
    f["meaning_ko"] = f["expression"].apply(offline_meaning)
    f["example_en"] = f["expression"].apply(example_for)

    c1, c2 = st.columns([3, 1])
    q = c1.text_input("표현 검색", placeholder="don't worry / 걱정하지 마", key="phrase_search")
    per = c2.selectbox("한 화면", [20, 30, 40, 50], index=3, key="phrase_per")

    if q:
        qq = q.strip().lower()
        f = f[
            f["expression"].str.lower().str.contains(qq, regex=False)
            | f["meaning_ko"].str.lower().str.contains(qq, regex=False)
        ]

    pages = max(1, math.ceil(len(f) / per))
    if "phrase_page" not in st.session_state:
        st.session_state.phrase_page = 1
    st.session_state.phrase_page = max(1, min(int(st.session_state.phrase_page), pages))

    page_input = st.number_input(
        "표현 페이지 직접 이동",
        min_value=1,
        max_value=pages,
        value=st.session_state.phrase_page,
        step=1,
        key="phrase_page_input",
    )
    if int(page_input) != st.session_state.phrase_page:
        st.session_state.phrase_page = int(page_input)
        st.rerun()

    page = st.session_state.phrase_page
    view = f.iloc[(page - 1) * per:page * per]
    st.markdown(
        f'<div class="page-caption">전체 {len(f):,}개 표현 · 현재 {len(view)}개 표시 · {page}/{pages} 페이지</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    for i, (_, r) in enumerate(view.iterrows()):
        exp = html.escape(str(r["expression"]))
        ko = html.escape(str(r["meaning_ko"]))
        ex = html.escape(str(r["example_en"]))
        card = '<div class="card"><div class="e">' + exp + '</div><div class="ko">' + ko + '</div><div class="ex">💬 ' + ex + '</div></div>'
        with cols[i % 5]:
            st.markdown(card, unsafe_allow_html=True)

    st.divider()
    block_start = ((page - 1) // 5) * 5 + 1
    block_end = min(block_start + 4, pages)
    btns = st.columns(7)
    with btns[0]:
        if st.button("◀ 이전", key="phrase_prev", use_container_width=True, disabled=(page <= 1)):
            st.session_state.phrase_page = page - 1
            st.rerun()

    for idx, p in enumerate(range(block_start, block_end + 1), start=1):
        with btns[idx]:
            if st.button(("● " + str(p)) if p == page else str(p), key=f"phrase_page_{p}", use_container_width=True):
                st.session_state.phrase_page = p
                st.rerun()

    with btns[6]:
        if st.button("다음 ▶", key="phrase_next", use_container_width=True, disabled=(page >= pages)):
            st.session_state.phrase_page = page + 1
            st.rerun()
