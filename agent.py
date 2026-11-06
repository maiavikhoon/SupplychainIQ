
import os
from dotenv import load_dotenv
from google import genai

from tools import (
    inventory,
    sales_analysis,
    supplier_comparison
)

from procurement import generate_procurement_plan

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.8-flash"


def get_inventory():
    return inventory.to_dict(orient="records")


def get_demand(product_id: str):
    demand = sales_analysis(product_id)

    return {
        "product_id": product_id,
        "average_daily_demand": demand
    }


def get_suppliers(product_id: str):
    result = supplier_comparison(product_id)

    if result.empty:
        return {"message": "No suppliers found"}

    return result.to_dict(orient="records")


def check_stockout():
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

        results.append({
            "product": product["product_name"],
            "stock": int(product["stock"]),
            "reorder_point": reorder_point,
            "status": (
                "REORDER REQUIRED"
                if product["stock"] <= reorder_point
                else "STOCK SAFE"
            )
        })

    return results


def create_procurement_plan():
    generate_procurement_plan()
    return "Procurement plan generated. See the terminal output."


tools = [
    get_inventory,
    get_demand,
    get_suppliers,
    check_stockout,
    create_procurement_plan
]


chat = client.chats.create(
    model=MODEL,
    config=genai.types.GenerateContentConfig(
        system_instruction="""
        You are SupplyChainIQ, an intelligent
        supply chain management assistant.

        You help users with:
        1. Inventory analysis
        2. Demand analysis
        3. Supplier comparison
        4. Stockout risk detection
        5. Procurement planning

        Use Python tools whenever actual business
        data is required.

        Never invent inventory numbers.
        Explain recommendations clearly.
        Never claim that an order was placed.
        """,
        tools=tools,
        automatic_function_calling=
            genai.types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=5
            )
    )
)


def ask_agent(question):
    try:
        response = chat.send_message(question)

        return response.text or "No response received."

    except Exception as error:
        return f"AI service error: {error}"


if __name__ == "__main__":

    print("\n================================")
    print("       SUPPLYCHAINIQ AI")
    print("================================")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("You: ")

        if question.lower() == "exit":
            break

        answer = ask_agent(question)

        print("\nSupplyChainIQ:", answer, "\n")