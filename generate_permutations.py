#!/usr/bin/env python3

import os

import argparse

parser = argparse.ArgumentParser(description='dns permutator')
parser.add_argument('word', type=str, help='word to permutate')
args = parser.parse_args()

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
PERMITATIONS_FILE_PATH = f'{WORKING_DIR}/permutations.txt'
LIST_FILE_PATH = f'{WORKING_DIR}/list.txt'


def generate_bucket_permutations(keyword):
    permutation_templates = [
        '{keyword}-{permutation}',
        '{permutation}-{keyword}',
        '{keyword}_{permutation}',
        '{permutation}_{keyword}',
        '{keyword}{permutation}',
        '{permutation}{keyword}'
    ]
    with open(PERMITATIONS_FILE_PATH, 'r') as f:
        buckets = {f'{keyword}', f'{keyword}.com', f'{keyword}.net', f'{keyword}.org', }
        for perm in f:
            perm = perm.rstrip()
            for template in permutation_templates:
                generated_string = template.replace('{keyword}', keyword).replace('{permutation}', perm)
                if len(generated_string) < 3 or len(generated_string) > 63:
                    continue
                buckets.add(generated_string)
                
    with open(LIST_FILE_PATH, 'a') as f:
        for line in buckets:
            f.write(line + '\n')
            
    return buckets


if __name__ == '__main__':
    generate_bucket_permutations(args.word)
