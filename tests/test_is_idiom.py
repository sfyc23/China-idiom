# -*- coding: utf-8 -*-
import pytest
import china_idiom as idiom


class TestIsIdiom:
    """is_idiom 正例、反例、边界值测试"""

    def test_common_idiom(self):
        assert idiom.is_idiom('一心一意') is True

    def test_another_idiom(self):
        assert idiom.is_idiom('一生一世') is True

    def test_not_idiom(self):
        assert idiom.is_idiom('你好世界') is False

    def test_single_char(self):
        assert idiom.is_idiom('一') is False

    def test_empty_string(self):
        assert idiom.is_idiom('') is False

    def test_with_punctuation(self):
        """输入带标点，应自动清洗后判断"""
        assert idiom.is_idiom('一心一意！') is True

    def test_with_spaces(self):
        assert idiom.is_idiom('一心 一意') is True

    def test_non_string_raises(self):
        with pytest.raises(TypeError):
            idiom.is_idiom(123)

    def test_none_raises(self):
        with pytest.raises(TypeError):
            idiom.is_idiom(None)
