# -*- coding: utf-8 -*-
import pytest
import china_idiom as idiom


class TestGenerateFillBlank:

    def test_default(self):
        result = idiom.generate_fill_blank()
        assert result['puzzle_type'] == 'fill_blank'
        assert result['difficulty'] == 'medium'
        assert len(result['blanks']) == 2
        assert len(result['display']) == len(result['word'])
        assert result['total_blanks'] == 2

    def test_easy(self):
        result = idiom.generate_fill_blank(difficulty='easy')
        assert result['difficulty'] == 'easy'
        assert len(result['blanks']) == 1

    def test_hard(self):
        result = idiom.generate_fill_blank(difficulty='hard')
        assert result['difficulty'] == 'hard'
        assert len(result['blanks']) == 3

    def test_specified_word(self):
        result = idiom.generate_fill_blank(word='一心一意')
        assert result['word'] == '一心一意'
        assert idiom.is_idiom(result['word'])

    def test_display_has_blanks(self):
        result = idiom.generate_fill_blank(difficulty='medium')
        blank_count = sum(1 for c in result['display'] if c == '□')
        assert blank_count == len(result['blanks'])

    def test_blanks_have_correct_answer(self):
        result = idiom.generate_fill_blank(word='一心一意')
        word = result['word']
        for blank in result['blanks']:
            pos = blank['position']
            assert blank['answer'] == word[pos]

    def test_invalid_word_raises(self):
        with pytest.raises(ValueError):
            idiom.generate_fill_blank(word='不存在的词语')

    def test_invalid_difficulty_fallback(self):
        result = idiom.generate_fill_blank(difficulty='invalid')
        assert result['difficulty'] == 'medium'

    def test_has_puzzle_id(self):
        result = idiom.generate_fill_blank()
        assert result['puzzle_id'].startswith('fb_')

    def test_has_pinyin_and_explanation(self):
        result = idiom.generate_fill_blank()
        assert 'pinyin' in result and result['pinyin']
        assert 'explanation' in result and result['explanation']


class TestGenerateCrossword:

    def test_small(self):
        result = idiom.generate_crossword(size='small')
        assert result['puzzle_type'] == 'crossword'
        assert len(result['idioms']) >= 2
        assert result['grid']['rows'] > 0
        assert result['grid']['cols'] > 0
        assert len(result['grid']['cells']) > 0

    def test_has_hidden_cells(self):
        result = idiom.generate_crossword(size='small', difficulty='medium')
        hidden = [c for c in result['grid']['cells'] if not c['visible']]
        assert len(hidden) > 0
        assert result['total_blanks'] == len(hidden)

    def test_seed_word(self):
        result = idiom.generate_crossword(seed_word='一心一意')
        words = [i['word'] for i in result['idioms']]
        assert '一心一意' in words

    def test_invalid_seed_raises(self):
        with pytest.raises(ValueError):
            idiom.generate_crossword(seed_word='不存在词')

    def test_cells_have_required_fields(self):
        result = idiom.generate_crossword(size='small')
        for cell in result['grid']['cells']:
            assert 'row' in cell
            assert 'col' in cell
            assert 'char' in cell
            assert 'visible' in cell
            assert 'idiom_ids' in cell

    def test_idioms_have_required_fields(self):
        result = idiom.generate_crossword(size='small')
        for entry in result['idioms']:
            assert 'idiom_id' in entry
            assert 'word' in entry
            assert 'direction' in entry
            assert entry['direction'] in ('horizontal', 'vertical')
            assert 'start' in entry
            assert 'pinyin' in entry

    def test_each_idiom_has_visible_cell(self):
        result = idiom.generate_crossword(size='small', difficulty='hard')
        cells_by_idiom = {}
        for cell in result['grid']['cells']:
            for iid in cell['idiom_ids']:
                cells_by_idiom.setdefault(iid, []).append(cell)
        for iid, cells in cells_by_idiom.items():
            visible = [c for c in cells if c['visible']]
            assert len(visible) >= 1, f"成语 {iid} 没有可见字"


