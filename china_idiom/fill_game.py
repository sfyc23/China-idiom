# -*- coding: utf-8 -*-
import re
import random
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from china_idiom.models import Idiom
from china_idiom.loader import get_word_index, get_all_idioms, get_random_idioms
from china_idiom.core import (
    _clean_word, is_idiom, get_idiom_info,
    auto_idioms_solitaire, validate_solitaire_chain,
)

__all__ = [
    'generate_fill_blank',
    'generate_crossword',
    'generate_chain_fill',
    'generate_clue_fill',
    'verify_fill_answer',
    'get_fill_hint',
    'generate_fill_game_set',
]

_BLANK = '□'

_DIFFICULTY_BLANK_COUNT = {'easy': 1, 'medium': 2, 'hard': 3}

_DIFFICULTY_HIDE_RATIO = {'easy': 0.3, 'medium': 0.5, 'hard': 0.7}

_SIZE_IDIOM_COUNT = {'small': 2, 'medium': 4, 'large': 6}

_HINT_PENALTY = [0.1, 0.25, 0.4, 1.0]


def _make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _split_pinyin(pinyin: str) -> List[str]:
    """将成语拼音字符串拆分为每个字的拼音列表"""
    return pinyin.strip().split()


def _get_initial(pinyin_syllable: str) -> str:
    """从单个拼音音节中提取声母"""
    initials = [
        'zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l',
        'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's', 'y', 'w',
    ]
    clean = re.sub(r'[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]',
                   lambda m: m.group(), pinyin_syllable.lower())
    for ini in initials:
        if clean.startswith(ini):
            return ini
    return clean[0] if clean else ''


def _pick_idiom_by_difficulty(difficulty: str, length: int = 4) -> Optional[Idiom]:
    """根据难度和字数选取成语"""
    all_idioms = get_all_idioms()
    filtered = [i for i in all_idioms if len(i.word) == length]
    if not filtered:
        return None

    if difficulty == 'easy':
        pool = [i for i in filtered if i.next_count > 200]
    elif difficulty == 'medium':
        pool = [i for i in filtered if 50 <= i.next_count <= 200]
    else:
        pool = filtered

    if not pool:
        pool = filtered
    return random.choice(pool)


def _select_blank_positions(word_len: int, blank_count: int,
                            difficulty: str) -> List[int]:
    """根据难度策略选择需要隐藏的位置"""
    blank_count = min(blank_count, word_len - 1)
    positions = list(range(word_len))

    if difficulty == 'easy':
        inner = [p for p in positions if 0 < p < word_len - 1]
        if len(inner) >= blank_count:
            return sorted(random.sample(inner, blank_count))
        return sorted(random.sample(positions, blank_count))

    if difficulty == 'medium' and word_len == 4 and blank_count == 2:
        return [1, 3]

    if difficulty == 'hard':
        keep = random.choice(positions)
        return sorted([p for p in positions if p != keep])

    return sorted(random.sample(positions, blank_count))


def _build_blanks(idiom_obj: Idiom, blank_positions: List[int]) -> List[Dict[str, Any]]:
    """为指定位置构建空白格信息"""
    pinyins = _split_pinyin(idiom_obj.pinyin)
    blanks = []
    for pos in blank_positions:
        py = pinyins[pos] if pos < len(pinyins) else ''
        blanks.append({
            'position': pos,
            'answer': idiom_obj.word[pos],
            'pinyin': py,
        })
    return blanks


def _build_display(word: str, blank_positions: List[int]) -> List[str]:
    """生成展示数组"""
    return [_BLANK if i in blank_positions else ch
            for i, ch in enumerate(word)]


# ============================================================
# API 1: 单条成语填空题
# ============================================================

