
import streamlit as st
import pandas as pd
import plotly.express as px

from tools import (
    inventory,
    sales_analysis,
    supplier_comparison
)

from local_agent import ask_local_agent

# PAGE CONFIG
st.set_page_config(
    page_title="SupplyChainIQ",
    page_icon="📦",
    layout="wide"
)

# CUSTOM DESIGN
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: white;
}
[data-testid="stMetric"] {
    background: #17243a;
    padding: 20px;
    border-radius: 12px;
}
h1, h2, h3 {
    color: #64d8cb;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.title("📦 SupplyChainIQ")
st.caption("AI-Powered Supply Chain Intelligence Platform")

# SIDEBAR
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Inventory",
        "Demand Analytics",
        "Supplier Analysis",
        "AI Assistant",
        "Procurement"
    ]
)

# STOCKOUT CALCULATIONS
risk_count = 0
total_stock = int(inventory["stock"].sum())

for _, product in inventory.iterrows():

    demand = sales_analysis(product["product_id"])

    if demand is None or demand <= 0:
        continue

    suppliers_data = supplier_comparison(
        product["product_id"]
    )

    if suppliers_data.empty:
        continue

    lead_time = suppliers_data.iloc[0]["lead_time"]

    reorder_point = (
        demand * lead_time
        + product["safety_stock"]
    )

    if product["stock"] <= reorder_point:
        risk_count += 1

# DASHBOARD
if page == "Dashboard":

    st.subheader("Executive Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Products",
        len(inventory)
    )

    col2.metric(
        "Total Stock Units",
        total_stock
    )

    col3.metric(
        "Products at Risk",
        risk_count
    )

    st.divider()

    st.subheader("Inventory Overview")

    fig = px.bar(
        inventory,
        x="product_name",
        y="stock",
        color="stock",
        title="Current Stock Levels",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Stockout Alerts")

    for _, product in inventory.iterrows():

        demand = sales_analysis(product["product_id"])

        if demand is None or demand <= 0:
            continue

        suppliers_data = supplier_comparison(
            product["product_id"]
        )

        if suppliers_data.empty:
            continue

        lead_time = suppliers_data.iloc[0]["lead_time"]

        reorder_point = (
            demand * lead_time
            + product["safety_stock"]
        )

        if product["stock"] <= reorder_point:

            st.error(
                f"⚠️ {product['product_name']} needs attention!"
            )

        else:

            st.success(
                f"✅ {product['product_name']} stock is safe."
            )

# INVENTORY
elif page == "Inventory":

    st.subheader("Inventory Management")

    st.dataframe(
        inventory,
        use_container_width=True
    )

    search = st.text_input("Search Product ID")

    if search:
        filtered = inventory[
            inventory["product_id"].astype(str).str.contains(
                search,
                case=False
            )
        ]

        st.dataframe(filtered)

# DEMAND ANALYTICS
elif page == "Demand Analytics":

    st.subheader("Sales and Demand Analytics")

    demand_data = []

    for _, product in inventory.iterrows():

        demand = sales_analysis(product["product_id"])

        demand_data.append({
            "Product": product["product_name"],
            "Average Daily Demand": demand
        })

    df = pd.DataFrame(demand_data)

    st.dataframe(df)

    fig = px.bar(
        df,
        x="Product",
        y="Average Daily Demand",
        template="plotly_dark",
        title="Average Daily Product Demand"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# SUPPLIER ANALYSIS
elif page == "Supplier Analysis":

    st.subheader("Supplier Comparison")

    product_id = st.selectbox(
        "Choose Product",
        inventory["product_id"].tolist()
    )

    supplier_data = supplier_comparison(product_id)

    st.dataframe(
        supplier_data,
        use_container_width=True
    )

# AI ASSISTANT
elif page == "AI Assistant":

    st.subheader("SupplyChainIQ Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask about inventory, suppliers or procurement..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Analysing supply chain data..."):

                answer = ask_local_agent(question)

                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

# PROCUREMENT
elif page == "Procurement":

    st.subheader("Procurement Planning")

    st.write(
        "Generate a procurement recommendation "
        "using current inventory and supplier data."
    )

    if st.button("Generate Procurement Plan"):

        from procurement import generate_procurement_plan

        with st.spinner("Generating procurement plan..."):

            generate_procurement_plan()

        st.success(
            "Procurement analysis completed. "
            "Check the VS Code terminal for the detailed report."
        )