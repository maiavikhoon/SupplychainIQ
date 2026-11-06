import pandas as pd

# Load datasets

inventory = pd.read_csv("data/inventory.csv")
sales = pd.read_csv("data/sales.csv")
suppliers = pd.read_csv("data/suppliers.csv")


# TOOL 1: Inventory Lookup

def inventory_lookup():

    print("\n--- INVENTORY REPORT ---")

    print(inventory)


# TOOL 2: Sales History Analysis

def sales_analysis(product_id):

    product_sales = sales[
        sales["product_id"] == product_id
    ]

    if product_sales.empty:
        return None

    average = product_sales["units_sold"].mean()

    return round(average, 2)


# TOOL 3: Supplier Comparison

def supplier_comparison(product_id):

    available = suppliers[
        suppliers["product_id"] == product_id
    ]

    available = available.sort_values(
        by=["lead_time", "reliability"],
        ascending=[True, False]
    )

    return available


# TOOL 4: Reorder Calculation

def reorder_calculation(product_id):

    product = inventory[
        inventory["product_id"] == product_id
    ]

    if product.empty:
        return None

    stock = int(product.iloc[0]["stock"])

    safety_stock = int(
        product.iloc[0]["safety_stock"]
    )

    demand = sales_analysis(product_id)

    if demand is None:
        return None

    best_supplier = supplier_comparison(product_id)

    if best_supplier.empty:
        return None

    lead_time = int(
        best_supplier.iloc[0]["lead_time"]
    )

    reorder_point = (
        demand * lead_time + safety_stock
    )

    stockout_days = stock / demand if demand > 0 else None

    print("\n--- REORDER REPORT ---")

    print("Product:", product_id)
    print("Current Stock:", stock)
    print("Average Daily Demand:", demand)
    print("Supplier Lead Time:", lead_time)
    print("Reorder Point:", reorder_point)
    print("Estimated Stockout Days:", stockout_days)

    if stock <= reorder_point:
        print("STATUS: REORDER REQUIRED")
    else:
        print("STATUS: STOCK SUFFICIENT")

# TOOL 5: Stockout Risk Detection

def stockout_detection():

    print("\n--- STOCKOUT RISK REPORT ---")

    for index, product in inventory.iterrows():

        product_id = product["product_id"]

        stock = product["stock"]

        demand = sales_analysis(product_id)

        suppliers_data = supplier_comparison(product_id)

        if demand is None or suppliers_data.empty:
            continue

        lead_time = suppliers_data.iloc[0]["lead_time"]

        expected_demand = demand * lead_time

        reorder_point = expected_demand + product["safety_stock"]

        print("\nProduct:", product["product_name"])
        print("Current Stock:", stock)
        print("Expected Demand:", expected_demand)

        if stock < expected_demand:

            print("RISK: CRITICAL STOCKOUT RISK")

        elif stock <= reorder_point:

            print("RISK: REORDER REQUIRED")

        else:

            print("RISK: STOCK SAFE")
# TEST OUR TOOLS

if __name__ == "__main__":

    inventory_lookup()

    print("\nAverage Demand:", sales_analysis("P001"))

    print("\nSupplier Comparison:")
    print(supplier_comparison("P001"))

    reorder_calculation("P001")
    stockout_detection()