def generate_fill_blank(
    difficulty: str = 'medium',
    length: int = 4,
    word: Optional[str] = None,
) -> Dict[str, Any]:
    """
    生成单条成语填空题。
    :param difficulty: 难度等级 'easy'/'medium'/'hard'
    :param length: 成语字数，默认 4
    :param word: 指定成语（为 None 时随机选取）
    :return: 题目字典
    """
    if difficulty not in _DIFFICULTY_BLANK_COUNT:
        difficulty = 'medium'

    if word is not None:
        word = _clean_word(word)
        idiom_obj = get_word_index().get(word)
        if idiom_obj is None:
            raise ValueError(f"成语「{word}」不存在")
    else:
        idiom_obj = _pick_idiom_by_difficulty(difficulty, length)
        if idiom_obj is None:
            raise ValueError(f"未找到 {length} 字的成语")

    word_len = len(idiom_obj.word)
    blank_count = _DIFFICULTY_BLANK_COUNT[difficulty]
    blank_positions = _select_blank_positions(word_len, blank_count, difficulty)
    blanks = _build_blanks(idiom_obj, blank_positions)
    display = _build_display(idiom_obj.word, blank_positions)

    return {
        'puzzle_id': _make_id('fb'),
        'puzzle_type': 'fill_blank',
        'display': display,
        'blanks': blanks,
        'word': idiom_obj.word,
        'pinyin': idiom_obj.pinyin,
        'explanation': idiom_obj.explanation,
        'difficulty': difficulty,
        'total_blanks': len(blanks),
    }


# ============================================================
# API 2: 交叉填字格
# ============================================================

def _find_cross_candidates(
    char: str,
    target_pos: int,
    word_len: int,
    exclude: set,
) -> List[Idiom]:
    """查找包含指定字且位于指定位置的成语，用于交叉放置"""
    all_idioms = get_all_idioms()
    results = []
    for item in all_idioms:
        if item.word in exclude:
            continue
        if len(item.word) != word_len:
            continue
        if target_pos < len(item.word) and item.word[target_pos] == char:
            results.append(item)
    return results


def _try_place_vertical(
    grid: Dict[Tuple[int, int], str],
    idiom_obj: Idiom,
    cross_row: int,
    cross_col: int,
    cross_pos: int,
) -> Optional[List[Tuple[int, int]]]:
    """尝试在网格中纵向放置成语，返回占用的坐标列表，冲突则返回 None"""
    start_row = cross_row - cross_pos
    cells = []
    for i, ch in enumerate(idiom_obj.word):
        r = start_row + i
        c = cross_col
        existing = grid.get((r, c))
        if existing is not None and existing != ch:
            return None
        cells.append((r, c))
    return cells


def _try_place_horizontal(
    grid: Dict[Tuple[int, int], str],
    idiom_obj: Idiom,
    cross_row: int,
    cross_col: int,
    cross_pos: int,
) -> Optional[List[Tuple[int, int]]]:
    """尝试在网格中横向放置成语，返回占用的坐标列表，冲突则返回 None"""
    start_col = cross_col - cross_pos
    cells = []
    for i, ch in enumerate(idiom_obj.word):
        r = cross_row
        c = start_col + i
        existing = grid.get((r, c))
        if existing is not None and existing != ch:
            return None
        cells.append((r, c))
    return cells


