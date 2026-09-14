# -*- coding: utf-8 -*-
"""
Speak English - 회화 단어 자동 선별기

실행:
    python collect_words.py

결과:
    conversation_words.csv

선별 원칙:
  1) SUBTLEX-US와 OpenSubtitles 2018 두 빈도 자료를 결합
  2) 관사/전치사/대명사 등 기능어 및 자막 토큰 노이즈 제거
  3) 오픈 영한사전의 CEFR/POS/한국어 뜻을 결합
  4) A1 기초어를 기본 제외하고 A2~C2 학습 가치 반영
  5) 활용형을 가능한 범위에서 기본형으로 합산
  6) 실사용 빈도 × 회화 활용도 × 학습가치로 최종 점수 산정

Sources:
  - SUBTLEX-US frequencies: words/subtlex-word-frequencies
  - OpenSubtitles frequency: hermitdave/FrequencyWords
  - Korean meanings/CEFR/POS: jhseo1211/open-english-korean-dict
"""

from collections import defaultdict
from pathlib import Path
import csv
import json
import math
import re

import requests

BASE = Path(__file__).resolve().parent
OUT = BASE / "conversation_words.csv"

SUBTLEX_URL = "https://raw.githubusercontent.com/words/subtlex-word-frequencies/refs/heads/master/index.json"
OPEN_SUBS_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt"
DICT_URL = "https://raw.githubusercontent.com/jhseo1211/open-english-korean-dict/main/dict/words.json"

TARGET_N = 3000
MIN_WORD_LEN = 3
MAX_WORD_LEN = 18
TIMEOUT = (20, 180)

# 의미 학습 가치가 거의 없는 기능어와 자막 분리 토큰을 제거합니다.
FUNCTION_WORDS = {
    "the","a","an","of","to","in","on","at","for","from","with","without","by","as","into","onto","upon",
    "and","or","but","so","if","then","than","that","this","these","those","which","what","who","whom","whose",
    "i","you","he","she","it","we","they","me","him","her","us","them","my","your","his","its","our","their",
    "mine","yours","hers","ours","theirs","am","is","are","was","were","be","been","being","do","does","did",
    "have","has","had","can","could","will","would","shall","should","may","might","must","not","no","yes",
    "there","here","where","when","why","how","all","any","some","each","every","both","either","neither","one",
    "two","first","last","more","most","much","many","few","little","other","another","such","only","own","same",
    "s","t","m","re","ve","ll","d","don","didn","doesn","isn","aren","wasn","weren","won","wouldn","couldn","shouldn",
}

# A1이 아니더라도 이미 너무 쉬워서 별도 단어장 우선순위가 낮은 단어입니다.
TOO_BASIC = {
    "good","bad","big","small","new","old","man","woman","boy","girl","friend","family","mom","dad","mother","father",
    "house","home","room","car","phone","food","water","money","name","day","night","morning","today","tomorrow","yesterday",
    "go","come","get","give","take","make","say","tell","see","look","know","think","want","need","like","love","work",
    "eat","drink","sleep","walk","run","sit","stand","open","close","start","stop","help","call","play","read","write",
    "happy","sad","hot","cold","easy","hard","nice","fine","right","wrong","time","thing","people","way","place","life",
}

# 활용형 합산에 자주 필요한 불규칙형 중심의 소형 사전입니다.
IRREGULAR = {
    "went":"go","gone":"go","got":"get","gotten":"get","gave":"give","given":"give","took":"take","taken":"take",
    "made":"make","said":"say","told":"tell","saw":"see","seen":"see","knew":"know","known":"know","thought":"think",
    "bought":"buy","brought":"bring","caught":"catch","felt":"feel","found":"find","heard":"hear","left":"leave",
    "lost":"lose","met":"meet","paid":"pay","ran":"run","sent":"send","sat":"sit","stood":"stand","understood":"understand",
    "wrote":"write","written":"write","spoke":"speak","spoken":"speak","drove":"drive","driven":"drive","forgot":"forget",
    "forgotten":"forget","realised":"realize","realising":"realize","cancelled":"cancel","travelling":"travel",
}

