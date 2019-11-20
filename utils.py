import os
import pickle
import tempfile

from contextlib import contextmanager


class Config(object):
    realpath = os.path.dirname(os.path.realpath(__file__))
    db_path = os.path.join(realpath, 'data', 'db.p')
    report_path = os.path.join(realpath, 'results')


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


def strip_version(idstr):
    parts = idstr.split('v')
    return parts[0] + 'v' + parts[1]
