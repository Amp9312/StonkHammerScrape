from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import random
import pandas as pd
import time

BASE_URL = "https://www.warhammer.com/en-US/shop/warhammer-40000"
SESSION_FILE = "auth.json"

def create_session():
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=False)
		context = browser.new_context()
		page = context.new_page()

		print("Opening browser. Solve the CAPTCHA and accept cookies for me, my valiant human!")

		page.goto(BASE_URL)

		#Give hooman some time to be a hooman
		input("\nPress ENTER after you have solved CAPTCHA and accepted cookies, my valiant human!\n")

		#Save session
		context.storage_state(path=SESSION_FILE)
		print(f"Session saved to {SESSION_FILE}")

		browser.close()

def scrape_products():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()

        page.goto(BASE_URL)
        page.wait_for_selector('[data-testid="product-card-details"]')

        for i in range(5):
            try:
                print(f"Clicking 'Show More' ({i+1}/5)...")

                button = page.locator("#show-more")

                if button.is_visible():
                    button.click()
                    page.wait_for_timeout(3000)

                    # simulate user scroll
                    page.mouse.wheel(0, 3000)
                    time.sleep(random.uniform(1, 2))
                else:
                    print("Show More button not visible anymore.")
                    break

            except Exception as e:
                print("Error clicking Show More:", e)
                break

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        products = []

        # Wait explicitly for products to exist
        page.wait_for_selector('[data-testid="product-card-details"]')

        names = page.locator('[data-testid="product-card-details"]')
        prices = page.locator('[data-testid="product-card-current-price"]')

        count = names.count()
        print(f"Found {count} products")

        for i in range(count):
            try:
                name = names.nth(i).inner_text().strip()
                price = prices.nth(i).inner_text().strip()

                print("NAME:", name)
                print("PRICE:", price)
                print("------")

                products.append({
                    "name": name,
                    "price": price.replace("$", "")
                })

                print("Name elements:", names.count())
                print("Price elements:", prices.count())

            except Exception as e:
                print("Error parsing item:", e)
                continue

        browser.close()

    return products

#save to csv for hooman inspection
def save_to_csv(products):
	df=pd.DataFrame(products)
	df.to_csv("Warhammer_40k_products.csv", index=False)
	print(f"Saved {len(products)} products to CSV.")

#main exe
if __name__ == "__main__":
	#session? no? I make
	if not os.path.exists(SESSION_FILE):
		create_session()

	#scrape using saved session with hooman solved challenged
	products=scrape_products()

	#save
	save_to_csv(products)