def generate_crossword(
    size: str = 'small',
    difficulty: str = 'medium',
    seed_word: Optional[str] = None,
) -> Dict[str, Any]:
    """
    生成交叉填字格。
    :param size: 'small'（2 条交叉）/ 'medium'（3~4 条）/ 'large'（5~6 条）
    :param difficulty: 隐藏比例 'easy'(30%)/'medium'(50%)/'hard'(70%)
    :param seed_word: 种子成语（为 None 时随机选取）
    :return: 交叉填字格数据
    """
    if size not in _SIZE_IDIOM_COUNT:
        size = 'small'
    if difficulty not in _DIFFICULTY_HIDE_RATIO:
        difficulty = 'medium'

    target_count = _SIZE_IDIOM_COUNT[size]

    if seed_word is not None:
        seed_word = _clean_word(seed_word)
        seed_obj = get_word_index().get(seed_word)
        if seed_obj is None:
            raise ValueError(f"成语「{seed_word}」不存在")
    else:
        seed_obj = _pick_idiom_by_difficulty('medium', 4)
        if seed_obj is None:
            raise ValueError("未找到可用的种子成语")

    word_len = len(seed_obj.word)
    grid: Dict[Tuple[int, int], str] = {}
    cell_idioms: Dict[Tuple[int, int], List[str]] = {}
    placed_idioms: List[Dict[str, Any]] = []
    used_words: set = set()

    seed_row = word_len
    seed_start_col = 0
    seed_id = f"h{len(placed_idioms)}"
    for i, ch in enumerate(seed_obj.word):
        coord = (seed_row, seed_start_col + i)
        grid[coord] = ch
        cell_idioms.setdefault(coord, []).append(seed_id)
    placed_idioms.append({
        'idiom_id': seed_id,
        'word': seed_obj.word,
        'direction': 'horizontal',
        'start': {'row': seed_row, 'col': seed_start_col},
        'pinyin': seed_obj.pinyin,
        'explanation': seed_obj.explanation,
    })
    used_words.add(seed_obj.word)

    pending: List[Tuple[Dict[str, Any], str]] = [(placed_idioms[0], 'vertical')]

    max_attempts = target_count * 20
    attempt = 0

    while len(placed_idioms) < target_count and pending and attempt < max_attempts:
        attempt += 1
        base_info, next_dir = pending[0]
        base_word = base_info['word']
        base_obj = get_word_index()[base_word]
        base_start = base_info['start']
        base_direction = base_info['direction']

        placed_one = False
        char_indices = list(range(len(base_word)))
        random.shuffle(char_indices)

        for ci in char_indices:
            if len(placed_idioms) >= target_count:
                break

            ch = base_word[ci]
            if base_direction == 'horizontal':
                cross_row = base_start['row']
                cross_col = base_start['col'] + ci
            else:
                cross_row = base_start['row'] + ci
                cross_col = base_start['col']

            for target_pos in range(word_len):
                candidates = _find_cross_candidates(ch, target_pos, word_len, used_words)
                if not candidates:
                    continue
                random.shuffle(candidates)

                for cand in candidates[:10]:
                    if next_dir == 'vertical':
                        cells = _try_place_vertical(
                            grid, cand, cross_row, cross_col, target_pos)
                    else:
                        cells = _try_place_horizontal(
                            grid, cand, cross_row, cross_col, target_pos)

                    if cells is None:
                        continue

                    idiom_id = f"{'v' if next_dir == 'vertical' else 'h'}{len(placed_idioms)}"
                    for idx, coord in enumerate(cells):
                        grid[coord] = cand.word[idx]
                        cell_idioms.setdefault(coord, []).append(idiom_id)

                    if next_dir == 'vertical':
                        start = {'row': cells[0][0], 'col': cells[0][1]}
                    else:
                        start = {'row': cells[0][0], 'col': cells[0][1]}

                    new_entry = {
                        'idiom_id': idiom_id,
                        'word': cand.word,
                        'direction': next_dir,
                        'start': start,
                        'pinyin': cand.pinyin,
                        'explanation': cand.explanation,
                    }
                    placed_idioms.append(new_entry)
                    used_words.add(cand.word)

                    opposite = 'horizontal' if next_dir == 'vertical' else 'vertical'
                    pending.append((new_entry, opposite))
                    placed_one = True
                    break

                if placed_one:
                    break
            if placed_one:
                break

        if not placed_one:
            pending.pop(0)

    if not grid:
        raise ValueError("无法生成交叉填字格")

    min_r = min(r for r, c in grid)
    min_c = min(c for r, c in grid)
    max_r = max(r for r, c in grid)
    max_c = max(c for r, c in grid)

    for entry in placed_idioms:
        entry['start']['row'] -= min_r
        entry['start']['col'] -= min_c

    normalized_grid: Dict[Tuple[int, int], str] = {}
    normalized_cell_idioms: Dict[Tuple[int, int], List[str]] = {}
    for (r, c), ch in grid.items():
        new_coord = (r - min_r, c - min_c)
        normalized_grid[new_coord] = ch
        normalized_cell_idioms[new_coord] = cell_idioms.get((r, c), [])

    rows = max_r - min_r + 1
    cols = max_c - min_c + 1

    hide_ratio = _DIFFICULTY_HIDE_RATIO[difficulty]
    all_coords = list(normalized_grid.keys())
    total_cells = len(all_coords)
    hide_count = max(1, int(total_cells * hide_ratio))

    cross_points = {coord for coord, ids in normalized_cell_idioms.items()
                    if len(ids) > 1}
    non_cross = [c for c in all_coords if c not in cross_points]
    random.shuffle(non_cross)

    hidden: set = set()
    for coord in non_cross:
        if len(hidden) >= hide_count:
            break
        hidden.add(coord)

    if len(hidden) < hide_count:
        cross_list = list(cross_points)
        random.shuffle(cross_list)
        for coord in cross_list:
            if len(hidden) >= hide_count:
                break
            hidden.add(coord)

    for entry in placed_idioms:
        word = entry['word']
        start_r = entry['start']['row']
        start_c = entry['start']['col']
        direction = entry['direction']
        visible_count = 0
        for i in range(len(word)):
            if direction == 'horizontal':
                coord = (start_r, start_c + i)
            else:
                coord = (start_r + i, start_c)
            if coord not in hidden:
                visible_count += 1
        if visible_count == 0:
            if direction == 'horizontal':
                restore = (start_r, start_c)
            else:
                restore = (start_r, start_c)
            hidden.discard(restore)

    cells_output = []
    for coord in sorted(normalized_grid.keys()):
        r, c = coord
        cells_output.append({
            'row': r,
            'col': c,
            'char': normalized_grid[coord],
            'visible': coord not in hidden,
            'idiom_ids': normalized_cell_idioms.get(coord, []),
        })

    return {
        'puzzle_id': _make_id('cw'),
        'puzzle_type': 'crossword',
        'grid': {
            'rows': rows,
            'cols': cols,
            'cells': cells_output,
        },
        'idioms': placed_idioms,
        'difficulty': difficulty,
        'total_blanks': len(hidden),
    }


