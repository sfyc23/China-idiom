# -*- coding: utf-8 -*-
import china_idiom as idiom


class TestIsSolitaire:
    """is_idiom_solitaire 接龙判断测试"""

    def test_valid_solitaire(self):
        result = idiom.next_idioms_solitaire('一生一世', count=1)
        if result:
            assert idiom.is_idiom_solitaire('一生一世', result[0]) is True

    def test_invalid_solitaire(self):
        assert idiom.is_idiom_solitaire('一生一世', '风和日丽') is False

    def test_not_idiom_before(self):
        assert idiom.is_idiom_solitaire('不存在词', '一心一意') is False

    def test_not_idiom_after(self):
        assert idiom.is_idiom_solitaire('一心一意', '不存在词') is False

    def test_empty_input(self):
        assert idiom.is_idiom_solitaire('', '一心一意') is False


class TestNextSolitaire:
    """next_idioms_solitaire 接龙查找测试"""

    def test_basic(self):
        result = idiom.next_idioms_solitaire('一生一世')
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_count(self):
        result = idiom.next_idioms_solitaire('一生一世', count=3)
        assert len(result) <= 3

    def test_no_heteronym(self):
        result = idiom.next_idioms_solitaire('一生一世', heteronym=False)
        assert isinstance(result, list)

    def test_smaller_strategy(self):
        result = idiom.next_idioms_solitaire('一生一世', count=3, smaller=True)
        assert isinstance(result, list)
        assert len(result) <= 3

    def test_nonexistent_word(self):
        result = idiom.next_idioms_solitaire('不存在的成语')
        assert result == []

    def test_empty_word(self):
        result = idiom.next_idioms_solitaire('')
        assert result == []
