# -*- coding: utf-8 -*-
"""Corpus-based conversational vocabulary builder (v2)."""
from collections import defaultdict
from pathlib import Path
import bz2
import csv
import math
import re

import requests

BASE = Path(__file__).resolve().parent
OUT = BASE / "conversation_words.csv"

SUBTLEX_URL = "https://raw.githubusercontent.com/words/subtlex-word-frequencies/refs/heads/master/index.json"
OPEN_SUBS_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt"
DICT_URL = "https://raw.githubusercontent.com/jhseo1211/open-english-korean-dict/main/dict/words.json"
TATOEBA_CC0_URL = "https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences_CC0.tsv.bz2"
TARGET_N = 3000
TIMEOUT = (20, 180)

FUNCTION_WORDS = set("""
the a an of to in on at for from with without by as into onto upon and or but so if then than that this these those which what who whom whose
i you he she it we they me him her us them my your his its our their mine yours hers ours theirs am is are was were be been being do does did
have has had can could will would shall should may might must not no yes there here where when why how all any some each every both either neither
one two first last more most much many few little other another such only own same s t m re ve ll d don didn doesn isn aren wasn weren won wouldn
couldn shouldn up down out off over under again once very even still ever never always sometimes often already yet also too quite rather enough
mr mrs ms sir maam okay ok yeah yep nope oh hey hi hello thanks thank please
""".split())

TOO_BASIC = set("""
good bad big small new old young man woman boy girl child children friend family mom dad mother father brother sister husband wife son daughter
guy guys house home room car phone food water money name day night morning afternoon evening today tomorrow yesterday week month year hour minute
go come get give take make say tell see look know think want need like love work eat drink sleep walk run sit stand open close start stop help call
play read write buy bring find show use leave stay talk speak ask hear listen feel remember forget keep move turn happen try put live meet pay send
happy sad hot cold easy hard nice fine right wrong sure ready sorry tired afraid time thing people way place life world problem idea job school work
book door table bed hand head face eye eyes dog cat red blue black white number ten hundred thousand here there now back away around maybe really
understand explain show leave talk use very even god jesus christ police mom dad daddy mommy baby
""".split())

LOW_VALUE = set("""
okay okayy gonna wanna gotta ain hell damn fuck fucking shit bitch bastard dude bro buddy honey darling sweetheart mister captain officer doctor
lord king queen president american english french german russian john jack tom mary mike sam charlie david james michael
""".split())

IRREGULAR = {
    "went":"go","gone":"go","going":"go","got":"get","gotten":"get","getting":"get","gave":"give","given":"give","took":"take","taken":"take",
    "made":"make","said":"say","told":"tell","saw":"see","seen":"see","knew":"know","known":"know","thought":"think","bought":"buy",
    "brought":"bring","caught":"catch","felt":"feel","found":"find","heard":"hear","left":"leave","lost":"lose","met":"meet","paid":"pay",
    "ran":"run","sent":"send","sat":"sit","stood":"stand","understood":"understand","wrote":"write","written":"write","spoke":"speak",
    "spoken":"speak","drove":"drive","driven":"drive","forgot":"forget","forgotten":"forget","supposed":"suppose","realised":"realize",
    "realising":"realize","cancelled":"cancel","travelling":"travel",
}

