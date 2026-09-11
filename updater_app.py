
# -*- coding: utf-8 -*-
import streamlit as st
import random
from update_database import SEARCH_TERMS, collect_term, collect_many

st.set_page_config(page_title="V4 Database Updater", page_icon="🌐", layout="centered")
st.title("🌐 Speak English V4 DB Updater")
st.caption("Tatoeba에서 영어↔한국어 예문을 가져와 english_v4.db에 저장합니다.")

term=st.selectbox("표현",SEARCH_TERMS)
limit=st.slider("검색 문장 수",5,50,20,5)

if st.button("이 표현 예문 수집",use_container_width=True):
    try:
        added,found=collect_term(term,limit)
        st.success(f"검색 {found}건 / 새 예문 {added}건 저장")
    except Exception as e:
        st.error(str(e))

st.divider()
count=st.slider("랜덤으로 수집할 표현 수",3,30,10)
if st.button("랜덤 일괄 수집",use_container_width=True):
    terms=random.sample(SEARCH_TERMS,min(count,len(SEARCH_TERMS)))
    bar=st.progress(0)
    total=0
    for i,t in enumerate(terms,1):
        try:
            a,_=collect_term(t,15); total+=a
        except: pass
        bar.progress(i/len(terms))
    st.success(f"완료: 새 예문 {total}건 저장")
