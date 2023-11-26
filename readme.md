
ls ~/app/spiders

```
scrapy runspider --overwrite-output=players.json:json ./players_search_spider.py
scrapy runspider --overwrite-output=players_ext.json:json ./players_extended_spider.py
```

crontab -e (-l: list)

```
15 0 * * * ~/.local/bin/scrapy runspider --overwrite-output=app/spiders/players.json:json ~/app/spiders/players_search_spider.py > ~/app/spiders/players_search_spider.log 2>&1
30 0 * * * ~/.local/bin/scrapy runspider --overwrite-output=app/spiders/players_ext.json:json ~/app/spiders/players_extended_spider.py > ~/app/spiders/players_extended_spider.log 2>&1
```

