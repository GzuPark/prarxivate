import argparse
import os
import pickle
import tempfile

from contextlib import contextmanager


class Config(object):
    realpath = os.path.dirname(os.path.realpath(__file__))
    db_path = os.path.join(realpath, 'data', 'db.p')
    tmp_dir = os.path.join(realpath, 'tmp')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sq', '--search-query', type=str,
                        default='cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:stat.ML+OR+cat:cs.RO',
                        help='query used for arXiv API. See https://arxiv.org/help/api/user-manual#subject_classifications')
    parser.add_argument('-si', '--start-index', type=int, default=0, help='0 = most recent API result')
    parser.add_argument('-mi', '--max-index', type=int, default=10000, help='upper bound on paper index we will fetch')
    parser.add_argument('-pi', '--results-per-iteration', type=int, default=100, help='passed to arXiv API')
    parser.add_argument('--wait-time', type=float, default=5.0, help='lets be gentle to arXiv API (seconds)')
    parser.add_argument('-break', '--break-on-no-added', type=int, default=1, help='break out early in db: 1=yes, 0=no')
    args = parser.parse_args()
    
    args.db_path = Config.db_path
    args.tmp_dir = Config.tmp_dir
    return args

    
# https://github.com/karpathy/arxiv-sanity-preserver/blob/dd4ae7eac55ebf198e1dc0cf459600e3eeb323f8/utils.py
@contextmanager
def _tempfile(*args, **kwargs):
    fd, name = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    try:
        yield name
    finally:
        try:
            os.remove(name)
        except OSError as e:
            if e.errno == 2:
                pass
            else:
                raise e
                

@contextmanager
def open_atomic(filepath, *args, **kwargs):
    fsync = kwargs.pop('fsync', False)
    
    with _tempfile(dir=os.path.dirname(filepath)) as tmppath:
        with open(tmppath, *args, **kwargs) as f:
            yield f
            if fsync:
                f.flush()
                os.fsync(f.fileno())
        os.rename(tmppath, filepath)

                
def safe_pickle_dump(obj, fname):
    with open_atomic(fname, 'wb') as f:
        pickle.dump(obj, f, -1)

        
def pickle_load(fname):
    try:
        db = pickle.load(open(fname, 'rb'))
    except Exception as e:
        print('error loading existing database:\n{}\nstarting from an empty database'.format(e))
        db = {}
    return db
