# -*- coding: utf-8 -*-
import re
import random
from collections import Counter
from typing import List, Optional, Union, Dict, Any, Tuple

from china_idiom.models import Idiom
from china_idiom.loader import (
    get_word_index, get_head_word_index, get_head_pinyin_index,
    get_abbreviation_index, get_all_idioms, get_random_idioms,
)

__all__ = [
    # 原有功能
    'is_idiom', 'is_idiom_solitaire',
    'next_idioms_solitaire', 'auto_idioms_solitaire',
    'search_idiom', 'sample',
    # 核心游戏必需
    'get_idiom_info', 'get_difficulty', 'validate_solitaire_chain',
    # 趣味玩法
    'longest_solitaire_chain', 'dead_end_idioms',
    'counter_attack', 'solitaire_battle',
    # 查询辅助
    'search_by_pinyin', 'search_by_length', 'random_quiz', 'similar_idioms',
    # 统计分析
    'stats', 'hottest_start_chars',
]

_CLEAN_RE = re.compile(r'[^\u4e00-\u9fa5]')


def _clean_word(word: str) -> str:
    """统一输入清洗：类型校验 + 去除非中文字符"""
    if not isinstance(word, str):
        raise TypeError(f"参数必须是字符串，实际收到: {type(word).__name__}")
    return _CLEAN_RE.sub('', word)


def _get_candidates(idiom_obj: Idiom, heteronym: bool = True) -> Dict[str, Idiom]:
    """获取某个成语可接龙的所有候选成语（去重）"""
    candidates: Dict[str, Idiom] = {}
    hw_index = get_head_word_index()
    for item in hw_index.get(idiom_obj.end_word, []):
        candidates[item.word] = item
    if heteronym:
        hp_index = get_head_pinyin_index()
        for item in hp_index.get(idiom_obj.end_pinyin, []):
            candidates[item.word] = item
    return candidates


# ============================================================
# 原有功能
# ============================================================

def is_idiom(word: str) -> bool:
    """
    判断一个词是否是成语。
    :param word: 待判断的词
    :return: True 是成语，False 不是成语
    """
    word = _clean_word(word)
    if not word:
        return False
    return word in get_word_index()


def is_idiom_solitaire(before_word: str, after_word: str) -> bool:
    """
    判断前一个成语与后一个成语是否可连接（用于成语接龙）。
    :param before_word: 前一个成语
    :param after_word: 后一个成语
    :return: True 可以接龙，False 不可以
    """
    before_word = _clean_word(before_word)
    after_word = _clean_word(after_word)
    if not before_word or not after_word:
        return False

    word_index = get_word_index()
    b = word_index.get(before_word)
    a = word_index.get(after_word)
    if b is None or a is None:
        return False

    return b.end_word == a.head_word or b.end_pinyin == a.head_pinyin


def next_idioms_solitaire(
    word: str,
    count: int = 1,
    heteronym: bool = True,
    smaller: bool = False,
) -> List[str]:
    """
    获取可以接龙的下一个成语。
    :param word: 成语
    :param count: 返回数量，默认 1
    :param heteronym: 是否可以使用同音字，默认 True
    :param smaller: 是否选择后续接龙数量最少的成语（让对方更难接），默认 False
    :return: 成语列表
    """
    count = max(count, 1)
    word = _clean_word(word)
    if not word:
        return []

    idiom_obj = get_word_index().get(word)
    if idiom_obj is None:
        return []

    candidates = _get_candidates(idiom_obj, heteronym)
    if not candidates:
        return []

    items = list(candidates.values())
    count = min(count, len(items))

    if smaller:
        items.sort(key=lambda x: x.next_count)
        return [item.word for item in items[:count]]
    else:
        return [item.word for item in random.sample(items, count)]


def auto_idioms_solitaire(
    word: str = '',
    max_count: int = 10,
    heteronym: bool = True,
) -> List[str]:
    """
    自动接龙模式 - 输入一个汉字或者成语，程序自动输出一组成语接龙的结果。
    :param word: 起始汉字或成语
    :param max_count: 最大长度，默认 10
    :param heteronym: 是否可以用同音字，默认 True
    :return: 成语列表
    """
    word = _clean_word(word)
    if not word:
        return []

    word_index = get_word_index()

    if word in word_index:
        start_word = word
    else:
        matched = [w for w in word_index if w.startswith(word)]
        if not matched:
            return []
        start_word = matched[0]

    result: List[str] = [start_word]
    seen: set = {start_word}

    for _ in range(max_count - 1):
        candidates = next_idioms_solitaire(result[-1], heteronym=heteronym, count=5)
        next_word = None
        for c in candidates:
            if c not in seen:
                next_word = c
                break
        if next_word is None:
            break
        result.append(next_word)
        seen.add(next_word)

    return result


