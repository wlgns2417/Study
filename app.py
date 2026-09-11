
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import sqlite3, json, random, os
from pathlib import Path

st.set_page_config(page_title="Speak English V4", page_icon="🗣️", layout="wide")
BASE = Path(__file__).parent
PHRASES = BASE/"phrases.csv"
DB = BASE/"english_v4.db"
STATE = BASE/"study_state.json"

@st.cache_data
def load_phrases():
    return pd.read_csv(PHRASES)

def load_state():
    if STATE.exists():
        try: return json.loads(STATE.read_text(encoding="utf-8"))
        except: pass
    return {"favorites":[],"mastered":[],"review":[],"seen":[]}

def save_state(s):
    try: STATE.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8")
    except: pass

def ext_examples(expression, n=5):
    if not DB.exists(): return []
    try:
        con=sqlite3.connect(DB)
        rows=con.execute("""
            SELECT en,ko,source,source_sentence_id,source_user,license
            FROM examples WHERE lower(expression)=lower(?)
            ORDER BY RANDOM() LIMIT ?
        """,(expression,n)).fetchall()
        con.close()
        return rows
    except:
        return []

def ext_count():
    if not DB.exists(): return 0
    try:
        con=sqlite3.connect(DB)
        n=con.execute("SELECT COUNT(*) FROM examples").fetchone()[0]
        con.close(); return n
    except: return 0

df=load_phrases()
state=load_state()

st.markdown("""
<style>
.block-container{max-width:1320px;padding-top:1.2rem}
.study-card{border:1px solid rgba(128,128,128,.28);border-radius:22px;padding:34px;min-height:410px}
.expr{font-size:48px;font-weight:800;line-height:1.12;margin:8px 0 18px}
.meaning{font-size:30px;font-weight:750;margin-bottom:18px}
.muted{opacity:.68;font-size:14px}
.tag{display:inline-block;border:1px solid rgba(128,128,128,.35);border-radius:999px;padding:5px 11px;margin:2px 5px 2px 0;font-size:13px}
.exbox{border-left:4px solid rgba(128,128,128,.45);padding-left:16px;margin:10px 0 20px}
div.stButton>button{border-radius:12px}
</style>
""",unsafe_allow_html=True)

st.title("🗣️ Speak English V4")
st.caption("핵심 회화 표현 + 외부 실제 예문 DB")

with st.sidebar:
    st.header("📚 학습 설정")
    cat=st.selectbox("카테고리",["전체"]+sorted(df.category.dropna().unique().tolist()))
    lev=st.selectbox("난이도",["전체"]+sorted(df.level.dropna().unique().tolist()))
    mode=st.radio("학습 목록",["전체 표현","즐겨찾기","다시 보기","암기 완료 제외"])
    q=st.text_input("🔎 검색",placeholder="figure out / 괜찮아 / 여행")
    st.divider()
    st.metric("핵심 표현",len(df))
    st.metric("🌐 외부 예문",ext_count())
    st.metric("⭐ 즐겨찾기",len(state["favorites"]))
    st.metric("✅ 암기 완료",len(state["mastered"]))

f=df.copy()
if cat!="전체": f=f[f.category==cat]
if lev!="전체": f=f[f.level==lev]
if q:
    ql=q.lower()
    f=f[
        f.expression.fillna("").str.lower().str.contains(ql,regex=False) |
        f.meaning.fillna("").str.lower().str.contains(ql,regex=False) |
        f.nuance.fillna("").str.lower().str.contains(ql,regex=False) |
        f.example_en.fillna("").str.lower().str.contains(ql,regex=False)
    ]
if mode=="즐겨찾기": f=f[f.expression.isin(state["favorites"])]
elif mode=="다시 보기": f=f[f.expression.isin(state["review"])]
elif mode=="암기 완료 제외": f=f[~f.expression.isin(state["mastered"])]
f=f.reset_index(drop=True)

if len(f)==0:
    st.warning("현재 조건에 맞는 표현이 없습니다.")
    st.stop()

if "idx" not in st.session_state: st.session_state.idx=0
if st.session_state.idx>=len(f): st.session_state.idx=0

a,b,c,d,_=st.columns([1,1,1,1,5])
if a.button("◀ 이전",use_container_width=True):
    st.session_state.idx=(st.session_state.idx-1)%len(f); st.rerun()
if b.button("🎲 랜덤",use_container_width=True):
    st.session_state.idx=random.randrange(len(f)); st.rerun()
