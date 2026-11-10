# tip-of-tongue

**English** | [简体中文](README.zh-CN.md)

> Turn "I can picture it but I don't know what it's called" into a named, measured ask that an AI (or a person) can follow exactly.

## Introduction

Most disappointing results from video models, image models and coding agents start with a request like "make the intro smooth and cinematic" or "标题要有高级感". The person knows exactly what they want. They just do not have the word for it, so the AI fills the gap with a generic guess.

**tip-of-tongue** is an agent skill that closes that gap. It teaches your agent to:

- interview the user about what they can **see**, not about jargon they do not know;
- offer a short list of candidate **names**, each paired with its nearest **look-alike** and the one visible difference;
- attach the **knobs** that decide the result (duration, distance, direction, easing, trigger, level...);
- write the final ask in the **dialect of the receiver**: a sentence for a video/image model, a spec for code, a brief for a human;
- grow a small **house lexicon** so a team uses the same word for the same thing.

It is field-agnostic: motion graphics, camera work, editing, UI components, web effects, lighting, sound, and anything else where knowing the name is what lets you ask.

## Features

- **Six-step routine**: wish card, visible-difference questions, candidates with look-alikes, knobs, dialect, save.
- **Look-alike first**: every name comes with what it is *not* (dolly in vs zoom in, mask reveal vs fade in, rim light vs silhouette).
- **Knob tables** for motion, camera, text, UI/web, light, sound and editing.
- **Bilingual**: complete instructions in English and Chinese; the helper understands both.
- **`lexicon.py` helper** (Python standard library only):
  - `check` validates a house lexicon (required fields, at least two knobs, a look-alike, an example ask with real values, no circular definitions, no duplicate names or aliases);
  - `find` ranks lexicon entries against an everyday description, in English or Chinese;
  - `lint` grades a prompt as `VAGUE`, `NAMED` or `MEASURED` and points out feeling-words.
- **Starter lexicon** with 12 example entries across camera, motion graphics, UI, web, lighting, sound and editing.
- 27 unit tests.

## Installation

The skill is the `SKILL.md` file plus the optional `scripts/` and `examples/` folders.

**Claude Code**

```sh
git clone https://github.com/fangdididi/tip-of-tongue ~/.claude/skills/tip-of-tongue
```

**Codex / other agents that read `AGENTS.md` or a skills folder**

```sh
git clone https://github.com/fangdididi/tip-of-tongue ~/.codex/skills/tip-of-tongue
```

or reference `SKILL.md` from your `AGENTS.md`.

**Cursor**

Clone into your project (for example `.cursor/skills/tip-of-tongue`) and add a rule that points to `SKILL.md`, or paste the routine into a project rule.

**Any chat assistant**

Paste the contents of `SKILL.md` (or `SKILL.zh-CN.md`) at the start of the conversation.

## Usage

Just talk the way you normally would:

```text
The title should kind of come up out of nowhere, but not a fade. Help me say it properly for Remotion.
```

```text
帮我把这条提示词改到视频模型能听懂：“开场要丝滑、有电影感”。
```

```text
Start a house lexicon for our design team and add "skeleton screen" and "sticky header shrink".
```

Helper commands:

```sh
# validate a lexicon
python scripts/lexicon.py check examples/lexicon.example.json

# find the name for something you can describe
python scripts/lexicon.py find examples/lexicon.example.json "the camera floats around the cup"
python scripts/lexicon.py find examples/lexicon.example.json "文字从线后面冒出来"

# grade a prompt before sending it
echo "Make the intro smooth and cinematic" | python scripts/lexicon.py lint -
python scripts/lexicon.py lint prompt.txt --lexicon examples/lexicon.example.json --json
```

`lint` exit codes: `0` MEASURED, `1` NAMED, `2` VAGUE, so it can sit in a script or CI step.

## Examples

| Before | After |
|---|---|
| "Make the stats numbers do something cool." | "Count-up from 0 to the final value over 1.2 s, ease-out so the last digits slow down, thousands separator on, start when the slide appears." |
| "Make her pop off the dark background." | "Soft key light from front left, warm rim light from behind right outlining hair and shoulders at about twice the key's brightness." |
| "列表加载别一直转圈。" | "骨架屏：按卡片布局的灰色占位块，1.4 秒一次微光，至少显示 300 毫秒；开启‘减少动态效果’时关闭微光。" |
| "Smooth, cinematic, premium intro." | "5 s slow orbit of 60° to the left around the bottle at label height, ease-in-out, then a match cut on the bottle's silhouette to the logo, hold 1.5 s." |

More walk-throughs are in [SKILL.md](SKILL.md#examples).

## Lexicon entry format

```json
{
  "name": "dolly in",
  "aliases": ["push in", "推镜"],
  "field": "camera",
  "means": "The camera itself travels toward the subject...",
  "tell": "Objects at different distances grow at different speeds...",
  "not": ["zoom in"],
  "knobs": ["distance travelled", "duration", "easing"],
  "cues": ["camera moves closer", "镜头往前走"],
  "ask": "Slow dolly in from a medium shot to a close-up over 4 s, ease-in-out, no zoom."
}
```

`cues` holds the everyday phrases people used before they knew the name, which is what makes `find` match real descriptions.

## File structure

```
tip-of-tongue/
├── SKILL.md                     # skill instructions (English)
├── SKILL.zh-CN.md               # skill instructions (Chinese)
├── README.md                    # this file
├── README.zh-CN.md              # Chinese README
├── LICENSE                      # MIT
├── scripts/
│   └── lexicon.py               # check / find / lint helper, stdlib only
├── examples/
│   └── lexicon.example.json     # starter house lexicon (example data)
└── tests/
    └── test_lexicon.py          # 27 unit tests
```

Run the tests with `python -m unittest discover -s tests`.

## License

[MIT](LICENSE) © fangdididi
