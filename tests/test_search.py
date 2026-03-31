# -*- coding: utf-8 -*-
import china_idiom as idiom


class TestSearchIdiom:
    """search_idiom 关键词搜索、位置搜索、详情模式测试"""

    def test_search_basic(self):
        result = idiom.search_idiom(word='心')
        assert len(result) == 1
        assert isinstance(result[0], str)
        assert '心' in result[0]

    def test_search_count(self):
        result = idiom.search_idiom(word='心', count=5)
        assert len(result) <= 5
        for w in result:
            assert '心' in w

    def test_search_position(self):
        """position=2 表示第 2 个字"""
        result = idiom.search_idiom(word='心', position=2, count=3)
        for w in result:
            assert len(w) >= 2
            assert w[1] == '心'

    def test_search_detail(self):
        result = idiom.search_idiom(word='心', count=1, is_detail=True)
        assert len(result) == 1
        item = result[0]
        assert 'word' in item
        assert 'pinyin' in item
        assert 'explanation' in item

    def test_search_no_match(self):
        result = idiom.search_idiom(word='啊啊啊啊啊')
        assert result == []

    def test_search_empty(self):
        result = idiom.search_idiom(word='')
        assert result == []
