import requests
import uuid
import os
import json
import urllib.request
import boto3 
import pandas
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine


class scraper:

    '''
    A scraper class that takes in a specific website ("https://liquipedia.net/leagueoflegends/Portal:Teams") 
    and automatically scrapes all team and player information of said teams as well as downloads their logos.
    
    Parameters:
    ----------
    URL: str
        URL of the teams in each region ("https://liquipedia.net/leagueoflegends/Portal:Teams")
    
    Attributes:
    ----------
    driver: webdriver
        The webdriver used from selenium. In this case, it is a chromedriver.

    Methods:
    -------
    __click_link(URL)
        Click on the link
    __find_all_links(URL) --> list
        Returns all the links on the webpage for each team as a list
    __collect_team_data(soup) --> dict
        Returns a dictionary containing all the teams data from a given BeautifulSoup of the webpage
    __collect_player_data(soup) --> dict
        Returns a dictionary containing all the players data from a given BeautifulSoup of the webpage
    __collect_image_data() --> str
        Returns a dictionary containing the logo of the team
    __generate_id() --> list
        Returns a list of the name of the team and a UUID4 value
    __save_image_data(data, region)
        Saves the logo of the team to a folder named of the team's region 
    __save_text_data(all_data)
        Saves the text data of all teams to a file named data.json 
    __collect_data(URL) --> dict
        Returns a dictionary of all text and image data collected
    collect_all_data()
        Collects and saves all data on the teams from the original webpage

    '''

    def __init__(self):
        '''
        Initializes an object of the class.
        Creates a new webdriver object.
        
        Parameters:
        ----------
        letter: str
            Webpage that the data is collected from

        '''
        self.driver = webdriver.Chrome()

    def __click_link(self, URL):
        '''
        Clicks on the given link
        
        Parameters:
        ----------
        letter: str
            URL to be traversed to

        '''
        self.driver.get(URL)

    def get_regions(self, URL):
        '''
        Returns a list of regions on the main webpage
        
        Parameters:
        ----------
        URL: str
            Webpage that the information are collected from

        Returns:
        ----------
        regions: list
            List of all the regions found on the main webpage

        '''
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html.parser')
        regions = [region.text for region in soup.find_all(name = "div", attrs = {"class": "panel-box-heading"})]
        return regions

    def __create_folders(self, regions):
        '''
        Creates the necessary folder for the data to be saved in (raw_data, images, and folders named after the regions)
        
        Parameters:
        ----------
        regions: list
            List of all regions found in the web page

        '''
        if not os.path.exists("raw_data"):
            os.makedirs("raw_data")
        if not os.path.exists("raw_data\images"):
            os.makedirs("raw_data\images")
        for region in regions:
            if not os.path.exists("raw_data\images\\" + region):
                os.makedirs("raw_data\images\\" + region)

    def find_all_links(self, URL, regions):
        '''
        Finds all the links of each team in each region from the given webpage
        
        Parameters:
        ----------
        URL: str
            Webpage that the links are collected from

        Returns:
        ----------
        links: dict
            Dictionary with keys as the name of region and the values as a list of all teams from said region

        '''
        self.__click_link(URL)
        site_content = self.driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
        region_tables = site_content.find_elements(by=By.CLASS_NAME, value="panel-box-body")
        index = 0
        links = {}
        for region in region_tables:
            teams_in_region = []
            team_links = region.find_elements(by=By.CLASS_NAME, value="team-template-text")
            for team in team_links:
                a_tag = team.find_element(by=By.TAG_NAME, value='a')
                link = a_tag.get_attribute('href')
                teams_in_region.append(link)
            links[regions[index]] = teams_in_region
            index += 1
        return links

    def __collect_team_data(self, soup):
        '''
        Collects the team's data from the right side box section of the webpage 
        
        Parameters:
        ----------
        URL: str
            The BeautifulSoup of the webpage that the data is collected from
        
        Returns:
        ----------
        info_dict: dict
            Dictionary with the team's data

        '''
        side_box = soup.find(name = "div", attrs = {"class": "fo-nttax-infobox"})
        side_info = [info.text for info in side_box.find_all(name = "div", attrs = {"class": "infobox-cell-2"})]
        key_list = ["Location", "Region", "Coach", "Manager", "Approx. Total Winnings", "Created"]
        info_dict = {}
        for key in key_list:
            if (key + ":") in side_info:
                if key == "Coach" or key == "Manager":
                    info_dict[key] = side_info[side_info.index(key + ":")+1].split("\xa0")
                    del info_dict[key][0]
                elif key == "Approx. Total Winnings":
                    info_dict[key] = int(side_info[side_info.index(key + ":")+1].replace("$", "").replace(",", ""))
                    info_dict[key + " ($)"] = info_dict.pop(key)
                elif key == "Created":
                    info_dict[key] = side_info[side_info.index(key + ":")+1][-10:]
                else:
                    info_dict[key] = side_info[side_info.index(key + ":")+1].replace("\xa0", "")
        return info_dict
    
    def __collect_player_data(self, soup):
        '''
        Collects the team's players' data from the main content section of the webpage 
        
        Parameters:
        ----------
        letter: str
            The BeautifulSoup of the webpage that the data is collected from
        
        Returns:
        ----------
        info_dict: dict
            Dictionary containing the data on each player of a given team

        '''
        player_box = soup.find(name = "div", attrs = {"class": "table-responsive"})
        players = player_box.find_all(name = "tr", attrs = {"class": "Player"})
        info_dict = {}
        for player in players:
            p_row = player.find_all("td")
            player_dict = {"ID": p_row[0].text.replace("\xa0", ""), "Name": p_row[2].text.replace("(", "").replace(")", ""), "Join Date": p_row[4].text[10:21].replace("\xa0", "")}
            info_dict[p_row[3].text.replace("Position:\xa0", "")] = player_dict
        return info_dict

    def __collect_image_data(self):
        '''
        Collects the team's logo's link from the right side box section of the webpage 

        Returns:
        ----------
        src: str
            Link to the original version of the team's logo

        '''
        content = self.driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
        image_link = content.find_element(by=By.CLASS_NAME, value="image")
        link = image_link.get_attribute("href")
        self.__click_link(link)
        image = self.driver.find_element(by=By.CLASS_NAME, value="fullImageLink")
        a_tag = image.find_element(by=By.TAG_NAME, value="a")
        src = a_tag.get_attribute("href")
        return src

    def __generate_id(self):
        '''
        Generates a unique 
         
        Returns:
        ----------
        list: list
            List containing the team's name and the UUID4 value, each acting as unique IDs

        '''
        content = self.driver.find_element(by=By.XPATH, value='//*[@id="firstHeading"]')
        return [content.text, str(uuid.uuid4())]
    
    def __save_image_data(self, data, region):
        '''
        Saves the logo of the team to a folder with the respective region of the team

        '''
        urllib.request.urlretrieve(data["Logo Data"], "raw_data\images\\" + region  + "\\" + data["ID"][0] + ".png")

    def __save_text_data(self, all_data):
        '''
        Saves the data on all teams from all regions to a file named 'data.json'

        '''
        with open('raw_data\data.json', 'w') as f:
            json.dump(all_data, f)

    def __collect_data(self, URL):
        '''
        Collects all data regarding a specific team from a given webpage 
        
        Parameters:
        ----------
        URL: str
            The webpage the data is collected from
        
        Returns:
        ----------
        data: dict
            Dictionary containing the congragated data on each team (team and players' data as well as the source link for their logo)

        '''
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html.parser')
        data = {}
        data["ID"] = self.__generate_id()
        data.update(self.__collect_team_data(soup))
        data.update(self.__collect_player_data(soup))
        data["Logo Data"] = self.__collect_image_data()
        # print(data)
        return data

    def save_to_machine(self, all_links):
        '''
        Collects all the teams' data from a list of links to the team's webpages
        Saves the data collected into a file named data.json and the images to their respective folders

        Parameters:
        ----------
        all_links: dict
            Dictionary with keys as the name of region and the values as a list of all teams from said region

        '''
        self.__create_folders(all_links.keys())
        i = 0
        all_data = {}
        for region in all_links:
            curr_region = list(all_links.keys())[i]
            all_data[curr_region] = []
            for team_link in all_links[region]:
                self.__click_link(team_link)
                data = self.__collect_data(team_link)
                self.__save_image_data(data, curr_region)
                all_data[curr_region].append(data)
            i += 1
        self.__save_text_data(all_data)
    
    def save_to_database(self, all_links):
        '''
        Collects all the teams' data from a list of links to the team's webpages
        Saves the data collected onto an AWS RDS database using sqlalchemy

        Parameters:
        ----------
        all_links: list
            A list of all links collected from the original webpage

        '''
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'lol-team-database.ckzvrpsnhpk2.eu-west-2.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'Cosamona94'
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        engine.connect()
        i = 0
        all_data = {}
        for region in all_links:
            curr_region = list(all_links.keys())[i]
            all_data[curr_region] = []
            for team_link in all_links[region]:
                self.__click_link(team_link)
                data = self.__collect_data(team_link)
                all_data[curr_region].append(data)
            i += 1
            df = pandas.DataFrame(data)
            print(df)
    
    def test(self, all_links):
        i = 0
        all_data = {}
        for region in all_links:
            curr_region = list(all_links.keys())[i]
            all_data[curr_region] = []
            pandas_data = {}
            for team_link in all_links[region]:
                self.__click_link(team_link)
                data = self.__collect_data(team_link)
                all_data[curr_region].append(data)
                for key, value in data.items():
                    if key not in pandas_data:
                        pandas_data[key] = [value]
                    else:  
                        pandas_data[key].append(value)
                    print(pandas_data.items())
            i += 1
            df = pandas.DataFrame(all_data)
            print(df)
        pandas_data = {"Region" : [], "ID" : [], "Players" : {1: 1, 2 : 3}}
        df = pandas.DataFrame(pandas_data)
        print(df)
            


    def upload_data_to_bucket(self, bucket_name):
        '''
        Uploads the data.json file and images to their respective folders in an s3 bucket 

        Parameters:
        ----------
        bucket_name: str
            The name of the s3 bucket the files are uploaded into

        '''
        s3_client = boto3.client('s3')
        s3_client.upload_file("raw_data\data.json", bucket_name, "data.json")
        for folder_name in os.listdir("raw_data\images\\"):
            s3_client.put_object(Bucket = bucket_name, Key = ("images/" + folder_name + "/"))
            for image in os.listdir("raw_data\images\\" + folder_name):
                s3_client.upload_file("raw_data\images\\" + folder_name + "\\" + image, bucket_name, "images/" + folder_name + "/" + image)

if __name__ == "__main__":
    s = scraper()
    teams_portal_link = "https://liquipedia.net/leagueoflegends/Portal:Teams"

    regions = s.get_regions(teams_portal_link)
    
    all_links = s.find_all_links(teams_portal_link, regions)

    s.test(all_links)
    # s.save_to_machine(all_links)
    # s.save_to_database(all_links)
    # s.upload_data_to_bucket("lol-team-data-scraper")
    
