from argparse import ArgumentParser
from multiprocessing import Pool
from time import sleep
import requests
import os.path
import json
import sys
from datetime import datetime

def args():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-c', dest='crawl_top', required=False, default=False, type=int, help='Crawl for domains in the top-1m by Alexa. Set how many domains to crawl, for example: 100. Up to 1000000')
    group.add_argument('-l', dest='list', required=False, default=False, help='Path to a file containing the DBs names to be checked. One per file')
    parser.add_argument('-o', dest='fn', required=False, default='results.json', help='Output file name. Default: results.json')
    parser.add_argument('-d', dest='path', required=False, default=False, help="Absolute path to the downloaded HTML file")
    parser.add_argument('-p', dest='process', required=False, default=1, type=int, help='How many processes to execute')
    parser.add_argument('--dnsdumpster', action='store_true', required=False, default=False, help='Use the DNSDumpster API to gather DBs')
    parser.add_argument('--just-v', action='store_true', required=False, default=False, help='Ignore non-vulnerable DBs')
    parser.add_argument('--amass', dest='amass', required=False, default=False, help='Path to the output file of an amass scan ([-o] argument)')
    
    if len(sys.argv) == 1:
        parser.error("No arguments supplied.")
        sys.exit()

    return parser.parse_args()


def clean(domain):
    '''
    Clean the url so they are sutiable to be crawled.
    '''
    if domain.count('http://') == 0:
        url = ('https://{}/.json').format(domain)
    else:
        domain = domain.replace('http', 'https')
        url = ('{}.json').format(domain)
    return url


def worker(url):
    '''
    Main function in charge of the bulk of the crawling, it assess a status to
    each DB depending on the response.
    '''
    sleep(0.2) #a bit of delay to not abuse in excess the servers
    try:
        r = requests.get(url).json()
    except requests.exceptions.RequestException as e:
        print(e)
    
    try:
        now = datetime.now()
        print(now.strftime("%H:%M:%S "), "URL: ", url)
        if 'error' in r.keys():
            if r['error'] == 'Permission denied' and not args_.just_v:
                # print("Protected: {}".format(url))
                return {'status':-2, 'url':url} #successfully protected
            elif r['error'] == '404 Not Found' and not args_.just_v:
                # print("Not found: {}".format(url))
                return {'status':-1, 'url':url} #doesn't exist
            elif r['error'] == "Invalid Firebase database name":
                # print("Invalid Firebase database name: {}".format(url))
                pass
            elif not args_.just_v:
                return {'status':0, 'url':url} #maybe there's a chance for further explotiation
        else:
            print("Potential vulnerable firebase: {}".format(url))
            return {'status':1, 'url':url, 'data':r} #vulnerable
    except AttributeError:
        '''
        Some DBs may just return null
        '''
        if not args_.just_v:
            print("Returned null: {}".format(url))
            return {'status':0, 'url':url}


def load_file():
    '''
    Parse the HTML file with the results of the pentest-tools subdomains scanner.
    '''
    try:
        from bs4 import BeautifulSoup

        with open(args_.path, 'r') as f:
            print('Gathering subdomains through the downloaded file...')
            s = BeautifulSoup(f.read(), 'html.parser')
        
        table = s.find('div', class_='col-xs-12').find('table')
        return [row.find('a')['href'] for row in table.find('tbody').find_all('tr')[:-1]]
    
    except IOError as e:
        raise e

        

if __name__ == '__main__':
    args_ = args()
    if not args_.list:
        dbs = []

        if args_.dnsdumpster:
           dbs.extend(dns_dumpster())

        if args_.path:
            dbs.extend(load_file())

        urls = list(set(map(clean, dbs)))
        if args_.crawl_top:
            urls.extend(tops())

        if args_.amass:
            urls.extend(amass())
        
        print('\nLooting...')
        p = Pool(args_.process)
        loot = [result for result in list(p.map(worker, urls)) if result != None]

    else:
        urls = set()
        with open(args_.list, 'r') as f:
            [urls.add('https://{}.firebaseio.com/.json'.format(line.rstrip())) for line in f]
        
        p = Pool(args_.process)
        loot = [result for result in list(p.map(worker, urls)) if result != None]



    print('Saving results to {}\n'.format(args_.fn))
    with open(args_.fn, 'w') as f:
        json.dump(loot, f)

    l = {'1':0, '0':0, '-1':0, '-2':0}
    for result in loot:
        l[str(result['status'])] += 1

    print('404 DBs:                 {}'.format(l['-2']))
    print('Secure DBs:              {}'.format(l['-1']))
    print('Possible vulnerable DBs: {}'.format(l['0']))
    print('Vulnerable DBs:          {}'.format(l['1']))
