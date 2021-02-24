#!/usr/bin/env python3
import argparse
import time
import multiprocessing
import json
import sys
import textwrap
import sys

parser = argparse.ArgumentParser(description='dns permutator')
parser.add_argument('word', type=str, help='word to permutate')
args = parser.parse_args()

def generate_bucket_permutations(keyword):
    permutation_templates = [
        '{keyword}-{permutation}',
        '{permutation}-{keyword}',
        '{keyword}_{permutation}',
        '{permutation}_{keyword}',
        '{keyword}{permutation}',
        '{permutation}{keyword}'
    ]
    with open('./permutations.txt', 'r') as f:
        permutations = f.readlines()
        buckets = []
        for perm in permutations:
            perm = perm.rstrip()
            for template in permutation_templates:
                generated_string = template.replace('{keyword}', keyword).replace('{permutation}', perm)
                buckets.append(generated_string)

    buckets.append(keyword)
    buckets.append('{}.com'.format(keyword))
    buckets.append('{}.net'.format(keyword))
    buckets.append('{}.org'.format(keyword))
    buckets = list(set(buckets))

    # Strip any guesses less than 3 characters or more than 63 characters
    for bucket in buckets:
        if len(bucket) < 3 or len(bucket) > 63:
            del buckets[bucket]

    print('\nGenerated {} bucket permutations.\n'.format(len(buckets)))
    return buckets


for line in generate_bucket_permutations(args.word):
    print(line)