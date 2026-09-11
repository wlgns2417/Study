
# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import requests
import random
import re
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher

st.set_page_config(page_title="Speak English V2", page_icon="🗣️", layout="wide")

DB_PATH = "english_trainer.db"
TATOEBA_API = "https://api.tatoeba.org/v1/sentences"

SEED_LESSONS = [
("A2","일상","feel like ~ing","~하고 싶은 기분이다","나 오늘 그냥 집에 있고 싶어.","I feel like staying home today.","I just want to stay home today."),
("A2","일상","be down for","~할 마음이 있다 / 좋다","나도 그거 할래.","I'm down for that.","Yeah, I'm totally down for that."),
("B1","구동사","figure out","알아내다 / 이해하다","결국 방법을 알아냈어.","I finally figured it out.","I finally managed to figure it out."),
("A2","친구","hang out","같이 시간을 보내다","우리 나중에 만나서 놀자.","Let's hang out later.","Do you want to hang out later?"),
("B1","구동사","run into","우연히 마주치다","어제 우연히 옛 친구를 만났어.","I ran into an old friend yesterday.","I happened to run into an old friend yesterday."),
("B1","구동사","come up with","생각해내다","좋은 아이디어가 하나 떠올랐어.","I came up with a good idea.","I just came up with a really good idea."),
("B1","구동사","end up ~ing","결국 ~하게 되다","결국 늦게까지 일했어.","I ended up working late.","I ended up working pretty late."),
("B1","구동사","turn out","결과적으로 ~되다","생각보다 잘 됐어.","It turned out better than I expected.","It actually turned out better than I expected."),
("A2","구동사","put off","미루다","그 일은 내일까지 미루자.","Let's put it off until tomorrow.","Let's just put it off until tomorrow."),
("A2","구동사","pick up","데리러 가다","내가 데리러 갈게.","I'll pick you up.","I'll come pick you up."),
("B1","관계","get along","잘 지내다","걔랑 잘 지내?","Do you get along with him?","Do you two get along?"),
("A2","일상","take your time","천천히 해","천천히 해도 돼.","Take your time.","No rush. Take your time."),
("A2","일상","no worries","괜찮아 / 걱정 마","괜찮아, 신경 쓰지 마.","No worries.","No worries at all."),
("B1","일상","I'm good","괜찮아요 / 됐어요","저는 괜찮아요.","I'm good.","No thanks, I'm good."),
("B1","일상","sounds good","좋아 / 괜찮네","좋아, 그렇게 하자.","Sounds good.","Sounds good to me."),
("B1","일상","that works for me","난 괜찮아","그 시간 괜찮아.","That works for me.","Yeah, that works for me."),
("B1","일상","I'm all set","다 됐어요 / 괜찮아요","전 다 됐어요.","I'm all set.","Thanks, I'm all set."),
("B1","일상","my bad","내 실수야","아, 내 실수야.","My bad.","Oh, my bad."),
("B1","일상","fair enough","그럴 만하네 / 인정","그건 인정할게.","Fair enough.","Yeah, fair enough."),
("B2","일상","you've got a point","일리가 있다","네 말도 일리가 있어.","You've got a point.","Actually, you've got a point."),
("A2","상태","be tired of","~에 질리다","이거 이제 지겨워.","I'm tired of this.","I'm getting tired of this."),
("B1","상태","be used to","~에 익숙하다","나는 이제 일찍 일어나는 게 익숙해.","I'm used to getting up early.","I'm pretty used to getting up early now."),
("B1","상태","get used to","~에 익숙해지다","곧 익숙해질 거야.","You'll get used to it.","Don't worry, you'll get used to it."),
("B1","계획","be supposed to","~하기로 되어 있다","나 오늘 그 사람 만나기로 했어.","I'm supposed to meet him today.","I'm supposed to meet him later today."),
("B1","계획","be about to","막 ~하려던 참이다","나 막 나가려던 참이야.","I'm about to leave.","I was just about to leave."),
("B1","계획","might as well","이왕이면 ~하다","이왕 온 김에 먹고 가자.","We might as well eat while we're here.","We might as well grab something to eat."),
("B2","계획","I'm thinking of ~ing","~할까 생각 중이다","주말에 여행 갈까 생각 중이야.","I'm thinking of traveling this weekend.","I'm thinking of taking a trip this weekend."),
("A2","의견","I think","내 생각에는","내 생각엔 괜찮은 것 같아.","I think it's okay.","I think it's pretty good."),
("B1","의견","I guess","아마 / 그런 것 같아","그런 것 같아.","I guess so.","Yeah, I guess so."),
("B1","의견","as far as I know","내가 알기로는","내가 알기로는 오늘 쉬는 날이야.","As far as I know, today is a day off.","As far as I know, they're closed today."),
("B2","의견","from my point of view","내 관점에서는","내 관점에서는 그게 더 나아.","From my point of view, that's better.","From my point of view, that's the better option."),
("B1","요청","do you mind if","~해도 괜찮나요","창문 좀 열어도 괜찮아?","Do you mind if I open the window?","Would you mind if I opened the window?"),
("A2","요청","could you","~해주시겠어요","사진 좀 찍어주시겠어요?","Could you take a picture for me?","Could you take a photo of us?"),
("B1","요청","would you mind ~ing","~해주시겠어요","조금 조용히 해주시겠어요?","Would you mind keeping it down?","Would you mind being a little quieter?"),
("A2","식당","I'd like","~을 원합니다","아메리카노 한 잔 주세요.","I'd like an Americano, please.","Can I get an Americano, please?"),
("B1","식당","Can I get ~?","~주세요","물 좀 주실 수 있나요?","Can I get some water?","Could I get some water, please?"),
("B1","식당","I'll have ~","~로 할게요","저는 스테이크로 할게요.","I'll have the steak.","I'll go with the steak."),
("B1","식당","go with","~을 선택하다","저는 이걸로 할게요.","I'll go with this one.","I think I'll go with this one."),
("A2","쇼핑","I'm just looking","그냥 둘러보는 중이에요","그냥 둘러보는 중이에요.","I'm just looking.","Thanks, I'm just looking."),
("A2","쇼핑","try on","입어보다","이거 입어봐도 돼요?","Can I try this on?","Could I try this on?"),
("A2","여행","check in","체크인하다","체크인하고 싶어요.","I'd like to check in.","Hi, I'd like to check in."),
("A2","여행","check out","체크아웃하다","체크아웃은 몇 시예요?","What time is check-out?","What time do I need to check out?"),
("B1","여행","get around","돌아다니다 / 이동하다","여기서는 어떻게 돌아다니는 게 좋아요?","What's the best way to get around here?","How do people usually get around here?"),
("A2","전화","hold on","잠깐만","잠깐만 기다려.","Hold on.","Hold on a second."),
("B1","전화","get back to","나중에 답하다","확인하고 다시 연락할게.","I'll check and get back to you.","Let me check and I'll get back to you."),
("B1","전화","cut off","전화가 끊기다","전화가 갑자기 끊겼어.","We got cut off.","Sorry, I think we got cut off."),
("B1","감정","can't stand","정말 못 견디다","나는 그 소음을 못 참겠어.","I can't stand that noise.","I seriously can't stand that noise."),
("B1","감정","be into","~에 푹 빠져 있다","요즘 러닝에 빠졌어.","I'm into running these days.","I've been really into running lately."),
("B1","감정","not really my thing","내 취향은 아니다","그건 내 취향은 아니야.","It's not really my thing.","That's not really my thing."),
("B2","감정","have mixed feelings","복잡한 감정이 들다","그 일에 대해 마음이 복잡해.","I have mixed feelings about it.","Honestly, I have mixed feelings about it."),
("B1","시간","every now and then","가끔","가끔 거기 가.","I go there every now and then.","I still go there every now and then."),
("B1","시간","once in a while","가끔씩","가끔은 쉬어야 해.","You need to rest once in a while.","You should take a break once in a while."),
("B2","시간","sooner or later","조만간 결국","조만간 알게 될 거야.","You'll find out sooner or later.","Sooner or later, you'll find out."),
("B1","문제","deal with","처리하다 / 다루다","내가 이 문제를 처리할게.","I'll deal with this problem.","Don't worry, I'll deal with it."),
("B1","문제","work on","~을 개선하려고 노력하다","내 영어를 더 연습해야 해.","I need to work on my English.","I really need to work on my English."),
("B2","문제","sort out","정리하다 / 해결하다","내가 이 문제를 해결해볼게.","I'll sort this out.","Give me a minute. I'll sort it out."),
("B1","변화","cut down on","~을 줄이다","커피를 좀 줄이려고 해.","I'm trying to cut down on coffee.","I'm trying to cut down on how much coffee I drink."),
("B1","변화","give up","포기하다","아직 포기하지 마.","Don't give up yet.","Come on, don't give up yet."),
("B1","변화","keep up with","따라가다","요즘 너무 바빠서 못 따라가겠어.","I'm too busy to keep up.","I've been so busy I can't keep up."),
("B2","변화","catch up on","밀린 것을 따라잡다","주말에 밀린 잠 좀 잘 거야.","I'm going to catch up on sleep this weekend.","I need to catch up on some sleep this weekend."),
("B1","대화","by the way","그런데 / 그러고 보니","그런데, 내일 시간 돼?","By the way, are you free tomorrow?","Oh, by the way, are you free tomorrow?"),
("B1","대화","speaking of","~ 얘기가 나와서 말인데","여행 얘기가 나와서 말인데, 부산 가봤어?","Speaking of travel, have you been to Busan?","Speaking of trips, have you ever been to Busan?"),
("B2","대화","come to think of it","생각해보니","생각해보니 나도 그 사람 본 적 있어.","Come to think of it, I've seen him before.","Now that I think about it, I've seen him before."),
("B1","대화","to be honest","솔직히 말하면","솔직히 나는 별로였어.","To be honest, I didn't really like it.","Honestly, it wasn't really my thing."),
("B2","대화","if you ask me","내 생각에는","내 생각엔 그건 너무 비싸.","If you ask me, it's too expensive.","If you ask me, that's way too expensive."),
("B1","업무일상","take care of","처리하다 / 돌보다","내가 그거 처리할게.","I'll take care of it.","Don't worry, I'll take care of it."),
("B1","업무일상","look into","알아보다 / 조사하다","내가 한번 알아볼게.","I'll look into it.","Let me look into it and get back to you."),
("B2","업무일상","follow up on","후속 확인하다","내일 다시 확인해볼게.","I'll follow up on it tomorrow.","I'll follow up on that tomorrow."),
("B1","상태","run out of","~이 다 떨어지다","우유가 다 떨어졌어.","We ran out of milk.","Looks like we ran out of milk."),
("B1","상태","be running low on","~이 얼마 안 남다","커피가 얼마 안 남았어.","We're running low on coffee.","Looks like we're running low on coffee."),
("A2","일상","wake up","잠에서 깨다","오늘 늦게 일어났어.","I woke up late today.","I ended up waking up late today."),
("A2","일상","head out","나가다 / 출발하다","나 이제 나갈게.","I'm heading out now.","Alright, I'm gonna head out now."),
("B1","일상","drop by","잠깐 들르다","집에 가는 길에 들를게.","I'll drop by on my way home.","I'll probably drop by on my way home."),
("B1","일상","chill out","쉬다 / 진정하다","오늘은 그냥 집에서 쉴 거야.","I'm just going to chill at home today.","I'm just gonna chill at home today."),
("B1","일상","grab a bite","간단히 먹다","뭐 좀 간단히 먹자.","Let's grab a bite.","Do you want to grab a bite?"),
("B1","일상","give it a shot","한번 해보다","일단 한번 해봐.","Just give it a shot.","Why don't you just give it a shot?"),
("B2","일상","go for it","해봐 / 밀어붙여","하고 싶으면 해봐.","If you want to do it, go for it.","If that's what you want, go for it."),
("B1","일상","I'm on my way","가는 중이야","나 지금 가는 중이야.","I'm on my way.","I'm already on my way."),
("B1","일상","I'm running late","늦고 있다","나 조금 늦을 것 같아.","I'm running a little late.","Sorry, I'm running a bit late."),
("B1","일상","it's up to you","네가 정해","네가 정해.","It's up to you.","Whatever you want. It's up to you."),
("B1","일상","I'll pass","사양할게","난 이번엔 사양할게.","I'll pass this time.","Thanks, but I think I'll pass."),
("B2","일상","I'm not sure yet","아직 잘 모르겠다","아직 결정 못 했어.","I'm not sure yet.","I haven't decided yet."),
("B1","일상","let me know","알려줘","결정하면 알려줘.","Let me know when you decide.","Just let me know when you decide."),
("B1","일상","make sure","꼭 확인하다","문 잠갔는지 꼭 확인해.","Make sure you locked the door.","Make sure the door is locked."),
("B2","일상","it depends","경우에 따라 다르다","상황에 따라 달라.","It depends.","It really depends on the situation."),
("B1","일상","not a big deal","별일 아니다","별거 아니야.","It's not a big deal.","Don't worry. It's really not a big deal."),
("B2","일상","I couldn't agree more","전적으로 동의한다","완전 동의해.","I couldn't agree more.","Yeah, I couldn't agree more."),
]