def search_idiom(
    word: str,
    position: int = 0,
    count: int = 1,
    is_detail: bool = False,
) -> Union[List[str], List[Dict[str, Any]]]:
    """
    搜索查找成语。
    :param word: 关键词
    :param position: 关键词所在位置（1-based），0 表示任意位置
    :param count: 返回最大数量，默认 1
    :param is_detail: 是否返回详细内容
    :return: 成语列表或详细信息列表
    """
    word = _clean_word(word)
    if not word:
        return []

    all_idioms = get_all_idioms()
    count = max(count, 1)

    if position > 0:
        idx = position - 1
        matched = [item for item in all_idioms
                    if len(item.word) > idx and item.word[idx] == word]
    else:
        matched = [item for item in all_idioms if word in item.word]

    if not matched:
        return []

    count = min(count, len(matched))
    selected = random.sample(matched, count)

    if not is_detail:
        return [item.word for item in selected]
    else:
        return [
            {
                'word': item.word,
                'pinyin': item.pinyin,
                'abbreviation': item.abbreviation,
                'explanation': item.explanation,
                'derivation': item.derivation,
                'example': item.example,
            }
            for item in selected
        ]


def sample() -> str:
    """
    获取一个随机的成语。
    :return: 成语字符串
    """
    items = get_random_idioms(1)
    return items[0].word if items else ''


# ============================================================
# 核心游戏必需
# ============================================================

def get_idiom_info(word: str) -> Optional[Dict[str, Any]]:
    """
    精确查询一个成语的完整信息。
    :param word: 成语
    :return: 包含所有字段的字典，不存在则返回 None
    """
    word = _clean_word(word)
    if not word:
        return None

    idiom_obj = get_word_index().get(word)
    if idiom_obj is None:
        return None

    return {
        'word': idiom_obj.word,
        'pinyin': idiom_obj.pinyin,
        'abbreviation': idiom_obj.abbreviation,
        'explanation': idiom_obj.explanation,
        'derivation': idiom_obj.derivation,
        'example': idiom_obj.example,
        'head_word': idiom_obj.head_word,
        'end_word': idiom_obj.end_word,
        'head_pinyin': idiom_obj.head_pinyin,
        'end_pinyin': idiom_obj.end_pinyin,
        'next_count': idiom_obj.next_count,
    }


def get_difficulty(word: str, heteronym: bool = True) -> int:
    """
    获取成语的难度分（对方可接的成语数量）。
    数值越小 = 对方越难接 = 出这个成语越"狠"。
    0 表示绝杀（无人能接）。-1 表示该成语不存在。
    :param word: 成语
    :param heteronym: 是否算同音字接龙
    :return: 可接成语数量
    """
    word = _clean_word(word)
    if not word:
        return -1

    idiom_obj = get_word_index().get(word)
    if idiom_obj is None:
        return -1

    return len(_get_candidates(idiom_obj, heteronym))


def validate_solitaire_chain(
    words: List[str],
    heteronym: bool = True,
) -> Dict[str, Any]:
    """
    校验一整条接龙链是否合法。
    :param words: 成语列表
    :param heteronym: 是否允许同音字接龙
    :return: {'valid': bool, 'length': int, 'errors': list}
    """
    errors: List[str] = []
    if not words:
        return {'valid': False, 'length': 0, 'errors': ['接龙链为空']}

    word_index = get_word_index()
    seen: set = set()

    for i, raw_word in enumerate(words):
        w = _clean_word(raw_word)
        if w not in word_index:
            errors.append(f"第 {i + 1} 个「{raw_word}」不是有效成语")
            continue
        if w in seen:
            errors.append(f"第 {i + 1} 个「{w}」重复出现")
        seen.add(w)

    for i in range(len(words) - 1):
        w1 = _clean_word(words[i])
        w2 = _clean_word(words[i + 1])
        b = word_index.get(w1)
        a = word_index.get(w2)
        if b is None or a is None:
            continue
        can_link = b.end_word == a.head_word
        if heteronym:
            can_link = can_link or b.end_pinyin == a.head_pinyin
        if not can_link:
            errors.append(f"第 {i + 1} 个「{w1}」无法接第 {i + 2} 个「{w2}」")

    return {
        'valid': len(errors) == 0,
        'length': len(words),
        'errors': errors,
    }


# ============================================================
# 趣味玩法
# ============================================================

