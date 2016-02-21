# arxiv-crawler
Crawl [arXiv](http://arxiv.org/) paper and organize as a database

### Modifying crawling range

```sh
# crawler.py
fields = ['CV']
months = ['{:0>2d}'.format(i+1) for i in range(12)]
years = ['{:0>2d}'.format(i) for i in range(6, 17)]
```

### Launch the crawler

```sh
python crawler.py
```

### Check the results

```sh
python
>>> import sqlite3
>>> conn = sqlite3.connect('arxiv_raw.sqlite')
>>> cur = conn.cursor()
>>> cur.execute('SELECT * FROM sql_master')
>>> print cur.fetchall() # print the information for all tables
```

## Future work

Still figuring the best way to visualize papers
