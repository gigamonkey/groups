#!/usr/bin/env python

from itertools import combinations
from dataclasses import dataclass


@dataclass
class Score:
    pairs: int = 0
    meetings: int = 0
    missed: int = 0

    @property
    def score(self):
        return (self.meetings / self.pairs) + self.missed

    def __str__(self):
        s = f"{self.meetings} meetings for {self.pairs} pairs;"
        if self.missed > 0:
            s += f" missed: {self.missed};"
        s += f" score: {self.score}"
        return s


def pairs(xs):
    return {frozenset(p) for p in combinations(xs, 2)}


def score(groups, people):
    """
    Ratio of actual meetings to the minimal set where every pair meets
    exactly once plus a large penalty for any pair that doesn't meet
    at all.
    """
    all_pairs = pairs(people)
    meetings = [p for g in groups for p in pairs(g)]
    return Score(len(all_pairs), len(meetings), len(all_pairs - set(meetings)))