SEARCH_TERMS = [
"figure out","pick up","hang out","run into","work out","come up with","end up",
"turn out","get along","put off","take care of","look into","run out of","get back to",
"deal with","give up","check in","check out","hold on","by the way","to be honest",
"make sure","let me know","sounds good","take your time","no worries","on my way",
"running late","try on","drop by","grab a bite","go for it","give it a shot"
]

def conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    c = conn()
    c.execute("""CREATE TABLE IF NOT EXISTS lessons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT, category TEXT, expression TEXT, meaning TEXT,
        ko TEXT NOT NULL, en TEXT NOT NULL, natural TEXT,
        source TEXT NOT NULL DEFAULT 'Curated',
        source_id TEXT, license TEXT, created_at TEXT,
        UNIQUE(ko, en)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS progress(
        lesson_id INTEGER PRIMARY KEY,
        attempts INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        wrong INTEGER DEFAULT 0,
        last_score INTEGER DEFAULT 0,
        last_seen TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS stats(
        key TEXT PRIMARY KEY, value TEXT
    )""")
    count = c.execute("SELECT COUNT(*) FROM lessons WHERE source='Curated'").fetchone()[0]
    if count == 0:
        c.executemany("""INSERT OR IGNORE INTO lessons
        (level,category,expression,meaning,ko,en,natural,source,created_at)
        VALUES(?,?,?,?,?,?,?,'Curated',?)""",
        [(*row, datetime.now().isoformat(timespec="seconds")) for row in SEED_LESSONS])
    c.commit()
    c.close()

