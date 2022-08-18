import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import uuid
import os
import json
import urllib.request

class scraper:
    def __init__(self, URL):
        self.driver = webdriver.Chrome()
        self.links = self.find_links(URL)
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html.parser')
        self.regions = soup.find_all(name = "div", attrs = {"class": "panel-box-heading"})
        if not os.path.exists("raw_data"):
            os.makedirs("raw_data")
        if not os.path.exists("raw_data\images"):
            os.makedirs("raw_data\images")
        for r in self.regions:
            if not os.path.exists("raw_data\images\\" + r.text):
                os.makedirs("raw_data\images\\" + r.text)

    def click_link(self, URL):
        self.driver.get(URL)
    
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    def find_links(self, URL):
        self.click_link(URL)
        content = self.driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
        tables = content.find_elements(by=By.CLASS_NAME, value="panel-box-body")
        links = []
        for t in tables:
            teams_in_region = []
            teams = t.find_elements(by=By.CLASS_NAME, value="team-template-text")
            for team in teams:
                a_tag = team.find_element(by=By.TAG_NAME, value='a')
                link = a_tag.get_attribute('href')
                teams_in_region.append(link)
            links.append(teams_in_region)
        return links

    def collect_team_data(self, soup):
        side_box = soup.find(name = "div", attrs = {"class": "fo-nttax-infobox"})
        side_info = side_box.find_all(name = "div", attrs = {"class": "infobox-cell-2"})
        info_dict = {}
        for info in side_info[0::2]:
            info_dict[info.text.replace("\xa0", " ")] = side_info[side_info.index(info)+1].text.replace("\xa0", " ")
        return info_dict
    
    def collect_player_data(self, soup):
        player_box = soup.find(name = "div", attrs = {"class": "table-responsive"})
        players = player_box.find_all(name = "tr", attrs = {"class": "Player"})
        info_dict = {}
        for p in players:
            p_row = p.find_all("td")
            player_dict = {"ID": p_row[0].text.replace("\xa0", " "), "Name": p_row[2].text.replace("\xa0", " ")}
            info_dict[p_row[3].text.replace("\xa0", " ")] = player_dict
        return info_dict

    def collect_image_data(self):
        content = self.driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
        image_link = content.find_element(by=By.CLASS_NAME, value="image")
        link = image_link.get_attribute("href")
        self.click_link(link)
        image = self.driver.find_element(by=By.CLASS_NAME, value="fullImageLink")
        a_tag = image.find_element(by=By.TAG_NAME, value="a")
        src = a_tag.get_attribute("href")
        return src

    def generate_id(self):
        content = self.driver.find_element(by=By.XPATH, value='//*[@id="firstHeading"]')
        return [content.text, str(uuid.uuid4())]
    
    def save_image_data(self, data, region):
        urllib.request.urlretrieve(data["Logo Data"], "raw_data\images\\" + region  + "\\" + data["ID"][0] + ".png")

    def save_text_data(self, all_data):
        with open('raw_data\data.json', 'w') as f:
            json.dump(all_data, f)

    def collect_data(self, URL):
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html.parser')
        data = {}
        data["ID"] = self.generate_id()
        data["Team Data"] = self.collect_team_data(soup)
        data["Players Data"] = self.collect_player_data(soup)
        data["Logo Data"] = self.collect_image_data()
        return data

    def collect_all_data(self):
        i = 0
        all_data = {}
        for links in self.links:
            curr_region = self.regions[i].text
            all_data[curr_region] = []
            for link in links:
                self.click_link(link)
                data = s.collect_data(link)
                s.save_image_data(data, curr_region)
                all_data[curr_region].append(data)
            i += 1
        self.save_text_data(all_data)

if __name__ == "__main__":
    s = scraper("https://liquipedia.net/leagueoflegends/Portal:Teams")
    s.collect_all_data()