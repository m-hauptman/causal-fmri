### getngrams.py ###
# purpose: query GoogleNgrams
# script from https://github.com/econpy/google-ngrams/blob/master/getngrams.py,
# adapted by MH

from ast import literal_eval
from pandas import DataFrame  # http://github.com/pydata/pandas
import re
import requests               # http://github.com/kennethreitz/requests
import subprocess
import sys

corpora = dict(eng_us_2012=17, eng_us_2009=5, eng_us_2019=28,
               eng_gb_2012=18, eng_gb_2009=6, eng_gb_2019=26,
               chi_sim_2019=34, chi_sim_2012=23, chi_sim_2009=11,
               eng_2012=15, eng_2009=0,
               eng_fiction_2012=16, eng_fiction_2009=4, eng_1m_2009=1,
               fre_2019=30, fre_2012=19, fre_2009=7,
               ger_2019=31, ger_2012=20, ger_2009=8,
               heb_2012=24,
               heb_2009=9,
               spa_2019=32, spa_2012=21, spa_2009=10,
               rus_2019=36, rus_2012=25, rus_2009=12,
               ita_2019=33, ita_2012=22)

def getNgrams(query, corpus, startYear, endYear, smoothing, caseInsensitive):
    params = dict(content=query, year_start=startYear, year_end=endYear,
                  corpus=corpora[corpus], smoothing=smoothing,
                  case_insensitive=caseInsensitive)
    if params['case_insensitive'] is False:
        params.pop('case_insensitive')
    if '?' in params['content']:
        params['content'] = params['content'].replace('?', '*')
    if '@' in params['content']:
        params['content'] = params['content'].replace('@', '=>')

    req = requests.get('https://books.google.com/ngrams/graph', params=params)
    res = re.findall('\{.*?\]\}',req.text)

    if res:
        assert(len(res)==1)
        dataDict = literal_eval(res[0])
        data = dataDict["timeseries"]
        df = DataFrame(data,columns=["timeseries"])
        df.insert(0, 'year', list(range(startYear, endYear + 1)))
    else:
        df = DataFrame()
    return req.url, params['content'], df

def trimSpaceNearComma(argumentString):
    while (argumentString.find(', ')>=0):
        argumentString = argumentString.replace(', ',',')
    while (argumentString.find(' ,')>=0):
        argumentString = argumentString.replace(' ,',',')
    return argumentString

def runQuery(argumentString):
    arguments = trimSpaceNearComma(argumentString).split()
    query = ' '.join([arg for arg in arguments if not arg.startswith('-')])
    if '?' in query:
        query = query.replace('?', '*')
    if '@' in query:
        query = query.replace('@', '=>')
    params = [arg for arg in arguments if arg.startswith('-')]
    corpus, startYear, endYear, smoothing = 'eng_2012', 1800, 2000, 3
    printHelp, caseInsensitive, allData = False, False, False
    toSave, toPrint, toPlot = True, True, False

    # parsing the query parameters
    for param in params:
        if '-nosave' in param:
            toSave = False
        elif '-noprint' in param:
            toPrint = False
        elif '-plot' in param:
            toPlot = True
        elif '-corpus' in param:
            corpus = param.split('=')[1].strip()
        elif '-startYear' in param:
            startYear = int(param.split('=')[1])
        elif '-endYear' in param:
            endYear = int(param.split('=')[1])
        elif '-smoothing' in param:
            smoothing = int(param.split('=')[1])
        elif '-caseInsensitive' in param:
            caseInsensitive = True
        elif '-alldata' in param:
            allData = True
        elif '-help' in param:
            printHelp = True
        else:
            print(('Did not recognize the following argument: %s' % param))
    if printHelp:
        print('See README file.')
    else:
        if '*' in query and caseInsensitive is True:
            caseInsensitive = False
            notifyUser = True
            warningMessage = "*NOTE: Wildcard and case-insensitive " + \
                             "searches can't be combined, so the " + \
                             "case-insensitive option was ignored."
        elif '_INF' in query and caseInsensitive is True:
            caseInsensitive = False
            notifyUser = True
            warningMessage = "*NOTE: Inflected form and case-insensitive " + \
                             "searches can't be combined, so the " + \
                             "case-insensitive option was ignored."
        else:
            notifyUser = False
        url, urlquery, df = getNgrams(query, corpus, startYear, endYear,
                                      smoothing, caseInsensitive)
        if not allData:
            if caseInsensitive is True:
                for col in df.columns:
                    if col.count('(All)') == 1:
                        df[col.replace(' (All)', '')] = df.pop(col)
                    elif col.count(':chi_') == 1 or corpus.startswith('chi_'):
                        pass
                    elif col.count(':ger_') == 1 or corpus.startswith('ger_'):
                        pass
                    elif col.count(':heb_') == 1 or corpus.startswith('heb_'):
                        pass
                    elif col.count('(All)') == 0 and col != 'year':
                        if col not in urlquery.split(','):
                            df.pop(col)
            if '_INF' in query:
                for col in df.columns:
                    if '_INF' in col:
                        df.pop(col)
            if '*' in query:
                for col in df.columns:
                    if '*' in col:
                        df.pop(col)
    return df