def norm(s):
    s = s.lower().strip()
    s = re.sub(r"[^\w\s']", " ", s)
    s = s.replace("wanna","want to").replace("gonna","going to")
    return " ".join(s.split())

def score_answer(user, target):
    r = SequenceMatcher(None, norm(user), norm(target)).ratio()
    if r >= .90: return 100
    if r >= .78: return 90
    if r >= .66: return 80
    if r >= .52: return 65
    return 40

def update_progress(lesson_id, score):
    c=conn()
    row=c.execute("SELECT attempts,correct,wrong FROM progress WHERE lesson_id=?",(lesson_id,)).fetchone()
    attempts,correct,wrong = row if row else (0,0,0)
    attempts += 1
    if score >= 80: correct += 1
    else: wrong += 1
    c.execute("""INSERT OR REPLACE INTO progress
    (lesson_id,attempts,correct,wrong,last_score,last_seen) VALUES(?,?,?,?,?,?)""",
    (lesson_id,attempts,correct,wrong,score,date.today().isoformat()))
    c.commit(); c.close()

def get_stats():
    c=conn()
    total=c.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    curated=c.execute("SELECT COUNT(*) FROM lessons WHERE source='Curated'").fetchone()[0]
    tatoeba=c.execute("SELECT COUNT(*) FROM lessons WHERE source='Tatoeba'").fetchone()[0]
    attempts=c.execute("SELECT COALESCE(SUM(attempts),0) FROM progress").fetchone()[0]
    correct=c.execute("SELECT COALESCE(SUM(correct),0) FROM progress").fetchone()[0]
    wrongq=c.execute("SELECT COUNT(*) FROM progress WHERE last_score < 80").fetchone()[0]
    c.close()
    return total,curated,tatoeba,attempts,correct,wrongq

