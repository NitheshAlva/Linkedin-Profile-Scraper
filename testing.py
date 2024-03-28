from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def login(browser):
    with open("login.txt", "r") as file:
        lines = file.readlines()
    email = lines[0].strip()
    password = lines[1].strip()

    browser.get("https://www.linkedin.com/login")
    WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(email)
    browser.find_element(By.ID, "password").send_keys(password)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]").click()
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, "global-nav")))

def get_page_count(browser, keyword):
    base_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER"
    browser.get(base_url)
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)

    soup = BeautifulSoup(browser.page_source, "html.parser")

    # Target the <div> container for the page state information
    page_state_div = soup.find("div", class_="artdeco-pagination__page-state")
    print(page_state_div)
    if page_state_div:
        # Page state format = "Page X of Y"
        page_state_text = page_state_div.text.strip()
        # Extract the total number of pages (Y) from the text
        total_pages = int(page_state_text.split(' ')[-1])
        return total_pages
    else:
        return 1

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)

try:
    login(browser)  # Log into LinkedIn before searching
    test_keyword = "director"
    page_count = get_page_count(browser, test_keyword)
    print(f"Total pages for '{test_keyword}': {page_count}")
finally:
    browser.quit()