def longest_solitaire_chain(
    word: str,
    heteronym: bool = True,
    max_depth: int = 100,
) -> List[str]:
    """
    从某个成语出发，用贪心+回溯尽可能找到最长不重复接龙链。
    优先选择后续最少的分支（贪心策略），以此尽量走更深。
    :param word: 起始成语
    :param heteronym: 是否允许同音字
    :param max_depth: 最大搜索深度，默认 100
    :return: 最长接龙链
    """
    word = _clean_word(word)
    if not word:
        return []

    word_index = get_word_index()
    if word not in word_index:
        return []

    best: List[str] = []
    stack: List[str] = [word]
    seen: set = {word}

    def _dfs(current: str, depth: int) -> None:
        nonlocal best
        if len(stack) > len(best):
            best = list(stack)
        if depth >= max_depth:
            return

        idiom_obj = word_index[current]
        candidates = _get_candidates(idiom_obj, heteronym)
        nexts = [c for c in candidates.values() if c.word not in seen]
        nexts.sort(key=lambda x: x.next_count)

        for item in nexts:
            seen.add(item.word)
            stack.append(item.word)
            _dfs(item.word, depth + 1)
            stack.pop()
            seen.discard(item.word)

            if len(best) >= max_depth:
                return

    _dfs(word, 1)
    return best


def dead_end_idioms(count: int = 20, heteronym: bool = True) -> List[Dict[str, Any]]:
    """
    返回"绝杀成语"——接到它后对方无法继续的成语。
    :param count: 返回数量，默认 20
    :param heteronym: 是否考虑同音字
    :return: 绝杀成语列表，每条包含 word、pinyin、explanation
    """
    all_idioms = get_all_idioms()
    killers: List[Idiom] = []

    for item in all_idioms:
        if not _get_candidates(item, heteronym):
            killers.append(item)

    count = min(count, len(killers))
    if count <= 0:
        return []

    selected = random.sample(killers, count)
    return [
        {
            'word': item.word,
            'pinyin': item.pinyin,
            'explanation': item.explanation,
            'next_count': 0,
        }
        for item in selected
    ]


def counter_attack(word: str, heteronym: bool = True) -> Optional[str]:
    """
    给定对手出的成语，返回一个让对方最难接的应答。
    :param word: 对手的成语
    :param heteronym: 是否允许同音字
    :return: 最佳应答成语，无法接龙则返回 None
    """
    word = _clean_word(word)
    if not word:
        return None

    idiom_obj = get_word_index().get(word)
    if idiom_obj is None:
        return None

    candidates = _get_candidates(idiom_obj, heteronym)
    if not candidates:
        return None

    best = min(candidates.values(), key=lambda x: x.next_count)
    return best.word


def solitaire_battle(
    word1: str,
    word2: str,
    heteronym: bool = True,
) -> Dict[str, Any]:
    """
    对比两个成语的"战力"：各自有多少后续可接、各自的难度分。
    :param word1: 成语 A
    :param word2: 成语 B
    :param heteronym: 是否考虑同音字
    :return: 对比结果
    """
    word1 = _clean_word(word1)
    word2 = _clean_word(word2)
    word_index = get_word_index()

    def _analyze(w: str) -> Dict[str, Any]:
        obj = word_index.get(w)
        if obj is None:
            return {'word': w, 'exists': False, 'next_count': 0, 'difficulty': -1}
        c = _get_candidates(obj, heteronym)
        return {
            'word': w,
            'exists': True,
            'next_count': len(c),
            'difficulty': len(c),
        }

    a1 = _analyze(word1)
    a2 = _analyze(word2)

    if not a1['exists'] or not a2['exists']:
        winner = None
    elif a1['difficulty'] < a2['difficulty']:
        winner = word1
    elif a2['difficulty'] < a1['difficulty']:
        winner = word2
    else:
        winner = 'tie'

    return {
        'word1': a1,
        'word2': a2,
        'winner': winner,
        'reason': '难度分越低越强（对方越难接）',
    }


# ============================================================
# 查询辅助
# ============================================================

def search_by_pinyin(abbreviation: str, count: int = 10) -> List[str]:
    """
    按拼音缩写搜索成语。
    :param abbreviation: 拼音缩写，如 'yxyy'
    :param count: 最大返回数量
    :return: 成语列表
    """
    if not isinstance(abbreviation, str):
        raise TypeError(f"参数必须是字符串，实际收到: {type(abbreviation).__name__}")
    abbr = abbreviation.strip().lower()
    if not abbr:
        return []

    abbr_index = get_abbreviation_index()
    matched = abbr_index.get(abbr, [])

    if not matched:
        return []

    count = min(max(count, 1), len(matched))
    return [item.word for item in random.sample(matched, count)]


