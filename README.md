# Speak English - Clean v2

## 실행 순서
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python collect_phrases.py
python -m streamlit run app.py
```

`collect_phrases.py`는 OPUS API를 사용하지 않습니다.
공식 OPUS object storage의 OpenSubtitles v2018 영어 gzip을 직접 스트리밍하고,
처음 500,000 라인만 읽어 `mined_phrases.csv`를 생성합니다.
전체 수 GB 파일을 PC에 저장하지 않습니다.