class TestGenerateChainFill:

    def test_default(self):
        result = idiom.generate_chain_fill()
        assert result['puzzle_type'] == 'chain_fill'
        assert len(result['chain']) >= 2
        assert result['total_blanks'] > 0

    def test_chain_length(self):
        result = idiom.generate_chain_fill(chain_length=3)
        assert len(result['chain']) >= 2

    def test_easy_preserves_link_chars(self):
        result = idiom.generate_chain_fill(difficulty='easy', chain_length=3)
        chain = result['chain']
        for i in range(len(chain) - 1):
            current = chain[i]
            nxt = chain[i + 1]
            last_char = current['word'][-1]
            first_display = nxt['display'][0]
            assert first_display != '□' or result['heteronym'], \
                f"easy 模式下衔接字应可见: {current['word']} -> {nxt['word']}"

    def test_chain_items_have_blanks(self):
        result = idiom.generate_chain_fill(difficulty='medium')
        for item in result['chain']:
            assert 'blanks' in item
            assert 'display' in item
            assert 'word' in item
            blank_count = sum(1 for c in item['display'] if c == '□')
            assert blank_count == len(item['blanks'])

    def test_hard_hides_most(self):
        result = idiom.generate_chain_fill(difficulty='hard', chain_length=3)
        for item in result['chain']:
            visible = [c for c in item['display'] if c != '□']
            assert len(visible) <= 2


class TestGenerateClueFill:

    def test_default(self):
        result = idiom.generate_clue_fill()
        assert result['puzzle_type'] == 'clue_fill'
        assert len(result['questions']) == 1

    def test_multiple_questions(self):
        result = idiom.generate_clue_fill(count=3)
        assert len(result['questions']) == 3

    def test_easy_shows_most_chars(self):
        result = idiom.generate_clue_fill(difficulty='easy')
        q = result['questions'][0]
        visible = [c for c in q['display'] if c != '□']
        assert len(visible) >= len(q['word']) - 1

    def test_has_clue(self):
        result = idiom.generate_clue_fill()
        for q in result['questions']:
            assert 'clue' in q and q['clue']

    def test_hard_truncates_clue(self):
        result = idiom.generate_clue_fill(difficulty='hard')
        q = result['questions'][0]
        if len(q['clue']) > 12:
            assert q['clue'].endswith('……')

    def test_has_derivation(self):
        result = idiom.generate_clue_fill()
        for q in result['questions']:
            assert 'derivation' in q


class TestVerifyFillAnswer:

    def test_correct_fill_blank(self):
        puzzle = idiom.generate_fill_blank(word='一心一意', difficulty='medium')
        answer = {
            'blanks': [{'position': b['position'], 'char': b['answer']}
                       for b in puzzle['blanks']]
        }
        result = idiom.verify_fill_answer('fill_blank', answer, puzzle)
        assert result['correct'] is True
        assert result['score'] == 100

    def test_wrong_fill_blank(self):
        puzzle = idiom.generate_fill_blank(word='一心一意', difficulty='medium')
        answer = {
            'blanks': [{'position': b['position'], 'char': '错'}
                       for b in puzzle['blanks']]
        }
        result = idiom.verify_fill_answer('fill_blank', answer, puzzle)
        assert result['correct'] is False
        assert result['score'] < 100

    def test_partial_correct(self):
        puzzle = idiom.generate_fill_blank(word='一心一意', difficulty='medium')
        blanks = puzzle['blanks']
        answer_blanks = []
        for i, b in enumerate(blanks):
            if i == 0:
                answer_blanks.append({'position': b['position'], 'char': b['answer']})
            else:
                answer_blanks.append({'position': b['position'], 'char': '错'})
        result = idiom.verify_fill_answer(
            'fill_blank', {'blanks': answer_blanks}, puzzle)
        assert result['score'] == 50

    def test_correct_chain_fill(self):
        puzzle = idiom.generate_chain_fill(chain_length=3, difficulty='easy')
        answer_chain = []
        for item in puzzle['chain']:
            answer_chain.append({
                'index': item['index'],
                'blanks': [{'position': b['position'], 'char': b['answer']}
                           for b in item['blanks']],
            })
        result = idiom.verify_fill_answer(
            'chain_fill', {'chain': answer_chain}, puzzle)
        assert result['correct'] is True
        assert result['chain_valid'] is True

    def test_correct_clue_fill(self):
        puzzle = idiom.generate_clue_fill(difficulty='medium', count=1)
        answer_questions = []
        for q in puzzle['questions']:
            answer_questions.append({
                'blanks': [{'position': b['position'], 'char': b['answer']}
                           for b in q['blanks']],
            })
        result = idiom.verify_fill_answer(
            'clue_fill', {'questions': answer_questions}, puzzle)
        assert result['correct'] is True
        assert result['score'] == 100

    def test_correct_crossword(self):
        puzzle = idiom.generate_crossword(size='small', difficulty='medium')
        answer_cells = []
        for cell in puzzle['grid']['cells']:
            if not cell['visible']:
                answer_cells.append({
                    'row': cell['row'],
                    'col': cell['col'],
                    'char': cell['char'],
                })
        result = idiom.verify_fill_answer(
            'crossword', {'cells': answer_cells}, puzzle)
        assert result['correct'] is True

    def test_unknown_type(self):
        result = idiom.verify_fill_answer('unknown', {}, {})
        assert result['correct'] is False
        assert 'error' in result