CURATED_EXAMPLES = {
    "actually":"Actually, I changed my mind.", "probably":"I'll probably stay home tonight.",
    "realize":"I didn't realize that.", "instead":"Let's stay home instead.",
    "suppose":"I suppose we could try again.", "matter":"It doesn't really matter.",
    "apparently":"Apparently, he's already left.", "basically":"Basically, we need more time.",
    "definitely":"I'll definitely call you later.", "exactly":"That's exactly what I mean.",
    "seriously":"Are you seriously doing this now?", "obviously":"Obviously, we need a better plan.",
    "eventually":"We'll figure it out eventually.", "honestly":"Honestly, I don't know what to say.",
    "literally":"I literally just got here.", "otherwise":"Hurry up, otherwise we'll be late.",
    "somehow":"We'll make it work somehow.", "anyway":"Anyway, what were you saying?",
    "prefer":"I'd prefer to stay here.", "afford":"I can't afford to buy it right now.",
    "avoid":"I'm trying to avoid traffic.", "bother":"Sorry to bother you.",
    "consider":"Have you considered moving closer?", "depend":"It depends on what you want.",
    "deserve":"You deserve a break.", "expect":"I didn't expect that at all.",
    "imagine":"Can you imagine living there?", "manage":"I managed to finish it on time.",
    "mention":"Did she mention my name?", "notice":"Did you notice anything different?",
    "pretend":"Don't pretend you didn't know.", "remind":"Remind me to call him later.",
    "seem":"You seem a little tired today.", "suggest":"I suggest we leave early.",
    "wonder":"I wonder why he left.", "admit":"I have to admit, you were right.",
    "assume":"I assumed you already knew.", "handle":"Don't worry, I can handle it.",
    "ignore":"Just ignore what he said.", "regret":"I regret saying that.",
    "available":"Are you available this afternoon?", "awkward":"That was a little awkward.",
    "confused":"I'm a little confused right now.", "exhausted":"I'm exhausted after work.",
    "familiar":"That name sounds familiar.", "frustrated":"I'm getting really frustrated.",
    "likely":"It's likely to rain later.", "obvious":"The answer seems pretty obvious.",
    "reasonable":"That sounds reasonable to me.", "ridiculous":"That's absolutely ridiculous.",
    "specific":"Do you have a specific time in mind?", "weird":"That's kind of weird.",
    "issue":"There's one small issue we need to fix.", "point":"I see your point.",
    "reason":"Is there a reason you're asking?", "situation":"It's a complicated situation.",
    "choice":"I don't think we have much choice.", "chance":"There's a good chance he'll come.",
}

BAD_EXAMPLE_WORDS = set("fuck fucking shit bitch bastard nigger cunt porn sex nazi hitler".split())


def request_json(url):
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"SpeakEnglishStudy/3.0"})
    r.raise_for_status()
    return r.json()


def request_text(url):
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"SpeakEnglishStudy/3.0"})
    r.raise_for_status()
    return r.text


def valid_word(word):
    return bool(re.fullmatch(r"[a-z]{3,18}", word)) and word not in FUNCTION_WORDS and word not in TOO_BASIC and word not in LOW_VALUE


def lemma(word, dictionary):
    if word in IRREGULAR:
        return IRREGULAR[word]
    candidates = []
    if word.endswith("ies") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("ing") and len(word) > 5:
        base = word[:-3]
        candidates.extend([base, base + "e"])
        if len(base) > 2 and base[-1] == base[-2]: candidates.append(base[:-1])
    if word.endswith("ed") and len(word) > 4:
        base = word[:-2]
        candidates.extend([base, base + "e"])
        if len(base) > 2 and base[-1] == base[-2]: candidates.append(base[:-1])
    if word.endswith("es") and len(word) > 4:
        candidates.extend([word[:-2], word[:-1]])
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        candidates.append(word[:-1])
    for c in candidates:
        if c in dictionary and valid_word(c):
            return c
    return word


def aggregate(items, dictionary):
    counts = defaultdict(int)
    for raw, count in items:
        w = str(raw).strip().lower().replace("’", "'")
        if not re.fullmatch(r"[a-z]{3,18}", w):
            continue
        w = lemma(w, dictionary)
        if valid_word(w):
            counts[w] += int(count)
    return counts


def parse_open(text):
    out = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try: out.append((parts[0], int(parts[1])))
            except ValueError: pass
    return out


def cefr_score(level):
    return {"A1":0.0,"A2":0.48,"B1":1.0,"B2":0.96,"C1":0.80,"C2":0.62}.get(level, 0.55)


