# Data Collection Pipeline Project Documentation

> 

## Milestone 2: Decide which website you are going to collect data from 

## Milestone 3: Prototype finding the individual page for each entry

```python
def find_link(self, URL):
    self.click_link(URL)
    content = self.driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
    table = content.find_element(by=By.CLASS_NAME, value="panel-box-body")
    team = table.find_element(by=By.CLASS_NAME, value="team-template-text")
    a_tag = team.find_element(by=By.TAG_NAME, value='a')
    link = a_tag.get_attribute('href')
    return link
```

## Milestone 4: Retrieve data from details page

```python
def find_link(self, URL):
    self.click_link(URL)
    content = self.driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
    table = content.find_element(by=By.CLASS_NAME, value="panel-box-body")
    team = table.find_element(by=By.CLASS_NAME, value="team-template-text")
    a_tag = team.find_element(by=By.TAG_NAME, value='a')
    link = a_tag.get_attribute('href')
    return link

def collect_team_data(self, soup):
    side_box = soup.find(name = "div", attrs = {"class": "fo-nttax-infobox"})
    side_info = side_box.find_all(name = "div", attrs = {"class": "infobox-cell-2"})
    info_dict = {}
    for info in side_info[0::2]:
        info_dict[info.text.replace("\xa0", " ")] = side_info[side_info.index(info)+1].text.replace("\xa0", " ")
    return(info_dict)

def collect_player_data(self, soup):
    player_box = soup.find(name = "div", attrs = {"class": "table-responsive"})
    players = player_box.find_all(name = "tr", attrs = {"class": "Player"})
    info_dict = {}
    for p in players:
        p_row = p.find_all("td")
        player_dict = {"ID": p_row[0].text.replace("\xa0", " "), "Name": p_row[2].text.replace("\xa0", " ")}
        info_dict[p_row[3].text.replace("\xa0", " ")] = player_dict
    return(info_dict)

def collect_image_data(self):
    content = self.driver.find_element(by=By.XPATH, value='//*[@id="mw-content-text"]')
    image_link = content.find_element(by=By.CLASS_NAME, value="image")
    link = image_link.get_attribute("href")
    self.click_link(link)
    image = self.driver.find_element(by=By.CLASS_NAME, value="fullImageLink")
    a_tag = image.find_element(by=By.TAG_NAME, value="a")
    src = a_tag.get_attribute("href")
    return(src)

def generate_id(self):
    content = self.driver.find_element(by=By.XPATH, value='//*[@id="firstHeading"]')
    return(content.text, str(uuid.uuid4()))

def collect_data(self, URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = {}
    data["ID"] = self.generate_id()
    data["Team Data"] = self.collect_team_data(soup)
    data["Players Data"] = self.collect_player_data(soup)
    data["Logo Data"] = self.collect_image_data()
    print(data)
    return(data)

def save_data(self, data):
    if not os.path.exists("raw_data"):
        os.makedirs("raw_data")
    with open('raw_data\data.json', 'w') as d:
        json.dump(data, d)
    if not os.path.exists("raw_data\images"):
        os.makedirs("raw_data\images")
    urllib.request.urlretrieve(data["Logo Data"], "raw_data\images\\" + data["ID"][0] + ".png")

```

## Milestone 2:

## Milestone 2:

## Milestone 2:

## Milestone 2:

## Milestone 2:

## Milestone 2: