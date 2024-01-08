import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By


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
        #self.options.add_argument("--headless")

    def get_cookies(self):
        return self.session.cookies

    def login_data(self, user, password):
        headers = {
            "User-Agent": UserSpider.USER_AGENT
        }
        r = self.session.get(UserSpider.URL_LOGIN, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        token = soup.find("input", attrs={"name": "_token"})["value"]

        print(token)

        data = {
            "_username": user,
            "_password": password,
            "login": "**",
            "_target_path": "https://www.chess.com/home",
            "_token": token
        }

        res = self.session.post(UserSpider.URL_FORM_LOGIN, headers=headers, data=data, allow_redirects=True)
        post_soup = BeautifulSoup(res.text, "lxml")

        if res.url != UserSpider.URL_HOME:
            raise Exception

    def retrieve_user_info(self, username):
        headers = {
            "User-Agent": UserSpider.USER_AGENT
        }
        user_info = self.session.get(UserSpider.URL_MEMBER + username, headers=headers)
        soup = BeautifulSoup(user_info.text,"html.parser")
        is_logged = soup.find("button", attrs={"class":"btn-link logout"})
        if not is_logged:
            raise Exception
        name = soup.select_one("h1.profile-card-username").text
        print(name)
        description = soup.find("div", id="collapseAbout").text
        print(description)
        creation_date = soup.find_all("div", attrs={"class": "profile-card-info-item-value"})
        print(creation_date[1].text)
        driver = webdriver.Firefox(options=self.options)
        table_data = []
        driver.get("https://chess.com")
        print(self.session.cookies)
        for c in self.session.cookies:
            driver.add_cookie({'name': c.name, 'value': c.value, 'path': c.path, 'expiry': c.expires})
        driver.get(UserSpider.URL_MEMBER + username)
        tables = driver.find_element(By.XPATH, "//table[@class='trophy-history-table']")
        print(tables)
        print(len(tables))

        '''for row in table.findAll("tr"):
            rows.append(row)
        for r in rows:
            print(r)'''



if __name__ == '__main__':
    userinfo = UserSpider()
    userinfo.login_data("inhauls","Djai:7272$,Th")
    userinfo.retrieve_user_info("mikasinski")

