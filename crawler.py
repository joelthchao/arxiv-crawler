import urllib
import sqlite3
from BeautifulSoup import *
import re

url = 'http://arxiv.org/list/cs.{}/{}{}?show=1000'
fields = ['CV']
months = ['{:0>2d}'.format(i+1) for i in range(12)]
years = ['{:0>2d}'.format(i) for i in range(6, 17)]

conn = sqlite3.connect('arxiv_raw.sqlite')
cur = conn.cursor()
cur.executescript('''
CREATE TABLE IF NOT EXISTS Papers (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title TEXT UNIQUE,
    url TEXT,
    year INTEGER,
    month INTEGER
);
CREATE TABLE IF NOT EXISTS Authors (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS Publications (
    paper_id INTEGER, 
    author_id INTEGER,
    PRIMARY KEY (paper_id, author_id)
);
''')

for field in fields:
    for year in ['16']: #years:
        for month in ['02']: #months:
            query_url = url.format(field, year, month)
            print 'Retrieving {}'.format(query_url)
            uh = urllib.urlopen(query_url)
            data = uh.read()
            soup = BeautifulSoup(str(data))
            titles = soup.findAll('div', {'class': 'list-title'})
            authors = soup.findAll('div', {'class': 'list-authors'})
            paper_urls = soup.findAll('span', {'class': 'list-identifier'})
            #[0].findAll('a')[0].string
            if len(titles) != len(authors):
                print 'number of titles and authors mismatch'
            else:
                for i in range(len(titles)):
                    title = titles[i].contents[-1].strip()
                    paper_url = 'http://arxiv.org' + paper_urls[i].contents[0].attrs[0][1]
                    cur.execute('''
                        INSERT OR IGNORE INTO Papers (title, url, year, month) 
                        VALUES (?, ?, ?, ?)''', (title, paper_url, int(year), int(month)))
                    cur.execute('SELECT id FROM Papers WHERE title = ? ', (title, ))
                    paper_id = cur.fetchone()[0]
                    
                    author = [author.string.strip() for author in authors[i].findAll('a')]
                    for name in author:
                        cur.execute('''
                            INSERT OR IGNORE INTO Authors (name) 
                            VALUES (?)''', (name, ))
                        cur.execute('SELECT id FROM Authors WHERE name = ? ', (name, ))
                        author_id = cur.fetchone()[0]
                        cur.execute('''
                            INSERT OR REPLACE INTO Publications
                            (paper_id, author_id) VALUES (?, ?)''', (paper_id, author_id))
conn.commit()
