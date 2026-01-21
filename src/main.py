import argparse

from scraper import scrape_products
from excel_writer import save_product_list, sql_filter_and_save

DEFAULT_URL = ("https://www.wildberries.ru/catalog/0/"
    "search.aspx?search=%D0%BF%D0%B0%D0%BB%D1%8C%D1%82%D0%BE%20%"
    "D0%B8%D0%B7%20%D0%BD%D0%B0%D1%82%D1%83%D1%80%D0%B0%D0%BB%D1%"
    "8C%D0%BD%D0%BE%D0%B9%20%D1%88%D0%B5%D1%80%D1%81%D1%82%D0%B8"
)

def main():
    parser = argparse.ArgumentParser(description="Wildberries item scraper & query tool")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    scrape_parser = subparsers.add_parser("scrape")
    
    scrape_parser.add_argument("--url", default=DEFAULT_URL, 
                               help="Search something on the website, then copy and paste the url here")
    scrape_parser.add_argument("--scrolls", type=int, default=10)
    scrape_parser.add_argument("--v_width", type=int, default=1366)
    scrape_parser.add_argument("--v_height", type=int, default=768)
    scrape_parser.add_argument("--load_wait", type=int, default=4000)
    scrape_parser.add_argument("--scroll_wait_max", type=int, default=600)
    scrape_parser.add_argument("--scroll_wait_min", type=int, default=400)
    scrape_parser.add_argument("--next_wait_max", type=int, default=4000)
    scrape_parser.add_argument("--next_wait_min", type=int, default=1000)
    scrape_parser.add_argument("--filename", default="products.xlsx")
    
    sql_parser = subparsers.add_parser("sql")
    sql_parser.add_argument("query",
                            nargs="?",
                            help="SQL query to execute", 
                            default=('SELECT * FROM products WHERE \"Рейтинг\" '
                            '>= 4.5 AND \"Цена\" < 10000 AND \"Страна производства\"=\'Россия\''))
    sql_parser.add_argument("--input", default="products.xlsx")
    sql_parser.add_argument("--output", default="query_results.xlsx")

    args = parser.parse_args()

    if args.command == "scrape":
        product_list = scrape_products(
            url=args.url,
            scroll_amount=args.scrolls,
            viewport_width=args.v_width,
            viewport_height=args.v_height,
            load_wait=args.load_wait,
            scroll_wait_min=args.scroll_wait_min,
            scroll_wait_max=args.scroll_wait_max,
            next_product_wait_max=args.next_wait_max,
            next_product_wait_min=args.next_wait_min,
        )
        save_product_list(
            product_list=product_list,
            filename=args.filename
        )

    elif args.command == "sql":
        sql_filter_and_save(
            query=args.query, 
            input_filename=args.input,
            output_filename=args.output
        )

if __name__ == "__main__":
    main()