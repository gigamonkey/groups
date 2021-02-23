#!/usr/bin/env python

"Group people so everyone meets everyone."

import sys
from argparse import ArgumentParser
from argparse import FileType
from collections import defaultdict
from itertools import combinations
from math import ceil
from random import choice


def pairs(xs):
    return {frozenset(p) for p in combinations(xs, 2)}


def previous_meetings(met, group):
    return lambda pair: sum(p in met[g] for p in (pair - group) for g in group)


def not_present(g):
    return lambda p: len(p - g) > 0


def one_new(g):
    return lambda p: len(p - g) == 1


def random_person(people, g):
    return choice(list(people - g))


def make_group(pairs, people, met, n):
    g = set()
    to_add = n
    while to_add > 0:
        candidates = filter(not_present(g) if to_add > 1 else one_new(g), pairs)
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


def check(groups, people):
    """
    Check that everyone meets everyone else and print out the overall
    score.
    """

    p = len(people)
    n = len(groups[0])
    ideal = int(ceil((p - 1) / (n - 1)) * (p / n))

    print(f"{len(groups)} groups. {len(groups)/ideal:.0%} of ideal of {ideal:d}")

    met = defaultdict(set)

    for g in groups:
        for p in g:
            met[p].update(g)

    assert all(v == people for v in met.values())


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
