import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


class UserSpider:
    URL_LOGIN = "https://www.chess.com/login"
    URL_FORM_LOGIN = "https://www.chess.com/login_check"
    URL_HOME = "https://www.chess.com/home"
    URL_MEMBER = "https://www.chess.com/member/"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    URL_MATCHES = "https://www.chess.com/games/archive/"

    def __init__(self):
        self.session = requests.session()
        self.options = FirefoxOptions()
        self.options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=self.options)
        self.cookies = None

    def login_data(self, user, password):

        self.driver.get(UserSpider.URL_LOGIN)

        delay = 6
        password_field = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.ID, "password")))
        user_field = self.driver.find_element(By.ID, "username")

        user_field.send_keys(user)
        password_field.send_keys(password)

        self.driver.find_element(By.ID, "login").click()

        self.cookies = self.driver.get_cookies()

    def retrieve_user_info(self, username):
        for cookie in self.cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])

        headers = {
            "User-Agent": UserSpider.USER_AGENT
        }

        user_info = self.session.get(UserSpider.URL_MEMBER + username, headers=headers)
        soup = BeautifulSoup(user_info.text, "html.parser")
        is_logged = soup.find("button", attrs={"class": "btn-link logout"})

        if not is_logged:
            raise Exception

        # User info output
        user_data = []

        name = soup.select_one("h1.profile-card-username").text
        print("name: " + name)
        description = soup.find("div", id="collapseAbout").text
        print("description: " + description)
        creation_date = soup.find_all("div", attrs={"class": "profile-card-info-item-value"})
        print("creation_date: " + creation_date[1].text)
        first_data = {
            'name': str(name).strip(),
            'description': str(description),
            'creation_date': str(creation_date),
        }
        user_data.append(first_data)
        delay = 7
        self.driver.get(UserSpider.URL_MEMBER + username)
        table_trophy = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, "//table[@class='trophy-history-table']")))
        rows = table_trophy.find_elements(By.TAG_NAME, "tr")  # get all of the rows in the table
        for row in rows:
            col = row.find_elements(By.TAG_NAME, "td")
            table = {
                "date": col[0].text,
                "ranking": col[1].text,
                "cell": col[2].text,
                "division": col[3].text
            }
            user_data.append(table)
            print(table)
        table_recent_match = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, "//table[@class='table-component table-hover archived-games-table']/tbody")))
        rows_matches = table_recent_match.find_elements(By.TAG_NAME, "tr")
        for row in rows_matches:
            col = row.find_elements(By.TAG_NAME, "td")
            table = {
                "players": col[1].text.replace('\n',' '),
                "result": col[2].text.replace('\n',' '),
                "precision": col[3].text.replace('\n',' '),
                "movements": col[4].text.replace('\n',' '),
                "date": col[5].text.replace('\n',' ')
            }
            user_data.append(table)
            print(table)
        self.driver.close()
        self.to_json(user_data)

    def to_json(self,data):
        with open('user_info.json', "w") as file:
            for d in data:
                json.dump(d, file)
                file.write('\n')


if __name__ == '__main__':
    userinfo = UserSpider()
    userinfo.login_data("inhauls", "Djai:7272$,Th")
    userinfo.retrieve_user_info("mikasinski")

