import math
from tools import inventory, sales, suppliers, sales_analysis


def generate_procurement_plan():

    print("\n========== SUPPLYCHAINIQ PROCUREMENT PLAN ==========")

    for _, product in inventory.iterrows():

        product_id = product["product_id"]
        product_name = product["product_name"]
        stock = int(product["stock"])
        safety_stock = int(product["safety_stock"])

        demand = sales_analysis(product_id)

        if demand is None or demand <= 0:
            print(f"\n{product_name}: Demand data unavailable.")
            continue

        # Get suppliers for this product
        options = suppliers[
            suppliers["product_id"] == product_id
        ].copy()

        if options.empty:
            print(f"\n{product_name}: No supplier available.")
            continue

        # Calculate urgency
        options["days_until_stockout"] = (
            stock / demand
        )

        # Normalize supplier metrics
        options["cost_score"] = (
            options["price"] / options["price"].max()
        )

        options["time_score"] = (
            options["lead_time"] / options["lead_time"].max()
        )

        options["reliability_score"] = (
            options["reliability"] / 100
        )

        # Lower score means better supplier
        options["score"] = (
            0.35 * options["cost_score"]
            + 0.40 * options["time_score"]
            + 0.25 * (1 - options["reliability_score"])
        )

        # Prioritize faster delivery for urgent products
        if stock / demand <= options["lead_time"].min():
            selected = options.sort_values(
                ["lead_time", "score"]
            ).iloc[0]
        else:
            selected = options.sort_values(
                "score"
            ).iloc[0]

        lead_time = int(selected["lead_time"])

        # Target: supplier lead time + 7 days of coverage
        target_stock = math.ceil(
            demand * (lead_time + 7) + safety_stock
        )

        order_quantity = max(
            0, target_stock - stock
        )

        estimated_cost = (
            order_quantity * float(selected["price"])
        )

        print(f"\nPRODUCT: {product_name}")
        print("----------------------------------")
        print("Current Stock:", stock)
        print("Average Daily Demand:", demand)
        print("Selected Supplier:", selected["supplier_name"])
        print("Supplier Lead Time:", lead_time, "days")
        print("Recommended Order:", order_quantity, "units")
        print("Estimated Purchase Cost: ₹", round(estimated_cost, 2))

        if order_quantity > 0:
            print("DECISION: PURCHASE RECOMMENDED")
        else:
            print("DECISION: NO PURCHASE REQUIRED")

        print("Reason: Replenishment target includes delivery time,")
        print("7 additional days of demand and safety stock.")


if __name__ == "__main__":
    generate_procurement_plan()