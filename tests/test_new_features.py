# -*- coding: utf-8 -*-
import pytest
import china_idiom as idiom


class TestGetIdiomInfo:

    def test_existing(self):
        info = idiom.get_idiom_info('一心一意')
        assert info is not None
        assert info['word'] == '一心一意'
        assert 'pinyin' in info
        assert 'explanation' in info
        assert 'head_word' in info
        assert 'end_word' in info
        assert 'next_count' in info

    def test_not_found(self):
        assert idiom.get_idiom_info('不存在词') is None

    def test_empty(self):
        assert idiom.get_idiom_info('') is None

    def test_type_error(self):
        with pytest.raises(TypeError):
            idiom.get_idiom_info(123)


class TestGetDifficulty:

    def test_existing(self):
        d = idiom.get_difficulty('一心一意')
        assert isinstance(d, int)
        assert d >= 0

    def test_not_found(self):
        assert idiom.get_difficulty('不存在词') == -1

    def test_empty(self):
        assert idiom.get_difficulty('') == -1


class TestValidateChain:

    def test_valid_chain(self):
        chain = idiom.auto_idioms_solitaire('一心一意', max_count=5)
        if len(chain) > 1:
            result = idiom.validate_solitaire_chain(chain)
            assert result['valid'] is True
            assert result['errors'] == []

    def test_invalid_word(self):
        result = idiom.validate_solitaire_chain(['一心一意', '不存在词'])
        assert result['valid'] is False
        assert len(result['errors']) > 0

    def test_broken_link(self):
        result = idiom.validate_solitaire_chain(['一心一意', '风和日丽'])
        assert result['valid'] is False

    def test_duplicate(self):
        result = idiom.validate_solitaire_chain(['一心一意', '一心一意'])
        assert result['valid'] is False

    def test_empty_chain(self):
        result = idiom.validate_solitaire_chain([])
        assert result['valid'] is False


class TestLongestChain:

    def test_basic(self):
        chain = idiom.longest_solitaire_chain('一心一意', max_depth=15)
        assert isinstance(chain, list)
        assert len(chain) >= 1
        assert chain[0] == '一心一意'

    def test_no_duplicates(self):
        chain = idiom.longest_solitaire_chain('一心一意', max_depth=20)
        assert len(chain) == len(set(chain))

    def test_not_found(self):
        assert idiom.longest_solitaire_chain('不存在的') == []

    def test_empty(self):
        assert idiom.longest_solitaire_chain('') == []


class TestDeadEndIdioms:

    def test_basic(self):
        result = idiom.dead_end_idioms(count=5)
        assert isinstance(result, list)
        assert len(result) <= 5
        for item in result:
            assert item['next_count'] == 0

    def test_all_are_idioms(self):
        result = idiom.dead_end_idioms(count=3)
        for item in result:
            assert idiom.is_idiom(item['word'])


class TestCounterAttack:

    def test_basic(self):
        result = idiom.counter_attack('一心一意')
        assert result is not None
        assert isinstance(result, str)
        assert idiom.is_idiom(result)
        assert idiom.is_idiom_solitaire('一心一意', result)

    def test_not_found(self):
        assert idiom.counter_attack('不存在词') is None

    def test_empty(self):
        assert idiom.counter_attack('') is None


class TestSolitaireBattle:

    def test_basic(self):
        result = idiom.solitaire_battle('一心一意', '一生一世')
        assert 'word1' in result
        assert 'word2' in result
        assert 'winner' in result
        assert result['word1']['exists'] is True
        assert result['word2']['exists'] is True

    def test_nonexistent(self):
        result = idiom.solitaire_battle('一心一意', '不存在词')
        assert result['winner'] is None


class TestSearchByPinyin:

    def test_basic(self):
        result = idiom.search_by_pinyin('yxyy')
        assert isinstance(result, list)
        assert len(result) >= 1
        assert '一心一意' in result

    def test_empty(self):
        assert idiom.search_by_pinyin('') == []

    def test_no_match(self):
        assert idiom.search_by_pinyin('zzzzzzzz') == []

    def test_type_error(self):
        with pytest.raises(TypeError):
            idiom.search_by_pinyin(123)


class TestSearchByLength:

    def test_four_chars(self):
        result = idiom.search_by_length(4, count=5)
        assert isinstance(result, list)
        for w in result:
            assert len(w) == 4

    def test_five_chars(self):
        result = idiom.search_by_length(5, count=5)
        for w in result:
            assert len(w) == 5

    def test_no_match(self):
        result = idiom.search_by_length(100)
        assert result == []


class TestRandomQuiz:

    def test_guess_word(self):
        q = idiom.random_quiz(mode='guess_word')
        assert q['mode'] == 'guess_word'
        assert 'question' in q
        assert 'options' in q
        assert 'answer' in q
        assert len(q['options']) == 4
        assert q['answer'] in q['options']

    def test_guess_meaning(self):
        q = idiom.random_quiz(mode='guess_meaning')
        assert q['mode'] == 'guess_meaning'
        assert idiom.is_idiom(q['question'])
        assert len(q['options']) == 4
        assert q['answer'] in q['options']


class TestSimilarIdioms:

    def test_basic(self):
        result = idiom.similar_idioms('一心一意')
        assert 'same_head' in result
        assert 'same_tail' in result
        assert 'same_head_pinyin' in result
        assert isinstance(result['same_head'], list)

    def test_not_found(self):
        result = idiom.similar_idioms('不存在词')
        assert result == {'same_head': [], 'same_tail': [], 'same_head_pinyin': []}


class TestStats:

    def test_basic(self):
        s = idiom.stats()
        assert s['total'] > 0
        assert 'length_distribution' in s
        assert 'dead_end_count' in s
        assert 'max_next_count' in s
        assert 'avg_next_count' in s
        assert 4 in s['length_distribution']


class TestHottestStartChars:

    def test_basic(self):
        result = idiom.hottest_start_chars(count=5)
        assert isinstance(result, list)
        assert len(result) == 5
        for item in result:
            assert 'char' in item
            assert 'count' in item
            assert item['count'] > 0

    def test_ordered(self):
        result = idiom.hottest_start_chars(count=10)
        counts = [item['count'] for item in result]
        assert counts == sorted(counts, reverse=True)
