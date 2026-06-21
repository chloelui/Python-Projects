import requests
import pandas as pd
import time

from bs4 import BeautifulSoup

all_books = []

# Scrape all 50 pages
for page in range (1,51):
    url = (f"https://books.toscrape.com/catalogue/page-{page}.html")
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    # Extract info from all book on a page
    for book in books:
        title = book.h3.a["title"]

        price = book.find("p", class_="price_color").text

        rating = book.find("p", class_="star-rating")["class"][1]

        # Create dict for each book
        all_books.append({
            "title":title,
            "price":price,
            "rating":rating
        })

    print(f"Finished page {page}")
    time.sleep(1)       # Wait 1 sec between each request

# Create CSV file
df = pd.DataFrame(all_books)
df.to_csv("books.csv", index=False)

print(f"Saved {len(all_books)} books")