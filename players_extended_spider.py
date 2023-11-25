import json
import scrapy

from pathlib import Path

class PlayersExt(scrapy.Spider):
    name = 'players_ext'

    def start_requests(self):
        file_path = Path(__file__).parent / 'players.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        for player in data:
            yield scrapy.Request('https://warofrights.com' + player['SoldierLink'])

    def parse(self, response):
        player_info = response.css('#ContentPlaceHolder1_UpdatePanelGeneral > div.floatLeft > h3.handWritten::text').extract()
        regiment_name = response.css('#ContentPlaceHolder1_UpdatePanelGeneral > div.floatLeft > #ContentPlaceHolder1_companyLink > h3.handWritten::text').get().strip()
        remarks = response.css('#ContentPlaceHolder1_tbRemarks::text').get().strip()

        player_data = {
            "SoldierID": response.url.replace('https://warofrights.com/CT_ViewSoldier?soldierID=', ''),
            "SoldierLink": response.url.replace('https://warofrights.com', ''),
            "RegimentID": None,
            "RegimentLink": "/CT_ViewCompany?companyID=-1",
            "RegimentName": regiment_name,
            "Nickname": player_info[0].strip(),
            "SoldierName": player_info[1].strip(),
            "SoldierRank": player_info[2].strip(),
            "SoldierRole": player_info[3].strip(),
            "Nation": player_info[4].strip(),
            "Platoon": player_info[5].strip(),
            "LastLogin": player_info[6].strip(),
            "Remarks": remarks,
            "ServiceRecords": []
        }

        player_data["DisplayName"] = player_data["SoldierName"]
        service_records = response.css('p.handWritten.serviceRecord::text').extract()

        for i in range(0, len(service_records), 2):
            player_data["ServiceRecords"].append(service_records[i+1].strip() + ' - ' + service_records[i].strip())

        if regiment_name != "Not in a company":
            regiment_element_js_link = response.css('#ContentPlaceHolder1_UpdatePanelGeneral > div.floatLeft > #ContentPlaceHolder1_companyLink::attr(href)').get()
            regiment_link = regiment_element_js_link.split(',')[4].replace('"', '').replace('#companyToolHeader', '', 1).strip()

            player_data["DisplayName"] = player_data["SoldierRank"] + ' ' + player_data["SoldierName"]
            player_data["RegimentID"] = regiment_link.replace('CT_ViewCompany?companyID=', '')
            player_data["RegimentLink"] = '/' + regiment_link
            player_data["RegimentName"] = regiment_name

        yield player_data