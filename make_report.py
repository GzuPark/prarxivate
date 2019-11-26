import argparse
import copy
import os

from datetime import datetime, timedelta

from utils import Config, pickle_load, strip_version


def get_args():
    parser = argparse.ArgumentParser()
    now = datetime.now().strftime('%Y-%m-%d')
    parser.add_argument('-d', '--report-date', type=str, default='{}'.format(now), help='specific date for report (html), if multiple date: "FROM_DATE TO_DATE"')
    parser.add_argument('-c', '--filter-primary-category', type=str, default='none', help='specific primary category if want to choice multiple category use "+"')
    parser.add_argument('-nbc', '--number-break-contents', type=int, default=25, help='number of break point for contents')
    parser.add_argument('-nbs', '--number-break-summary', type=int, default=2, help='number of break point for summary')
    parser.add_argument('-ds', '--date-sort-by', type=str, default='p', help='sort by ( published (p) | updated (u) ), default: p')
    parser.add_argument('-pf', '--printable-format-a4', type=int, default='1', help='printable format A4: 1=yes, 0=no')
    args = parser.parse_args()

    args.db_path = Config.db_path
    args.report_path = Config.report_path
    return args


def date_sort_by(ds):
    if ds == 'u':
        sort_by = 'updated_parsed'
    elif ds == 'p':
        sort_by = 'published_parsed'
    else:
        print('[Warning] --date-sort-by changed to "updated_parsed"')
        sort_by = 'published_parsed'
    return sort_by


def find_papers(args):
    y, m, d = args.report_date.split('-')
    y = int(y); m = int(m); d = int(d)

    if 'none' in args.filter_primary_category:
        pcates = ['cs.CV', 'cs.AI', 'cs.LG', 'stat.ML', 'cs.RO']
    elif '+' in args.filter_primary_category:
        pcates = args.filter_primary_category.replace(' ', '').split('+')
    else:
        pcates = [args.filter_primary_category]
    assert type(pcates) == list, 'typeError: primary category list'

    sort_by = date_sort_by(args.date_sort_by)

    db = pickle_load(args.db_path)
    print('database has {} entries'.format(len(db)))

    result = {}
    for k, v in db.items():
        if (y == v[sort_by].tm_year) and (m == v[sort_by].tm_mon) and (d == v[sort_by].tm_mday):
            if v['arxiv_primary_category']['term'] in pcates:
                result[k] = v
    print('found {} entries'.format(len(result)))
    return result, pcates


# https://codepen.io/rafaelcastrocouto/pen/LFAes
def add_css():
    css = """
        table {
            align: center;
            border-collapse: collapse;
        }
        th, td {
            padding: 5px;
        }
        table, th, td {
            border: 1px black solid;
        }
        page {
          background: white;
          display: block;
          margin: 0 auto;
        }
        page[size="A4"] {  
          width: 21cm;
          height: 29.7cm; 
        }
        @media print {
          body, page {
            box-shadow: 0;
            margin: 0px;
          }
        }
    """
    return css


