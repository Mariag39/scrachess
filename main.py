import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import argparse


class UserSpider:

    """
    Urls from Chess.com to scrap
    """
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
        self.user_data = []

    def login_data(self, user, password):
        """
        Login to chess.com and store cookies
        :param user:
        :param password:
        :return:
        """
        self.driver.get(UserSpider.URL_LOGIN)

        # wait until page is fully loaded
        delay = 6
        password_field = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.ID, "password")))
        user_field = self.driver.find_element(By.ID, "username")
        user_field.send_keys(user)
        password_field.send_keys(password)

        self.driver.find_element(By.ID, "login").click()

        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, "//a[@class='home-username-link']")))
        except TimeoutException as e:
            raise SystemExit(e)

        # store cookies for further usage
        self.cookies = self.driver.get_cookies()

    def retrieve_user_info(self, username):
        """
        Get member name, desc and create_date with requests.
        Trophies and recent matches with selenium (dynamic js).
        :param username:
        :return:
        """

        # load cookies
        for cookie in self.cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])

        headers = {
            "User-Agent": UserSpider.USER_AGENT
        }
        try:
            user_info = self.session.get(UserSpider.URL_MEMBER + username, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        soup = BeautifulSoup(user_info.text, "html.parser")
        is_logged = soup.find("button", attrs={"class": "btn-link logout"})

        if not is_logged:
            print("Not logged")
            raise SystemExit()

        # name
        name = soup.select_one("h1.profile-card-username").text.strip()
        print("name: " + name)

        # description
        description = soup.find("div", id="collapseAbout")
        if description:
            print("description: " + f"{description.text.strip()}")
        else:
            description = "No description"

        # creation date
        creation_date = soup.find_all("div", attrs={"class": "profile-card-info-item-value"})[1].text.strip()
        print("creation_date: " + creation_date)

        # create data dict
        first_data = {
            'name': name,
            'description': description.strip(),
            'creation_date': creation_date,
        }
        self.user_data.append(first_data)

        # selenium block
        delay = 10
        self.driver.get(UserSpider.URL_MEMBER + username)

        # recent trophies info
        try:
            self.get_trophies(10)
        except TimeoutException:
            print("No trophies")
            pass

        # recent matches info
        try:
            self.get_recent_matches(10)
        except TimeoutException:
            print("No recent matches yet")
            pass

        self.driver.close()
        self.to_json(self.user_data)

    def get_trophies(self, delay):
        """
        Get trophies info if any
        :param delay:
        :return:
        """
        table_trophy = WebDriverWait(self.driver, delay).until(
            EC.presence_of_element_located((By.XPATH, "//table[@class='trophy-history-table']")))
        rows = table_trophy.find_elements(By.TAG_NAME, "tr")  # get all of the rows in the table
        for row in rows:
            col = row.find_elements(By.TAG_NAME, "td")
            table = {
                "date": col[0].text,
                "ranking": col[1].text,
                "cell": col[2].text,
                "division": col[3].text
            }
            self.user_data.append(table)
            print(table)

    def get_recent_matches(self,delay):
        """
        Get recent matches info if any
        :param delay:
        :return:
        """
        table_recent_match = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located(
            (By.XPATH, "//table[@class='table-component table-hover archived-games-table']/tbody")))
        rows_matches = table_recent_match.find_elements(By.TAG_NAME, "tr")
        for row in rows_matches:
            col = row.find_elements(By.TAG_NAME, "td")
            table = {
                "players": col[1].text.replace('\n', ' '),
                "result": col[2].text.replace('\n', ' '),
                "precision": col[3].text.replace('\n', ' '),
                "movements": col[4].text.replace('\n', ' '),
                "date": col[5].text.replace('\n', ' ')
            }
            self.user_data.append(table)
            print(table)

    def to_json(self,data):
        """
        Dump json data
        :param data:
        :return:
        """
        try:
            with open('logs/user_info.json', "w") as file:
                for d in data:
                    json.dump(d, file)
                    file.write('\n')
        except Exception as e:
            print("not writable")
            pass


def main(username, password, member):
    userinfo = UserSpider()
    userinfo.login_data(user=username, password=password)
    userinfo.retrieve_user_info(username=member)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Login credentials')
    parser.add_argument('-u', required=True,
                        help='username')
    parser.add_argument('-p', required=True,
                        help='password')
    parser.add_argument('-m', required=True,
                        help='member to get info')
    args = parser.parse_args()

    main(username=args.u, password=args.p, member=args.m)
