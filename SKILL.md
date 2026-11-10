---
name: tip-of-tongue
description: Turn "I can picture it but I don't know what it's called" into a named, measured ask. Use when someone describes a visual, motion, camera, UI, lighting, sound or editing effect in vague or roundabout words ("the text kind of slides up from behind a line", "make it feel premium", "the camera floats around the cup"), when a prompt for a video/image model, a coding agent or a human collaborator is full of feeling-words with no numbers, or when a team wants a shared house lexicon so everyone asks for the same thing the same way. Works in English and Chinese.
---

# tip-of-tongue

[中文版](SKILL.zh-CN.md)

## What this is

Most weak creative requests are not short of imagination. They are short of words. A person sees exactly what they want in their head, but the only words they have are "smooth", "cinematic", "more dynamic", or "高级感". An AI that receives those words guesses, and the guess is usually generic.

This skill gives the agent a short, repeatable routine for closing that gap:

1. **Name it.** Find the professional name for the thing the person is picturing, by asking about what they can *see*, not about jargon they do not know.
2. **Tell it apart.** Every good name has a look-alike (dolly in vs zoom in, mask reveal vs fade in, rim light vs silhouette). Ask one question that separates them so the right one is chosen on purpose.
3. **Measure it.** A name alone is still loose. Attach the two or three knobs that decide the result: how long, how far or how much, which direction, what moves and what stays still, how it eases, what triggers it.
4. **Say it in the receiver's dialect.** The same named move is written differently for a video-generation model, for code, and for a human editor.
5. **Keep it.** Confirmed names go into a small house lexicon so the next request, and the next teammate, uses the same word for the same thing.

It works for any field where knowing the name is what lets you ask: motion graphics, camera work, editing, UI components, web effects, photography and lighting, sound, even cooking or interior styling.

## When to use it

- The user describes an effect indirectly: "like that thing where...", "you know when the...", "不知道叫什么，就是那种…".
- A request or prompt leans on feeling-words with no numbers: smooth, punchy, clean, premium, cinematic, 丝滑, 大片感, 有质感.
- The user pastes a reference (a clip, a screenshot, a site) and says "make it like this" without saying which part of it matters.
- Two people keep talking past each other about the same effect.
- A team wants a shared vocabulary file for prompts and briefs.

Skip it when the user already gives a precise name with values, or when the request is about content (what to say) rather than form (how it looks, moves or sounds).

## The routine

### Step 1: Write a wish card

Before guessing names, capture what the person has in mind in their own words. Keep it to five lines:

```
wish:      "the title sort of comes up out of nowhere, but not a fade"
where:     opening title of a 30 s product video
medium:    motion graphics (could also be: camera, edit, UI, web, light, sound...)
receiver:  Remotion code  (or: video model, image model, CSS, a human editor)
reference: none / link / timestamp / screenshot
```

The receiver matters: it decides the dialect in Step 5.

### Step 2: Ask about what can be seen, not about vocabulary

Do not ask "do you want a mask reveal or a typewriter?" if the person does not know either word. Ask about observable differences instead:

- Does the whole thing appear at once, or piece by piece?
- Is it cut off by an edge while it comes in, or does it get gradually less see-through?
- Does the background change size, or only the subject?
- Does it react to the viewer (scroll, hover, tap), or play on its own?
- Is there a moment of stillness at the end?

One or two of these questions usually narrow the field to two or three candidates.

### Step 3: Offer a short list of candidates with their look-alikes

Give at most three to five candidates. For each one:

