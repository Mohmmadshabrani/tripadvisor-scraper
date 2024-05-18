import sys

from modules.Scraper import Scraper

def main():
    url = "https://www.tripadvisor.com/AttractionProductReview-g298101-d26586680-3_Hour_Shore_Dive_or_Snorkel_Experiences_in_Aqaba-Aqaba_Al_Aqabah_Governorate.html"
    scraper = Scraper(headless=False , output_path="reviews.csv")
    status = scraper.scrape(url)
    if status:
        print("Scraping was successful")
    else:
        print("Scraping failed")
        sys.exit(1)
    


if __name__ == "__main__":
    main()
