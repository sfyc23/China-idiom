# 成语与成语接龙查询工具（Python 版）

[![pypi](https://img.shields.io/badge/pypi-0.4.0-yellow.svg)](https://pypi.org/project/china-idiom/)
![python](https://img.shields.io/badge/python-%3E3.8-green.svg)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **[English README](README_EN.md)**

一个功能丰富的中文成语工具库，涵盖成语查询、成语接龙、对战策略、知识问答、数据统计、**填字游戏**等 **27 个公开 API**，适用于聊天机器人、教育类 APP、微信小程序、命令行小游戏等各类场景。

---

## 目录

- [项目信息](#项目信息)
- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [API 详解](#api-详解)
  - [一、基础查询](#一基础查询)
  - [二、成语接龙](#二成语接龙)
  - [三、对战策略](#三对战策略)
  - [四、查询辅助](#四查询辅助)
  - [五、统计分析](#五统计分析)
  - [六、填字游戏](#六填字游戏)
- [数据模型](#数据模型)
- [完整 API 速查表](#完整-api-速查表)
- [数据来源](#数据来源)
- [开发与测试](#开发与测试)
- [License](#license)

---

## 项目信息

| 项 | 值 |
|---|---|
| GitHub | <https://github.com/sfyc23/China-idiom> |
| PyPI | <https://pypi.org/project/china-idiom/> |
| Python | >= 3.8 |
| 依赖 | **无**（零外部依赖，纯标准库） |
| License | MIT |

---

## 特性

### 数据层
- **30,000+ 条成语**：内置经过校正的成语数据集，每条成语包含拼音、拼音缩写、释义、出处（典故）、例句、首尾字、首尾字拼音、可接龙数量等 12 个字段。
- **CSV 存储**：数据以 `idiom.csv` 形式随包分发，透明可查，方便二次加工。

### 架构层
- **零外部依赖**：仅使用 Python 标准库（`csv`、`re`、`random`、`collections`），无需安装 pandas 或其他第三方包，安装轻量、启动迅速。
- **懒加载**：数据仅在首次调用 API 时从 CSV 加载到内存，`import` 阶段零 I/O 开销。
- **O(1) 索引查询**：内部构建了四组 dict 索引（成语名索引、首字索引、首字拼音索引、拼音缩写索引），核心查询操作为常数时间复杂度。

### 功能层
- **27 个公开 API**，按场景分为六大类：
  - **基础查询**（4 个）：判断成语、搜索成语、查询详情、随机成语。
  - **成语接龙**（4 个）：查找可接龙成语、判断能否接龙、自动接龙、校验接龙链。
  - **对战策略**（5 个）：难度分评估、最优反击、战力对比、绝杀成语列表、最长接龙链。
  - **查询辅助**（4 个）：拼音缩写搜索、按字数搜索、相关成语查找、成语知识问答。
  - **统计分析**（2 个）：成语库全局统计、热门开头字排行。
  - **填字游戏**（7 个）：单条填空、交叉填字格、接龙填字、释义填字、答案校验、逐级提示、批量出题。
  - 所有涉及接龙的函数均支持 `heteronym` 参数，可自由切换**同字接龙**或**同音（谐音）接龙**。

### 工程层
- **完整类型注解**（Type Hints）：所有公开函数均提供参数和返回值类型标注，IDE 友好。
- **统一输入校验**：所有接受成语输入的函数自动清洗非中文字符、校验类型，传入 `None` 或非字符串会抛出 `TypeError`。
- **循环检测**：自动接龙（`auto_idioms_solitaire`）内置 `seen` 集合，保证结果链无重复。
- **`Idiom` 数据类**：提供 `dataclass` 结构化模型，可直接 `from china_idiom import Idiom`。
- **125 个单元测试**：使用 pytest，覆盖所有公开 API 的正例、反例、边界值和异常输入。

---

## 安装

```bash
pip install china-idiom
```

升级到最新版：

```bash
pip install -U china-idiom
```

---

## 快速开始

```python
import china_idiom as idiom

# 判断成语
idiom.is_idiom('一心一意')        # True
idiom.is_idiom('你好世界')        # False

# 自动接龙
idiom.auto_idioms_solitaire('龙', max_count=5)
# ['龙飞凤舞', '舞文弄墨', '墨守成规', '规行矩步', '步履维艰']

# 绝杀反击
idiom.counter_attack('一心一意')  # '义浆仁粟'（让对方最难接）

# 成语问答
idiom.random_quiz()               # 四选一题目

# 填字游戏 — 单条填空
puzzle = idiom.generate_fill_blank(difficulty='medium')
# {'display': ['一', '□', '一', '□'], 'word': '一心一意', ...}

# 填字游戏 — 交叉填字格
grid = idiom.generate_crossword(size='small')
# 多条成语交叉排列的网格数据

# 填字游戏 — 接龙填字
chain = idiom.generate_chain_fill(chain_length=4)
# 接龙链中隐藏部分字，玩家填入使链条成立
```

---

## API 详解

以下按使用场景逐一介绍每个 API 的功能、参数、返回值和适用场景。

所有示例假设已执行：

```python
import china_idiom as idiom
```

---

### 一、基础查询

#### 1. `is_idiom(word)` — 判断是否是成语

**说明**：传入一个字符串，判断它是否是一条合法成语。输入会自动清洗标点和空格。

**参数**：

| 参数 | 类型 | 说明 |
|---|---|---|
| `word` | `str` | 待判断的词 |

**返回**：`bool` — `True` 是成语，`False` 不是。

**使用场景**：聊天机器人中校验用户输入是否为合法成语；游戏中验证玩家出招。

```python
idiom.is_idiom('一心一意')    # True
idiom.is_idiom('一心一意！')  # True（自动清洗标点）
idiom.is_idiom('你好世界')    # False
idiom.is_idiom('一')          # False
```

---

#### 2. `search_idiom(word, position=0, count=1, is_detail=False)` — 搜索成语

**说明**：按关键字搜索成语，支持指定关键字在成语中的位置，支持返回详细信息。结果随机采样。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word` | `str` | — | 搜索关键词（单个汉字或多个汉字） |
| `position` | `int` | `0` | 关键词所在位置（1-based），`0` 表示任意位置 |
| `count` | `int` | `1` | 返回最大数量 |
| `is_detail` | `bool` | `False` | 是否返回详细内容（拼音、缩写、释义、出处、例句） |

**返回**：`list[str]`（简单模式）或 `list[dict]`（详细模式）。无匹配返回 `[]`。

**使用场景**：输入法联想、成语字典 APP、根据某个字查找相关成语。

```python
# 搜索包含「龙」的成语
idiom.search_idiom(word='龙', count=3)
# ['龙飞凤舞', '画龙点睛', '龙马精神']

# 搜索第 2 个字是「心」的成语，返回详细信息
idiom.search_idiom(word='心', position=2, count=1, is_detail=True)
# [{'word': '热心快肠', 'pinyin': 'rè xīn kuài cháng',
#   'abbreviation': 'rxkc', 'explanation': '形容热情直爽。',
#   'derivation': '柯岩《奇异的书简·东方的明珠三》...', 'example': '无'}]
```

---

#### 3. `get_idiom_info(word)` — 查询成语完整信息

**说明**：精确查询一条成语的全部字段，包括首尾字、首尾字拼音、可接龙数量等接龙相关信息。与 `search_idiom` 的区别在于：这里是精确匹配，返回所有字段。

**参数**：

| 参数 | 类型 | 说明 |
|---|---|---|
| `word` | `str` | 成语 |

**返回**：`dict` 或 `None`（成语不存在时）。

**使用场景**：成语词典详情页；接龙前查看某成语的首尾字信息；展示成语卡片。

```python
idiom.get_idiom_info('一心一意')
# {'word': '一心一意', 'pinyin': 'yī xīn yī yì', 'abbreviation': 'yxyy',
#  'explanation': '只有一个心眼儿，没有别的考虑。',
#  'derivation': '《三国志·魏志·杜恕传》...', 'example': '...',
#  'head_word': '一', 'end_word': '意', 'head_pinyin': 'yī', 'end_pinyin': 'yì',
#  'next_count': 380}

idiom.get_idiom_info('不存在的')  # None
```

---

#### 4. `sample()` — 获取随机成语

**说明**：从成语库中随机抽取一条成语。

**返回**：`str` — 成语字符串。

**使用场景**：每日一词推送；随机话题生成；游戏起始成语。

```python
idiom.sample()
# '胸有成竹'
```

---

### 二、成语接龙

#### 5. `next_idioms_solitaire(word, count=1, heteronym=True, smaller=False)` — 查找可接龙的成语

**说明**：给定一个成语，查找可以接在其后的成语。支持同字接龙和同音（谐音）接龙。`smaller=True` 时优先返回"让对方更难接"的成语。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word` | `str` | — | 当前成语 |
| `count` | `int` | `1` | 返回数量 |
| `heteronym` | `bool` | `True` | `True` 允许同音字接龙，`False` 仅限同字接龙 |
| `smaller` | `bool` | `False` | `True` 优先返回后续可接数量最少的成语（策略模式） |

**返回**：`list[str]`。无可接成语返回 `[]`。

**使用场景**：接龙游戏中 AI 出招；给玩家提供候选提示。

```python
idiom.next_idioms_solitaire('一生一世', count=3)
# ['世态炎凉', '世代书香', '世风日下']

# 仅同字接龙
idiom.next_idioms_solitaire('一生一世', count=3, heteronym=False)
# ['世态炎凉', '世代书香', '世上无难事']

# 策略模式：选择让对方最难接的
idiom.next_idioms_solitaire('一生一世', count=3, smaller=True)
# ['世道人情', '世济其美', '世外桃源']
```

---

#### 6. `is_idiom_solitaire(before_word, after_word)` — 判断能否接龙

**说明**：判断两个成语是否可以前后衔接（前一个的尾字/尾音 == 后一个的首字/首音）。

**参数**：

| 参数 | 类型 | 说明 |
|---|---|---|
| `before_word` | `str` | 前一个成语 |
| `after_word` | `str` | 后一个成语 |

**返回**：`bool`。

**使用场景**：接龙裁判；校验用户在游戏中的出招是否合法。

```python
idiom.is_idiom_solitaire('一生一世', '逝将去汝')   # True（同音 shì/shì）
idiom.is_idiom_solitaire('一生一世', '生生世世')   # False
```

---

#### 7. `auto_idioms_solitaire(word, max_count=10, heteronym=True)` — 自动接龙

**说明**：输入一个汉字或成语，程序自动输出一整条接龙链。内置循环检测，保证结果不重复。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word` | `str` | — | 起始汉字或成语 |
| `max_count` | `int` | `10` | 链的最大长度 |
| `heteronym` | `bool` | `True` | 是否允许同音字接龙 |

**返回**：`list[str]`。

**使用场景**：一键生成接龙演示；单机娱乐模式；社交分享"看我接了多少个"。

```python
idiom.auto_idioms_solitaire('龙', max_count=6)
# ['龙飞凤舞', '舞文弄墨', '墨守成规', '规行矩步', '步履维艰', '艰苦朴素']

# 输入完整成语也可以
idiom.auto_idioms_solitaire('一生一世', max_count=5)
# ['一生一世', '适心娱目', '目兔顾犬', '犬马之力', '立时三刻']
```

---

#### 8. `validate_solitaire_chain(words, heteronym=True)` — 校验接龙链

**说明**：校验一整条接龙链是否合法，检查三项：每个词是否为有效成语、相邻成语能否衔接、是否有重复。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `words` | `list[str]` | — | 成语列表 |
| `heteronym` | `bool` | `True` | 是否允许同音字接龙 |

**返回**：`dict`，包含 `valid`（是否合法）、`length`（链长度）、`errors`（错误列表）。

**使用场景**：多人对战中的裁判系统；提交接龙结果时的服务端校验。

```python
idiom.validate_solitaire_chain(['一心一意', '意气风发', '发奋图强'])
# {'valid': True, 'length': 3, 'errors': []}

idiom.validate_solitaire_chain(['一心一意', '风和日丽'])
# {'valid': False, 'length': 2, 'errors': ["第 1 个「一心一意」无法接第 2 个「风和日丽」"]}

idiom.validate_solitaire_chain(['一心一意', '不存在词'])
# {'valid': False, 'length': 2, 'errors': ["第 2 个「不存在词」不是有效成语"]}
```

---

### 三、对战策略

#### 9. `get_difficulty(word, heteronym=True)` — 获取难度分

**说明**：返回一个成语被接龙后对方可接的成语数量。数值越小 = 对方越难接 = 你出这个成语越"狠"。`0` 表示绝杀（对方无法继续），`-1` 表示该成语不存在。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word` | `str` | — | 成语 |
| `heteronym` | `bool` | `True` | 是否考虑同音字 |

**返回**：`int`。

**使用场景**：AI 决策时评估每步出招的"威力"；给玩家展示成语难度等级。

```python
idiom.get_difficulty('一心一意')    # 380（对方有 380 个成语可接，难度低）
idiom.get_difficulty('阿姑阿翁')   # 0（绝杀！对方无法接龙）
idiom.get_difficulty('不存在词')    # -1
```

---

#### 10. `counter_attack(word, heteronym=True)` — 最优反击

**说明**：给定对手出的成语，从所有可接龙的候选中选出一个让对方最难接的应答（即候选中 `next_count` 最小的）。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word` | `str` | — | 对手的成语 |
| `heteronym` | `bool` | `True` | 是否允许同音字 |

**返回**：`str` 或 `None`（无法接龙时）。

**使用场景**：AI 对战中的"困难模式"出招；玩家求助"最强应答"。

```python
idiom.counter_attack('一心一意')
# '义浆仁粟'（对方接到这个词后可选最少）

idiom.counter_attack('阿姑阿翁')
# None（没有成语可以接）
```

---

#### 11. `solitaire_battle(word1, word2, heteronym=True)` — 对比战力

**说明**：对比两个成语的"战斗力"——各自被接龙后对方有多少候选。难度分越低 = 越强（对方越难接）。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word1` | `str` | — | 成语 A |
| `word2` | `str` | — | 成语 B |
| `heteronym` | `bool` | `True` | 是否考虑同音字 |

**返回**：`dict`，包含 `word1`、`word2` 的分析以及 `winner`。

**使用场景**：趣味对比："一心一意 vs 一生一世，谁更强？"；社交分享互动。

```python
idiom.solitaire_battle('一心一意', '一生一世')
# {'word1': {'word': '一心一意', 'exists': True, 'next_count': 380, 'difficulty': 380},
#  'word2': {'word': '一生一世', 'exists': True, 'next_count': 125, 'difficulty': 125},
#  'winner': '一生一世',
#  'reason': '难度分越低越强（对方越难接）'}
```

---

#### 12. `dead_end_idioms(count=20, heteronym=True)` — 绝杀成语列表

**说明**：返回"绝杀成语"——接到它后对方无法继续的成语（`next_count == 0`）。结果随机采样。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `count` | `int` | `20` | 返回数量 |
| `heteronym` | `bool` | `True` | 是否考虑同音字 |

**返回**：`list[dict]`，每条包含 `word`、`pinyin`、`explanation`、`next_count`。

**使用场景**：玩家查看"必杀技宝典"；AI 策略中优先选择绝杀词。

```python
idiom.dead_end_idioms(count=3)
# [{'word': '阿姑阿翁', 'pinyin': 'ā gū ā wēng',
#   'explanation': '指公公婆婆。', 'next_count': 0},
#  {'word': '虎踞龙蟠', 'pinyin': 'hǔ jù lóng pán',
#   'explanation': '形容地势雄壮险要。', 'next_count': 0},
#  ...]
```

---

#### 13. `longest_solitaire_chain(word, heteronym=True, max_depth=100)` — 最长接龙链

**说明**：从指定成语出发，用贪心 + 回溯搜索尽可能长的不重复接龙链。优先探索后续最少的分支，以此走得更深。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word` | `str` | — | 起始成语 |
| `heteronym` | `bool` | `True` | 是否允许同音字 |
| `max_depth` | `int` | `100` | 最大搜索深度 |

**返回**：`list[str]`。

**使用场景**：挑战"一个成语最多能接多少轮"；社交分享"最长接龙纪录"。

```python
chain = idiom.longest_solitaire_chain('一心一意', max_depth=20)
print(f"最长链 {len(chain)} 步: {chain[:5]}...")
# 最长链 20 步: ['一心一意', '意气风发', '发奋图强', '强人所难', '难以为继']...
```

> **注意**：`max_depth` 越大搜索时间越长，建议日常使用设为 20~50。

---

### 四、查询辅助

#### 14. `search_by_pinyin(abbreviation, count=10)` — 按拼音缩写搜索

**说明**：根据拼音首字母缩写搜索成语。数据中每条成语都有 `abbreviation` 字段（如"一心一意"的缩写为 `yxyy`）。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `abbreviation` | `str` | — | 拼音缩写（不区分大小写） |
| `count` | `int` | `10` | 最大返回数量 |

**返回**：`list[str]`。

**使用场景**：拼音输入法联想；猜成语游戏中给拼音提示。

```python
idiom.search_by_pinyin('yxyy')
# ['一心一意']

idiom.search_by_pinyin('RXKC')
# ['热心快肠']
```

---

#### 15. `search_by_length(length, count=10)` — 按字数搜索

**说明**：按成语的字数筛选。虽然大多数成语是 4 个字，但数据库中也包含 3 字、5 字、6 字、7 字、8 字等非四字成语。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `length` | `int` | — | 成语字数 |
| `count` | `int` | `10` | 最大返回数量 |

**返回**：`list[str]`。

**使用场景**：探索非四字成语；按字数分类展示。

```python
idiom.search_by_length(5, count=3)
# ['十万八千里', '一去不复返', '桃李满天下']

idiom.search_by_length(8, count=2)
# ['不到黄河心不死', '狗嘴里吐不出象牙']
```

---

#### 16. `similar_idioms(word, count=10)` — 查找相关成语

**说明**：查找与给定成语相关的成语，分三类：同首字、同尾字（以该成语尾字开头的成语）、同首音。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `word` | `str` | — | 成语 |
| `count` | `int` | `10` | 每类最大返回数量 |

**返回**：`dict`，包含 `same_head`、`same_tail`、`same_head_pinyin` 三个列表。

**使用场景**：拓展词汇量；"你还知道哪些以 X 开头的成语？"。

```python
idiom.similar_idioms('一心一意', count=3)
# {'same_head': ['一马当先', '一举两得', '一鸣惊人'],
#  'same_tail': ['意气风发', '意味深长', '意在笔先'],
#  'same_head_pinyin': ['一帆风顺', '一见钟情', '一鼓作气']}
```

---

#### 17. `random_quiz(mode='guess_word')` — 成语知识问答

**说明**：随机生成一道四选一的成语知识题。两种模式：
- `guess_word`：给出释义，猜是哪个成语。
- `guess_meaning`：给出成语，选正确的释义。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `mode` | `str` | `'guess_word'` | `'guess_word'` 或 `'guess_meaning'` |

**返回**：`dict`，包含 `mode`、`question`、`options`（4 个选项）、`answer`、`pinyin`。

**使用场景**：教育类 APP 的练习模块；聊天机器人的"成语小课堂"；每日成语挑战。

```python
idiom.random_quiz(mode='guess_word')
# {'mode': 'guess_word',
#  'question': '只有一个心眼儿，没有别的考虑。',
#  'options': ['三心二意', '一心一意', '心猿意马', '左顾右盼'],
#  'answer': '一心一意',
#  'pinyin': 'yī xīn yī yì'}

idiom.random_quiz(mode='guess_meaning')
# {'mode': 'guess_meaning',
#  'question': '画龙点睛',
#  'options': ['比喻写文章或讲话时...', '形容书法生动...', ...],
#  'answer': '比喻写文章或讲话时...',
#  'pinyin': 'huà lóng diǎn jīng'}
```

---

### 五、统计分析

#### 18. `stats()` — 成语库统计

**说明**：返回成语库的全局统计数据。

**返回**：`dict`，包含：
- `total`：成语总数
- `length_distribution`：按字数分布（如 `{3: 2, 4: 28710, 5: 740, ...}`）
- `dead_end_count`：绝杀成语数量（无法被接龙的）
- `max_next_count`：单条成语最大可接龙数
- `avg_next_count`：平均可接龙数

**使用场景**：数据看板展示；了解成语库整体概况。

```python
idiom.stats()
# {'total': 30895,
#  'length_distribution': {3: 2, 4: 28710, 5: 740, 6: 566, 7: 467, 8: 410},
#  'dead_end_count': 1523,
#  'max_next_count': 658,
#  'avg_next_count': 92.15}
```

---

#### 19. `hottest_start_chars(count=10)` — 热门开头字排行

**说明**：返回以该字开头的成语数量最多的汉字排行。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `count` | `int` | `10` | 返回数量 |

**返回**：`list[dict]`，每项包含 `char`（汉字）和 `count`（成语数量），按数量降序。

**使用场景**：接龙策略参考（选择开头字多的成语更容易接下去）；数据可视化。

```python
idiom.hottest_start_chars(count=5)
# [{'char': '不', 'count': 780},
#  {'char': '一', 'count': 380},
#  {'char': '无', 'count': 326},
#  {'char': '自', 'count': 238},
#  {'char': '人', 'count': 210}]
```

---

### 六、填字游戏

成语填字游戏是一类以中文成语为载体的益智类文字游戏。核心玩法是：给出成语的部分汉字，隐藏其中若干个字，玩家需要根据已知信息推断并填入正确的缺失字。

本库提供 **4 种题型生成** + **答案校验** + **逐级提示** + **批量出题**，共 7 个 API，可直接驱动小程序、APP、网页等各类填字游戏前端。

**支持的玩法形态**：

| 玩法 | 说明 | 示例 |
|---|---|---|
| **单条填空** | 给出一条成语，隐藏 1~3 个字 | `一□一□` → 一心一意 |
| **交叉填字格** | 多条成语在网格中交叉排列，共享某些格子 | 类似十字填字谜 |
| **接龙填字** | 接龙链中隐藏部分字，需填入使链条成立 | `龙飞凤□ → □文弄墨` |
| **释义填字** | 给出释义 + 部分字，填入完整成语 | 释义 + `□守成□` → 墨守成规 |

**三级难度体系**：

| 维度 | Easy | Medium | Hard |
|---|---|---|---|
| 隐藏字比例 | 25%（4 字隐 1） | 50%（4 字隐 2） | 75%（4 字隐 3） |
| 成语常见度 | 高频成语 | 中频成语 | 不限（含冷门成语） |
| 接龙链长度 | 2~3 条 | 4~5 条 | 6+ 条 |

---

#### 20. `generate_fill_blank(difficulty='medium', length=4, word=None)` — 单条成语填空题

**说明**：随机选取一条成语，隐藏指定数量的字，生成一道填空题。支持指定成语出题。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `difficulty` | `str` | `'medium'` | 难度：`'easy'`（隐 1 字）、`'medium'`（隐 2 字）、`'hard'`（隐 3 字） |
| `length` | `int` | `4` | 成语字数 |
| `word` | `str\|None` | `None` | 指定出题成语，`None` 时随机选取 |

**返回**：`dict`，包含 `puzzle_id`、`display`（展示数组）、`blanks`（空白格详情）、`word`（完整答案）、`pinyin`、`explanation`、`difficulty`、`total_blanks`。

**使用场景**：每日一题推送；教育 APP 练习模块；小程序填字关卡。

```python
idiom.generate_fill_blank(difficulty='medium')
# {'puzzle_id': 'fb_a1b2c3d4',
#  'display': ['一', '□', '一', '□'],
#  'blanks': [
#      {'position': 1, 'answer': '心', 'pinyin': 'xīn'},
#      {'position': 3, 'answer': '意', 'pinyin': 'yì'},
#  ],
#  'word': '一心一意', 'pinyin': 'yī xīn yī yì',
#  'explanation': '只有一个心眼儿，没有别的考虑。',
#  'difficulty': 'medium', 'total_blanks': 2}

# 指定成语出题
idiom.generate_fill_blank(word='画龙点睛', difficulty='easy')
# {'display': ['画', '龙', '□', '睛'], ...}
```

---

#### 21. `generate_crossword(size='small', difficulty='medium', seed_word=None)` — 交叉填字格

**说明**：生成一个由多条成语交叉组成的填字网格。成语在网格中横向或纵向排列，交叉点共享同一个汉字。玩家需要根据已知的字推断并填入所有空白格。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `size` | `str` | `'small'` | 网格规模：`'small'`（2 条交叉）、`'medium'`（3~4 条）、`'large'`（5~6 条） |
| `difficulty` | `str` | `'medium'` | 隐藏字比例：`'easy'`（30%）、`'medium'`（50%）、`'hard'`（70%） |
| `seed_word` | `str\|None` | `None` | 种子成语，`None` 时随机选取 |

**返回**：`dict`，包含 `puzzle_id`、`grid`（网格数据含 `rows`、`cols`、`cells` 数组）、`idioms`（各成语的方向和位置）、`difficulty`、`total_blanks`。

**使用场景**：九宫格/田字格类填字游戏；微信小程序闯关模式；成语十字谜。

```python
idiom.generate_crossword(size='small', seed_word='一心一意')
# {'puzzle_id': 'cw_...',
#  'grid': {'rows': 7, 'cols': 4,
#           'cells': [
#               {'row': 0, 'col': 0, 'char': '一', 'visible': True, 'idiom_ids': ['h0']},
#               {'row': 0, 'col': 1, 'char': '心', 'visible': False, 'idiom_ids': ['h0', 'v1']},
#               ...
#           ]},
#  'idioms': [
#      {'idiom_id': 'h0', 'word': '一心一意', 'direction': 'horizontal',
#       'start': {'row': 0, 'col': 0}, 'pinyin': '...', 'explanation': '...'},
#      {'idiom_id': 'v1', 'word': '心口如一', 'direction': 'vertical',
#       'start': {'row': 0, 'col': 1}, 'pinyin': '...', 'explanation': '...'},
#  ],
#  'difficulty': 'medium', 'total_blanks': 4}
```

交叉填字格的核心玩法示意：

```
    col0  col1  col2  col3
row0:  一    □    一    □      ← 横向：一心一意
row1:        口
row2:        如
row3:        □                 ← 纵向：心口如一
```

交叉点 `(row0, col1)` = "心"，同时属于横向和纵向两条成语。

---

#### 22. `generate_chain_fill(chain_length=4, difficulty='medium', heteronym=True)` — 接龙填字题

**说明**：自动生成一条成语接龙链，隐藏其中部分字，玩家需要填入缺失的字使整条接龙链成立。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `chain_length` | `int` | `4` | 接龙链长度（成语数量） |
| `difficulty` | `str` | `'medium'` | `'easy'`（每条隐 1 字，保留衔接字）、`'medium'`（每条隐 2 字）、`'hard'`（仅显示衔接字） |
| `heteronym` | `bool` | `True` | 是否允许同音字接龙 |

**返回**：`dict`，包含 `puzzle_id`、`chain`（接龙链数组，每项含 `display`、`word`、`blanks`）、`difficulty`、`heteronym`、`total_blanks`。

**使用场景**：接龙+填字的混合玩法；闯关模式中的接龙关卡；成语学习应用。

```python
idiom.generate_chain_fill(chain_length=3, difficulty='easy')
# {'puzzle_id': 'cf_...',
#  'chain': [
#      {'index': 0, 'display': ['龙', '飞', '凤', '□'], 'word': '龙飞凤舞',
#       'blanks': [{'position': 3, 'answer': '舞', 'pinyin': 'wǔ'}]},
#      {'index': 1, 'display': ['舞', '□', '弄', '墨'], 'word': '舞文弄墨',
#       'blanks': [{'position': 1, 'answer': '文', 'pinyin': 'wén'}]},
#      {'index': 2, 'display': ['墨', '守', '□', '规'], 'word': '墨守成规',
#       'blanks': [{'position': 2, 'answer': '成', 'pinyin': 'chéng'}]},
#  ],
#  'difficulty': 'easy', 'heteronym': True, 'total_blanks': 3}
```

> **难度说明**：`easy` 模式下衔接字（前一成语尾字 = 后一成语首字）始终可见，玩家能看清接龙脉络；`hard` 模式下仅保留衔接字，其余全部隐藏。

---

#### 23. `generate_clue_fill(difficulty='medium', count=1)` — 释义填字题

**说明**：给出成语的释义作为线索，同时显示部分字，玩家根据释义推断并填入缺失的字。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `difficulty` | `str` | `'medium'` | `'easy'`（显示 3 字 + 完整释义）、`'medium'`（显示 2 字 + 完整释义）、`'hard'`（显示 1 字 + 释义摘要） |
| `count` | `int` | `1` | 题目数量 |

**返回**：`dict`，包含 `puzzle_id`、`questions`（题目数组，每项含 `display`、`clue`、`word`、`pinyin`、`blanks`、`derivation`）、`difficulty`。

**使用场景**：成语词汇学习；考试练习 APP；聊天机器人"猜成语"互动。

```python
idiom.generate_clue_fill(difficulty='medium', count=2)
# {'puzzle_id': 'cl_...',
#  'questions': [
#      {'display': ['□', '守', '成', '□'],
#       'clue': '指思想保守，守着老规矩不肯改变。',
#       'word': '墨守成规', 'pinyin': 'mò shǒu chéng guī',
#       'blanks': [{'position': 0, 'answer': '墨', 'pinyin': 'mò'},
#                  {'position': 3, 'answer': '规', 'pinyin': 'guī'}],
#       'derivation': '...'},
#      ...
#  ],
#  'difficulty': 'medium'}
```

---

#### 24. `verify_fill_answer(puzzle_type, answer, expected)` — 校验答案

**说明**：校验玩家填入的答案是否正确。支持全部四种填字题型，逐位比对并计算得分。

**参数**：

| 参数 | 类型 | 说明 |
|---|---|---|
| `puzzle_type` | `str` | 题目类型：`'fill_blank'`、`'crossword'`、`'chain_fill'`、`'clue_fill'` |
| `answer` | `dict` | 玩家提交的答案 |
| `expected` | `dict` | 标准答案（由题目生成 API 返回的原始数据） |

**返回**：`dict`，包含 `correct`（整体是否正确）、`details`（逐位校验结果）、`score`（百分制得分）。

**使用场景**：服务端答案校验；实时反馈对错；计算玩家成绩。

```python
# 生成题目
puzzle = idiom.generate_fill_blank(word='一心一意', difficulty='medium')

# 玩家提交正确答案
answer = {'blanks': [
    {'position': 1, 'char': '心'},
    {'position': 3, 'char': '意'},
]}
result = idiom.verify_fill_answer('fill_blank', answer, puzzle)
# {'correct': True, 'score': 100,
#  'details': [
#      {'position': 1, 'submitted': '心', 'expected': '心', 'correct': True},
#      {'position': 3, 'submitted': '意', 'expected': '意', 'correct': True},
#  ],
#  'complete_word': '一心一意', 'is_valid_idiom': True}

# 玩家提交错误答案
wrong = {'blanks': [{'position': 1, 'char': '口'}, {'position': 3, 'char': '意'}]}
result = idiom.verify_fill_answer('fill_blank', wrong, puzzle)
# {'correct': False, 'score': 50, ...}
```

---

#### 25. `get_fill_hint(word, position, hint_level=1)` — 获取提示

**说明**：为填字游戏提供逐级递进的提示。每升一级，信息量更大，但建议扣除更多分数。

**参数**：

| 参数 | 类型 | 说明 |
|---|---|---|
| `word` | `str` | 目标成语 |
| `position` | `int` | 需要提示的空格位置（0-based） |
| `hint_level` | `int` | 提示等级 1~4 |

**提示等级**：

| 等级 | 提示内容 | 建议扣分 |
|---|---|---|
| 1 | 拼音声母 | 10% |
| 2 | 完整拼音 | 25% |
| 3 | 成语释义 | 40% |
| 4 | 直接揭示答案 | 100% |

**返回**：`dict`，包含 `hint_type`、`content`、`description`、`penalty`。

**使用场景**：玩家卡关时的求助功能；付费提示系统；教学模式中的渐进引导。

```python
idiom.get_fill_hint('一心一意', position=1, hint_level=1)
# {'hint_type': 'initial', 'content': 'x', 'description': '该字声母为 x', 'penalty': 0.1}

idiom.get_fill_hint('一心一意', position=1, hint_level=2)
# {'hint_type': 'pinyin', 'content': 'xīn', 'description': '该字拼音为 xīn', 'penalty': 0.25}

idiom.get_fill_hint('一心一意', position=1, hint_level=4)
# {'hint_type': 'reveal', 'content': '心', 'description': '答案是「心」', 'penalty': 1.0}
```

---

#### 26. `generate_fill_game_set(total_questions=10, difficulty='medium', types=None)` — 批量生成一局题目集

**说明**：一次性生成一局完整的游戏关卡，包含多种题型的混合题目，附带计分规则。

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `total_questions` | `int` | `10` | 总题目数 |
| `difficulty` | `str` | `'medium'` | 整体难度 |
| `types` | `list[str]\|None` | `None` | 题型列表，`None` 表示全部题型混合 |

**返回**：`dict`，包含 `game_id`、`difficulty`、`total_questions`、`questions`（题目数组）、`scoring`（计分规则）。

**使用场景**：小程序闯关模式一次拉取整局数据；每日挑战赛；多人同题竞速。

```python
idiom.generate_fill_game_set(total_questions=5, difficulty='easy')
# {'game_id': 'game_20260331_a1b2c3',
#  'difficulty': 'easy',
#  'total_questions': 5,
#  'questions': [
#      {'type': 'fill_blank', 'data': {...}},
#      {'type': 'clue_fill', 'data': {...}},
#      {'type': 'chain_fill', 'data': {...}},
#      {'type': 'fill_blank', 'data': {...}},
#      {'type': 'crossword', 'data': {...}},
#  ],
#  'scoring': {
#      'per_blank': 10,
#      'hint_penalty': [0.1, 0.25, 0.4, 1.0],
#      'time_bonus': True,
#  }}

# 仅生成填空和释义题
idiom.generate_fill_game_set(total_questions=3, types=['fill_blank', 'clue_fill'])
```

---

## 数据模型

`Idiom` 是一个 frozen dataclass，可直接导入：

```python
from china_idiom import Idiom
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `word` | `str` | 成语 |
| `pinyin` | `str` | 拼音（带声调） |
| `abbreviation` | `str` | 拼音首字母缩写 |
| `explanation` | `str` | 释义 |
| `derivation` | `str` | 出处 / 典故 |
| `example` | `str` | 例句 |
| `head_pinyin` | `str` | 首字拼音 |
| `end_pinyin` | `str` | 尾字拼音 |
| `head_word` | `str` | 首字 |
| `end_word` | `str` | 尾字 |
| `next_count` | `int` | 可接龙的成语数量 |
| `letter` | `str` | 拼音字母（无声调） |

---

## 完整 API 速查表

| 分类 | 函数 | 说明 |
|---|---|---|
| 基础查询 | `is_idiom(word)` | 判断是否是成语 |
| 基础查询 | `search_idiom(word, position, count, is_detail)` | 搜索成语 |
| 基础查询 | `get_idiom_info(word)` | 查询成语完整信息 |
| 基础查询 | `sample()` | 随机获取一个成语 |
| 成语接龙 | `next_idioms_solitaire(word, count, heteronym, smaller)` | 查找可接龙的成语 |
| 成语接龙 | `is_idiom_solitaire(before, after)` | 判断两个成语能否接龙 |
| 成语接龙 | `auto_idioms_solitaire(word, max_count, heteronym)` | 自动接龙 |
| 成语接龙 | `validate_solitaire_chain(words, heteronym)` | 校验接龙链合法性 |
| 对战策略 | `get_difficulty(word, heteronym)` | 获取难度分 |
| 对战策略 | `counter_attack(word, heteronym)` | 最优反击 |
| 对战策略 | `solitaire_battle(word1, word2, heteronym)` | 对比战力 |
| 对战策略 | `dead_end_idioms(count, heteronym)` | 绝杀成语列表 |
| 对战策略 | `longest_solitaire_chain(word, heteronym, max_depth)` | 最长接龙链 |
| 查询辅助 | `search_by_pinyin(abbreviation, count)` | 拼音缩写搜索 |
| 查询辅助 | `search_by_length(length, count)` | 按字数搜索 |
| 查询辅助 | `similar_idioms(word, count)` | 相关成语 |
| 查询辅助 | `random_quiz(mode)` | 成语知识问答 |
| 统计分析 | `stats()` | 成语库全局统计 |
| 统计分析 | `hottest_start_chars(count)` | 热门开头字排行 |
| 填字游戏 | `generate_fill_blank(difficulty, length, word)` | 单条成语填空题 |
| 填字游戏 | `generate_crossword(size, difficulty, seed_word)` | 交叉填字格 |
| 填字游戏 | `generate_chain_fill(chain_length, difficulty, heteronym)` | 接龙填字题 |
| 填字游戏 | `generate_clue_fill(difficulty, count)` | 释义填字题 |
| 填字游戏 | `verify_fill_answer(puzzle_type, answer, expected)` | 校验玩家答案 |
| 填字游戏 | `get_fill_hint(word, position, hint_level)` | 逐级提示 |
| 填字游戏 | `generate_fill_game_set(total_questions, difficulty, types)` | 批量生成一局题目集 |

---

## 数据来源

- 原始数据来源：[chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua)
- 经过大量校正后的数据：[idiom.csv](https://github.com/sfyc23/China-idiom/blob/master/china_idiom/idiom.csv)

---

## 开发与测试

```bash
git clone https://github.com/sfyc23/China-idiom.git
cd China-idiom
pip install pytest
pytest tests/ -v
```

当前共 **125 个测试用例**，覆盖所有公开 API。

---

## License

```
MIT License

Copyright (c) 2019  Thunder Bouble
```
