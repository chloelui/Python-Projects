import requests
import pandas as pd
import time

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from time import sleep

BASE_URL = "https://books.toscrape.com/"

def safe_get(url, retries=3):
    for i in range(retries):
        try:
            return requests.get(url, timeout=10)
        except requests.exceptions.RequestException:
            print(f"Retrying {url} ({i+1}/{retries})")
            sleep(2)

    print(f"FAILED permanently: {url}")
    return None

def get_book_details(url):
    response = safe_get(url)
    if response is None:
        return {
            "upc": None,
            "stock": None,
            "category": None,
            "description": None
        }

    soup = BeautifulSoup(response.text,"html.parser")

    # Store info from table
    table = soup.find("table")

    product_info = {}

    for row in table.find_all("tr"):
        header = row.th.text
        value = row.td.text
        product_info[header] = value

    # Find book category using breadcrumb
    breadcrumb = soup.find("ul",class_="breadcrumb")
    category = (breadcrumb.find_all("li")[2].text.strip())

    # Get product description
    description = ""
    desc_header = soup.find("div",id="product_description")
    if desc_header:
        description = (desc_header.find_next("p").text.strip())

    return {
        "upc":product_info.get("UPC"),
        "stock":product_info.get("Availability"),
        "category":category,
        "description":description
    }

all_books = []

# Scrape all 50 pages
for page in range (1,51):
    page_url = (f"https://books.toscrape.com/catalogue/page-{page}.html")
    response = safe_get(page_url)
    if response is None:
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    # Extract info from all book on a page
    for book in books:
        title = book.h3.a["title"]

        price = book.find("p", class_="price_color").text

        rating = book.find("p", class_="star-rating")["class"][1]

        # Find each book link
        href = book.h3.a["href"]        # Relative book url
        book_url = urljoin(BASE_URL + "catalogue/",href)

        # Get individual book details
        book_details = get_book_details(book_url)

        # Create dict for each book
        all_books.append({
            "title":title,
            "price":price,
            "rating":rating,
            "category":book_details["category"],
            "stock":book_details["stock"],
            "description":book_details["description"],
            "upc":book_details["upc"]
        })

        print(f"Scraped {title}")
        time.sleep(0.2)

# Create CSV file
df = pd.DataFrame(all_books)
df.to_csv("books.csv", index=False)

print(f"Saved {len(all_books)} books")