def conversation_score(pos, word):
    p = str(pos).lower()
    if "verb" in p: score = 1.0
    elif "adverb" in p or p == "adv": score = 0.98
    elif "adjective" in p or p == "adj": score = 0.90
    elif "noun" in p: score = 0.58
    else: score = 0.45
    if word in CURATED_EXAMPLES: score = min(1.0, score + 0.08)
    return score


def cc0_examples(target_words):
    print("[4/6] Tatoeba CC0에서 자연스러운 실제 예문을 찾습니다...")
    r = requests.get(TATOEBA_CC0_URL, timeout=TIMEOUT, headers={"User-Agent":"SpeakEnglishStudy/3.0"})
    r.raise_for_status()
    text = bz2.decompress(r.content).decode("utf-8", errors="ignore")
    targets = set(target_words)
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
        if lowered & BAD_EXAMPLE_WORDS:
            continue
        matches = targets & lowered
        if not matches:
            continue
        distance = abs(len(words) - 8)
        for word in matches:
            if word not in best or distance < best_distance[word]:
                best[word] = sentence
                best_distance[word] = distance
    return best


def fallback_example(word):
    return f'Try using “{word}” in a sentence of your own today.'


def main():
    print("=" * 68)
    print(" Speak English - 회화 단어 선별 v2")
    print("=" * 68)
    print("[1/6] 영한 뜻/품사/CEFR 사전을 불러옵니다...")
    dictionary = request_json(DICT_URL)

    print("[2/6] SUBTLEX-US와 OpenSubtitles 빈도를 결합합니다...")
    subtlex_json = request_json(SUBTLEX_URL)
    sub = aggregate([(x.get("word", ""), x.get("count", 0)) for x in subtlex_json], dictionary)
    opn = aggregate(parse_open(request_text(OPEN_SUBS_URL)), dictionary)

    max_sub = max(sub.values()) if sub else 1
    max_opn = max(opn.values()) if opn else 1
    log_sub = math.log10(max_sub + 1)
    log_opn = math.log10(max_opn + 1)

    print("[3/6] 실사용 빈도 × 회화 활용도 × 학습가치를 점수화합니다...")
    rows = []
    for word in set(sub) | set(opn):
        if word not in dictionary or not valid_word(word):
            continue
        info = dictionary[word]
        meaning = str(info.get("meaning_ko", "")).strip()
        level = str(info.get("cefr", "")).strip().upper()
        pos = str(info.get("pos", "")).strip()
        if not meaning or level == "A1":
            continue
        sf = math.log10(sub.get(word, 0) + 1) / log_sub
        of = math.log10(opn.get(word, 0) + 1) / log_opn
        agreement = 1.0 if word in sub and word in opn else 0.62
        frequency = (0.55 * sf + 0.45 * of) * agreement
        score = 100 * (0.50 * frequency + 0.31 * conversation_score(pos, word) + 0.19 * cefr_score(level))
        rows.append({
            "word":word, "meaning_ko":meaning, "pos":pos, "cefr":level,
            "score":round(score, 2), "subtlex_count":sub.get(word, 0), "opensubtitles_count":opn.get(word, 0),
        })

    rows.sort(key=lambda x:(x["score"], x["subtlex_count"] + x["opensubtitles_count"]), reverse=True)
    rows = rows[:TARGET_N]

    examples = cc0_examples([r["word"] for r in rows])
    print("[5/6] 예문과 메타데이터를 결합합니다...")
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
        row["example_en"] = CURATED_EXAMPLES.get(row["word"], examples.get(row["word"], fallback_example(row["word"])))
        row["source"] = "SUBTLEX-US + OpenSubtitles 2018 / examples: Tatoeba CC0"

    print("[6/6] conversation_words.csv를 저장합니다...")
    fields = ["rank","word","meaning_ko","example_en","pos","cefr","score","subtlex_count","opensubtitles_count","source"]
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"      저장 단어: {len(rows):,}")
    print(f"      Tatoeba CC0 예문 매칭: {len(examples):,}")


if __name__ == "__main__":
    main()
