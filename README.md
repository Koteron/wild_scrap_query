# Wildberries scrape&query tool

A web data extraction utility that retrieves HTML content, parses structured information from it, and optionally automates browser behavior, with Python positioned as the most ergonomic implementation and Java as a more enterprise-oriented alternative.

#### What can it do:
1. Scrape Wildberries search page for products and then scrape each product page for details on them
2. Save the scraped data to xlsx
3. Query the saved data with SQL

## How to run

0. You need python(https://docs.python.org/3/using/index.html) installed in order to run it
1. Create a virtual environment

```
python -m venv <env_name>
```
3. Activate the virtual environment with appropriate script
```
.\<env_name>\Scripts\Activate.ps1
```
4. Install the requirements
```
pip install -r requirements.txt
```
5. Run the cli commands

## CLI description

### `scrape` - Scrape products from Wildberries

The scrape command launches a browser-based scraper, collects product information from a Wildberries search page, and saves the results to an Excel file.

By default, the tool is preconfigured to scrape a Wildberries search page for wool coats, but all scraping parameters can be customized via CLI flags.

#### Example
```
python main.py scrape
```

#### Options

- `--url` - Wildberries search URL to scrape

- `--scrolls` - Number of scrolls to load additional products

- `--v_width`, `--v_height` - Browser viewport size

- `--load_wait` - Initial page load wait time (ms)

- `--scroll_wait_min`, `--scroll_wait_max` - Randomized delay between scrolls (ms)

- `--next_wait_min`, `--next_wait_max` - Delay between opening products (ms)

- `--filename` - Output Excel file name (default: products.xlsx)

#### Example with custom parameters

```
python .\src\main.py scrape --scrolls 50 --load_wait 2000
```

### `sql` - Query scraped data

This command allows executing SQL queries against the previously scraped dataset and exporting the query results to Excel.

So all that SQL allows is possible to execute on the scraped data - filtering, aggregating, sorting, etc.

#### Example (for powershell)

Selecting all the products with rating not lower than 4.5, price lower than 10000 and country of manufacturing being Russia

```
python .\src\main.py query 'SELECT * FROM products WHERE \"Рейтинг\" >= 4.5 AND \"Цена\" < 10000 AND \"Страна производства\"=''Россия'''
```

#### Options

- `query` (positional) — SQL query to execute (default: SELECT * FROM products WHERE \"Рейтинг\" >= 4.5 AND \"Цена\" < 10000 AND \"Страна производства\"=''Россия'')

- `--input` - Input Excel file with scraped data (default: products.xlsx)

- `--output` - Output Excel file name with query results (default: query_results.xlsx)

