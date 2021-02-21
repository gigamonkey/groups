#!/usr/bin/env python

"Group people so everyone meets everyone."

import sys
from argparse import ArgumentParser, FileType
from collections import defaultdict
from itertools import combinations
from random import choice

from score import score


def make_pairs(people):
    return {frozenset(p) for p in combinations(people, 2)}


def next_pair(pairs, fn):
    return next(filter(fn, pairs), None)


def disjoint(g):
    return lambda p: not (p & g)


def overlapping(g):
    return lambda p: len(p & g) == 1


def random_person(people, g):
    return {choice(list(people - g))}


def make_group(pairs, people, n):
    g = set()
    while n > 0:
        to_add = (
            (next_pair(pairs, disjoint(g)) if n > 1 else None)
            or next_pair(pairs, overlapping(g))
            or random_person(people, g)
        )
        n -= len(to_add)
        g.update(to_add)

    return tuple(sorted(g))


def groups(people, size):
    pairs = make_pairs(people)

    while pairs:
        g = make_group(pairs, people, size)
        pairs -= make_pairs(g)
        yield g


def check(groups, people):

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
    print(score(gs, people))

    for g in gs:
        print(g)