# 문장 품질이 중요한 최상위 회화어는 사람이 다듬은 예문을 우선 사용합니다.
CURATED_EXAMPLES = {
    "actually":"Actually, I changed my mind.",
    "probably":"I'll probably stay home tonight.",
    "realize":"I didn't realize that.",
    "instead":"Let's stay home instead.",
    "suppose":"I suppose we could try again.",
    "matter":"It doesn't really matter.",
    "apparently":"Apparently, he's already left.",
    "basically":"Basically, we need more time.",
    "definitely":"I'll definitely call you later.",
    "exactly":"That's exactly what I mean.",
    "seriously":"Are you seriously doing this now?",
    "obviously":"Obviously, we need a better plan.",
    "eventually":"We'll figure it out eventually.",
    "honestly":"Honestly, I don't know what to say.",
    "literally":"I literally just got here.",
    "otherwise":"Hurry up, otherwise we'll be late.",
    "somehow":"We'll make it work somehow.",
    "anyway":"Anyway, what were you saying?",
    "prefer":"I'd prefer to stay here.",
    "afford":"I can't afford to buy it right now.",
    "avoid":"I'm trying to avoid traffic.",
    "bother":"Sorry to bother you.",
    "consider":"Have you considered moving closer?",
    "depend":"It depends on what you want.",
    "deserve":"You deserve a break.",
    "expect":"I didn't expect that at all.",
    "imagine":"Can you imagine living there?",
    "manage":"I managed to finish it on time.",
    "mention":"Did she mention my name?",
    "notice":"Did you notice anything different?",
    "pretend":"Don't pretend you didn't know.",
    "remind":"Remind me to call him later.",
    "seem":"You seem a little tired today.",
    "suggest":"I suggest we leave early.",
    "wonder":"I wonder why he left.",
    "admit":"I have to admit, you were right.",
    "assume":"I assumed you already knew.",
    "handle":"Don't worry, I can handle it.",
    "ignore":"Just ignore what he said.",
    "regret":"I regret saying that.",
    "available":"Are you available this afternoon?",
    "awkward":"That was a little awkward.",
    "confused":"I'm a little confused right now.",
    "exhausted":"I'm exhausted after work.",
    "familiar":"That name sounds familiar.",
    "frustrated":"I'm getting really frustrated.",
    "likely":"It's likely to rain later.",
    "obvious":"The answer seems pretty obvious.",
    "reasonable":"That sounds reasonable to me.",
    "ridiculous":"That's absolutely ridiculous.",
    "specific":"Do you have a specific time in mind?",
    "weird":"That's kind of weird.",
    "issue":"There's one small issue we need to fix.",
    "point":"I see your point.",
    "reason":"Is there a reason you're asking?",
    "situation":"It's a complicated situation.",
    "choice":"I don't think we have much choice.",
    "chance":"There's a good chance he'll come.",
}


def get_json(url):
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"SpeakEnglishStudy/2.0"})
    r.raise_for_status()
    return r.json()


def get_text(url):
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"SpeakEnglishStudy/2.0"})
    r.raise_for_status()
    return r.text


def clean_word(word):
    return str(word).strip().lower().replace("’", "'")


def candidate(word):
    if not re.fullmatch(r"[a-z]+", word):
        return False
    if not (MIN_WORD_LEN <= len(word) <= MAX_WORD_LEN):
        return False
    if word in FUNCTION_WORDS or word in TOO_BASIC:
        return False
    return True


def simple_lemma(word, dictionary):
    if word in IRREGULAR and IRREGULAR[word] in dictionary:
        return IRREGULAR[word]
    if word in dictionary:
        entry = dictionary[word]
        # 사전에 이미 정상 표제어로 존재하면 과도한 어간 추정을 하지 않습니다.
        if str(entry.get("pos", "")).lower() not in {"", "unknown"}:
            return word

    rules = []
    if word.endswith("ies") and len(word) > 4:
        rules.append(word[:-3] + "y")
    if word.endswith("ing") and len(word) > 5:
        base = word[:-3]
        rules += [base, base + "e"]
        if len(base) > 2 and base[-1] == base[-2]:
            rules.append(base[:-1])
    if word.endswith("ed") and len(word) > 4:
        base = word[:-2]
        rules += [base, base + "e"]
        if len(base) > 2 and base[-1] == base[-2]:
            rules.append(base[:-1])
    if word.endswith("es") and len(word) > 4:
        rules += [word[:-2], word[:-1]]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        rules.append(word[:-1])

    for base in rules:
        if base in dictionary:
            return base
    return word


def normalize_counts(items, dictionary):
    counts = defaultdict(int)
    for raw_word, raw_count in items:
        word = clean_word(raw_word)
        if not candidate(word):
            continue
        lemma = simple_lemma(word, dictionary)
        if candidate(lemma):
            counts[lemma] += int(raw_count)
    return counts


