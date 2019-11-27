import pytest

from fetch_papers import get_args as fetch_args

@pytest.fixture()
def get_fetch_args():
    args = fetch_args()
    args.max_index = 100
    return args