def extract_korean_translations(item):
    out=[]
    for t in item.get("translations",[]) or []:
        if isinstance(t, dict) and t.get("lang")=="kor" and t.get("text"):
            out.append(t)
    return out

def import_tatoeba(term, limit=20):
    params = {
        "lang":"eng",
        "q":term,
        "trans:lang":"kor",
        "trans:is_direct":"yes",
        "trans:is_unapproved":"no",
        "word_count":"2-14",
        "sort":"random",
        "limit":limit,
        "showtrans":"matching"
    }
    r=requests.get(TATOEBA_API, params=params, timeout=15)
    r.raise_for_status()
    payload=r.json()
    added=0
    c=conn()
    for item in payload.get("data",[]) or []:
        en=(item.get("text") or "").strip()
        sid=str(item.get("id") or "")
        lic=item.get("license") or ""
        if not en or len(en)>140:
            continue
        trans=extract_korean_translations(item)
        for t in trans[:2]:
            ko=(t.get("text") or "").strip()
            if not ko or len(ko)>120:
                continue
            try:
                c.execute("""INSERT INTO lessons
                (level,category,expression,meaning,ko,en,natural,source,source_id,license,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                ("Mixed","Tatoeba",term,"Tatoeba 영어-한국어 예문",ko,en,en,"Tatoeba",sid,lic,datetime.now().isoformat(timespec="seconds")))
                added += 1
            except sqlite3.IntegrityError:
                pass
    c.commit(); c.close()
    return added, len(payload.get("data",[]) or [])

def fetch_lesson(mode="all", level="전체", category="전체"):
    c=conn()
    where=[]; params=[]
    if level!="전체":
        where.append("l.level=?"); params.append(level)
    if category!="전체":
        where.append("l.category=?"); params.append(category)
    if mode=="review":
        where.append("COALESCE(p.last_score,100) < 80")
    sql="""SELECT l.id,l.level,l.category,l.expression,l.meaning,l.ko,l.en,l.natural,l.source,l.source_id,l.license,
                  COALESCE(p.attempts,0),COALESCE(p.last_score,0)
           FROM lessons l LEFT JOIN progress p ON l.id=p.lesson_id"""
    if where: sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY RANDOM() LIMIT 1"
    row=c.execute(sql,params).fetchone()
    c.close()
    return row

def options_values(col):
    c=conn()
    vals=[r[0] for r in c.execute(f"SELECT DISTINCT {col} FROM lessons WHERE {col} IS NOT NULL AND {col}<>'' ORDER BY {col}").fetchall()]
    c.close()
    return ["전체"]+vals

init_db()

st.title("🗣️ Speak English V2")
st.caption("구동사 · 구어체 · 상황회화 · Tatoeba 문장 DB · 오답 복습")

total,curated,tatoeba,attempts,correct,wrongq=get_stats()
m1,m2,m3,m4,m5=st.columns(5)
m1.metric("📚 전체 문장", total)
m2.metric("⭐ 내장 회화", curated)
m3.metric("🌐 Tatoeba", tatoeba)
m4.metric("✍️ 누적 풀이", attempts)
acc=round(correct/attempts*100,1) if attempts else 0
m5.metric("🎯 정답률", f"{acc}%")

with st.sidebar:
    st.header("학습 설정")
    mode=st.radio("모드",["회화 훈련","오답 복습","표현 탐색","데이터 수집"])
    level=st.selectbox("난이도", options_values("level"))
    category=st.selectbox("카테고리", options_values("category"))
    st.divider()
    st.caption("V2는 SQLite에 학습 데이터와 오답 기록을 저장합니다.")

if mode in ["회화 훈련","오답 복습"]:
    review = mode=="오답 복습"
    if "lesson_row" not in st.session_state or st.button("🎲 새 문제"):
        st.session_state.lesson_row=fetch_lesson("review" if review else "all",level,category)
        st.session_state.checked=False

    row=st.session_state.get("lesson_row")
    if not row:
        st.warning("조건에 맞는 문제가 없습니다. 필터를 바꾸거나 먼저 학습해 주세요.")
    else:
        (lid,lvl,cat,expr,meaning,ko,en,natural,source,sid,lic,att,last)=row
        c1,c2=st.columns([2,1])
        with c1:
            st.subheader("🇰🇷 영어로 말해보세요")
            st.info(ko)
            user=st.text_input("영어 답변", key=f"ans_{lid}", placeholder="머릿속으로 먼저 말한 다음 입력해보세요.")
            if st.button("✅ 채점하기", use_container_width=True):
                if not user.strip():
                    st.warning("답변을 먼저 입력해 주세요.")
                else:
                    s=score_answer(user,en)
                    update_progress(lid,s)
                    st.session_state.checked=True
                    st.session_state.last_eval=(s,user)
        with c2:
            st.markdown("#### 표현 정보")
            st.write(f"**Level:** {lvl}")
            st.write(f"**분류:** {cat}")
            if expr: st.write(f"**표현:** `{expr}`")
            if meaning: st.write(f"**뜻:** {meaning}")
            st.write(f"**Source:** {source}")

        if st.session_state.get("checked") and st.session_state.get("last_eval"):
            s,user_ans=st.session_state.last_eval
            st.divider()
            if s>=90: st.success(f"🔥 아주 좋습니다 — {s}점")
            elif s>=80: st.success(f"👍 의미와 표현이 좋습니다 — {s}점")
            elif s>=65: st.warning(f"🙂 거의 왔습니다 — {s}점")
            else: st.error(f"💪 다시 한 번 연습해보세요 — {s}점")
            a,b=st.columns(2)
            with a:
                st.markdown("#### ✅ 기준 표현")
                st.code(en, language=None)
                if natural and natural!=en:
                    st.markdown("#### 💬 더 자연스럽게")
                    st.code(natural, language=None)
            with b:
                st.markdown("#### 🧠 암기 포인트")
                if expr: st.write(f"**{expr}**")
                if meaning: st.write(meaning)
                if source=="Tatoeba":
                    st.caption(f"Tatoeba sentence ID: {sid or '-'} · License: {lic or 'see Tatoeba source'}")
            if st.button("다음 문제 ➜", use_container_width=True):
                st.session_state.lesson_row=fetch_lesson("review" if review else "all",level,category)
                st.session_state.checked=False
                st.rerun()

elif mode=="표현 탐색":
    st.subheader("🔎 표현 데이터베이스")
    keyword=st.text_input("검색", placeholder="예: figure out, 여행, 미루다")
    c=conn()
    if keyword:
        q=f"%{keyword}%"
        rows=c.execute("""SELECT level,category,expression,meaning,ko,en,source
                          FROM lessons WHERE expression LIKE ? OR meaning LIKE ? OR ko LIKE ? OR en LIKE ?
                          ORDER BY source,expression LIMIT 200""",(q,q,q,q)).fetchall()
    else:
        rows=c.execute("""SELECT level,category,expression,meaning,ko,en,source
                          FROM lessons ORDER BY RANDOM() LIMIT 100""").fetchall()
    c.close()
    st.dataframe(rows, use_container_width=True,
                 column_config={
                    0:"Level",1:"분류",2:"표현",3:"뜻",4:"한국어",5:"영어",6:"출처"
                 })

elif mode=="데이터 수집":
    st.subheader("🌐 Tatoeba 영어-한국어 문장 가져오기")
    st.write("공식 Tatoeba API에서 영어 문장과 한국어 번역을 찾아 SQLite DB에 추가합니다.")
    st.caption("수집한 각 문장은 Source=Tatoeba로 구분되며, 가능한 경우 sentence ID와 라이선스를 함께 저장합니다.")

    term=st.selectbox("회화 표현", SEARCH_TERMS)
    limit=st.slider("한 번에 검색할 문장 수",5,50,20,5)

    if st.button("이 표현 문장 가져오기", use_container_width=True):
        with st.spinner("Tatoeba에서 문장을 가져오는 중..."):
            try:
                added,found=import_tatoeba(term,limit)
                st.success(f"검색 {found}건 중 새 영어-한국어 문장 {added}건을 DB에 추가했습니다.")
            except Exception as e:
                st.error(f"가져오기에 실패했습니다: {e}")

    st.divider()
    st.markdown("#### 🚀 여러 표현 한꺼번에 수집")
    howmany=st.slider("수집할 표현 개수",3,min(20,len(SEARCH_TERMS)),8)
    if st.button("랜덤 표현 일괄 수집", use_container_width=True):
        chosen=random.sample(SEARCH_TERMS,howmany)
        total_added=0
        progress=st.progress(0)
        status=st.empty()
        for i,t in enumerate(chosen,1):
            status.write(f"수집 중: **{t}** ({i}/{howmany})")
            try:
                added,_=import_tatoeba(t,15)
                total_added += added
            except Exception:
                pass
            progress.progress(i/howmany)
        st.success(f"완료: 새 문장 {total_added}건 추가")
        st.caption("중복 문장은 자동으로 제외됩니다.")

st.divider()
st.caption("내장 회화 표현은 학습용으로 직접 구성한 데이터이며, Tatoeba에서 가져온 문장은 출처를 별도로 표시합니다.")