# ============================================================
# API 3: 接龙填字题
# ============================================================

def generate_chain_fill(
    chain_length: int = 4,
    difficulty: str = 'medium',
    heteronym: bool = True,
) -> Dict[str, Any]:
    """
    生成接龙填字题。
    :param chain_length: 接龙链长度（成语数量），默认 4
    :param difficulty: 难度 'easy'/'medium'/'hard'
    :param heteronym: 是否允许同音字接龙
    :return: 接龙填字题数据
    """
    if difficulty not in _DIFFICULTY_BLANK_COUNT:
        difficulty = 'medium'
    chain_length = max(2, chain_length)

    for _ in range(50):
        seed = _pick_idiom_by_difficulty(difficulty, 4)
        if seed is None:
            raise ValueError("未找到可用的起始成语")
        chain = auto_idioms_solitaire(seed.word, max_count=chain_length,
                                      heteronym=heteronym)
        if len(chain) >= chain_length:
            chain = chain[:chain_length]
            break
    else:
        chain = auto_idioms_solitaire(
            random.choice(get_all_idioms()).word,
            max_count=chain_length, heteronym=heteronym,
        )
        if len(chain) < 2:
            raise ValueError("无法生成足够长度的接龙链")

    word_index = get_word_index()
    chain_items: List[Dict[str, Any]] = []
    total_blanks = 0

    for idx, w in enumerate(chain):
        idiom_obj = word_index[w]
        word_len = len(w)
        pinyins = _split_pinyin(idiom_obj.pinyin)

        if difficulty == 'easy':
            link_positions = set()
            if idx > 0:
                link_positions.add(0)
            if idx < len(chain) - 1:
                link_positions.add(word_len - 1)
            inner = [p for p in range(word_len) if p not in link_positions]
            blank_count = min(1, len(inner))
            blank_positions = sorted(random.sample(inner, blank_count)) if inner else []

        elif difficulty == 'medium':
            keep_positions = set()
            if idx == 0:
                keep_positions.add(0)
            elif idx == len(chain) - 1:
                keep_positions.add(word_len - 1)
            else:
                keep_positions.add(random.choice([0, word_len - 1]))
            removable = [p for p in range(word_len) if p not in keep_positions]
            blank_count = min(2, len(removable))
            blank_positions = sorted(random.sample(removable, blank_count))

        else:  # hard
            link_positions = set()
            if idx > 0:
                link_positions.add(0)
            if idx < len(chain) - 1:
                link_positions.add(word_len - 1)
            blank_positions = sorted(
                [p for p in range(word_len) if p not in link_positions])

        blanks = []
        for pos in blank_positions:
            py = pinyins[pos] if pos < len(pinyins) else ''
            blanks.append({'position': pos, 'answer': w[pos], 'pinyin': py})

        display = _build_display(w, blank_positions)
        total_blanks += len(blanks)

        chain_items.append({
            'index': idx,
            'display': display,
            'word': w,
            'blanks': blanks,
        })

    return {
        'puzzle_id': _make_id('cf'),
        'puzzle_type': 'chain_fill',
        'chain': chain_items,
        'difficulty': difficulty,
        'heteronym': heteronym,
        'total_blanks': total_blanks,
    }


