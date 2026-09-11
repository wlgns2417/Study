
import streamlit as st
import pandas as pd
import random, json
from pathlib import Path

st.set_page_config(page_title="Speak English V3", page_icon="🗣️", layout="wide")
BASE = Path(__file__).parent
DB = BASE/"phrases.csv"
STATE = BASE/"study_state.json"

@st.cache_data
def load_db():
    return pd.read_csv(DB)

def load_state():
    if STATE.exists():
        try: return json.loads(STATE.read_text(encoding="utf-8"))
        except: pass
    return {"favorites":[],"mastered":[],"review":[],"seen":[]}

def save_state(s):
    try: STATE.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8")
    except: pass

df = load_db()
s = load_state()

st.markdown("""
<style>
.block-container{max-width:1280px;padding-top:1.3rem}
.study-card{border:1px solid rgba(128,128,128,.28);border-radius:22px;padding:34px;min-height:410px}
.expr{font-size:48px;font-weight:800;line-height:1.12;margin:8px 0 18px}
.meaning{font-size:30px;font-weight:750;margin-bottom:18px}
.muted{opacity:.68;font-size:14px}
.tag{display:inline-block;border:1px solid rgba(128,128,128,.35);border-radius:999px;padding:5px 11px;margin:2px 5px 2px 0;font-size:13px}
.exbox{border-left:4px solid rgba(128,128,128,.45);padding-left:16px;margin:10px 0 20px}
div.stButton>button{border-radius:12px}
</style>
""", unsafe_allow_html=True)

st.title("🗣️ Speak English V3")
st.caption("회화 표현을 많이 보고, 소리 내어 읽고, 실제 뉘앙스까지 함께 익히는 학습 앱")

with st.sidebar:
    st.header("📚 학습 설정")
    cat = st.selectbox("카테고리", ["전체"]+sorted(df.category.unique().tolist()))
    lev = st.selectbox("난이도", ["전체"]+sorted(df.level.unique().tolist()))
    mode = st.radio("학습 목록", ["전체 표현","즐겨찾기","다시 보기","암기 완료 제외"])
    q = st.text_input("🔎 표현 검색", placeholder="figure out / 괜찮아 / 여행")
    st.divider()
    st.metric("전체 표현", len(df))
    st.metric("⭐ 즐겨찾기", len(s["favorites"]))
    st.metric("🔁 다시 보기", len(s["review"]))
    st.metric("✅ 암기 완료", len(s["mastered"]))

f = df.copy()
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
if mode=="즐겨찾기": f=f[f.expression.isin(s["favorites"])]
elif mode=="다시 보기": f=f[f.expression.isin(s["review"])]
elif mode=="암기 완료 제외": f=f[~f.expression.isin(s["mastered"])]
f=f.reset_index(drop=True)

if len(f)==0:
    st.warning("현재 조건에 맞는 표현이 없습니다.")
    st.stop()

if "idx" not in st.session_state: st.session_state.idx=0
if st.session_state.idx>=len(f): st.session_state.idx=0

a,b,c,d,e = st.columns([1,1,1,1,5])
if a.button("◀ 이전",use_container_width=True):
    st.session_state.idx=(st.session_state.idx-1)%len(f); st.rerun()
if b.button("🎲 랜덤",use_container_width=True):
    st.session_state.idx=random.randrange(len(f)); st.rerun()
if c.button("다음 ▶",use_container_width=True):
    st.session_state.idx=(st.session_state.idx+1)%len(f); st.rerun()
d.markdown(f"**{st.session_state.idx+1} / {len(f)}**")

r=f.iloc[st.session_state.idx]
expr=str(r.expression)
if expr not in s["seen"]:
    s["seen"].append(expr); save_state(s)

left,right=st.columns([0.9,1.35],gap="large")
stars="★"*int(r.frequency)+"☆"*(5-int(r.frequency))

with left:
    st.markdown(f"""
    <div class="study-card">
      <div class="muted">TODAY'S EXPRESSION</div>
      <div class="expr">{r.expression}</div>
      <span class="tag">{r.category}</span>
      <span class="tag">{r.level}</span>
      <span class="tag">{r.style}</span>
      <br><br><div class="muted">회화 빈도</div>
      <div style="font-size:25px">{stars}</div>
      <br><div class="muted">추천 학습법</div>
      <div style="font-size:18px;line-height:1.75;margin-top:7px">
        ① 표현을 소리 내어 3번 읽기<br>
        ② 예문을 통째로 한 번 말하기<br>
        ③ 예문의 단어 하나를 바꿔 내 문장 만들기
      </div>
    </div>""",unsafe_allow_html=True)

with right:
    st.markdown(f"""
    <div class="study-card">
      <div class="meaning">{r.meaning}</div>
      <div class="muted">💡 실제 뉘앙스</div>
      <div style="font-size:18px;line-height:1.75;margin:8px 0 20px">{r.nuance}</div>
      <div class="muted">💬 실제 예문</div>
      <div class="exbox">
        <div style="font-size:21px;font-weight:650">{r.example_en}</div>
        <div style="font-size:16px;opacity:.72;margin-top:6px">{r.example_ko}</div>
      </div>
      <div class="muted">🔗 비슷한 표현</div>
      <div style="font-size:17px;margin-top:6px">{r.similar}</div>
    </div>""",unsafe_allow_html=True)

st.write("")
x1,x2,x3,x4=st.columns(4)
fav=expr in s["favorites"]; rev=expr in s["review"]; mas=expr in s["mastered"]

if x1.button("⭐ 즐겨찾기 해제" if fav else "☆ 즐겨찾기",use_container_width=True):
    s["favorites"].remove(expr) if fav else s["favorites"].append(expr); save_state(s); st.rerun()
if x2.button("🔁 다시 보기 해제" if rev else "🔁 다시 보기",use_container_width=True):
    s["review"].remove(expr) if rev else s["review"].append(expr); save_state(s); st.rerun()
if x3.button("✅ 암기 완료 해제" if mas else "✅ 암기 완료",use_container_width=True):
    if mas: s["mastered"].remove(expr)
    else:
        s["mastered"].append(expr)
        if expr in s["review"]: s["review"].remove(expr)
    save_state(s); st.rerun()
if x4.button("🎯 다음 랜덤 표현",use_container_width=True):
    st.session_state.idx=random.randrange(len(f)); st.rerun()

st.divider()
with st.expander("📖 전체 표현 목록"):
    st.dataframe(
        f[["expression","meaning","category","level","frequency","style"]],
        use_container_width=True, hide_index=True,
        column_config={"expression":"영어 표현","meaning":"뜻","category":"분류","level":"난이도","frequency":"빈도","style":"말투"}
    )

st.subheader("📊 학습 현황")
m1,m2,m3,m4=st.columns(4)
m1.metric("본 표현",len(s["seen"]))
m2.metric("암기 완료",len(s["mastered"]))
m3.metric("즐겨찾기",len(s["favorites"]))
m4.metric("다시 보기",len(s["review"]))
st.progress(min(len(s["mastered"])/max(len(df),1),1.0))
st.caption(f"전체 {len(df)}개 중 {len(s['mastered'])}개 암기 완료")

with st.expander("⚙️ 학습 기록 초기화"):
    if st.button("모든 학습 기록 초기화"):
        save_state({"favorites":[],"mastered":[],"review":[],"seen":[]})
        st.session_state.clear()
        st.rerun()