- **Name** (and the common alternative name, in the user's language too).
- **Means:** one plain sentence.
- **Tell:** the visible sign that proves it is this and not something else.
- **Not to be confused with:** its nearest look-alike, and the one difference.

If you have a house lexicon, search it first:

```sh
python scripts/lexicon.py find lexicon.json "the camera floats around the cup"
```

Then ask the single question that splits the top two. Example: "When the camera moves, does the background swing around behind the cup (orbit), or does the cup itself spin while the background stays still (turntable)?"

Let the user choose. If they cannot decide, show or describe both and let them pick; do not quietly choose for them.

### Step 4: Set the knobs

Every name has a handful of dials that decide the actual result. Fill in at least two. Typical knobs:

| Kind | Knobs worth setting |
|---|---|
| Any motion | duration, delay or stagger, easing (ease-out, ease-in-out, linear, overshoot), hold at the end |
| Camera | distance or angle, direction, start and end framing, height |
| Text and graphics | direction of entry, per-line or per-letter, speed in characters per second |
| UI and web | trigger (load, scroll distance, hover, tap), start and end size, minimum show time, reduced-motion fallback |
| Light | direction, strength relative to the main light, colour temperature, hard or soft |
| Sound | level change in dB, attack, release, where it starts |
| Editing | cut point, what carries over (shape, motion, colour, sound) |

When the user has no opinion on a knob, propose a sensible default out loud and say it is a default, so they can push back.

### Step 5: Write the named ask in the receiver's dialect

- **Video or image model:** full sentences. Name the move, say what moves and in what order, how long it takes, how it eases and where it ends, then add the subject, look and aspect ratio. Note that models treat timings as guidance.
  > "Slow dolly in from a medium shot to a close-up of the barista's hands over 4 seconds, smooth ease-in-out, camera physically moving closer, no zoom. Warm morning light, 16:9."
- **Code (CSS, Remotion, Canvas, After Effects):** a spec list the code can follow exactly: properties, values, units, easing curve, trigger, and the reduced-motion behaviour for interfaces.
  > `mask reveal · each line from below · 600 ms · 80 ms stagger · ease-out (0.2, 0.8, 0.2, 1) · hold 1.2 s`
- **A human collaborator:** the name, one reference, the knobs, and what must not change.

Before handing the ask over, lint it:

```sh
python scripts/lexicon.py lint prompt.txt --lexicon lexicon.json
```

- `VAGUE` means only feeling-words; go back to Step 2.
- `NAMED` means a name without knobs, or numbers buried in fog; add values or remove the fog.
- `MEASURED` means ready.

### Step 6: Save the confirmed name

Add the entry to the team's `lexicon.json` with: `name`, `aliases` (other names, other languages), `field`, `means`, `tell`, `not` (look-alikes) or `contrast`, `knobs` (at least two), `cues` (the everyday phrases people used before they knew the name), and `ask` (one example that sets real values). Validate it:

```sh
python scripts/lexicon.py check lexicon.json
```

The `cues` field is the secret: it records how people actually describe the thing, so the next `find` call matches their words directly.

## Examples

**Vague motion request.**
User: "Can the numbers on the stats slide do something cool?"
Agent asks: "Should each number appear already at its final value, or visibly climb up to it?" User: "Climb." Agent offers count-up (digits race then settle) vs odometer flip (each digit rolls like a mechanical counter). User picks count-up.
Named ask: "Count-up from 0 to the final value over 1.2 s, ease-out so the last digits slow down, thousands separator on, start when the slide appears."

**Chinese UI request.**
用户：“列表加载的时候别一直转圈，太土了。”
Agent 问：“加载时你希望先看到页面大致的排版轮廓，还是只要一个进度提示？” 用户：“先看到排版。”
命名请求：“骨架屏：灰色占位块按卡片布局排列，1.4 秒一次的微光扫过，至少显示 300 毫秒以免闪烁；开启‘减少动态效果’时关闭微光。”

**Lighting for an image model.**
User: "Make her pop off the dark background."
Agent asks: "Should her face stay lit from the front, with only a bright outline added, or should she become a dark shape against light?" User: "Face lit." So rim light, not silhouette.
Named ask: "Portrait on a near-black background, soft key light from front left, warm rim light from behind right outlining hair and shoulders at about twice the key's brightness."

**Fixing a teammate's prompt.**
Prompt: "Make the intro smooth, cinematic and premium." Lint says `VAGUE`. After two questions it becomes: "Open on a 5 s slow orbit of 60° to the left around the bottle at label height, ease-in-out, then a match cut on the bottle's silhouette to the logo, hold 1.5 s."

## Tips

- Ask at most two questions per round. People tire of quizzes fast.
- Always present the look-alike. Choosing between two named options is far easier than recalling a name from nothing.
- Feeling-words are useful as goals, not as instructions. Keep "premium" as the intent, then translate it into named moves and numbers.
- Keep one easing family and one main move per moment unless contrast is the point.
- For interfaces, always state the reduced-motion behaviour.
- If no name exists for what the user wants, say so, describe it with knobs only, and consider adding a house name for it.
- Never invent a name and pass it off as an industry term. If you are unsure whether a term is standard, say so.
- Lexicon entries are written in your own words. Short and concrete beats complete.
