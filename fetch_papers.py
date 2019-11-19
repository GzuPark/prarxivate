import random
import time
import urllib.request

import feedparser

from utils import get_args, pickle_load, safe_pickle_dump


# https://github.com/karpathy/arxiv-sanity-preserver/blob/6ea68b90279ea00b354bb6982918e5415292c887/fetch_papers.py
def encode_feedparser_dict(d):
    if isinstance(d, feedparser.FeedParserDict) or isinstance(d, dict):
        j = {}
        for k in d.keys():
            j[k] = encode_feedparser_dict(d[k])
        return j
    elif isinstance(d, list):
        l = []
        for k in d:
            l.append(encode_feedparser_dict(k))
        return l
    else:
        return d


def parse_arxiv_url(url):
    ix = url.rfind('/')
    idversion = url[ix+1:]
    parts = idversion.split('v')
    assert len(parts) == 2, 'error parsing url' + url
    return parts[0], int(parts[1])


def compare_db(db, new):
    cnt = False
    if not (new['_rawid'] in db):
        db[new['_rawid']] = new
        print('Updated {p} added {t}'.format(
            p=new['published'].encode('utf-8'), t=new['title'].encode('utf-8')
        ))
        cnt = True
    return db, cnt


def fetch(args):
    base_url = 'http://export.arxiv.org/api/query?'
    
    db = pickle_load(args.db_path)
    print("database has {} entries at start".format(len(db)))

    assert args.max_index - args.start_index > 0, 'error index range from {f} to {t}'.format(f=args.start_index, t=args.max_index)
    num_iter = min(args.max_index - args.start_index, args.results_per_iteration)
    num_added_total = 0
    
    for i in range(args.start_index, args.max_index, args.results_per_iteration):
        print("Result {} - {}".format(i, i+num_iter))
        query = 'search_query={q}&sortBy=submittedDate&start={s}&max_results={m}'.format(q=args.search_query, s=i, m=num_iter)
        
        with urllib.request.urlopen(base_url + query) as url:
            resp = url.read()
        parse = feedparser.parse(resp)
        num_added = 0
        
        for e in parse.entries:
            j = encode_feedparser_dict(e)
            
            rawid, version = parse_arxiv_url(j['id'])
            j['_rawid'] = rawid
            j['_version'] = version
            
            
            db, cnt = compare_db(db, j)
            
            if cnt == True:
                num_added += 1
                num_added_total += 1
            
        if len(parse.entries) == 0:
            print('Received no results from arXiv.')
            print(resp)
            break
            
        if num_added == 0:
            print('No more new papers.')
            
        if args.break_on_no_added == 0:
            break
            
        print('Sleeping for {} seconds'.format(args.wait_time))
        time.sleep(args.wait_time + random.uniform(0, 3))
        
    if num_added_total > 0:
        print('Saving database with {n} papers to {p}'.format(n=len(db), p=args.db_path))
        safe_pickle_dump(db, args.db_path)


def main():
    args = get_args()
    fetch(args)


if __name__ == '__main__':
    main()
