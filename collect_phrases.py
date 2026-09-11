# -*- coding: utf-8 -*-
"""
Speak English - OpenSubtitles frequent phrase collector (direct streaming version)

Run:
    python collect_phrases.py

This version DOES NOT use the OPUS API.
It streams the official OPUS object-storage gzip directly and stops after a
practical sample, so it does not need to download the whole multi-GB corpus.
"""

from collections import Counter
from pathlib import Path
import csv
import gzip
import html
import io
import math
import re
import requests

BASE = Path(__file__).resolve().parent
OUT = BASE / "mined_phrases.csv"

SOURCE_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/mono/en.txt.gz"
SOURCE_NAME = "OpenSubtitles v2018 / OPUS"

MAX_LINES = 500_000
TOP_N = 3000

STOP_PHRASES = {
    "of the","in the","to the","on the","at the","for the","and the","from the",
    "it is","that is","this is","there is","there are","i am","you are","we are",
    "he is","she is","they are","i have","you have","we have","do you","did you",
    "are you","have you","can you","will you","would you","could you","the one",
    "a lot","one of","as a","with the","about the","into the","by the","or the",
    "was the","is the","are the","to be","have the","has the","had the"
}

MARKERS = {
    "gonna","wanna","gotta","yeah","yep","nope","okay","ok","hey","sorry",
    "thanks","thank","please","really","just","know","mean","guess","think",
    "want","need","let","come","go","get","take","give","look","find","work",
    "hang","hold","wait","tell","talk","call","feel","sounds","sure","right",
    "way","thing","time","kidding","serious","maybe","fine","good","bad",
    "love","hate","believe","remember","forget","care","mind","ready","wrong",
    "deal","problem","happen","happened","matter","trying","try"
}

PARTICLES = {
    "up","out","off","on","over","back","down","away","around","through",
    "by","in","along","across","after","ahead"
}

def normalize(text: str) -> str:
    text = html.unescape(text).lower().replace("’", "'")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def useful(phrase: str) -> bool:
    words = phrase.split()
    if not (2 <= len(words) <= 5):
        return False
    if phrase in STOP_PHRASES:
        return False
    if len(set(words)) == 1:
        return False
    if all(len(w) <= 2 for w in words):
        return False

    conversational = any(w in MARKERS for w in words)
    contraction = any("'" in w for w in words)
    phrasal = len(words) <= 4 and any(w in PARTICLES for w in words)
    return conversational or contraction or phrasal

def stream_lines():
    print("[1/3] OpenSubtitles 데이터를 직접 스트리밍합니다.")
    print("      전체 파일을 저장하지 않고 필요한 부분만 읽습니다.")
    print(f"      목표 분석 라인: {MAX_LINES:,}\n")

    headers = {
        "User-Agent": "Mozilla/5.0 SpeakEnglishStudy/1.0",
        "Accept-Encoding": "identity",
    }

    with requests.get(
        SOURCE_URL,
        stream=True,
        timeout=(20, 120),
        headers=headers,
    ) as response:
        response.raise_for_status()
        response.raw.decode_content = False

        with gzip.GzipFile(fileobj=response.raw, mode="rb") as gz:
            text = io.TextIOWrapper(gz, encoding="utf-8", errors="ignore")
            for i, line in enumerate(text, start=1):
                yield line
                if i >= MAX_LINES:
                    break

def mine():
    counts = Counter()
    lines = 0

    print("[2/3] 실제 자막에서 2~5단어 회화 표현 빈도를 계산합니다.")

    for line in stream_lines():
        lines += 1

        if lines % 50_000 == 0:
            print(f"      {lines:,}줄 분석 완료...")

        text = normalize(line)
        words = text.split()

        if not (2 <= len(words) <= 30):
            continue

        for n in range(2, 6):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i:i+n])
                if useful(phrase):
                    counts[phrase] += 1

    return counts, lines

def save(counts):
    rows = []

    for rank, (phrase, count) in enumerate(counts.most_common(TOP_N), 1):
        score = min(100.0, round(20 * math.log10(count + 1), 1))
        rows.append([
            rank,
            phrase,
            count,
            score,
            SOURCE_NAME,
        ])

    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank",
            "expression",
            "count",
            "frequency_score",
            "source",
        ])
        writer.writerows(rows)

    return len(rows)

def main():
    print("=" * 64)
    print(" Speak English - 실사용 표현 자동 수집")
    print("=" * 64)

    try:
        counts, lines = mine()
    except requests.exceptions.SSLError as e:
        print("\n[오류] OPUS object storage SSL 연결에 실패했습니다.")
        print("회사 보안 프록시/SSL 검사 환경일 가능성이 있습니다.")
        raise
    except requests.exceptions.RequestException:
        print("\n[오류] 다운로드 연결에 실패했습니다.")
        print("인터넷 또는 회사 방화벽/프록시를 확인해 주세요.")
        raise

    if lines == 0:
        raise RuntimeError("영어 자막 데이터를 읽지 못했습니다.")

    if not counts:
        raise RuntimeError("분석 가능한 회화 표현을 찾지 못했습니다.")

    saved = save(counts)

    print("\n[3/3] 완료")
    print(f"      분석 라인 : {lines:,}")
    print(f"      저장 표현 : {saved:,}")
    print(f"      생성 파일 : {OUT.name}")
    print("\n다음 명령으로 앱을 실행하세요:")
    print("python -m streamlit run app.py")

if __name__ == "__main__":
    main()
