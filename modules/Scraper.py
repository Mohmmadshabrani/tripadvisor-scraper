import sys
import subprocess
import time
import csv
from random import randint
from pathlib import Path
from modules.Review import Review
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.chrome.service import Service as ChromeService

    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error importing a module: {e}")
    print("Attempting to install required packages...")
    try:
        subprocess.run(["pip", "install", "-r -user", "requirements.txt"], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as install_error:
        print(f"Error installing dependencies: {install_error}")

class Scraper:
    def __init__(self, url=None, headless=True , output_path=None):
        """Initialize the Scraper class with the URL and headless mode"""
        self.url = url
        self.headless = headless
        self.driver = None
        self.html = None
        self.links = []
        self.developer_mode = not headless
        self.output_path = output_path
        self.proxies = open("./modules/proxies_list.txt").read().splitlines()
        if self.developer_mode:
            print("Developer mode enabled")
            print("Scraper initialized")

    def __del__ (self):
        """Destructor to close the driver when the object is deleted"""
        try:
            if self.driver:
                self.driver.quit()
        except WebDriverException as e:
            print(f"Error closing the driver: {e}")
        if self.developer_mode:
            print("Scraper deleted")

    def start_driver(self):
        """Start the Chrome WebDriver using the ChromeDriverManager and a custom user-data-dir profile which is signed in to TripAdvisor"""
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("user-data-dir=C:\\Users\\m7mad\\TripAdvisorProfile")
            
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install(), options=options)
            )
            if self.developer_mode:
                print("Driver started successfully")
        except Exception as e:
            print(f"Error starting the driver: {e}")
            time.sleep(20)
            sys.exit(1)
    
    def get_reviews_links(self):
        """Get the links to the reviews by getting the total number of reviews from the base URL (GIVEN) and generating the links"""
        try:
            self.driver.get(self.url)
            showing_results_text = self.driver.find_element(
                By.XPATH, "//div[contains(text(),'Showing results')]"
            ).text
            total_reviews = int(showing_results_text.split("of")[-1].strip())
            links = generate_links(total_reviews, self.url)
            if self.developer_mode:
                print(f"Total reviews: {total_reviews}")
                print(f"Links generated: {len(links)}")
                print(f"First Link: {links[0]}")
                print(f"Last Link: {links[-1]}")
    
            for link in links:
                self.links.append(link)

        except WebDriverException as e:
            print(f"Error getting the reviews links: {e}")
            time.sleep(20)
            sys.exit(1)

    def get_reviews(self):
        """Get the HTML content of the links got from the reviews links on 5 seconds intervals"""
        """ Scrape the reviews from the HTML content"""
        try:
            for link in self.links:
                if self.developer_mode:
                    print(f"Getting the HTML for: {link}")
                self.driver.get(link)
                self.html = self.driver.page_source
                self.scrape_reviews()
                time.sleep(5)

        except WebDriverException as e:
            print(f"Error getting the HTML: {e}")
            time.sleep(20)
            sys.exit(1)

    def scrape_reviews(self):
        soup = parse_html(self.html)
        reviews_div = soup.select_one(
            "div[id^='tab-data-qa-reviews'] div div:last-child"
        )
        reviews = reviews_div.select(
            "div[data-automation='tab'] div[data-automation='reviewCard']"
        )
        for review in reviews:
            reviewer_name = review.select_one("div:nth-child(1) span a").text
            review_profile = f"https://www.tripadvisor.com{review.select_one("div:nth-child(1) span a")["href"]}"
            review_title = review.select_one("a span").text
            review_stars = len(review.select("div>svg path"))

            if self.developer_mode:
                print(f"Reviewer Name: {reviewer_name}")
            
            temp_check = review.select_one("div:nth-child(4)")
            if len(temp_check.find_all("div")) > 1:
                review_trip_date = None
                traveler_types = None
                review_text = temp_check.select_one("span span").text
            else:
                review_trip_date = temp_check.text.split("•")[0].strip()
                traveler_types = temp_check.text.split("•")[1].strip()
                review_text = review.select_one("div:nth-child(5) span span").text
            
            # get the last div 
            last_div = review.select("div")[-1]
            if len(last_div.find_all("a")) > 0:
                review_writing_date = review.select("div")[-2].select_one("div").text
            else:
                review_writing_date = last_div.select_one("div").text
            
            review = Review(reviewer_name, review_profile, review_title, review_stars, review_trip_date, traveler_types, review_text , review_writing_date)
            
            with open(self.output_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(review.to_csv())
            
            if self.developer_mode:
                print(review)

    def close_driver(self):
        try:
            self.driver.quit()
        except WebDriverException as e:
            print(f"Error closing the driver: {e}")
            time.sleep(20)
            sys.exit(1)

    def scrape(self, url):
        self.url = url
        self.start_driver()
        self.get_reviews_links()
        self.get_reviews()
        self.close_driver()


def generate_links(total_reviews, url):
    """Generate the links to scrape the reviews"""
    links = []
    for i in range(0, total_reviews + 1, 10):
        links.append(prepare_url(url, i))

def prepare_url(url, increment=10):
    """Takes a url and checks if the it has a number of reviews (-orNN-)if so it increments it by 10 if not it adds -or10 to the url"""
    url_parts = url.split("-or")
    print(f"URL parts: {url_parts}")
    if len(url_parts) > 1:
        current_number = int(url_parts[-1].split("-")[0])
        new_number = current_number + increment
        url_parts[-1] = f"{new_number}-" + "-".join(url_parts[-1].split("-")[1:])
        return "-or".join(url_parts)
    else:
        return url[:-5] + f"-or{increment}" + url[-5:]


def parse_html(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except Exception as e:
        print(f"Error parsing the HTML: {e}")
        return None
