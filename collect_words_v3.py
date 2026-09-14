# -*- coding: utf-8 -*-
"""Final ranking/filter layer for conversational vocabulary."""
import bz2
import re
import time

import requests

import collect_words_v2 as core

EXTRA_EXCLUDE = set("""
wait through until since men years days things haven early hit hurt pick shut sound simple possible
clear went came coming wanted talking looking called show used using left took made said told seen gave given
word words tonight tomorrow yesterday morning night everyone everybody someone somebody anyone anything
somewhere everything nothing
""".split())

FORMALISH = set("""
involve require maintain negotiate acknowledge demonstrate transform generate advocate justify
independent various effective essential establish determine indicate obtain ensure implement analyze
analysis significant specific approach process provide identify represent occur assume
""".split())

MORE_IRREGULAR = {
    "men":"man", "women":"woman", "children":"child", "things":"thing", "years":"year", "days":"day",
    "came":"come", "coming":"come", "wanted":"want", "talking":"talk", "looking":"look", "called":"call",
    "leaving":"leave", "waiting":"wait", "picked":"pick", "picking":"pick", "shown":"show", "showed":"show",
    "using":"use", "used":"use", "hurt":"hurt", "went":"go", "left":"leave",
}


def valid_word(word):
    return core.valid_word_original(word) and word not in EXTRA_EXCLUDE


def lemma(word, dictionary):
    if word in MORE_IRREGULAR:
        return MORE_IRREGULAR[word]
    if word in core.IRREGULAR:
        return core.IRREGULAR[word]

    candidates = []
    if word.endswith("ies") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("ing") and len(word) > 5:
        base = word[:-3]
        candidates.extend([base, base + "e"])
        if len(base) > 2 and base[-1] == base[-2]:
            candidates.append(base[:-1])
    if word.endswith("ed") and len(word) > 4:
        base = word[:-2]
        candidates.extend([base, base + "e"])
        if len(base) > 2 and base[-1] == base[-2]:
            candidates.append(base[:-1])
    if word.endswith("es") and len(word) > 4:
        candidates.extend([word[:-2], word[:-1]])
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        candidates.append(word[:-1])

    # 먼저 기본형으로 합친 뒤 basic-word 필터를 적용해 talking/talk 같은 중복을 없앱니다.
    for candidate in candidates:
        if candidate in dictionary:
            return candidate
    return word


def cefr_score(level):
    return {"A1":0.0, "A2":0.78, "B1":1.0, "B2":0.93, "C1":0.76, "C2":0.60}.get(level, 0.55)


def conversation_score(pos, word):
    p = str(pos).lower()
    if "verb" in p:
        score = 1.0
    elif "adverb" in p or p == "adv":
        score = 0.99
    elif "adjective" in p or p == "adj":
        score = 0.91
    elif "noun" in p:
        score = 0.57
    else:
        score = 0.48
    if word in core.CURATED_EXAMPLES:
        score = 1.0
    if word in FORMALISH:
        score *= 0.68
    return score


def resilient_cc0_examples(target_words):
    """Tatoeba CC0를 재시도하고, 일시 장애 시에도 CSV 생성 자체는 완료합니다."""
    targets = set(target_words)
    content = None
    last_error = None
    for attempt in range(4):
        try:
            response = requests.get(
                core.TATOEBA_CC0_URL,
                timeout=core.TIMEOUT,
                headers={"User-Agent":"SpeakEnglishStudy/3.1", "Accept-Encoding":"identity"},
            )
            response.raise_for_status()
            content = response.content
            break
        except requests.exceptions.RequestException as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2 ** attempt)

    if content is None:
        print(f"[경고] Tatoeba CC0 연결 실패. curated/fallback 예문으로 계속합니다: {last_error}")
        return {}

    try:
        text = bz2.decompress(content).decode("utf-8", errors="ignore")
    except (OSError, EOFError) as exc:
        print(f"[경고] Tatoeba CC0 압축 해제 실패. fallback 예문으로 계속합니다: {exc}")
        return {}

    best = {}
    best_distance = {}
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        sentence = parts[2].strip()
        words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", sentence)
        if not (4 <= len(words) <= 14) or len(sentence) > 110:
            continue
        lowered = {w.lower() for w in words}
        if lowered & core.BAD_EXAMPLE_WORDS:
            continue
        matches = targets & lowered
        if not matches:
            continue
        distance = abs(len(words) - 8)
        for word in matches:
            if word not in best or distance < best_distance[word]:
                best[word] = sentence
                best_distance[word] = distance
    print(f"      Tatoeba CC0 실제 예문 매칭: {len(best):,}")
    return best


core.valid_word_original = core.valid_word
core.valid_word = valid_word
core.lemma = lemma
core.cefr_score = cefr_score
core.conversation_score = conversation_score
core.cc0_examples = resilient_cc0_examples


def main():
    core.main()


if __name__ == "__main__":
    main()
