#!/usr/bin/env python

"Group people so everyone meets everyone."

import sys
from argparse import ArgumentParser
from argparse import FileType
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from random import choice


def pairs(xs):
    return {frozenset(p) for p in combinations(xs, 2)}


def previous_meetings(met, group):
    return lambda pair: sum(p in met[g] for p in (pair - group) for g in group)


def disjoint(g):
    return lambda p: not (p & g)


def one_new(g):
    return lambda p: len(p - g) == 1


def random_person(people, g):
    return choice(list(people - g))


def make_group(pairs, people, met, n):
    g = set()
    to_add = n
    while to_add > 0:
        candidates = filter(disjoint(g) if to_add > 1 else one_new(g), pairs)
        if p := min(candidates, key=previous_meetings(met, g), default=None):
            g.update(p)
        else:
            g.add(random_person(people, g))
        to_add = n - len(g)
    return tuple(sorted(g))


def groups(people, size):
    to_meet = pairs(people)
    met = defaultdict(set)

    while to_meet:
        g = make_group(to_meet, people, met, size)
        for p in g:
            met[p].update(g)
        to_meet -= pairs(g)
        yield g


#
# Check how we're doing
#


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

    met = defaultdict(set)

    for g in groups:
        for p in g:
            for x in g:
                met[p].update(g)

    assert all(v == people for v in met.values())
    print(score(groups, people))


if __name__ == "__main__":

    p = ArgumentParser(description=__doc__)
    p.add_argument(
        "input",
        nargs="?",
        help="Input containing names. Defaults to standard in.",
        type=FileType("r"),
        default=sys.stdin,
    )
    p.add_argument("--size", help="Group size.", type=int, default=4)
    args = p.parse_args(sys.argv[1:])

    people = {line[:-1] for line in args.input}

    gs = list(groups(people, args.size))

    check(gs, people)

    for g in gs:
        print(g)
