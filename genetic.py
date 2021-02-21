#!/usr/bin/env python

# Genome: sequence of permutations of the people list.

# Fitness: Treat each permutation as a list of the complete groups.
# (E.g. if we're making groups of 4 out of a list of 25 people, each
# permutation will yield 6 groups with one person left over.) Count
# the number of times each pair meets across all the groups.
# Substantial demerits for any pairs that don't meet at all. Lesser
# demerits for extra meetings.

# Cross at the permutations joints. Mutate by swapping elements within
# a permutation.


from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import ceil
from math import floor
from random import choices
from random import random
from random import randrange
from random import shuffle
import json
import sys


population_size = 1_000
mutation_probability = 0.01
overlap = 0.10
children_per_pair = 4


@dataclass
class Fitness:
    exact: int = 0
    missing: int = 0
    extra: int = 0

    @property
    def fitness(self):
        return self.exact - (100 * self.missing) - self.extra

def shuffled(xs):
    copy = xs[:]
    shuffle(copy)
    return copy


def random_dna(people, n, multiple=5):
    length = multiple * ceil((len(people) - 1) / (n - 1))
    return [shuffled(people) for _ in range(length)]


def extract_pairs(dna, n):
    for g in extract_groups(dna, n):
        yield from pairs(g)

def extract_groups(dna, n):
    if dna:
        end = len(dna[0]) - (len(dna[0]) % n)
        for g in dna:
            yield from (g[i:i+n] for i in range(0, end, n))


def pairs(xs):
    return {frozenset(p) for p in combinations(xs, 2)}


def fitness(dna, n):
    counts = Counter(extract_pairs(dna, n))
    f = Fitness()
    for p in pairs(dna[0]):
        c = counts[p]
        if c == 1:
            f.exact += 1
        elif c == 0:
            f.missing += 1
        else:
            #print(f"{p} met {c} times")
            f.extra += (c - 1)
    return f

def cross(dna1, dna2):
    g1 = random_genes(dna1)
    g2 = random_genes(dna2)
    return [mutated(g) for g in g1 + g2]

def mutated(g):
    g = g[:]
    if random() < mutation_probability:
        i = randrange(len(g))
        j = randrange(len(g))
        g[i], g[j] = g[j], g[i]
    return g


def random_genes(dna):
    return shuffled(dna)[:ceil(len(dna) * (0.25 + (random() * 0.5)))]


def show_fitness(dna, n):
    f = fitness(dna, n)
    print(f"{f.fitness} ({f})")


def population(people, n, size=population_size):
    return [random_dna(people, n) for _ in range(size)]

def best_worst(pop, n):
    key = lambda o: fitness(o, n).fitness
    best = max(pop, key=key)
    worst = min(pop, key=key)
    best_f = fitness(best, n)
    worst_f = fitness(worst, n)
    print(f"best: {best_f} => {best_f.fitness}; worst: {worst_f} => {worst_f.fitness}")



def next_generation(pop, n):
    by_fitness = sorted(pop, key=lambda x: fitness(x, n).fitness, reverse=True)

    num_survivors = floor(len(pop) * overlap)

    newgen = by_fitness[:num_survivors]

    for i in range(0, len(pop), 2):
        mom, dad = by_fitness[i:i+2]
        for _ in range(children_per_pair):
            newgen.append(cross(mom, dad))
            if len(newgen) == len(pop):
                return newgen


if __name__ == "__main__":

    people = list("abcdefghijklmnopqrstuvwxyz")

    N = 4
    pop = population(people, N)


    for _ in range(1000):
        best_worst(pop, N)
        pop = next_generation(pop, N)
