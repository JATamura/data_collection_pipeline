import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class scraper:
    def __init__(self, URL):
        self.page = requests.get(URL)
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        self.driver = webdriver.Chrome()


    def click_link(self, URL):
        self.driver.get(URL)
    
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")


if __name__ == "__main__":
    s = scraper("https://liquipedia.net/leagueoflegends/Main_Page")
    driver = webdriver.Chrome()
    driver.get("https://liquipedia.net/leagueoflegends/LEC/2022/Summer/Group_Stage")
    content = driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
    table = content.find_element(by=By.CLASS_NAME, value="template-box")
    a_tag = table.find_element(by=By.TAG_NAME, value='a')
    link = a_tag.get_attribute('href')
    print(a_tag)
    print(link)
    driver.get(link)
