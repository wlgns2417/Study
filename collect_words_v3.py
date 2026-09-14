# -*- coding: utf-8 -*-
"""Final ranking/filter layer for conversational vocabulary."""
import collect_words_v2 as core

EXTRA_EXCLUDE = set("""
wait through until since men years days things haven early hit hurt pick shut sound simple possible
clear went came coming wanted talking looking called show used using left took made said told seen gave given
word words tonight tomorrow yesterday morning night everyone everybody someone somebody anyone anything
somewhere everything nothing somewhere
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

    # 기본형이 너무 쉬워 제외 대상이어도 먼저 기본형으로 합칩니다.
    # 이후 aggregate()의 valid_word()에서 기본형 전체가 제거됩니다.
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


# Monkey-patch only the ranking/filter hooks. Downloading, Tatoeba CC0 example
# selection and CSV generation remain in v2.
core.valid_word_original = core.valid_word
core.valid_word = valid_word
core.lemma = lemma
core.cefr_score = cefr_score
core.conversation_score = conversation_score


def main():
    core.main()


if __name__ == "__main__":
    main()
