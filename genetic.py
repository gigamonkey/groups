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


from itertools import combinations
from math import ceil
from math import floor
from random import random
from random import randrange
from random import shuffle

from util import score

population_size = 1_000
mutation_probability = 0.01
overlap = 0.10
children_per_pair = 4


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
            yield from (g[i : i + n] for i in range(0, end, n))


def pairs(xs):
    return {frozenset(p) for p in combinations(xs, 2)}


def fitness(dna, n):
    return score(list(extract_groups(dna, n)), dna[0])


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
    return shuffled(dna)[: ceil(len(dna) * (0.25 + (random() * 0.5)))]


def show_fitness(dna, n):
    print(fitness(dna, n))


def population(people, n, size=population_size):
    return [random_dna(people, n) for _ in range(size)]


def best_worst(pop, n):
    key = lambda o: fitness(o, n).score
    best = min(pop, key=key)
    worst = max(pop, key=key)
    print(f"best: {fitness(best, n)}; worst: {fitness(worst, n)}")


def next_generation(pop, n):
    by_fitness = sorted(pop, key=lambda x: fitness(x, n).score)

    num_survivors = floor(len(pop) * overlap)

    newgen = by_fitness[:num_survivors]

    for i in range(0, len(pop), 2):
        mom, dad = by_fitness[i : i + 2]
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
