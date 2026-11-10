# tip-of-tongue（话到嘴边）

[English](README.md) | **简体中文**

> 把“我脑子里有画面，但不知道它叫什么”，变成 AI（或人）能准确照做的、有名字有数值的请求。

## 简介

视频模型、图像模型和编程智能体交出的让人失望的结果，大多始于这样一句话：“开场要丝滑、有电影感”或者“标题要有高级感”。提需求的人心里非常清楚自己要什么，只是缺了那个词，于是 AI 只能用一个平庸的猜测去填空。

**tip-of-tongue** 是一个智能体技能，专门补上这段距离。它教你的智能体：

- 围绕用户**看得见的东西**提问，而不是考他不懂的术语；
- 给出一份候选**名称**短名单，每个都配上最容易混淆的**近亲**和唯一的可见区别；
- 挂上决定结果的**旋钮**（时长、距离、方向、缓动、触发方式、音量……）；
- 用**接收方的说法**写出最终请求：给视频/图像模型写句子，给代码写规格，给人写需求单；
- 慢慢积累一份**内部词典**，让团队用同一个词说同一件事。

它不限领域：动态图形、镜头运动、剪辑、界面组件、网页特效、灯光、声音，以及任何“知道名字才能提要求”的地方。

## 功能特点

- **六步流程**：愿望卡、问可见差别、带近亲的候选、拧旋钮、换说法、存词典。
- **先摆近亲**：每个名字都说明它“不是什么”（推镜 vs 变焦、遮罩显现 vs 淡入、轮廓光 vs 剪影）。
- **旋钮表**：覆盖动效、镜头、文字、界面/网页、灯光、声音、剪辑。
- **中英双语**：中英文完整说明，辅助脚本两种语言都能理解。
- **`lexicon.py` 辅助脚本**（只用 Python 标准库）：
  - `check` 校验内部词典（必填字段、至少两个旋钮、有近亲、示例请求带真实数值、不循环定义、名称和别名不重复）；
  - `find` 用日常描述（中文或英文）在词典里查名字；
  - `lint` 把提示词评为 `VAGUE`（含糊）、`NAMED`（有名无数）或 `MEASURED`（可交付），并指出感觉词。
- **入门词典**：12 条示例，涵盖镜头、动态图形、界面、网页、灯光、声音、剪辑。
- 27 个单元测试。

## 安装

技能本体是 `SKILL.md`（中文版 `SKILL.zh-CN.md`），`scripts/` 和 `examples/` 可选。

**Claude Code**

```sh
git clone https://github.com/fangdididi/tip-of-tongue ~/.claude/skills/tip-of-tongue
```

**Codex / 其他读取 `AGENTS.md` 或技能目录的智能体**

```sh
git clone https://github.com/fangdididi/tip-of-tongue ~/.codex/skills/tip-of-tongue
```

或者在 `AGENTS.md` 里引用 `SKILL.md`。

**Cursor**

克隆到项目里（例如 `.cursor/skills/tip-of-tongue`），再添加一条指向 `SKILL.md` 的规则，或把流程粘贴进项目规则。

**任意聊天助手**

在对话开头粘贴 `SKILL.zh-CN.md`（或 `SKILL.md`）的内容即可。

## 使用方法

像平时一样说话就行：

```text
标题要像凭空冒出来的那种，但不是淡入。帮我写成 Remotion 能照做的说法。
```

```text
Rewrite this prompt so a video model understands it: "make the intro smooth and cinematic".
```

```text
给我们设计组建一份内部词典，先加上“骨架屏”和“吸顶收缩”。
```

辅助命令：

```sh
# 校验词典
python scripts/lexicon.py check examples/lexicon.example.json

# 用描述查名字
python scripts/lexicon.py find examples/lexicon.example.json "文字从线后面冒出来"
python scripts/lexicon.py find examples/lexicon.example.json "the camera floats around the cup"

# 发送前给提示词打分
echo "标题要有高级感，丝滑一点" | python scripts/lexicon.py lint -
python scripts/lexicon.py lint prompt.txt --lexicon examples/lexicon.example.json --json
```

`lint` 的退出码：`0` 为 MEASURED，`1` 为 NAMED，`2` 为 VAGUE，可以直接放进脚本或 CI。

## 示例

| 之前 | 之后 |
|---|---|
| “数据页的数字弄得酷一点。” | “数字递增：从 0 到最终值，1.2 秒，缓出让最后几位慢下来，显示千位分隔符，页面出现时开始。” |
| “让她从黑背景里跳出来。” | “左前方柔和主光，右后方暖色轮廓光勾出头发和肩膀，亮度约为主光的两倍。” |
| "Don't show a spinner while the list loads." | "Skeleton screen in the card layout, 1.4 s shimmer, shown at least 300 ms; no shimmer under reduced motion." |
| “开场要丝滑、有电影感、有高级感。” | “开场 5 秒，围绕瓶子在标签高度向左缓慢环绕 60°，缓入缓出；然后按瓶身轮廓匹配剪辑到品牌标志，停留 1.5 秒。” |

更多完整演示见 [SKILL.zh-CN.md](SKILL.zh-CN.md#示例)。

## 词典条目格式

```json
{
  "name": "dolly in",
  "aliases": ["push in", "推镜"],
  "field": "camera",
  "means": "摄影机本身向主体移动……",
  "tell": "远近不同的物体放大速度不同……",
  "not": ["zoom in"],
  "knobs": ["移动距离", "时长", "缓动"],
  "cues": ["镜头往前走", "camera moves closer"],
  "ask": "从中景缓慢推镜到特写，4 秒，缓入缓出，不要变焦。"
}
```

`cues` 记录人们在知道名字之前的日常说法，正是它让 `find` 能匹配真实的描述。

## 文件结构

```
tip-of-tongue/
├── SKILL.md                     # 技能说明（英文）
├── SKILL.zh-CN.md               # 技能说明（中文）
├── README.md                    # 英文说明
├── README.zh-CN.md              # 本文件
├── LICENSE                      # MIT
├── scripts/
│   └── lexicon.py               # check / find / lint 辅助脚本，仅标准库
├── examples/
│   └── lexicon.example.json     # 入门内部词典（示例数据）
└── tests/
    └── test_lexicon.py          # 27 个单元测试
```

运行测试：`python -m unittest discover -s tests`。

## 许可证

[MIT](LICENSE) © fangdididi
