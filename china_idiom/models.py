# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Idiom:
    """成语数据模型"""
    word: str
    pinyin: str
    abbreviation: str
    explanation: str
    derivation: str
    example: str
    head_pinyin: str
    end_pinyin: str
    head_word: str
    end_word: str
    next_count: int
    letter: str
