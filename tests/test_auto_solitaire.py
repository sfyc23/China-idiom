# -*- coding: utf-8 -*-
import china_idiom as idiom


class TestAutoSolitaire:
    """auto_idioms_solitaire 自动接龙测试"""

    def test_basic(self):
        result = idiom.auto_idioms_solitaire('一生一世')
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0] == '一生一世'

    def test_max_count(self):
        result = idiom.auto_idioms_solitaire('一生一世', max_count=5)
        assert len(result) <= 5

    def test_no_duplicates(self):
        """自动接龙结果不应有重复（循环检测）"""
        result = idiom.auto_idioms_solitaire('一生一世', max_count=20)
        assert len(result) == len(set(result))

    def test_chain_continuity(self):
        """相邻两个成语应该能接龙"""
        result = idiom.auto_idioms_solitaire('一心一意', max_count=5)
        for i in range(len(result) - 1):
            assert idiom.is_idiom_solitaire(result[i], result[i + 1])

    def test_single_char_start(self):
        result = idiom.auto_idioms_solitaire('龙')
        assert isinstance(result, list)
        if result:
            assert result[0].startswith('龙')

    def test_empty_input(self):
        result = idiom.auto_idioms_solitaire('')
        assert result == []

    def test_no_match(self):
        result = idiom.auto_idioms_solitaire('啊啊啊啊')
        assert result == []
