
# Speak English V2

영어회화를 직접 말하고, 입력하고, 틀린 문장을 복습하는 개인 학습용 프로그램입니다.

## 주요 기능
- 80개+ 내장 핵심 회화 표현
- 구동사 / 구어체 / 여행 / 식당 / 전화 / 친구 / 일상 표현
- SQLite 로컬 데이터베이스
- Tatoeba 공식 API 영어-한국어 문장 추가 수집
- Tatoeba 문장 ID / 라이선스 정보 저장
- 한국어 → 영어 작문 훈련
- 간단 문자열 유사도 채점
- 틀린 문제 자동 복습
- 난이도 / 카테고리 필터
- 표현 DB 검색
- 누적 학습 통계

## 설치
Python 3.10 이상 권장

```bash
pip install -r requirements.txt
```

## 실행
```bash
streamlit run app.py
```

## 데이터베이스
첫 실행 시 `english_trainer.db`가 자동 생성됩니다.

## Tatoeba
'데이터 수집' 메뉴에서 공식 Tatoeba API를 통해 영어 문장과 한국어 번역을 추가로 수집할 수 있습니다.
인터넷 연결이 필요합니다.

Tatoeba:
https://tatoeba.org/
API:
https://api.tatoeba.org/

Tatoeba 데이터에는 Creative Commons 라이선스가 적용될 수 있으므로
재배포 또는 공개 서비스에 사용할 경우 각 데이터의 라이선스와 출처 표시 조건을 반드시 확인하십시오.

## 현재 V2의 한계
채점은 AI가 아니라 문자열 유사도 기반입니다.
같은 의미의 자연스러운 다른 영어 표현이더라도 점수가 낮을 수 있습니다.

다음 버전 권장 기능:
- LLM 기반 의미/문법/자연스러움 채점
- 음성 인식 및 발음 연습
- 개인 약점 분석
- spaced repetition
- 실제 AI 자유회화