def create_html(args, db, pcates):
    db_list = list(db.keys())
    sort_by = date_sort_by(args.date_sort_by).split('_')[0]
    fname = '{d}-{ds}-{n}-{c}.html'.format(d=args.report_date, ds=sort_by, n=len(db), c='+'.join(pcates))
    path = os.path.join(args.report_path, fname)
    html = open(path, 'w')
    
    html.write('<html><head>')
    html.write('<title>arXiv {ds} {d}</title>'.format(ds=sort_by, d=args.report_date))
    html.write('<style type="text/css">')
    css = add_css()
    html.write(css)
    html.write('</style></head><body>')
    html.write('<a id="top"></a>')

    # make contents list
    for i, e in enumerate(db_list):
        if (i % args.number_break_contents == 0) and (args.printable_format_a4 == 1):
            html.write('<page size="A4"><center><h1>Report arXiv {ds} {d}</h1>'.format(ds=sort_by, d=args.report_date))
            html.write('<table width="750px">')
            html.write('<tr><th>N</th><th>ID</th><th>Title</th><th>P.C.</th></tr>')
        elif  (i == 0) and (args.printable_format_a4 == 0):
            html.write('<page><center><h1>Report arXiv {ds} {d}</h1>'.format(ds=sort_by, d=args.report_date))
            html.write('<table width="750px">')
            html.write('<tr><th>N</th><th>ID</th><th>Title</th><th>P.C.</th></tr>')
        html.write('<tr><td>{}</td>'.format(i+1))
        html.write('<td align="center"><a href="{link}">{id}</a></td>'.format(link=strip_version(db[e]['id']), id=e))
        html.write('<td><a href="#{aid}">{t}</a></td>'.format(aid=e, t=db[e]['title']))
        html.write('<td>{}</td></tr>'.format(db[e]['arxiv_primary_category']['term']))
        if (((i+1) % args.number_break_contents == 0) or (i == len(db_list) - 1)) and (args.printable_format_a4 == 1):
            html.write('</table>')
            html.write('</center></page>')
        elif (i == len(db_list) - 1) and (args.printable_format_a4 == 0):
            html.write('</table>')
            html.write('</center></page>')

    # make summary details
    for i, e in enumerate(db_list):
        if (i % args.number_break_summary == 0) and (args.printable_format_a4 == 1):
            _end = (i + args.number_break_summary) if len(db_list) > (i + args.number_break_summary) else len(db_list)
            html.write('<page size="A4"><center><h3>Papers {s} - {e}</h3>'.format(s=i+1, e=_end))
        elif (i == 0) and (args.printable_format_a4 == 0):
            html.write('<page><center><h3>Papers {s} - {e}</h3>'.format(s=i+1, e=len(db_list)))
        html.write('<p><table width="750px">')
        # Number, ID, Tags
        html.write('<tr><td style="padding: 0; border: none;"><table style="border: none;" width="750px">')
        html.write('<tr><td align="center" width="30px" style="border: none;"><a id="{aid}"><b>{n}</b></a></td>'.format(aid=e, n=i+1))
        html.write('<td align="center" width="250px" style="{s}"><a href="{link}">{id}</a></td>'.format(
            s='border: none; border-right: 1px black solid; border-left: 1px black solid;',
            link=strip_version(db[e]['id']),
            id=strip_version(db[e]['id']),
        ))
        tags = [t['term'] for t in db[e]['tags']]
        html.write('<td width="450px" style="border: none;">{}</td>'.format(' | '.join(tags)))
        html.write('<td width="20px" style="border: none;"><a href="#top">top</a></td></tr>')
        html.write('</table></td></tr>')
        # Authors
        authors = [a['name'] for a in db[e]['authors']]
        html.write('<tr><td>{}</td></tr>'.format(', '.join(authors)))
        # Title
        html.write('<tr><td>{}</td></tr>'.format(db[e]['title']))
        # Summary
        html.write('<tr><td>{}</td></tr>'.format(db[e]['summary']))
        html.write('</table></p>')
        if (((i+1) % args.number_break_summary == 0) or (i == len(db_list))) and (args.printable_format_a4 == 1):
            html.write('</center></page>')
        elif (i == len(db_list)) and (args.printable_format_a4 == 0):
            html.write('</center></page>')

    html.write('</body></html>')
    html.close()
    print('saved {}'.format(fname))


def make_date_list(report_date):
    if ' ' in  report_date:
        from_date, to_date = report_date.split(' ')
    else:
        from_date = report_date
        to_date = report_date

    if from_date < to_date:
        tmp = copy.deepcopy(from_date)
        from_date = copy.deepcopy(to_date)
        to_date = copy.deepcopy(tmp)

    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')
    diff_date = (from_date - to_date).days
    result = [(from_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(diff_date + 1)]
    return result


def main():
    args = get_args()
    date_list = make_date_list(args.report_date)
    for d in date_list:
        args.report_date = d
        db, pcates = find_papers(args)
        if len(db) == 0:
            print('recommend to run fetch_papers.py with large enough --max-index {}'.format(d))
        else:
            create_html(args, db, pcates)

    
if __name__ == '__main__':
    main()
