import scrapy

class WarOfRightsSpider(scrapy.Spider):
    name = 'search_players'
    start_urls = ['https://warofrights.com/CT']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WarOfRightsSpider, cls).from_crawler(crawler, *args, **kwargs)
        # Set FEEDS setting here
        crawler.settings.set('FEEDS', {
            'players.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
                'item_export_kwargs': {
                    'export_empty_fields': True,
                }
            }
        })

        return spider

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.settings.set('FEEDS', {
    #         'players.json': {
    #             'format': 'json',
    #             'encoding': 'utf8',
    #             'store_empty': False,
    #             'indent': 4,
    #             'item_export_kwargs': {
    #                 'export_empty_fields': True,
    #             }
    #         }
    #     })

    def start_requests(self):
        for url in self.start_urls:
            # Make the first GET request
            yield scrapy.FormRequest(url,
                    method='GET',
                    callback=self.parse_get)

    def parse_get(self, response):

        viewstate = response.css('input[name="__VIEWSTATE"]::attr(value)').get()
        viewstategenerator = response.css('input[name="__VIEWSTATEGENERATOR"]::attr(value)').get()
        eventvalidation = response.css('input[name="__EVENTVALIDATION"]::attr(value)').get()

        formdata = {
            'ctl00$ScriptManager1': 'ctl00$ContentPlaceHolder1$UpdatePanelSearchResults|ctl00$ContentPlaceHolder1$lbSearch',
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$lbSearch',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            '__ASYNCPOST': 'true',
        }

        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

        yield scrapy.FormRequest(
            url='https://warofrights.com/CT',
            method='POST',
            headers=headers,
            formdata=formdata,
            callback=self.parse_first_post
        )

    def parse_first_post(self, response):

        headers = {
            'accept': '*/*',
            'authority': 'warofrights.com',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://warofrights.com',
            'referer': 'https://warofrights.com/CT',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }

        server_data = response.text.split('|')

        formdata = {
            'ctl00$ScriptManager1': 'ctl00$ContentPlaceHolder1$UpdatePanelSearchResults|ctl00$ContentPlaceHolder1$lbSearch',
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$lbSearch',
            '__VIEWSTATE': server_data[server_data.index('__VIEWSTATE') + 1],
            '__VIEWSTATEGENERATOR': server_data[server_data.index('__VIEWSTATEGENERATOR') + 1],
            '__EVENTVALIDATION': server_data[server_data.index('__EVENTVALIDATION') + 1],
            '__ASYNCPOST': 'true',
        }

        yield scrapy.FormRequest(
            url='https://warofrights.com/CT',
            method='POST',
            headers=headers,
            formdata=formdata,
            callback=self.parse_second_post
        )

    def parse_second_post(self, response):

        players = response.xpath('//table//tr[position()>1]')

        for player in players:

            player_data = {
                'SoldierID': player.xpath('.//td[1]/a/@href').re_first('soldierID=(\d+)'),
                'SoldierLink': player.xpath('.//td[1]/a/@href').extract_first().replace('#companyToolHeader', ''),
                'DisplayName': player.xpath('.//td[1]/a/text()').extract_first().strip(),
                'RegimentID': player.xpath('.//td[2]/a/@href').re_first('companyID=(\d+)'),
                'RegimentLink': player.xpath('.//td[2]/a/@href').extract_first().replace('#companyToolHeader', ''),
                'RegimentName': player.xpath('.//td[2]/a/text()').extract_first().strip(),
            }

            yield player_data