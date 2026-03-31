# -*- coding: utf-8 -*-
import csv
import os
import random
from collections import defaultdict
from typing import Dict, List, Optional

from china_idiom.models import Idiom

_current_dir = os.path.abspath(os.path.dirname(__file__))
_csv_path = os.path.join(_current_dir, 'idiom.csv')

_word_index: Optional[Dict[str, Idiom]] = None
_head_word_index: Optional[Dict[str, List[Idiom]]] = None
_head_pinyin_index: Optional[Dict[str, List[Idiom]]] = None
_abbreviation_index: Optional[Dict[str, List[Idiom]]] = None
_all_idioms: Optional[List[Idiom]] = None


def _load():
    """懒加载：首次调用时从 CSV 加载数据并构建索引"""
    global _word_index, _head_word_index, _head_pinyin_index
    global _abbreviation_index, _all_idioms

    if _word_index is not None:
        return

    word_idx: Dict[str, Idiom] = {}
    hw_idx: Dict[str, List[Idiom]] = defaultdict(list)
    hp_idx: Dict[str, List[Idiom]] = defaultdict(list)
    abbr_idx: Dict[str, List[Idiom]] = defaultdict(list)
    all_list: List[Idiom] = []

    with open(_csv_path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                next_count = int(row.get('next_count', 0) or 0)
            except (ValueError, TypeError):
                next_count = 0

            idiom = Idiom(
                word=row.get('word', ''),
                pinyin=row.get('pinyin', ''),
                abbreviation=row.get('abbreviation', ''),
                explanation=row.get('explanation', ''),
                derivation=row.get('derivation', ''),
                example=row.get('example', ''),
                head_pinyin=row.get('head_pinyin', ''),
                end_pinyin=row.get('end_pinyin', ''),
                head_word=row.get('head_word', ''),
                end_word=row.get('end_word', ''),
                next_count=next_count,
                letter=row.get('letter', ''),
            )
            if not idiom.word:
                continue

            word_idx[idiom.word] = idiom
            hw_idx[idiom.head_word].append(idiom)
            hp_idx[idiom.head_pinyin].append(idiom)
            if idiom.abbreviation:
                abbr_idx[idiom.abbreviation].append(idiom)
            all_list.append(idiom)

    _word_index = word_idx
    _head_word_index = dict(hw_idx)
    _head_pinyin_index = dict(hp_idx)
    _abbreviation_index = dict(abbr_idx)
    _all_idioms = all_list


def get_word_index() -> Dict[str, Idiom]:
    _load()
    return _word_index  # type: ignore[return-value]


def get_head_word_index() -> Dict[str, List[Idiom]]:
    _load()
    return _head_word_index  # type: ignore[return-value]


def get_head_pinyin_index() -> Dict[str, List[Idiom]]:
    _load()
    return _head_pinyin_index  # type: ignore[return-value]


def get_abbreviation_index() -> Dict[str, List[Idiom]]:
    _load()
    return _abbreviation_index  # type: ignore[return-value]


def get_all_idioms() -> List[Idiom]:
    _load()
    return _all_idioms  # type: ignore[return-value]


def get_random_idioms(n: int = 1) -> List[Idiom]:
    """从全量成语中随机采样 n 条"""
    all_items = get_all_idioms()
    n = min(n, len(all_items))
    return random.sample(all_items, n)
