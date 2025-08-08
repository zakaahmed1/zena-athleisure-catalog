# streamlit_app.py
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd

st.title("Zena's Amazing Athleisure Catalog")

# ---- Snowflake connection (uses [connections.snowflake] in Secrets) ----
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# ---- Load color/style list once and cache it ----
@st.cache_data(ttl=300)
def load_colors():
    df = session.table("CATALOG_FOR_WEBSITE").select(col("COLOR_OR_STYLE")).collect()
    return [row["COLOR_OR_STYLE"] for row in df]

colors = load_colors()

# UI: pick a color/style
option = st.selectbox("Pick a sweatsuit color or style:", colors)

# Build the image caption
product_caption = f"Our warm, comfortable, {option} sweatsuit!"

# ---- Query product data safely with Snowpark API (avoids SQL injection) ----
prod_df = (
    session.table("CATALOG_FOR_WEBSITE")
    .filter(col("COLOR_OR_STYLE") == option)
    .select("FILE_NAME", "PRICE", "SIZE_LIST", "UPSELL_PRODUCT_DESC", "FILE_URL")
    .to_pandas()
)

if prod_df.empty:
    st.info("No product found for that color/style.")
else:
    row = prod_df.iloc[0]
    price = f"${row['PRICE']:.2f}"
    url = row["FILE_URL"]

    st.image(image=url, width=400, caption=product_caption)
    st.markdown(f"**Price:** {price}")
    st.markdown(f"**Sizes Available:** {row['SIZE_LIST']}")
    st.markdown(f"**Also Consider:** {row['UPSELL_PRODUCT_DESC']}")
