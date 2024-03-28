from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

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

def get_profile_urls(browser, keyword, max_profiles=100):
    base_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER"
    browser.get(base_url)
    WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    profile_urls = set()
    while len(profile_urls) < max_profiles:
        soup = BeautifulSoup(browser.page_source, "html.parser")
        profiles = soup.find_all("a", {"href": True, "class": "app-aware-link"})

        return list(profile_urls)[:max_profiles]

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

def scrape_profile(entry):
    profile_info = {
        "URL": "N/A",
        "Name": "N/A",
        "Position": "N/A",
        "Location": "N/A",
    }

    # URL extraction
    url_anchor = entry.find("a", class_="app-aware-link")
    if url_anchor and 'href' in url_anchor.attrs:
        profile_info["URL"] = url_anchor['href']

    # Name extraction
    name_span = entry.find("span", {"aria-hidden": "true"})
    if name_span:
        profile_info["Name"] = name_span.text.strip()

    # Position extraction
    position_div = entry.find("div", class_="entity-result__primary-subtitle")
    if position_div:
        profile_info["Position"] = position_div.text.strip()

    # Location extraction
    location_div = entry.find("div", class_="entity-result__secondary-subtitle")
    if location_div:
        profile_info["Location"] = location_div.text.strip()

    return profile_info

def scrape_multiple_profiles(browser, keyword):
    actual_total_pages = 5  # Change the code here. Will not be using get_page_count function. Doesn't Work               #get_page_count(browser, keyword)
    print(f"Total pages for '{keyword}': {actual_total_pages}")

    # Limit to the first 3 pages for the moment
    # testing_pages = min(actual_total_pages, 3)
    all_profiles = []
    for page in range(1, actual_total_pages + 1):
        page_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&page={page}"
        browser.get(page_url)
        WebDriverWait(browser, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".reusable-search__result-container")))
        # Brief pause to mimic human-like interaction and avoid triggering anti-bot mechanisms
        time.sleep(random.uniform(1.5, 3.5))
        soup = BeautifulSoup(browser.page_source, "html.parser")
        profile_entries = soup.find_all("li", class_="reusable-search__result-container")
        for entry in profile_entries:
            profile_info = scrape_profile(entry)
            all_profiles.append(profile_info)
    return all_profiles

def profiles_to_excel(profiles, filename="LinkedIn_Profiles.xlsx"):
    df = pd.DataFrame(profiles)
    df.to_excel(filename, index=False)
    print(f"Data exported to {filename}")