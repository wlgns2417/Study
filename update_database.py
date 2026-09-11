
# -*- coding: utf-8 -*-
"""
Tatoeba -> SQLite example collector for Speak English V4.

This script does not scrape HTML pages.
It calls Tatoeba's public API and stores attribution metadata.
"""
from __future__ import annotations
import sqlite3
import re
import time
import random
import requests
from pathlib import Path
from typing import Iterable

BASE = Path(__file__).parent
DB_PATH = BASE / "english_v4.db"
PHRASES_CSV = BASE / "phrases.csv"
API = "https://api.tatoeba.org/v1/sentences"

# Search targets. These are learning targets, not copied dictionary entries.
SEARCH_TERMS = [
    "figure out","find out","work out","come up with","end up","turn out",
    "run into","hang out","meet up","pick up","drop off","drop by","stop by",
    "come over","head out","show up","bring up","point out","go over","look into",
    "check out","check in","follow up","get back to","get along","get over",
    "move on","let go","give up","keep up","catch up","run out of","cut down on",
    "put off","take care of","deal with","sort out","mess up","calm down",
    "chill out","hold on","wake up","stay up","sleep in","eat out","stay in",
    "try on","get rid of","set up","sign up","fill out","look up","call back",
    "call off","break down","break up","make up","count on","grow up","cheer up",
    "sounds good","fair enough","makes sense","no worries","my bad","not really",
    "pretty much","for sure","no way","same here","good point","up to you",
    "might as well","on my way","running late","take your time","no rush",
    "I mean","you know","actually","basically","honestly","by the way",
    "speaking of","come to think of it","as far as I know","the thing is",
    "I'm starving","I'm exhausted","I'm beat","I'm broke","I'm swamped",
    "not my thing","I'm gonna","I wanna","I gotta","I'm supposed to",
    "I'm about to","feel free to","do you mind if","could you",
    "what's up","how's it going","how have you been","take care"
]

def connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS examples(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            en TEXT NOT NULL,
            ko TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'Tatoeba',
            source_sentence_id TEXT,
            source_user TEXT,
            license TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(expression,en,ko)
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_examples_expression ON examples(expression)")
    return con

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def usable_english(text: str, term: str) -> bool:
    text = clean_text(text)
    if not text or len(text) < 4 or len(text) > 130:
        return False
    if len(text.split()) < 2 or len(text.split()) > 18:
        return False
    # remove odd corpus-like content
    if re.search(r"https?://|www\.|[@#]{2,}|_{2,}", text):
        return False
    # Prefer sentences that really contain the target words.
    words = [w.lower() for w in re.findall(r"[A-Za-z']+", term)]
    low = text.lower()
    return all(w in low for w in words[:2]) if words else True

def usable_korean(text: str) -> bool:
    text = clean_text(text)
    if len(text) < 2 or len(text) > 120:
        return False
    return bool(re.search(r"[가-힣]", text))

def extract_korean(item):
    result = []
    trans = item.get("translations") or []
    # API responses have used both flat dicts and grouped lists in different clients.
    def walk(obj):
        if isinstance(obj, dict):
            if obj.get("lang") == "kor" and obj.get("text"):
                result.append(obj)
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
    walk(trans)
    seen = set()
    unique = []
    for x in result:
        t = clean_text(x.get("text",""))
        if t and t not in seen:
            seen.add(t); unique.append(x)
    return unique

def fetch(term: str, limit: int = 30):
    params = {
        "lang": "eng",
        "q": term,
        "trans:lang": "kor",
        "sort": "relevance",
        "limit": limit,
        "showtrans": "matching",
    }
    r = requests.get(API, params=params, timeout=20, headers={"User-Agent":"SpeakEnglishV4/1.0"})
    r.raise_for_status()
    return r.json().get("data", [])

def collect_term(term: str, limit: int = 30) -> tuple[int,int]:
    data = fetch(term, limit)
    con = connect()
    added = 0
    try:
        for item in data:
            en = clean_text(item.get("text",""))
            if not usable_english(en, term):
                continue
            sid = str(item.get("id",""))
            user = ""
            owner = item.get("user")
            if isinstance(owner, dict):
                user = owner.get("username") or owner.get("name") or ""
            elif isinstance(owner, str):
                user = owner
            lic = item.get("license") or "CC BY 2.0 FR / verify source metadata"
            for t in extract_korean(item)[:3]:
                ko = clean_text(t.get("text",""))
                if not usable_korean(ko):
                    continue
                cur = con.execute("""
                    INSERT OR IGNORE INTO examples
                    (expression,en,ko,source,source_sentence_id,source_user,license)
                    VALUES(?,?,?,?,?,?,?)
                """,(term,en,ko,"Tatoeba",sid,user,lic))
                if cur.rowcount:
                    added += 1
        con.commit()
    finally:
        con.close()
    return added, len(data)

def collect_many(terms: Iterable[str], per_term: int = 20, delay: float = .25):
    total = 0
    results = []
    for i, term in enumerate(terms, 1):
        try:
            added, found = collect_term(term, per_term)
            results.append((term, added, found, "OK"))
            total += added
        except Exception as e:
            results.append((term, 0, 0, f"ERROR: {e}"))
        time.sleep(delay)
    return total, results

if __name__ == "__main__":
    sample = SEARCH_TERMS[:20]
    total, results = collect_many(sample, 20)
    print("Added:", total)
    for x in results:
        print(x)
