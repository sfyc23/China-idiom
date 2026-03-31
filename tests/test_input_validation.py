# -*- coding: utf-8 -*-
import pytest
import china_idiom as idiom


class TestInputValidation:
    """输入校验边界测试"""

    def test_is_idiom_type_error(self):
        with pytest.raises(TypeError):
            idiom.is_idiom(123)

    def test_is_idiom_none(self):
        with pytest.raises(TypeError):
            idiom.is_idiom(None)

    def test_search_type_error(self):
        with pytest.raises(TypeError):
            idiom.search_idiom(word=123)

    def test_next_solitaire_type_error(self):
        with pytest.raises(TypeError):
            idiom.next_idioms_solitaire(123)

    def test_auto_solitaire_type_error(self):
        with pytest.raises(TypeError):
            idiom.auto_idioms_solitaire(123)

    def test_is_solitaire_type_error(self):
        with pytest.raises(TypeError):
            idiom.is_idiom_solitaire(123, '一心一意')

    def test_sample_returns_string(self):
        result = idiom.sample()
        assert isinstance(result, str)
        assert len(result) >= 2
