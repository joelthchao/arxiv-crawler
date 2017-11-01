import urllib
import sqlite3
from bs4 import *
import re

url = 'http://arxiv.org/list/cs.{}/{}{}?show=1000'
fields = ['CV']
months = ['{:0>2d}'.format(i+1) for i in range(2)]
years = ['{:0>2d}'.format(i) for i in range(16, 17)]

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
    for year in years:
        for month in months:
            query_url = url.format(field, year, month)
            print('Retrieving {}'.format(query_url))
            uh = urllib.request.urlopen(query_url)
            data = uh.read()
            soup = BeautifulSoup(str(data), "html5lib")
            titles = soup.findAll('div', {'class': 'list-title'})
            authors = soup.findAll('div', {'class': 'list-authors'})
            paper_urls = soup.findAll('span', {'class': 'list-identifier'})
            if len(titles) != len(authors):
                print('number of titles and authors mismatch')
            else:
                for title, author, paper_url in zip(titles, authors, paper_urls):
                    title = title.contents[-1].strip()
                    paper_url = 'http://arxiv.org' + paper_url.contents[0].attrs['href']
                    cur.execute('''
                        INSERT OR IGNORE INTO Papers (title, url, year, month) 
                        VALUES (?, ?, ?, ?)''', (title, paper_url, int(year), int(month)))
                    cur.execute('SELECT id FROM Papers WHERE title = ? ', (title, ))
                    paper_id = cur.fetchone()[0]
                    
                    paper_authors = [au.string.strip() for au in author.findAll('a')]
                    for name in paper_authors:
                        cur.execute('''
                            INSERT OR IGNORE INTO Authors (name) 
                            VALUES (?)''', (name, ))
                        cur.execute('SELECT id FROM Authors WHERE name = ? ', (name, ))
                        author_id = cur.fetchone()[0]
                        cur.execute('''
                            INSERT OR REPLACE INTO Publications
                            (paper_id, author_id) VALUES (?, ?)''', (paper_id, author_id))
conn.commit()