def search_by_length(length: int, count: int = 10) -> List[str]:
    """
    按成语字数搜索。
    :param length: 成语字数（如 4、5、6、8）
    :param count: 最大返回数量
    :return: 成语列表
    """
    all_idioms = get_all_idioms()
    matched = [item for item in all_idioms if len(item.word) == length]

    if not matched:
        return []

    count = min(max(count, 1), len(matched))
    return [item.word for item in random.sample(matched, count)]


def random_quiz(mode: str = 'guess_word') -> Dict[str, Any]:
    """
    成语知识问答。
    :param mode: 'guess_word' — 给释义猜成语；'guess_meaning' — 给成语选释义
    :return: 题目信息
    """
    all_idioms = get_all_idioms()

    if mode == 'guess_word':
        target = random.choice(all_idioms)
        distractors_pool = [i for i in all_idioms if i.word != target.word]
        distractors = random.sample(distractors_pool, min(3, len(distractors_pool)))

        options = [target.word] + [d.word for d in distractors]
        random.shuffle(options)
        return {
            'mode': 'guess_word',
            'question': target.explanation,
            'options': options,
            'answer': target.word,
            'pinyin': target.pinyin,
        }
    else:
        target = random.choice(all_idioms)
        distractors_pool = [i for i in all_idioms if i.word != target.word]
        distractors = random.sample(distractors_pool, min(3, len(distractors_pool)))

        options = [target.explanation] + [d.explanation for d in distractors]
        random.shuffle(options)
        return {
            'mode': 'guess_meaning',
            'question': target.word,
            'options': options,
            'answer': target.explanation,
            'pinyin': target.pinyin,
        }


def similar_idioms(word: str, count: int = 10) -> Dict[str, List[str]]:
    """
    查找与给定成语相关的成语：同首字、同尾字、同首音。
    :param word: 成语
    :param count: 每类最大返回数量
    :return: {'same_head': [...], 'same_tail': [...], 'same_head_pinyin': [...]}
    """
    word = _clean_word(word)
    if not word:
        return {'same_head': [], 'same_tail': [], 'same_head_pinyin': []}

    word_index = get_word_index()
    idiom_obj = word_index.get(word)
    if idiom_obj is None:
        return {'same_head': [], 'same_tail': [], 'same_head_pinyin': []}

    hw_index = get_head_word_index()
    hp_index = get_head_pinyin_index()

    same_head = [i.word for i in hw_index.get(idiom_obj.head_word, [])
                 if i.word != word]
    same_tail = [i.word for i in hw_index.get(idiom_obj.end_word, [])
                 if i.word != word]
    same_hp = [i.word for i in hp_index.get(idiom_obj.head_pinyin, [])
               if i.word != word]

    count = max(count, 1)
    if len(same_head) > count:
        same_head = random.sample(same_head, count)
    if len(same_tail) > count:
        same_tail = random.sample(same_tail, count)
    if len(same_hp) > count:
        same_hp = random.sample(same_hp, count)

    return {
        'same_head': same_head,
        'same_tail': same_tail,
        'same_head_pinyin': same_hp,
    }


# ============================================================
# 统计分析
# ============================================================

def stats() -> Dict[str, Any]:
    """
    返回成语库统计信息。
    :return: 统计字典
    """
    all_idioms = get_all_idioms()
    total = len(all_idioms)
    next_counts = [item.next_count for item in all_idioms]
    lengths = Counter(len(item.word) for item in all_idioms)

    dead_ends = sum(1 for n in next_counts if n == 0)
    max_next = max(next_counts) if next_counts else 0
    avg_next = sum(next_counts) / total if total > 0 else 0

    return {
        'total': total,
        'length_distribution': dict(sorted(lengths.items())),
        'dead_end_count': dead_ends,
        'max_next_count': max_next,
        'avg_next_count': round(avg_next, 2),
    }


def hottest_start_chars(count: int = 10) -> List[Dict[str, Any]]:
    """
    返回最热门的开头字（以该字开头的成语数量最多）。
    :param count: 返回数量
    :return: [{'char': '一', 'count': 380}, ...]
    """
    hw_index = get_head_word_index()
    char_counts = [(char, len(items)) for char, items in hw_index.items()]
    char_counts.sort(key=lambda x: x[1], reverse=True)

    count = min(max(count, 1), len(char_counts))
    return [{'char': c, 'count': n} for c, n in char_counts[:count]]
