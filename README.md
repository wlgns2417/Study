# Speak English V4

V4는 **핵심 표현 카드 + 외부 실제 예문 DB** 구조입니다.

## 파일
- `app.py` : 학습 화면
- `phrases.csv` : 핵심 표현 DB
- `update_database.py` : Tatoeba 예문 수집기
- `updater_app.py` : GUI 방식 데이터 수집기
- `english_v4.db` : 수집 후 자동 생성
- `requirements.txt`

## 1. 설치
```bash
pip install -r requirements.txt
```

## 2. 기존 학습 화면 실행
```bash
streamlit run app.py
```

## 3. 외부 예문 수집 화면 실행
새 터미널에서:
```bash
streamlit run updater_app.py
```

표현 하나를 골라 수집하거나 여러 표현을 랜덤으로 일괄 수집할 수 있습니다.

## 4. CLI로 대량 수집
```bash
python update_database.py
```

필요하면 `SEARCH_TERMS`와 `sample = SEARCH_TERMS[:20]` 부분을 조절할 수 있습니다.

## GitHub / Streamlit Cloud에서 중요한 점
Streamlit Community Cloud의 로컬 파일 시스템은 앱 재시작/재배포 시 영구 저장소로 생각하면 안 됩니다.
따라서 가장 안전한 방식은:

1. PC에서 `updater_app.py` 또는 `update_database.py` 실행
2. 생성된 `english_v4.db` 확인
3. `english_v4.db`를 GitHub 저장소에 업로드
4. Streamlit Cloud가 다시 배포되면 외부 예문이 학습 화면에 표시

즉 **수집은 로컬 → DB를 GitHub에 반영 → 웹앱은 읽기 전용** 구조를 권장합니다.

## 출처
외부 예문은 Tatoeba 공개 API를 통해 수집합니다.
Tatoeba 문장을 재사용/배포할 경우 해당 프로젝트의 최신 라이선스와 attribution 조건을 확인하십시오.
