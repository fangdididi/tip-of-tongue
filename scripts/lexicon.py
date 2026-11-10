#!/usr/bin/env python3
"""tip-of-tongue lexicon tool (stdlib only).

Commands:
  check LEXICON.json            validate a house lexicon
  find  LEXICON.json WORDS...   rank entries against a plain description (EN/ZH)
  lint  PROMPT.txt [--lexicon LEXICON.json] [--json]
                                grade a prompt VAGUE / NAMED / MEASURED

Exit codes: check 0 ok / 1 problems; lint 0 MEASURED, 1 NAMED, 2 VAGUE; 3 usage error.
"""
import json
import re
import sys

REQUIRED = ("name", "field", "means", "tell", "knobs", "ask")

# Words that sound like direction but carry no instruction on their own.
FOG_WORDS = {
    "en": ["smooth", "cinematic", "dynamic", "pop", "punchy", "clean", "modern",
           "premium", "sleek", "epic", "vibe", "energetic", "elegant", "nice",
           "cool", "professional", "engaging", "snappy", "polished", "slick"],
    "zh": ["流畅", "丝滑", "高级感", "高级", "大片感", "电影感", "动感", "酷炫", "炫酷",
           "有质感", "质感", "氛围感", "大气", "精致", "灵动", "有冲击力", "专业感", "顺滑"],
}

# Signs that a knob was actually set: a number with a unit, or an explicit direction/limit.
MEASURE_PATTERNS = [
    r"\d+(\.\d+)?\s*(ms|s|sec|seconds?|frames?|fps|px|%|deg|°|mm|x|bpm)\b",
    r"\d+(\.\d+)?\s*(毫秒|秒|帧|像素|度|倍|毫米)",
    r"\b(from|to)\s+(the\s+)?(left|right|top|bottom|above|below|center)\b",
    r"(从|向)(左|右|上|下|中心|中间)",
    r"\b(ease[- ]?(in|out|in-out)|linear|overshoot|spring)\b",
    r"(缓入|缓出|缓入缓出|线性|回弹|弹簧)",
    r"\b(hold|pause)\s+\d",
    r"(停留|停顿)\s*\d",
]


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    entries = data.get("entries") if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise ValueError("lexicon must be a list or an object with 'entries'")
    return entries


def all_names(entry):
    names = [entry.get("name", "")]
    names += entry.get("aliases", []) or []
    return [n.strip().lower() for n in names if isinstance(n, str) and n.strip()]


def check(entries):
    problems = []
    seen = {}
    for i, e in enumerate(entries):
        label = e.get("name") or f"entry #{i + 1}"
        for key in REQUIRED:
            if not e.get(key):
                problems.append(f"{label}: missing '{key}'")
        knobs = e.get("knobs") or []
        if knobs and len(knobs) < 2:
            problems.append(f"{label}: needs at least 2 knobs (got {len(knobs)})")
        if not e.get("not") and not e.get("contrast"):
            problems.append(f"{label}: no look-alike in 'not' - a name nobody can confuse is rarely worth listing")
        ask = e.get("ask") or ""
        if ask and not any(re.search(p, ask, re.I) for p in MEASURE_PATTERNS):
            problems.append(f"{label}: 'ask' example sets no knob with a number or direction")
        means = (e.get("means") or "").lower()
        if means and e.get("name") and e["name"].lower() in means:
            problems.append(f"{label}: 'means' defines the name with itself")
        for n in all_names(e):
            if n in seen and seen[n] != label:
                problems.append(f"{label}: name/alias '{n}' already used by {seen[n]}")
            seen.setdefault(n, label)
    return problems


STOP = {"the", "a", "an", "and", "or", "of", "to", "it", "is", "in", "on", "at",
        "with", "like", "kind", "sort", "thing", "that", "this", "my", "its", "be", "so"}


def tokens(text):
    text = text.lower()
    words = [w for w in re.findall(r"[a-z0-9]+", text) if w not in STOP]
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    bigrams = ["".join(cjk[i:i + 2]) for i in range(len(cjk) - 1)]
    return set(words) | set(bigrams)


def find(entries, query, limit=5):
    q = tokens(query)
    scored = []
    for e in entries:
        hay_main = " ".join([e.get("tell", ""), e.get("means", "")] + (e.get("cues") or []))
        hay_name = " ".join(all_names(e))
        score = 2 * len(q & tokens(hay_main)) + 3 * len(q & tokens(hay_name))
        if score:
            scored.append((score, e.get("name", "?"), e))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[:limit]


def lint(text, entries=None):
    low = text.lower()
    fog = []
    for w in FOG_WORDS["en"]:
        if re.search(r"\b" + re.escape(w) + r"\b", low):
            fog.append(w)
    for w in FOG_WORDS["zh"]:
        if w in text:
            fog.append(w)
    # drop shorter zh fog words already covered by a longer hit (高级 inside 高级感)
    fog = [w for w in fog if not any(w != o and w in o for o in fog)]
    measures = sorted({m.group(0) for p in MEASURE_PATTERNS for m in re.finditer(p, text, re.I)})
    named = []
    for e in entries or []:
        for n in all_names(e):
            if n and n in low:
                named.append(e.get("name"))
                break
    if measures and (named or not fog):
        verdict = "MEASURED"   # knobs set, and either a house name or no fog left
    elif named or measures:
        verdict = "NAMED"      # half way: a name without knobs, or knobs drowned in fog
    else:
        verdict = "VAGUE"
    advice = []
    for w in fog:
        advice.append(f"'{w}' is a feeling, not an instruction: replace it with a name plus how long / how far / what moves")
    if named and not measures:
        advice.append("names found but no knob is set: add duration, distance or direction, and easing")
    if not named and not fog and not measures:
        advice.append("nothing to grade: describe one move with a name and at least one number")
    return {"verdict": verdict, "fog": fog, "named": sorted(set(named)), "measures": measures, "advice": advice}


def main(argv):
    if len(argv) < 2 or argv[0] not in ("check", "find", "lint"):
        print(__doc__)
        return 3
    cmd = argv[0]
    if cmd == "check":
        entries = load(argv[1])
        probs = check(entries)
        if probs:
            for p in probs:
                print("PROBLEM", p)
            print(f"{len(probs)} problem(s) in {len(entries)} entries")
            return 1
        print(f"OK {len(entries)} entries")
        return 0
    if cmd == "find":
        if len(argv) < 3:
            print(__doc__)
            return 3
        entries = load(argv[1])
        hits = find(entries, " ".join(argv[2:]))
        if not hits:
            print("no match: describe what changes on screen (what moves, where, how fast)")
            return 1
        for score, name, e in hits:
            print(f"{score:>3}  {name}  [{e.get('field', '')}]  {e.get('means', '')}")
            if e.get("not"):
                print(f"     not: {', '.join(e['not'])}")
        return 0
    # lint
    args = argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    entries = []
    if "--lexicon" in args:
        i = args.index("--lexicon")
        entries = load(args[i + 1])
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return 3
    text = sys.stdin.read() if args[0] == "-" else open(args[0], encoding="utf-8").read()
    res = lint(text, entries)
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(res["verdict"])
        for k in ("fog", "named", "measures"):
            if res[k]:
                print(f"  {k}: {', '.join(res[k])}")
        for a in res["advice"]:
            print("  -", a)
    return {"MEASURED": 0, "NAMED": 1, "VAGUE": 2}[res["verdict"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
