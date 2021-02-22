#!/usr/bin/env python

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from random import shuffle


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


def check(groups, people):
    """
    Check that everyone meets everyone else and print out the overall
    score.
    """

    num_groups = defaultdict(int)
    counts = defaultdict(lambda: defaultdict(int))
    met = defaultdict(set)

    for g in groups:
        for p in g:
            num_groups[p] += 1
            for x in g:
                counts[p][x] += 1
            met[p].update(g)

    assert all(v == people for v in met.values())
    print(score(groups, people))


def shuffled(xs):
    copy = xs[:]
    shuffle(copy)
    return copy
