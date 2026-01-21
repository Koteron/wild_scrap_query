import random

from playwright.sync_api import sync_playwright

# no reason to make these too big or too small, so not cli args
MIN_SCROLL_SIZE = 400
MAX_SCROLL_SIZE = 600

def scrape_products(
        url,
        scroll_amount,
        viewport_width,
        viewport_height,
        load_wait,
        scroll_wait_max,
        scroll_wait_min,
        next_product_wait_max,
        next_product_wait_min,
    ):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            viewport={"width": viewport_width, "height": viewport_height}
        )

        page = context.new_page()
        page.goto(url, wait_until="load")
        page.wait_for_timeout(load_wait)

        # Scroll to capture more products
        for i in range(scroll_amount):
            page.evaluate(f"window.scrollBy(0, {random.uniform(MIN_SCROLL_SIZE, MAX_SCROLL_SIZE)})")
            page.wait_for_timeout(random.uniform(scroll_wait_min, scroll_wait_max))

        products = page.locator(".product-card__link")
        count = products.count()

        product_detail_urls = list()
        for i in range(count):
            product = products.nth(i)
            product_detail_urls.append(product.get_attribute("href"))

        print(f"Search page scraped. Found {len(product_detail_urls)} products")

        product_list = list()

        for i in range(len(product_detail_urls)):
            product_url = product_detail_urls[i]
            product = {}

            page.goto(product_url, wait_until="load")
            print(f"{i+1} / {len(product_detail_urls)} scraped. Now scraping: {product_url}")

            page.wait_for_timeout(load_wait)

            product["Ссылка на товар"] = product_url

            number_row = page.locator("tr", has_text="Артикул")
            product["Артикул"] = int(number_row.locator("td span").first.inner_text())

            product["Название"] = page.locator('[class*="productTitle"]').inner_text()

            is_sold_out = page.locator('[class*=soldOutProduct]').count() == 1
            price_raw_locator = page.locator('[class*="priceBlockPrice"]')
            if not is_sold_out:
                product["Цена"] = int(price_raw_locator.locator("ins").inner_text()
                                  .replace('&nbsp;', '').replace('₽', '').replace(' ', ''))
            elif page.locator('[class*=soldOutProduct]').count() != 0:
                product["Цена"] = 0

            image_containers = page.locator('[class*="imgContainer"]')
            # There may be 2 images - preview and the real one there. last should pick the real one
            product["Ссылки на изображения"] = image_containers.nth(0).locator("img").last.get_attribute("src") 
            count = image_containers.count()
            for i in range(1, count):
                if i != count:
                    product["Ссылки на изображения"] += ', '
                product["Ссылки на изображения"] += image_containers.nth(i).locator("img").last.get_attribute("src")

            seller_name = page.locator(
                '[class*=sellerInfoNameDefaultText], [class*=sellerInfoDefaultNameText]')
            # There won't be these classes if it's a user seller
            if seller_name.count() == 1:
                product["Название селлера"] = seller_name.inner_text()
            else:
                product["Название селлера"] = page.locator(
                    '[class*=cTocSellerUserButtonTitle]').locator("span").first.inner_text()

            seller_path = page.locator('[class*=sellerInfoButtonLink] [class*=cTocSellerUserButton]')
            product["Ссылка на селлера"] = "https://www.wildberries.ru"
            # If it's wildberries itself there won't be any link there
            if seller_path.count() == 1:
                product["Ссылка на селлера"] += seller_path.get_attribute("href")
            
            sizes = page.locator('[class*=sizesListSize]')
            count = sizes.count()
            if count > 0:
                product["Размеры"] = sizes.nth(0).inner_text()
                for i in range(1, count):
                    if i != count:
                        product["Размеры"] += ', '
                    product["Размеры"] += sizes.nth(i).inner_text()

            review_locator = page.locator('[class*=productReviewRating]')
            product["Рейтинг"] = 0.0
            product["Количество отзывов"] = 0
            # Not sellers don't have reviews
            if review_locator.count() == 1:
                product_review_raw = review_locator.inner_text().split(' ')
                if len(product_review_raw) > 2:
                    product["Рейтинг"] = float(product_review_raw[0].replace(',', '.'))
                    product["Количество отзывов"] = int(product_review_raw[2].replace(' ', ''))

            if is_sold_out:
                product["Остатки по товару"] = 0
            else:
                left_list = page.locator('[class*=qtyTrigger]').locator("span")
                if left_list.count() > 0:
                    quantity_text = left_list.inner_text().split(' ')
                    product["Остатки по товару"] = int(quantity_text[1])
                else:
                    product["Остатки по товару"] = "Не указано"
            

            chars_button = page.locator("span", has_text='Характеристики и описание')
            if chars_button.count() == 1:
                page.locator("span", has_text='Характеристики и описание').click()
            else:
                page.locator("button", has_text='Все характеристики').click()

            description = page.locator(
                '[class*="descriptionText"], [class*="DescriptionText"]'
            )
            if description.count() == 1:
                product["Описание"] = description.first.text_content()

            char_tables = page.locator('[data-testid*=product_additional_information]').locator('tbody tr')
            product["characteristics"] = {}

            for i in range(char_tables.count()):
                row = char_tables.nth(i)
                key = row.locator("th").inner_text().strip()
                value = row.locator("td").inner_text().strip()
                product["characteristics"][key] = value

            product_list.append(product)

            page.wait_for_timeout(random.uniform(next_product_wait_min, next_product_wait_max))
        
        print("Scraping finished")

    return product_list