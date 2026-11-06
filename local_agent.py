
from tools import (
    inventory,
    sales_analysis,
    supplier_comparison
)

from procurement import generate_procurement_plan


def ask_local_agent(question):

    q = question.lower()

    # INVENTORY
    if "inventory" in q or "stock" in q:
        return inventory.to_string(index=False)

    # DEMAND ANALYSIS
    elif "demand" in q or "sales" in q:

        results = []

        for pid in inventory["product_id"]:
            demand = sales_analysis(pid)

            results.append(
                f"{pid}: {demand} units/day"
            )

        return "\n".join(results)

    # SUPPLIER ANALYSIS
    elif "supplier" in q:

        results = []

        for pid in inventory["product_id"]:
            data = supplier_comparison(pid)

            results.append(
                f"\nProduct: {pid}\n"
                + data.to_string(index=False)
            )

        return "\n".join(results)

    # PROCUREMENT
    elif "procurement" in q or "purchase" in q:

        generate_procurement_plan()

        return "Procurement plan generated successfully."

    # STOCKOUT RISK
    elif "risk" in q or "reorder" in q:

        results = []

        for _, product in inventory.iterrows():

            pid = product["product_id"]
            demand = sales_analysis(pid)

            if demand is None or demand <= 0:
                continue

            options = supplier_comparison(pid)

            if options.empty:
                continue

            lead_time = options.iloc[0]["lead_time"]

            reorder_point = (
                demand * lead_time
                + product["safety_stock"]
            )

            status = (
                "URGENT REORDER"
                if product["stock"] <= reorder_point
                else "STOCK SAFE"
            )

            results.append(
                f"{product['product_name']}: {status}"
            )

        return "\n".join(results)

    return """
    Welcome to SupplyChainIQ!

    I can help with:
    1. Inventory analysis
    2. Sales and demand analysis
    3. Supplier comparison
    4. Stockout detection
    5. Procurement planning
    """


if __name__ == "__main__":

    print("\n================================")
    print("     SUPPLYCHAINIQ ASSISTANT")
    print("        LOCAL MODE")
    print("================================")

    while True:

        question = input("\nYou: ")

        if question.lower() == "exit":
            print("Goodbye!")
            break

        try:
            answer = ask_local_agent(question)
            print("\nSupplyChainIQ:\n", answer)

        except Exception as error:
            print("Error:", error)