import duckdb
import pandas as pd


def save_product_list(filename, product_list):
    print("Saving the scraped products...")
    rows = []

    for product in product_list:
        characteristics = product.pop("characteristics", {})
        product.update(characteristics)
        rows.append(product)

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False)
    print(f"The scraped products were saved to {filename}")


def sql_filter_and_save(input_filename, output_filename, query):
    print(f"Reading {input_filename}...")
    df = pd.read_excel(input_filename)
    print(f"Read {len(df)} products")
    con = duckdb.connect()
    con.register("products", df)
    print(f"Executing given sql query and saving results...")
    result_df = con.execute(query).df()
    result_df.to_excel(output_filename, index=False)
    print(f"Query was executed and the results were saved to {output_filename}")
