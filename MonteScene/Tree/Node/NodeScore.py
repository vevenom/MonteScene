import numpy as np

from ..constants import ScoreModes

class NodeScore(object):
    """
        Class used for tracking Node score.

        Attributes:
            max_score: Max. score
            min_score: Max. score
            score_sum: Sum of scores
    """
    def __init__(self):
        self.max_score = -np.inf
        self.min_score = np.inf
        self.score_sum = 0

    def get_score(self, score_mode):
        if score_mode == ScoreModes.MAX_NODE_SCORE_MODE:
            return self.max_score
        elif score_mode == ScoreModes.AVG_NODE_SCORE_MODE:
            return self.score_sum
        else:
            assert False

    def update_score(self, score):
        if score > self.max_score:
            self.max_score = score
        if score < self.min_score:
            self.min_score = score

        self.score_sum += score