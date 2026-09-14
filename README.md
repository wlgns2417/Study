# Speak English - Clean v3

실제 영어 회화 데이터에 기반한 Streamlit 학습 앱입니다.

## 화면 구성
- **💬 회화 표현**: OpenSubtitles v2018에서 발굴한 2~5단어 구어체 표현
- **📚 회화 단어**: SUBTLEX-US + OpenSubtitles 빈도와 학습가치를 결합한 단어

## 실행 순서
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python collect_phrases.py
python collect_words.py
python -m streamlit run app.py
```

## 회화 표현 데이터
`collect_phrases.py`는 OPUS API를 사용하지 않습니다.
공식 OPUS object storage의 OpenSubtitles v2018 영어 gzip을 직접 스트리밍하고,
처음 500,000 라인만 읽어 `mined_phrases.csv`를 생성합니다.
전체 수 GB 파일을 PC에 저장하지 않습니다.

## 회화 단어 데이터
`collect_words.py`는 다음 자료를 결합해 `conversation_words.csv`를 생성합니다.

1. **SUBTLEX-US** 계열 빈도표 (`words/subtlex-word-frequencies`)
2. **OpenSubtitles 2018** 빈도표 (`hermitdave/FrequencyWords`)
3. **Open English-Korean Dictionary** (`jhseo1211/open-english-korean-dict`)

선별 과정은 다음과 같습니다.

```text
실사용 코퍼스 빈도
    ↓
기능어 / 자막 노이즈 제거
    ↓
너무 쉬운 기초어 및 A1 단어 제거
    ↓
활용형을 가능한 범위에서 기본형으로 통합
    ↓
한국어 뜻 / 품사 / CEFR 결합
    ↓
실사용 빈도 × 회화 활용도 × 학습 가치 점수화
    ↓
상위 3,000개 저장
```

`conversation_words.csv`가 아직 없으면 앱의 **회화 단어** 탭에는 대표 단어 미리보기가 표시됩니다. `python collect_words.py`를 실행해 CSV를 생성하면 앱은 자동으로 실제 코퍼스 기반 데이터로 전환됩니다.
