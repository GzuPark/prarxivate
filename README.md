# Private arXiv
This is a project for collecting arXiv papers, which I'm interesting, and converting to html files per day.

## Pre-requsite
- [feedparser](https://pypi.org/project/feedparser/)

```sh
pip install -r requirements.txt
```

## How to use
- `fetch_papers.py` will be save papers at data directory
- example of `--search-query`
  - [guide](https://arxiv.org/help/api/user-manual#subject_classifications)
  - `cat:cs.CV`
  - `cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:stat.ML+OR+cat:cs.RO`
  - `cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.NE+OR+cat:stat.ML`
  - `cat:cs.CV+AND+cat:cs.LG`

```sh
usage: fetch_papers.py [-h] [-sq SEARCH_QUERY] [-si START_INDEX]
                       [-mi MAX_INDEX] [-pi RESULTS_PER_ITERATION]
                       [--wait-time WAIT_TIME] [-break BREAK_ON_NO_ADDED]

optional arguments:
  -h, --help            show this help message and exit
  -sq SEARCH_QUERY, --search-query SEARCH_QUERY
                        query used for arXiv API. See
                        https://arxiv.org/help/api/user-
                        manual#subject_classifications
  -si START_INDEX, --start-index START_INDEX
                        0 = most recent API result
  -mi MAX_INDEX, --max-index MAX_INDEX
                        upper bound on paper index we will fetch
  -pi RESULTS_PER_ITERATION, --results-per-iteration RESULTS_PER_ITERATION
                        passed to arXiv API
  --wait-time WAIT_TIME
                        lets be gentle to arXiv API (seconds)
  -break BREAK_ON_NO_ADDED, --break-on-no-added BREAK_ON_NO_ADDED
                        break out early in db: 1=yes, 0=no
```

- `make_report.py` will be make the html file at results directory
- example of `--report-date`
  - `2019-11-20`
```sh
usage: make_report.py [-h] [-d REPORT_DATE] [-nbc NUMBER_BREAK_CONTENTS]
                      [-nbs NUMBER_BREAK_SUMMARY]

optional arguments:
  -h, --help            show this help message and exit
  -d REPORT_DATE, --report-date REPORT_DATE
                        specific date for report (html)
  -nbc NUMBER_BREAK_CONTENTS, --number-break-contents NUMBER_BREAK_CONTENTS
                        number of break point for contents
  -nbs NUMBER_BREAK_SUMMARY, --number-break-summary NUMBER_BREAK_SUMMARY
                        number of break point for summary
```


## Reference
- [arXiv api user manual](https://arxiv.org/help/api/user-manual)
- [arxiv-sanity by karpathy](https://github.com/karpathy/arxiv-sanity-preserver)
- [A4 CSS page template](https://codepen.io/rafaelcastrocouto/pen/LFAes)
