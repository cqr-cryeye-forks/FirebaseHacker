#!/usr/bin/env python3

import os

import json
import asyncio
from datetime import datetime
from argparse import ArgumentParser

import aiohttp

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))


def args():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-l', dest='list', required=False, default='list.txt',
                       help='Path to a file containing the DBs names to be checked. One per file')
    parser.add_argument('-o', dest='fn', required=False, default='results.json',
                        help='Output file name. Default: results.json')

    return parser.parse_args()


async def async_get(client: aiohttp.ClientSession, url):
    try:
        async with client.get(url, verify_ssl=False, timeout=1000) as response:
            print(f'{datetime.now()} Received response with status: {response.status} for url: {url}')
            assert response.status == 200
            data = await response.json()
            if data:
                return {
                    'url': url
                }
    except Exception as e:
        if not isinstance(e, AssertionError):
            print(f'Occurred an error (with url: {url}): {e}')


async def main():
    args_ = args()
    works = []
    loop = asyncio.get_running_loop()
    
    async with aiohttp.ClientSession(loop=loop) as client:
        with open(f'{WORKING_DIR}/{args_.list}', 'r') as f:
            for url in f:
                url = f'https://{url.rstrip()}.firebaseio.com/.json'
                works.append(asyncio.ensure_future(async_get(client, url.strip())))
                
        results = await asyncio.gather(*works)
        results = list(filter(None, results))
        
        with open(f'{WORKING_DIR}/{args_.fn}', 'w') as output_file:
            json.dump(results, output_file, indent=2)


if __name__ == '__main__':
    asyncio.run(main())