def parse_open_subtitles(text):
    rows = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        try:
            rows.append((parts[0], int(parts[1])))
        except ValueError:
            continue
    return rows


def cefr_value(level):
    return {"A1":0.0, "A2":0.62, "B1":1.0, "B2":0.95, "C1":0.82, "C2":0.68}.get(str(level).upper(), 0.55)


def conversation_value(pos, word):
    p = str(pos).lower()
    score = 0.58
    if "verb" in p:
        score = 1.0
    elif "adverb" in p or "adv" == p:
        score = 0.98
    elif "adjective" in p or "adj" == p:
        score = 0.88
    elif "noun" in p:
        score = 0.72
    if word in CURATED_EXAMPLES:
        score = min(1.0, score + 0.08)
    return score


def make_example(word, pos):
    if word in CURATED_EXAMPLES:
        return CURATED_EXAMPLES[word]
    p = str(pos).lower()
    if "verb" in p:
        return f"I need to {word} this before we decide."
    if "adverb" in p or p == "adv":
        return f"I {word} didn't expect that to happen."
    if "adjective" in p or p == "adj":
        return f"That sounds pretty {word} to me."
    if "noun" in p:
        return f"That's the {word} we were talking about."
    return f"You'll hear the word '{word}' often in everyday conversation."


def main():
    print("=" * 68)
    print(" Speak English - 코퍼스 기반 회화 단어 자동 선별")
    print("=" * 68)

    print("[1/5] 영한사전/CEFR 데이터를 불러옵니다...")
    dictionary = get_json(DICT_URL)

    print("[2/5] SUBTLEX-US 빈도 데이터를 불러옵니다...")
    subtlex_raw = get_json(SUBTLEX_URL)
    subtlex_items = [(x.get("word", ""), x.get("count", 0)) for x in subtlex_raw]

    print("[3/5] OpenSubtitles 2018 빈도 데이터를 불러옵니다...")
    open_items = parse_open_subtitles(get_text(OPEN_SUBS_URL))

    subtlex = normalize_counts(subtlex_items, dictionary)
    opensubs = normalize_counts(open_items, dictionary)

    max_sub = max(subtlex.values()) if subtlex else 1
    max_open = max(opensubs.values()) if opensubs else 1
    denom_sub = math.log10(max_sub + 1)
    denom_open = math.log10(max_open + 1)

    print("[4/5] 빈도 × 회화 활용도 × 학습가치를 계산합니다...")
    rows = []
    common = set(subtlex) | set(opensubs)

    for word in common:
        if word not in dictionary or not candidate(word):
            continue
        info = dictionary[word]
        meaning = str(info.get("meaning_ko", "")).strip()
        if not meaning:
            continue

        cefr = str(info.get("cefr", "")).upper().strip()
        if cefr == "A1":
            continue

        sub_norm = math.log10(subtlex.get(word, 0) + 1) / denom_sub
        open_norm = math.log10(opensubs.get(word, 0) + 1) / denom_open
        # 두 코퍼스에 모두 등장하면 단일 코퍼스 특이어보다 신뢰도를 높입니다.
        cross_bonus = 1.0 if word in subtlex and word in opensubs else 0.68
        frequency = (0.55 * sub_norm + 0.45 * open_norm) * cross_bonus

        pos = str(info.get("pos", "")).strip()
        conv = conversation_value(pos, word)
        learning = cefr_value(cefr)
        score = 100 * (0.58 * frequency + 0.24 * conv + 0.18 * learning)

        rows.append({
            "word": word,
            "meaning_ko": meaning,
            "example_en": make_example(word, pos),
            "pos": pos,
            "cefr": cefr,
            "score": round(score, 2),
            "subtlex_count": subtlex.get(word, 0),
            "opensubtitles_count": opensubs.get(word, 0),
            "source": "SUBTLEX-US + OpenSubtitles 2018",
        })

    rows.sort(key=lambda x: (x["score"], x["subtlex_count"] + x["opensubtitles_count"]), reverse=True)
    rows = rows[:TARGET_N]
    for i, row in enumerate(rows, 1):
        row["rank"] = i

    print("[5/5] CSV를 저장합니다...")
    fields = ["rank","word","meaning_ko","example_en","pos","cefr","score","subtlex_count","opensubtitles_count","source"]
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"      저장 단어 : {len(rows):,}")
    print(f"      생성 파일 : {OUT.name}")
    print("\n앱은 conversation_words.csv가 있으면 미리보기 대신 이 데이터를 자동 사용합니다.")


if __name__ == "__main__":
    main()
