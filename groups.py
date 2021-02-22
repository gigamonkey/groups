#!/usr/bin/env python

"Group people so everyone meets everyone."

import sys
from argparse import ArgumentParser
from argparse import FileType
from collections import defaultdict
from random import choice

from util import pairs
from util import score


def next_pair(pairs, fn):
    return next(filter(fn, pairs), None)


def disjoint(g):
    return lambda p: not (p & g)


def one_new(g):
    return lambda p: len(p - g) == 1


def random_person(people, g):
    return {choice(list(people - g))}


def make_group(pairs, people, met, n):
    g = set()
    to_add = n
    while to_add > 0:
        already_met = g | {p2 for p in g for p2 in met[p]}
        to_add = (
            (next_pair(pairs, disjoint(already_met)) if to_add > 1 else None)
            or next_pair(pairs, one_new(already_met))
            or (
                next_pair(pairs, disjoint(g))
                if to_add > 1
                else next_pair(pairs, one_new(g))
            )
            or random_person(people, g)
        )
        g.update(to_add)
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

    met = defaultdict(set)

    for g in groups:
        for p in g:
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
