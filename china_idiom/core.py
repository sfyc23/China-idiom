# -*- coding: utf-8 -*-
"""
Project: China-idiom
Creator: DoubleThunder
Create time: 2019-10-12 11:45
Introduction:
"""
import re
import pandas as pd
from china_idiom.constants import (
    idiom_df, clean_complie
)

__all__ = [
    'is_idiom', 'is_idiom_solitaire',
    'next_idioms_solitaire', 'auto_idioms_solitaire', 'search_idiom'
]


def multiple_replace(dict_, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict_.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict_[mo.string[mo.start():mo.end()]], text)


def is_idiom(word):
    """
    判断一个词是否是成语
    :param word: str,成语
    :return: bool, True，是成语。False，不是成语。
    """
    word = re.sub(clean_complie, '', word)  # 清除非中文的符号
    num = idiom_df[idiom_df['word'] == word].shape[0]
    if num > 0:
        return True
    return False


# 是否是下一个成语
def is_idiom_solitaire(before_word, after_word):
    """
    判断前一个成语与后一个成语是否可连接（用于成语接龙）
    :param before_word: str,前一个成语
    :param after_word: str,后一个成语
    :return: bool
    """
    before_word = re.sub(clean_complie, '', before_word)
    after_word = re.sub(clean_complie, '', after_word)
    bwdf = idiom_df[idiom_df['word'] == before_word]
    if not bwdf.shape[0]:
        return False

    awdf = idiom_df[idiom_df['word'] == after_word]
    if not awdf.shape[0]:
        return False
    b_ser, a_ser = bwdf.iloc[0], awdf.iloc[0]

    if b_ser['end_word'] == a_ser['head_word'] or b_ser['end_pinyin'] == a_ser['head_pinyin']:
        return True
    return False


def next_idioms_solitaire(word, count=1, heteronym=True, smaller=False):
    """
    :param word: str, 成语
    :param count: int, 返回数量。默认为 1。
    :param heteronym: bool,是否可以使用同音字。默认为 True。
    :param smaller: bool, 是否选择尽可能的少的后续（为了让别人更难接）。默认为 False。
    :return: list
    """
    # 确保 count 值有意义
    count = count if count > 1 else 1

    result_list = []

    word = re.sub(clean_complie, '', word)  # 清除非中文的字符
    wdf = idiom_df[idiom_df['word'] == word]  # 查詢此成語是否存在。如果不存在則直接返回空
    if wdf.shape[0] == 0:
        return result_list

    single_ser = wdf.iloc[0]
    end_word, end_pinyin = single_ser['end_word'], single_ser['end_pinyin']

    dfw = idiom_df[idiom_df['head_word'] == end_word]
    if heteronym:
        dfp = idiom_df[idiom_df['head_pinyin'] == end_pinyin]
        # 合并两种结果的数据，非清除重复项
        dfw = pd.concat([dfw, dfp]).drop_duplicates('word').reset_index(drop=True)

    w_count = dfw.shape[0]
    # 獲取數據不能大於數值的最大值
    if w_count == 0:
        return result_list
    count = count if count < w_count else w_count
    if smaller:
        # 對數組進行排列
        dfw = dfw.sort_values(['next_count'])
        return dfw[:count]['word'].tolist()
    else:
        return dfw.sample(n=count)['word'].tolist()

    return result_list


def auto_idioms_solitaire(word='', max_count=10, heteronym=True):
    """
    自动接龙模式 - 输入一个汉字或者成语，程序自动输出一组成语接龙的结果。
    :param word: str 起始汉字或者成语，用输入''
    :param max_count: int, 最大长度。默认为：10 条
    :param heteronym: bool, 是否可以用同音字。默认为 True
    :return: list
    """
    result_list = []

    word = re.sub(clean_complie, '', word)  # 清除非中文的字符

    wdf = idiom_df[idiom_df['word'].str.contains(r'^{}'.format(word), regex=True)]  # 查詢此成語是否存在。如果不存在則直接返回空
    if wdf.shape[0] == 0:
        return result_list

    word = wdf.iloc[0].word
    result_list.append(word)
    for _ in range(max_count - 1):
        nis = next_idioms_solitaire(word, heteronym=heteronym)
        if nis:
            word = nis[0]
            result_list.append(word)
        # 没有后续，则跳出循环
        else:
            break
    return result_list


def search_idiom(word, position=0, count=1, is_detail=False):
    """
    搜索查找成语。
    :param word: str,关键词
    :param position: int, 所在位置，默认为：0
    :param count: int ，返回最大数量 默认为： 1
    :param is_detail: bool,是否返回详细内容（包括：拼音，拼音缩写，解释，来源，造句）
    :return: list。
    """
    if position > 0:
        check_complie = r'^.{{{position}}}{word}.*'.format(word=word, position=position - 1)
        rdf = idiom_df[idiom_df['word'].str.contains(check_complie, regex=True)]
    else:
        rdf = idiom_df[idiom_df['word'].str.contains(word, regex=False)]

    length = rdf.shape[0]
    count = count if count > 0 else 1
    count = count if count < length else length

    if not is_detail:
        return rdf.sample(n=count)['word'].tolist()
    else:
        return rdf.sample(n=count)[['word', 'pinyin', 'abbreviation', 'explanation', 'derivation', 'example']].to_dict(
            'records')

    # contains(self, pat, case=True, flags=0, na=nan, regex=True)