# ============================================================
# API 4: 释义填字题
# ============================================================

def generate_clue_fill(
    difficulty: str = 'medium',
    count: int = 1,
) -> Dict[str, Any]:
    """
    生成释义填字题。
    :param difficulty: 难度 'easy'/'medium'/'hard'
    :param count: 题目数量，默认 1
    :return: 释义填字题数据
    """
    if difficulty not in ('easy', 'medium', 'hard'):
        difficulty = 'medium'
    count = max(1, count)

    questions: List[Dict[str, Any]] = []

    for _ in range(count):
        idiom_obj = _pick_idiom_by_difficulty(difficulty, 4)
        if idiom_obj is None:
            continue

        word_len = len(idiom_obj.word)
        pinyins = _split_pinyin(idiom_obj.pinyin)

        if difficulty == 'easy':
            blank_count = 1
        elif difficulty == 'medium':
            blank_count = max(1, word_len // 2)
        else:
            blank_count = max(1, word_len - 1)

        blank_positions = _select_blank_positions(word_len, blank_count, difficulty)
        blanks = _build_blanks(idiom_obj, blank_positions)
        display = _build_display(idiom_obj.word, blank_positions)

        clue = idiom_obj.explanation
        if difficulty == 'hard' and len(clue) > 10:
            clue = clue[:10] + '……'

        questions.append({
            'display': display,
            'clue': clue,
            'word': idiom_obj.word,
            'pinyin': idiom_obj.pinyin,
            'blanks': blanks,
            'derivation': idiom_obj.derivation,
        })

    return {
        'puzzle_id': _make_id('cl'),
        'puzzle_type': 'clue_fill',
        'questions': questions,
        'difficulty': difficulty,
    }


# ============================================================
# API 5: 校验答案
# ============================================================

def verify_fill_answer(
    puzzle_type: str,
    answer: Dict[str, Any],
    expected: Dict[str, Any],
) -> Dict[str, Any]:
    """
    校验玩家填入的答案。
    :param puzzle_type: 题目类型 'fill_blank'/'crossword'/'chain_fill'/'clue_fill'
    :param answer: 玩家答案
    :param expected: 标准答案（由生成 API 返回）
    :return: 校验结果
    """
    if puzzle_type == 'fill_blank':
        return _verify_single_fill(answer, expected)
    elif puzzle_type == 'crossword':
        return _verify_crossword(answer, expected)
    elif puzzle_type == 'chain_fill':
        return _verify_chain_fill(answer, expected)
    elif puzzle_type == 'clue_fill':
        return _verify_clue_fill(answer, expected)
    else:
        return {'correct': False, 'details': [], 'score': 0,
                'error': f"未知题目类型: {puzzle_type}"}


def _verify_single_fill(
    answer: Dict[str, Any],
    expected: Dict[str, Any],
) -> Dict[str, Any]:
    """校验单条填空题"""
    expected_blanks = {b['position']: b['answer'] for b in expected.get('blanks', [])}
    submitted_blanks = {b['position']: b['char'] for b in answer.get('blanks', [])}

    details = []
    correct_count = 0
    for pos, exp_char in expected_blanks.items():
        sub_char = submitted_blanks.get(pos, '')
        is_correct = sub_char == exp_char
        if is_correct:
            correct_count += 1
        details.append({
            'position': pos,
            'submitted': sub_char,
            'expected': exp_char,
            'correct': is_correct,
        })

    total = len(expected_blanks)
    score = int(correct_count / total * 100) if total > 0 else 0

    assembled = list(expected.get('word', ''))
    for pos, char in submitted_blanks.items():
        if 0 <= pos < len(assembled):
            assembled[pos] = char
    complete_word = ''.join(assembled)

    is_valid_idiom = is_idiom(complete_word)

    return {
        'correct': correct_count == total,
        'details': details,
        'score': score,
        'complete_word': complete_word,
        'is_valid_idiom': is_valid_idiom,
    }


def _verify_crossword(
    answer: Dict[str, Any],
    expected: Dict[str, Any],
) -> Dict[str, Any]:
    """校验交叉填字格"""
    expected_cells = {}
    for cell in expected.get('grid', {}).get('cells', []):
        if not cell.get('visible', True):
            expected_cells[(cell['row'], cell['col'])] = cell['char']

    submitted_cells = {}
    for cell in answer.get('cells', []):
        submitted_cells[(cell['row'], cell['col'])] = cell.get('char', '')

    details = []
    correct_count = 0
    for (r, c), exp_char in expected_cells.items():
        sub_char = submitted_cells.get((r, c), '')
        is_correct = sub_char == exp_char
        if is_correct:
            correct_count += 1
        details.append({
            'row': r, 'col': c,
            'submitted': sub_char, 'expected': exp_char,
            'correct': is_correct,
        })

    total = len(expected_cells)
    score = int(correct_count / total * 100) if total > 0 else 0

    return {
        'correct': correct_count == total,
        'details': details,
        'score': score,
    }


def _verify_chain_fill(
    answer: Dict[str, Any],
    expected: Dict[str, Any],
) -> Dict[str, Any]:
    """校验接龙填字题"""
    expected_chain = expected.get('chain', [])
    answer_chain = answer.get('chain', [])

    details = []
    correct_count = 0
    total = 0

    answer_map = {item['index']: item for item in answer_chain}

    for exp_item in expected_chain:
        idx = exp_item['index']
        ans_item = answer_map.get(idx, {})
        ans_blanks = {b['position']: b['char'] for b in ans_item.get('blanks', [])}

        for blank in exp_item.get('blanks', []):
            total += 1
            pos = blank['position']
            exp_char = blank['answer']
            sub_char = ans_blanks.get(pos, '')
            is_correct = sub_char == exp_char
            if is_correct:
                correct_count += 1
            details.append({
                'chain_index': idx,
                'position': pos,
                'submitted': sub_char,
                'expected': exp_char,
                'correct': is_correct,
            })

    score = int(correct_count / total * 100) if total > 0 else 0

    reconstructed = []
    for exp_item in expected_chain:
        idx = exp_item['index']
        word_chars = list(exp_item['word'])
        ans_item = answer_map.get(idx, {})
        ans_blanks = {b['position']: b['char'] for b in ans_item.get('blanks', [])}
        for pos, char in ans_blanks.items():
            if 0 <= pos < len(word_chars):
                word_chars[pos] = char
        reconstructed.append(''.join(word_chars))

    heteronym = expected.get('heteronym', True)
    chain_valid = validate_solitaire_chain(reconstructed, heteronym=heteronym)

    return {
        'correct': correct_count == total,
        'details': details,
        'score': score,
        'chain_valid': chain_valid['valid'],
    }


def _verify_clue_fill(
    answer: Dict[str, Any],
    expected: Dict[str, Any],
) -> Dict[str, Any]:
    """校验释义填字题"""
    exp_questions = expected.get('questions', [])
    ans_questions = answer.get('questions', [])

    all_details = []
    total_correct = 0
    total_blanks = 0

    for qi, exp_q in enumerate(exp_questions):
        ans_q = ans_questions[qi] if qi < len(ans_questions) else {}
        ans_blanks = {b['position']: b['char'] for b in ans_q.get('blanks', [])}

        for blank in exp_q.get('blanks', []):
            total_blanks += 1
            pos = blank['position']
            exp_char = blank['answer']
            sub_char = ans_blanks.get(pos, '')
            is_correct = sub_char == exp_char
            if is_correct:
                total_correct += 1
            all_details.append({
                'question_index': qi,
                'position': pos,
                'submitted': sub_char,
                'expected': exp_char,
                'correct': is_correct,
            })

    score = int(total_correct / total_blanks * 100) if total_blanks > 0 else 0

    return {
        'correct': total_correct == total_blanks,
        'details': all_details,
        'score': score,
    }


# ============================================================
# API 6: 获取提示
# ============================================================

def get_fill_hint(
    word: str,
    position: int,
    hint_level: int = 1,
) -> Dict[str, Any]:
    """
    为填字游戏提供逐级递进的提示。
    :param word: 目标成语
    :param position: 需要提示的空格位置（0-based）
    :param hint_level: 提示等级 1~4
    :return: 提示信息
    """
    word = _clean_word(word)
    idiom_obj = get_word_index().get(word)
    if idiom_obj is None:
        raise ValueError(f"成语「{word}」不存在")

    if position < 0 or position >= len(idiom_obj.word):
        raise ValueError(f"位置 {position} 超出范围 [0, {len(idiom_obj.word) - 1}]")

    hint_level = max(1, min(4, hint_level))
    target_char = idiom_obj.word[position]
    pinyins = _split_pinyin(idiom_obj.pinyin)
    target_pinyin = pinyins[position] if position < len(pinyins) else ''

    if hint_level == 1:
        initial = _get_initial(target_pinyin)
        return {
            'hint_type': 'initial',
            'content': initial,
            'description': f'该字声母为 {initial}',
            'penalty': _HINT_PENALTY[0],
        }
    elif hint_level == 2:
        return {
            'hint_type': 'pinyin',
            'content': target_pinyin,
            'description': f'该字拼音为 {target_pinyin}',
            'penalty': _HINT_PENALTY[1],
        }
    elif hint_level == 3:
        return {
            'hint_type': 'explanation',
            'content': idiom_obj.explanation,
            'description': f'成语释义：{idiom_obj.explanation}',
            'penalty': _HINT_PENALTY[2],
        }
    else:
        return {
            'hint_type': 'reveal',
            'content': target_char,
            'description': f'答案是「{target_char}」',
            'penalty': _HINT_PENALTY[3],
        }


# ============================================================
# API 7: 批量生成一局题目集
# ============================================================

_ALL_TYPES = ['fill_blank', 'clue_fill', 'chain_fill', 'crossword']


def generate_fill_game_set(
    total_questions: int = 10,
    difficulty: str = 'medium',
    types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    批量生成一局完整的填字游戏题目集。
    :param total_questions: 总题目数，默认 10
    :param difficulty: 整体难度 'easy'/'medium'/'hard'
    :param types: 题型列表，None 表示全部题型混合
    :return: 游戏题目集
    """
    if difficulty not in ('easy', 'medium', 'hard'):
        difficulty = 'medium'
    total_questions = max(1, total_questions)

    if types is None:
        available_types = list(_ALL_TYPES)
    else:
        available_types = [t for t in types if t in _ALL_TYPES]
        if not available_types:
            available_types = list(_ALL_TYPES)

    questions: List[Dict[str, Any]] = []
    type_cycle = available_types * ((total_questions // len(available_types)) + 1)
    random.shuffle(type_cycle)

    for i in range(total_questions):
        q_type = type_cycle[i % len(type_cycle)]
        try:
            if q_type == 'fill_blank':
                data = generate_fill_blank(difficulty=difficulty)
            elif q_type == 'clue_fill':
                data = generate_clue_fill(difficulty=difficulty, count=1)
            elif q_type == 'chain_fill':
                chain_len = {'easy': 3, 'medium': 4, 'hard': 6}.get(difficulty, 4)
                data = generate_chain_fill(
                    chain_length=chain_len, difficulty=difficulty)
            elif q_type == 'crossword':
                data = generate_crossword(size='small', difficulty=difficulty)
            else:
                continue
            questions.append({'type': q_type, 'data': data})
        except (ValueError, IndexError):
            fallback = generate_fill_blank(difficulty=difficulty)
            questions.append({'type': 'fill_blank', 'data': fallback})

    now = datetime.now().strftime('%Y%m%d')
    game_id = f"game_{now}_{uuid.uuid4().hex[:6]}"

    return {
        'game_id': game_id,
        'difficulty': difficulty,
        'total_questions': len(questions),
        'questions': questions,
        'scoring': {
            'per_blank': 10,
            'hint_penalty': _HINT_PENALTY,
            'time_bonus': True,
        },
    }