class TestGetFillHint:

    def test_level_1_initial(self):
        result = idiom.get_fill_hint('一心一意', position=1, hint_level=1)
        assert result['hint_type'] == 'initial'
        assert result['content'] == 'x'
        assert result['penalty'] == 0.1

    def test_level_2_pinyin(self):
        result = idiom.get_fill_hint('一心一意', position=1, hint_level=2)
        assert result['hint_type'] == 'pinyin'
        assert 'xīn' in result['content']

    def test_level_3_explanation(self):
        result = idiom.get_fill_hint('一心一意', position=1, hint_level=3)
        assert result['hint_type'] == 'explanation'
        assert result['content']

    def test_level_4_reveal(self):
        result = idiom.get_fill_hint('一心一意', position=1, hint_level=4)
        assert result['hint_type'] == 'reveal'
        assert result['content'] == '心'

    def test_invalid_word_raises(self):
        with pytest.raises(ValueError):
            idiom.get_fill_hint('不存在词', position=0, hint_level=1)

    def test_invalid_position_raises(self):
        with pytest.raises(ValueError):
            idiom.get_fill_hint('一心一意', position=10, hint_level=1)

    def test_level_clamped(self):
        result = idiom.get_fill_hint('一心一意', position=0, hint_level=0)
        assert result['hint_type'] == 'initial'
        result = idiom.get_fill_hint('一心一意', position=0, hint_level=99)
        assert result['hint_type'] == 'reveal'


class TestGenerateFillGameSet:

    def test_default(self):
        result = idiom.generate_fill_game_set(total_questions=5)
        assert 'game_id' in result
        assert result['total_questions'] == 5
        assert len(result['questions']) == 5

    def test_difficulty(self):
        result = idiom.generate_fill_game_set(total_questions=3, difficulty='easy')
        assert result['difficulty'] == 'easy'

    def test_specific_types(self):
        result = idiom.generate_fill_game_set(
            total_questions=3, types=['fill_blank', 'clue_fill'])
        for q in result['questions']:
            assert q['type'] in ('fill_blank', 'clue_fill')

    def test_scoring_info(self):
        result = idiom.generate_fill_game_set(total_questions=1)
        assert 'scoring' in result
        assert result['scoring']['per_blank'] == 10
        assert result['scoring']['time_bonus'] is True
        assert len(result['scoring']['hint_penalty']) == 4

    def test_each_question_has_data(self):
        result = idiom.generate_fill_game_set(total_questions=3)
        for q in result['questions']:
            assert 'type' in q
            assert 'data' in q
            assert q['data'] is not None

    def test_game_id_format(self):
        result = idiom.generate_fill_game_set(total_questions=1)
        assert result['game_id'].startswith('game_')