if c.button("다음 ▶",use_container_width=True):
    st.session_state.idx=(st.session_state.idx+1)%len(f); st.rerun()
d.markdown(f"**{st.session_state.idx+1} / {len(f)}**")

r=f.iloc[st.session_state.idx]
expr=str(r.expression)
if expr not in state["seen"]:
    state["seen"].append(expr); save_state(state)

left,right=st.columns([.9,1.35],gap="large")
stars="★"*int(r.frequency)+"☆"*(5-int(r.frequency))

with left:
    st.markdown(f"""
    <div class="study-card">
      <div class="muted">TODAY'S EXPRESSION</div>
      <div class="expr">{r.expression}</div>
      <span class="tag">{r.category}</span><span class="tag">{r.level}</span><span class="tag">{r.style}</span>
      <br><br><div class="muted">회화 활용도</div>
      <div style="font-size:25px">{stars}</div>
      <br><div class="muted">학습법</div>
      <div style="font-size:18px;line-height:1.75;margin-top:7px">
      ① 표현 3번 소리 내기<br>② 예문 통째로 말하기<br>③ 단어 하나 바꿔 내 문장 만들기
      </div>
    </div>""",unsafe_allow_html=True)

with right:
    st.markdown(f"""
    <div class="study-card">
      <div class="meaning">{r.meaning}</div>
      <div class="muted">💡 실제 뉘앙스</div>
      <div style="font-size:18px;line-height:1.75;margin:8px 0 20px">{r.nuance}</div>
      <div class="muted">💬 대표 예문</div>
      <div class="exbox">
        <div style="font-size:21px;font-weight:650">{r.example_en}</div>
        <div style="font-size:16px;opacity:.72;margin-top:6px">{r.example_ko}</div>
      </div>
      <div class="muted">🔗 비슷한 표현</div>
      <div style="font-size:17px;margin-top:6px">{r.similar}</div>
    </div>""",unsafe_allow_html=True)

x1,x2,x3,x4=st.columns(4)
fav=expr in state["favorites"]; rev=expr in state["review"]; mas=expr in state["mastered"]
if x1.button("⭐ 즐겨찾기 해제" if fav else "☆ 즐겨찾기",use_container_width=True):
    state["favorites"].remove(expr) if fav else state["favorites"].append(expr); save_state(state); st.rerun()
if x2.button("🔁 다시 보기 해제" if rev else "🔁 다시 보기",use_container_width=True):
    state["review"].remove(expr) if rev else state["review"].append(expr); save_state(state); st.rerun()
if x3.button("✅ 암기 완료 해제" if mas else "✅ 암기 완료",use_container_width=True):
    if mas: state["mastered"].remove(expr)
    else:
        state["mastered"].append(expr)
        if expr in state["review"]: state["review"].remove(expr)
    save_state(state); st.rerun()
if x4.button("🎯 다음 랜덤 표현",use_container_width=True):
    st.session_state.idx=random.randrange(len(f)); st.rerun()

# External real examples
st.divider()
st.subheader("🌐 외부 실제 예문")
examples=ext_examples(expr,5)
if examples:
    for i,(en,ko,src,sid,user,lic) in enumerate(examples,1):
        with st.container(border=True):
            st.markdown(f"**{i}. {en}**")
            st.write(ko)
            details=f"{src}"
            if sid: details+=f" · sentence #{sid}"
            if user: details+=f" · contributor: {user}"
            if lic: details+=f" · {lic}"
            st.caption(details)
else:
    st.info("아직 이 표현의 외부 예문이 없습니다. `update_database.py`를 실행하면 실제 영어↔한국어 예문을 추가할 수 있습니다.")

st.divider()
st.subheader("📊 학습 현황")
m1,m2,m3,m4=st.columns(4)
m1.metric("본 표현",len(state["seen"]))
m2.metric("암기 완료",len(state["mastered"]))
m3.metric("즐겨찾기",len(state["favorites"]))
m4.metric("다시 보기",len(state["review"]))

with st.expander("📖 전체 표현 목록"):
    st.dataframe(f[["expression","meaning","category","level","frequency","style"]],
                 use_container_width=True,hide_index=True)

with st.expander("ℹ️ 데이터 출처"):
    st.write("핵심 표현의 뜻·뉘앙스·대표 예문은 학습용으로 직접 구성했습니다.")
    st.write("외부 예문은 Tatoeba API에서 수집하며, DB에 문장 ID·기여자·라이선스 정보를 가능한 범위에서 함께 저장합니다.")
