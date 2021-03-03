#!/usr/bin/env python3
import argparse

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
    with open('permutations.txt', 'r') as f:
        buckets = {f'{keyword}', f'{keyword}.com', f'{keyword}.net', f'{keyword}.org', }
        for perm in f:
            perm = perm.rstrip()
            for template in permutation_templates:
                generated_string = template.replace('{keyword}', keyword).replace('{permutation}', perm)
                if len(generated_string) < 3 or len(generated_string) > 63:
                    continue
                buckets.add(generated_string)
    with open('list.txt', 'a') as f:
        for line in buckets:
            f.write(line + '\n')
    return buckets


if __name__ == '__main__':
    generate_bucket_permutations(args.word)
