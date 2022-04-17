import os
from datetime import date
import pytest

from result import Result
from util import Util
from wordlesolver import WordleSolver


class MockBrowserWrapper:
    def __init__(self, target_word):
        self.target_word = target_word

    def submit_word(self, word, _):

        result = []
        for idx, val in enumerate(word):
            if val == self.target_word[idx]:
                result.append(Result.CORRECT)
            elif val in self.target_word:
                result.append(Result.PRESENT)
            else:
                result.append(Result.ABSENT)
        return result

    def save_game_summary(self):
        pass


class TestWordleSolver:

    @pytest.mark.parametrize("target_word,will_solve", [
        ("cheek", True),
    ])
    def test_simple_case(self, target_word, will_solve):
        mb = MockBrowserWrapper(target_word)

        app_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = f"{app_dir}/logs/{date.today().strftime('%Y-%m-%d')}"
        util = Util()

        s = WordleSolver(output_dir, mb, util)
        result, time_to_solve = s.solve_wordle()

        assert result is will_solve
