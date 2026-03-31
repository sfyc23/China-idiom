# Chinese Idiom & Idiom Solitaire Toolkit (Python)

[![pypi](https://img.shields.io/badge/pypi-0.4.0-yellow.svg)](https://pypi.org/project/china-idiom/)
![python](https://img.shields.io/badge/python-%3E3.8-green.svg)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **[中文文档](README.md)**

A feature-rich Chinese idiom (成语, chéngyǔ) toolkit with **27 public APIs** covering idiom lookup, idiom-chain solitaire, battle strategy, quiz generation, data analytics, and **fill-in puzzle games**. Ideal for chatbots, educational apps, WeChat mini-programs, and CLI games.

---

## Table of Contents

- [Project Info](#project-info)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [1. Basic Lookup](#1-basic-lookup)
  - [2. Idiom Solitaire (Chain Game)](#2-idiom-solitaire-chain-game)
  - [3. Battle Strategy](#3-battle-strategy)
  - [4. Search Helpers](#4-search-helpers)
  - [5. Statistics](#5-statistics)
  - [6. Fill-in Puzzle Game](#6-fill-in-puzzle-game)
- [Data Model](#data-model)
- [Full API Quick Reference](#full-api-quick-reference)
- [Data Source](#data-source)
- [Development & Testing](#development--testing)
- [License](#license)

---

## Project Info

| Item | Value |
|---|---|
| GitHub | <https://github.com/sfyc23/China-idiom> |
| PyPI | <https://pypi.org/project/china-idiom/> |
| Python | >= 3.8 |
| Dependencies | **None** (zero external deps, pure stdlib) |
| License | MIT |

---

## Features

### Data
- **30,000+ idioms**: A curated and corrected dataset. Each entry contains 12 fields: pinyin, pinyin abbreviation, meaning, origin (allusion), example sentence, head/tail characters, head/tail pinyin, chainable count, etc.
- **CSV format**: Shipped as `idiom.csv`, transparent and easy to inspect or extend.

### Architecture
- **Zero external dependencies**: Built entirely on Python stdlib (`csv`, `re`, `random`, `collections`). No pandas or other third-party packages needed — lightweight install, fast startup.
- **Lazy loading**: Data is loaded from CSV only on the first API call, not at `import` time. Zero I/O overhead during module import.
- **O(1) indexed lookups**: Internally builds four dict indexes (word index, head-char index, head-pinyin index, abbreviation index). Core lookups run in constant time.

### Functionality
- **27 public APIs** organized into six categories:
  - **Basic Lookup** (4): Check if a word is an idiom, search idioms, get detailed info, random idiom.
  - **Idiom Solitaire** (4): Find chainable idioms, check if two idioms can chain, auto-chain, validate a chain.
  - **Battle Strategy** (5): Difficulty score, optimal counter-attack, power comparison, dead-end (killer) idioms, longest chain.
  - **Search Helpers** (4): Pinyin abbreviation search, search by character count, find similar idioms, quiz generation.
  - **Statistics** (2): Database-wide stats, hottest starting characters ranking.
  - **Fill-in Puzzle** (7): Single fill-blank, crossword grid, chain fill, clue fill, answer verification, progressive hints, batch game set generation.
- All solitaire-related functions support a `heteronym` parameter to toggle between **same-character chaining** and **homophone (same-pinyin) chaining**.

### Engineering
- **Full type hints**: All public functions have parameter and return type annotations.
- **Unified input validation**: All functions accepting idiom input auto-strip non-Chinese characters and validate types (`TypeError` on `None` or non-string).
- **Cycle detection**: `auto_idioms_solitaire` uses a `seen` set to guarantee no duplicates in the result chain.
- **`Idiom` dataclass**: A structured frozen dataclass model, importable via `from china_idiom import Idiom`.
- **125 unit tests**: Full pytest coverage for all public APIs — positive cases, negative cases, edge cases, and invalid input.

---

## Installation

```bash
pip install china-idiom
```

Upgrade to latest:

```bash
pip install -U china-idiom
```

---

## Quick Start

```python
import china_idiom as idiom

# Check if it's an idiom
idiom.is_idiom('一心一意')        # True

# Auto-chain from a single character
idiom.auto_idioms_solitaire('龙', max_count=5)
# ['龙飞凤舞', '舞文弄墨', '墨守成规', '规行矩步', '步履维艰']

# Counter-attack (hardest response for opponent)
idiom.counter_attack('一心一意')  # '义浆仁粟'

# Quiz
idiom.random_quiz()               # 4-option multiple choice

# Fill-in puzzle — single blank
puzzle = idiom.generate_fill_blank(difficulty='medium')
# {'display': ['一', '□', '一', '□'], 'word': '一心一意', ...}

# Fill-in puzzle — crossword grid
grid = idiom.generate_crossword(size='small')
# Crossword grid with multiple idioms crossing each other

# Fill-in puzzle — chain fill
chain = idiom.generate_chain_fill(chain_length=4)
# Solitaire chain with hidden characters for players to fill in
```

---

## API Reference

All examples assume:

```python
import china_idiom as idiom
```

---

### 1. Basic Lookup

#### `is_idiom(word)` — Check if a word is a valid idiom

**Description**: Returns whether the input string is a recognized Chinese idiom. Punctuation and spaces are auto-stripped.

| Param | Type | Description |
|---|---|---|
| `word` | `str` | Word to check |

**Returns**: `bool`

**Use cases**: Validate user input in chatbots; verify player moves in games.

```python
idiom.is_idiom('一心一意')    # True
idiom.is_idiom('一心一意！')  # True (punctuation stripped)
idiom.is_idiom('hello')       # False
```

---

#### `search_idiom(word, position=0, count=1, is_detail=False)` — Search idioms

**Description**: Search idioms by keyword. Supports positional matching and detailed output. Results are randomly sampled.

| Param | Type | Default | Description |
|---|---|---|---|
| `word` | `str` | — | Search keyword (one or more Chinese characters) |
| `position` | `int` | `0` | Character position (1-based), `0` = any position |
| `count` | `int` | `1` | Max results |
| `is_detail` | `bool` | `False` | Whether to return detailed info (pinyin, meaning, origin, example) |

**Returns**: `list[str]` (simple) or `list[dict]` (detailed). `[]` if no match.

**Use cases**: Input method suggestions; idiom dictionary app; find idioms containing a specific character.

```python
idiom.search_idiom(word='龙', count=3)
# ['龙飞凤舞', '画龙点睛', '龙马精神']

idiom.search_idiom(word='心', position=2, count=1, is_detail=True)
# [{'word': '热心快肠', 'pinyin': 'rè xīn kuài cháng', ...}]
```

---

#### `get_idiom_info(word)` — Get full idiom details

**Description**: Exact lookup for a single idiom's complete information, including solitaire-related fields (head/tail characters, head/tail pinyin, chainable count).

| Param | Type | Description |
|---|---|---|
| `word` | `str` | Idiom |

**Returns**: `dict` or `None` (if not found).

**Use cases**: Idiom detail page; inspect an idiom's chaining properties before playing.

```python
idiom.get_idiom_info('一心一意')
# {'word': '一心一意', 'pinyin': 'yī xīn yī yì', 'abbreviation': 'yxyy',
#  'explanation': '...', 'derivation': '...', 'example': '...',
#  'head_word': '一', 'end_word': '意', 'head_pinyin': 'yī', 'end_pinyin': 'yì',
#  'next_count': 380}
```

---

#### `sample()` — Get a random idiom

**Returns**: `str`

**Use cases**: "Idiom of the Day"; random topic generation; game starting word.

```python
idiom.sample()  # '胸有成竹'
```

---

### 2. Idiom Solitaire (Chain Game)

> **What is Idiom Solitaire?** A popular Chinese word game where each player must say an idiom whose first character (or first-syllable pinyin) matches the last character (or last-syllable pinyin) of the previous idiom.

#### `next_idioms_solitaire(word, count=1, heteronym=True, smaller=False)` — Find chainable idioms

**Description**: Given an idiom, find idioms that can follow it in the chain. Supports both same-character and homophone chaining. `smaller=True` prioritizes responses that leave fewer options for the opponent.

| Param | Type | Default | Description |
|---|---|---|---|
| `word` | `str` | — | Current idiom |
| `count` | `int` | `1` | Number of results |
| `heteronym` | `bool` | `True` | Allow homophone chaining |
| `smaller` | `bool` | `False` | Prefer idioms with fewer follow-ups (strategic mode) |

**Returns**: `list[str]`. `[]` if none found.

**Use cases**: AI move generation; provide candidate hints to players.

```python
idiom.next_idioms_solitaire('一生一世', count=3)
# ['世态炎凉', '世代书香', '世风日下']

idiom.next_idioms_solitaire('一生一世', count=3, smaller=True)
# ['世济其美', '世道人情', '世外桃源']  (harder for opponent)
```

---

#### `is_idiom_solitaire(before_word, after_word)` — Check if two idioms can chain

| Param | Type | Description |
|---|---|---|
| `before_word` | `str` | Previous idiom |
| `after_word` | `str` | Next idiom |

**Returns**: `bool`

**Use cases**: Game referee; validate player moves.

```python
idiom.is_idiom_solitaire('一生一世', '逝将去汝')  # True (homophone: shì/shì)
idiom.is_idiom_solitaire('一生一世', '生生世世')  # False
```

---

#### `auto_idioms_solitaire(word, max_count=10, heteronym=True)` — Auto-chain

**Description**: Input a character or idiom, and the program automatically generates a full solitaire chain. Built-in cycle detection ensures no duplicates.

| Param | Type | Default | Description |
|---|---|---|---|
| `word` | `str` | — | Starting character or idiom |
| `max_count` | `int` | `10` | Max chain length |
| `heteronym` | `bool` | `True` | Allow homophone chaining |

**Returns**: `list[str]`

**Use cases**: One-click demo generation; single-player mode; social sharing.

```python
idiom.auto_idioms_solitaire('龙', max_count=5)
# ['龙飞凤舞', '舞文弄墨', '墨守成规', '规行矩步', '步履维艰']
```

---

#### `validate_solitaire_chain(words, heteronym=True)` — Validate a chain

**Description**: Validates an entire chain: checks that each entry is a valid idiom, adjacent entries can link, and no duplicates exist.

| Param | Type | Default | Description |
|---|---|---|---|
| `words` | `list[str]` | — | List of idioms |
| `heteronym` | `bool` | `True` | Allow homophone chaining |

**Returns**: `dict` with `valid` (bool), `length` (int), `errors` (list of error messages).

**Use cases**: Multiplayer game referee; server-side validation.

```python
idiom.validate_solitaire_chain(['一心一意', '意气风发', '发奋图强'])
# {'valid': True, 'length': 3, 'errors': []}

idiom.validate_solitaire_chain(['一心一意', '风和日丽'])
# {'valid': False, 'length': 2, 'errors': ['第 1 个「一心一意」无法接第 2 个「风和日丽」']}
```

---

### 3. Battle Strategy

#### `get_difficulty(word, heteronym=True)` — Difficulty score

**Description**: Returns how many idioms the opponent can use to follow this one. Lower = harder for opponent. `0` = dead end (killer move). `-1` = idiom not found.

| Param | Type | Default | Description |
|---|---|---|---|
| `word` | `str` | — | Idiom |
| `heteronym` | `bool` | `True` | Consider homophones |

**Returns**: `int`

**Use cases**: AI decision-making; display difficulty badges in UI.

```python
idiom.get_difficulty('一心一意')   # 380 (easy for opponent)
idiom.get_difficulty('阿姑阿翁')  # 0 (killer move!)
```

---

#### `counter_attack(word, heteronym=True)` — Optimal counter-attack

**Description**: Given the opponent's idiom, returns the response that leaves the fewest options for the opponent.

**Returns**: `str` or `None`

**Use cases**: AI "hard mode"; player hint "show me the best response".

```python
idiom.counter_attack('一心一意')  # '义浆仁粟'
```

---

#### `solitaire_battle(word1, word2, heteronym=True)` — Compare two idioms

**Description**: Compare the "battle power" of two idioms. The one with fewer follow-up options for the opponent wins.

**Returns**: `dict` with analysis for both words and a `winner`.

**Use cases**: Fun comparison: "Which idiom is stronger?"; social sharing.

```python
idiom.solitaire_battle('一心一意', '一生一世')
# {'word1': {'word': '一心一意', 'next_count': 380, ...},
#  'word2': {'word': '一生一世', 'next_count': 125, ...},
#  'winner': '一生一世', 'reason': '...'}
```

---

#### `dead_end_idioms(count=20, heteronym=True)` — Killer idioms

**Description**: Returns idioms that have zero follow-ups — if you play one of these, your opponent is stuck.

| Param | Type | Default | Description |
|---|---|---|---|
| `count` | `int` | `20` | Number of results |
| `heteronym` | `bool` | `True` | Consider homophones |

**Returns**: `list[dict]` with `word`, `pinyin`, `explanation`, `next_count`.

**Use cases**: "Killer move cheat sheet"; AI strategy — prefer dead-end words.

```python
idiom.dead_end_idioms(count=3)
# [{'word': '阿姑阿翁', 'pinyin': 'ā gū ā wēng',
#   'explanation': '...', 'next_count': 0}, ...]
```

---

#### `longest_solitaire_chain(word, heteronym=True, max_depth=100)` — Longest chain

**Description**: From a given idiom, use greedy DFS with backtracking to find the longest non-repeating chain. Explores branches with fewer follow-ups first (greedy heuristic to go deeper).

| Param | Type | Default | Description |
|---|---|---|---|
| `word` | `str` | — | Starting idiom |
| `heteronym` | `bool` | `True` | Allow homophones |
| `max_depth` | `int` | `100` | Max search depth |

**Returns**: `list[str]`

**Use cases**: Challenge "how long can you chain?"; record-breaking social sharing.

```python
chain = idiom.longest_solitaire_chain('一心一意', max_depth=20)
print(f"Longest chain: {len(chain)} steps")
```

> **Note**: Higher `max_depth` = longer search time. Recommended: 20–50 for interactive use.

---

### 4. Search Helpers

#### `search_by_pinyin(abbreviation, count=10)` — Search by pinyin abbreviation

**Description**: Search idioms by their pinyin initial abbreviation (e.g., `yxyy` for 一心一意).

| Param | Type | Default | Description |
|---|---|---|---|
| `abbreviation` | `str` | — | Pinyin abbreviation (case-insensitive) |
| `count` | `int` | `10` | Max results |

**Returns**: `list[str]`

**Use cases**: Pinyin input method suggestions; guessing games with pinyin hints.

```python
idiom.search_by_pinyin('yxyy')  # ['一心一意']
idiom.search_by_pinyin('RXKC')  # ['热心快肠']
```

---

#### `search_by_length(length, count=10)` — Search by character count

**Description**: Filter idioms by character count. While most idioms have 4 characters, the database also contains 3, 5, 6, 7, and 8-character idioms.

| Param | Type | Default | Description |
|---|---|---|---|
| `length` | `int` | — | Number of characters |
| `count` | `int` | `10` | Max results |

**Returns**: `list[str]`

**Use cases**: Explore non-standard-length idioms; categorized display.

```python
idiom.search_by_length(5, count=3)
# ['十万八千里', '一去不复返', '桃李满天下']
```

---

#### `similar_idioms(word, count=10)` — Find related idioms

**Description**: Find idioms related to the given one in three categories: same first character, same tail character (idioms starting with this idiom's last character), same first-character pinyin.

| Param | Type | Default | Description |
|---|---|---|---|
| `word` | `str` | — | Idiom |
| `count` | `int` | `10` | Max results per category |

**Returns**: `dict` with `same_head`, `same_tail`, `same_head_pinyin` lists.

**Use cases**: Vocabulary expansion; "What other idioms start with X?".

```python
idiom.similar_idioms('一心一意', count=3)
# {'same_head': ['一马当先', '一举两得', '一鸣惊人'],
#  'same_tail': ['意气风发', '意味深长', '意在笔先'],
#  'same_head_pinyin': ['一帆风顺', '一见钟情', '一鼓作气']}
```

---

#### `random_quiz(mode='guess_word')` — Idiom quiz

**Description**: Generate a random 4-option multiple-choice quiz question.
- `guess_word`: Given the meaning, guess which idiom it is.
- `guess_meaning`: Given the idiom, choose the correct meaning.

| Param | Type | Default | Description |
|---|---|---|---|
| `mode` | `str` | `'guess_word'` | `'guess_word'` or `'guess_meaning'` |

**Returns**: `dict` with `mode`, `question`, `options` (4 choices), `answer`, `pinyin`.

**Use cases**: Educational apps; chatbot "idiom class"; daily challenge.

```python
idiom.random_quiz(mode='guess_word')
# {'mode': 'guess_word', 'question': '只有一个心眼儿...', 
#  'options': ['三心二意', '一心一意', '心猿意马', '左顾右盼'],
#  'answer': '一心一意', 'pinyin': 'yī xīn yī yì'}
```

---

### 5. Statistics

#### `stats()` — Database statistics

**Returns**: `dict` with `total`, `length_distribution`, `dead_end_count`, `max_next_count`, `avg_next_count`.

**Use cases**: Dashboard display; understand the dataset at a glance.

```python
idiom.stats()
# {'total': 30895,
#  'length_distribution': {3: 2, 4: 28710, 5: 740, ...},
#  'dead_end_count': 1523, 'max_next_count': 658, 'avg_next_count': 92.15}
```

---

#### `hottest_start_chars(count=10)` — Top starting characters

**Description**: Characters that begin the most idioms, sorted descending.

| Param | Type | Default | Description |
|---|---|---|---|
| `count` | `int` | `10` | Number of results |

**Returns**: `list[dict]` with `char` and `count`.

**Use cases**: Strategy reference (pick idioms starting with popular chars for easier chaining); data visualization.

```python
idiom.hottest_start_chars(count=5)
# [{'char': '不', 'count': 780}, {'char': '一', 'count': 380}, ...]
```

---

### 6. Fill-in Puzzle Game

Idiom fill-in puzzles are a category of brain-teaser word games built around Chinese idioms. The core gameplay: present an idiom with some characters hidden, and the player must deduce and fill in the missing characters.

This library provides **4 puzzle generators** + **answer verification** + **progressive hints** + **batch game set** — 7 APIs total, ready to power mini-programs, apps, web games, and more.

**Supported puzzle types**:

| Type | Description | Example |
|---|---|---|
| **Single Fill-Blank** | One idiom with 1–3 characters hidden | `一□一□` → 一心一意 |
| **Crossword Grid** | Multiple idioms crossing in a grid, sharing characters | Similar to crossword puzzles |
| **Chain Fill** | A solitaire chain with hidden characters | `龙飞凤□ → □文弄墨` |
| **Clue Fill** | Given the meaning + partial characters, complete the idiom | meaning + `□守成□` → 墨守成规 |

**Three difficulty levels**:

| Dimension | Easy | Medium | Hard |
|---|---|---|---|
| Hidden ratio | 25% (hide 1 of 4) | 50% (hide 2 of 4) | 75% (hide 3 of 4) |
| Idiom frequency | Common idioms | Medium frequency | Any (incl. rare) |
| Chain length | 2–3 idioms | 4–5 idioms | 6+ idioms |

---

#### `generate_fill_blank(difficulty='medium', length=4, word=None)` — Single fill-blank puzzle

**Description**: Pick an idiom (randomly or specified), hide characters according to difficulty, and generate a fill-blank question.

| Param | Type | Default | Description |
|---|---|---|---|
| `difficulty` | `str` | `'medium'` | `'easy'` (hide 1), `'medium'` (hide 2), `'hard'` (hide 3) |
| `length` | `int` | `4` | Idiom character count |
| `word` | `str\|None` | `None` | Specify an idiom, or `None` for random |

**Returns**: `dict` with `puzzle_id`, `display` (display array with □), `blanks` (blank details), `word` (full answer), `pinyin`, `explanation`, `difficulty`, `total_blanks`.

**Use cases**: Daily challenge; educational app drills; mini-program levels.

```python
idiom.generate_fill_blank(difficulty='medium')
# {'puzzle_id': 'fb_a1b2c3d4',
#  'display': ['一', '□', '一', '□'],
#  'blanks': [{'position': 1, 'answer': '心', 'pinyin': 'xīn'},
#             {'position': 3, 'answer': '意', 'pinyin': 'yì'}],
#  'word': '一心一意', 'difficulty': 'medium', 'total_blanks': 2, ...}

idiom.generate_fill_blank(word='画龙点睛', difficulty='easy')
# {'display': ['画', '龙', '□', '睛'], ...}
```

---

#### `generate_crossword(size='small', difficulty='medium', seed_word=None)` — Crossword grid

**Description**: Generate a crossword grid where multiple idioms are placed horizontally and vertically, sharing characters at crossing points. Players fill in the hidden cells.

| Param | Type | Default | Description |
|---|---|---|---|
| `size` | `str` | `'small'` | `'small'` (2 idioms), `'medium'` (3–4), `'large'` (5–6) |
| `difficulty` | `str` | `'medium'` | Hide ratio: `'easy'` (30%), `'medium'` (50%), `'hard'` (70%) |
| `seed_word` | `str\|None` | `None` | Seed idiom, or `None` for random |

**Returns**: `dict` with `puzzle_id`, `grid` (containing `rows`, `cols`, `cells` array), `idioms` (direction and position of each idiom), `difficulty`, `total_blanks`.

**Use cases**: Crossword-style puzzle games; WeChat mini-program levels; idiom crossword puzzles.

```python
idiom.generate_crossword(size='small', seed_word='一心一意')
# {'grid': {'rows': 7, 'cols': 4, 'cells': [
#     {'row': 0, 'col': 0, 'char': '一', 'visible': True, 'idiom_ids': ['h0']},
#     {'row': 0, 'col': 1, 'char': '心', 'visible': False, 'idiom_ids': ['h0', 'v1']},
#     ...]},
#  'idioms': [
#     {'idiom_id': 'h0', 'word': '一心一意', 'direction': 'horizontal', ...},
#     {'idiom_id': 'v1', 'word': '心口如一', 'direction': 'vertical', ...}], ...}
```

---

#### `generate_chain_fill(chain_length=4, difficulty='medium', heteronym=True)` — Chain fill puzzle

**Description**: Auto-generate a solitaire chain, then hide characters according to difficulty. Players fill in the blanks to complete the chain.

| Param | Type | Default | Description |
|---|---|---|---|
| `chain_length` | `int` | `4` | Number of idioms in the chain |
| `difficulty` | `str` | `'medium'` | `'easy'` (hide 1/idiom, keep link chars), `'medium'` (hide 2), `'hard'` (show only link chars) |
| `heteronym` | `bool` | `True` | Allow homophone chaining |

**Returns**: `dict` with `puzzle_id`, `chain` (array of chain items with `display`, `word`, `blanks`), `difficulty`, `heteronym`, `total_blanks`.

**Use cases**: Solitaire + fill-in hybrid; level-based gameplay; idiom learning apps.

```python
idiom.generate_chain_fill(chain_length=3, difficulty='easy')
# {'chain': [
#     {'index': 0, 'display': ['龙', '飞', '凤', '□'], 'word': '龙飞凤舞',
#      'blanks': [{'position': 3, 'answer': '舞', 'pinyin': 'wǔ'}]},
#     {'index': 1, 'display': ['舞', '□', '弄', '墨'], 'word': '舞文弄墨', ...},
#     ...], 'total_blanks': 3, ...}
```

---

#### `generate_clue_fill(difficulty='medium', count=1)` — Clue fill puzzle

**Description**: Show the idiom's meaning as a clue plus partial characters. Players use the clue to fill in the missing characters.

| Param | Type | Default | Description |
|---|---|---|---|
| `difficulty` | `str` | `'medium'` | `'easy'` (show 3 chars + full meaning), `'medium'` (show 2 + meaning), `'hard'` (show 1 + truncated meaning) |
| `count` | `int` | `1` | Number of questions |

**Returns**: `dict` with `puzzle_id`, `questions` (array with `display`, `clue`, `word`, `pinyin`, `blanks`, `derivation`), `difficulty`.

**Use cases**: Vocabulary learning; exam practice apps; chatbot "guess the idiom" interaction.

```python
idiom.generate_clue_fill(difficulty='medium', count=1)
# {'questions': [
#     {'display': ['□', '守', '成', '□'],
#      'clue': '指思想保守，守着老规矩不肯改变。',
#      'word': '墨守成规', 'blanks': [...], ...}], ...}
```

---

#### `verify_fill_answer(puzzle_type, answer, expected)` — Verify answer

**Description**: Verify the player's submitted answer against the expected answer. Supports all four puzzle types. Returns per-cell correctness and a percentage score.

| Param | Type | Description |
|---|---|---|
| `puzzle_type` | `str` | `'fill_blank'`, `'crossword'`, `'chain_fill'`, or `'clue_fill'` |
| `answer` | `dict` | Player's submitted answer |
| `expected` | `dict` | Expected answer (original puzzle data from generator) |

**Returns**: `dict` with `correct` (bool), `details` (per-cell results), `score` (0–100).

**Use cases**: Server-side validation; real-time correctness feedback; scoring.

```python
puzzle = idiom.generate_fill_blank(word='一心一意', difficulty='medium')
answer = {'blanks': [{'position': 1, 'char': '心'}, {'position': 3, 'char': '意'}]}
result = idiom.verify_fill_answer('fill_blank', answer, puzzle)
# {'correct': True, 'score': 100, 'details': [...], ...}
```

---

#### `get_fill_hint(word, position, hint_level=1)` — Get hint

**Description**: Provide progressive hints for a fill-in puzzle. Higher levels reveal more information.

| Param | Type | Description |
|---|---|---|
| `word` | `str` | Target idiom |
| `position` | `int` | Position of the blank (0-based) |
| `hint_level` | `int` | Hint level 1–4 |

**Hint levels**:

| Level | Content | Suggested Penalty |
|---|---|---|
| 1 | Pinyin initial (consonant) | 10% |
| 2 | Full pinyin | 25% |
| 3 | Idiom meaning | 40% |
| 4 | Reveal the answer | 100% |

**Returns**: `dict` with `hint_type`, `content`, `description`, `penalty`.

**Use cases**: Player help system; paid hint feature; progressive teaching mode.

```python
idiom.get_fill_hint('一心一意', position=1, hint_level=1)
# {'hint_type': 'initial', 'content': 'x', 'description': '该字声母为 x', 'penalty': 0.1}

idiom.get_fill_hint('一心一意', position=1, hint_level=4)
# {'hint_type': 'reveal', 'content': '心', 'description': '答案是「心」', 'penalty': 1.0}
```

---

#### `generate_fill_game_set(total_questions=10, difficulty='medium', types=None)` — Batch game set

**Description**: Generate a complete game session with mixed puzzle types and scoring rules in a single call.

| Param | Type | Default | Description |
|---|---|---|---|
| `total_questions` | `int` | `10` | Total number of questions |
| `difficulty` | `str` | `'medium'` | Overall difficulty |
| `types` | `list[str]\|None` | `None` | Puzzle types to include; `None` = all types mixed |

**Returns**: `dict` with `game_id`, `difficulty`, `total_questions`, `questions` (array), `scoring` (rules).

**Use cases**: Mini-program level mode (fetch entire game at once); daily challenge; multiplayer same-question race.

```python
idiom.generate_fill_game_set(total_questions=5, difficulty='easy')
# {'game_id': 'game_20260331_a1b2c3', 'total_questions': 5,
#  'questions': [
#      {'type': 'fill_blank', 'data': {...}},
#      {'type': 'clue_fill', 'data': {...}},
#      {'type': 'chain_fill', 'data': {...}}, ...],
#  'scoring': {'per_blank': 10, 'hint_penalty': [0.1, 0.25, 0.4, 1.0],
#              'time_bonus': True}}

# Only fill-blank and clue-fill types
idiom.generate_fill_game_set(total_questions=3, types=['fill_blank', 'clue_fill'])
```

---

## Data Model

`Idiom` is a frozen dataclass, importable directly:

```python
from china_idiom import Idiom
```

| Field | Type | Description |
|---|---|---|
| `word` | `str` | Idiom text |
| `pinyin` | `str` | Pinyin with tones |
| `abbreviation` | `str` | Pinyin initial abbreviation |
| `explanation` | `str` | Meaning / definition |
| `derivation` | `str` | Origin / allusion |
| `example` | `str` | Example sentence |
| `head_pinyin` | `str` | Pinyin of first character |
| `end_pinyin` | `str` | Pinyin of last character |
| `head_word` | `str` | First character |
| `end_word` | `str` | Last character |
| `next_count` | `int` | Number of chainable idioms |
| `letter` | `str` | Pinyin letters (no tones) |

---

## Full API Quick Reference

| Category | Function | Description |
|---|---|---|
| Lookup | `is_idiom(word)` | Check if a word is an idiom |
| Lookup | `search_idiom(word, position, count, is_detail)` | Search idioms |
| Lookup | `get_idiom_info(word)` | Get full idiom info |
| Lookup | `sample()` | Random idiom |
| Solitaire | `next_idioms_solitaire(word, count, heteronym, smaller)` | Find chainable idioms |
| Solitaire | `is_idiom_solitaire(before, after)` | Check if two idioms can chain |
| Solitaire | `auto_idioms_solitaire(word, max_count, heteronym)` | Auto-chain |
| Solitaire | `validate_solitaire_chain(words, heteronym)` | Validate a chain |
| Strategy | `get_difficulty(word, heteronym)` | Difficulty score |
| Strategy | `counter_attack(word, heteronym)` | Optimal counter-attack |
| Strategy | `solitaire_battle(word1, word2, heteronym)` | Compare battle power |
| Strategy | `dead_end_idioms(count, heteronym)` | Killer idioms list |
| Strategy | `longest_solitaire_chain(word, heteronym, max_depth)` | Longest chain |
| Search | `search_by_pinyin(abbreviation, count)` | Pinyin abbreviation search |
| Search | `search_by_length(length, count)` | Search by character count |
| Search | `similar_idioms(word, count)` | Related idioms |
| Search | `random_quiz(mode)` | Idiom quiz |
| Stats | `stats()` | Database statistics |
| Stats | `hottest_start_chars(count)` | Top starting characters |
| Fill-in | `generate_fill_blank(difficulty, length, word)` | Single fill-blank puzzle |
| Fill-in | `generate_crossword(size, difficulty, seed_word)` | Crossword grid |
| Fill-in | `generate_chain_fill(chain_length, difficulty, heteronym)` | Chain fill puzzle |
| Fill-in | `generate_clue_fill(difficulty, count)` | Clue fill puzzle |
| Fill-in | `verify_fill_answer(puzzle_type, answer, expected)` | Verify player answer |
| Fill-in | `get_fill_hint(word, position, hint_level)` | Progressive hints |
| Fill-in | `generate_fill_game_set(total_questions, difficulty, types)` | Batch game set |

---

## Data Source

- Original data: [chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua)
- Corrected dataset: [idiom.csv](https://github.com/sfyc23/China-idiom/blob/master/china_idiom/idiom.csv)

---

## Development & Testing

```bash
git clone https://github.com/sfyc23/China-idiom.git
cd China-idiom
pip install pytest
pytest tests/ -v
```

Currently **125 test cases** covering all public APIs.

---

## License

```
MIT License

Copyright (c) 2019  Thunder Bouble
```
