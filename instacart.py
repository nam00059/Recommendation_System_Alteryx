import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
from itertools import chain, combinations
import ast

# -------------------------------
# ✅ Page Config and Custom CSS Styling
st.set_page_config(page_title="SmartBasket: Instacart Market Basket Intelligence", layout="wide")

st.markdown("""
<style>
    .main {
        background-color: #F5F5F5;
    }
    h1 {
        color: #43B02A; /* Instacart green */
    }
    h2, h3 {
        color: #333333; /* Dark gray for subheaders */
    }
    p, li, span, div {
        color: #555555; /* Standard text color */
    }
    .stButton button {
        background-color: #43B02A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------
# ✅ Optional: Add Instacart Logo
# Uncomment if you have a logo image file
st.image("instacart.png", width=150)

# -------------------------------
# 🏆 Header & Intro (Matching Brochure)
st.markdown("""
# 🛒 SmartBasket: Market Basket Intelligence for Instacart  
### Delivering real-time, AI-powered product recommendations to maximize **Order Value** and **Customer Retention**.
""")

# -------------------------------
# ✅ Load Data with Error Handling
@st.cache_data
def load_data():
    try:
        products_df = pd.read_excel('productss.xlsx')
        products_df['product_name'] = products_df['product_name'].str.lower()

        output_df = pd.read_csv('retail_market_basket_data.csv')
        output_df['LHS'] = output_df['LHS'].apply(lambda x: set(map(int, ast.literal_eval(x))))
        output_df['RHS'] = output_df['RHS'].apply(lambda x: set(map(int, ast.literal_eval(x))))

        lhs_to_rhs = {frozenset(row['LHS']): row['RHS'] for _, row in output_df.iterrows()}

        # st.success("✅ Data loaded successfully!")
        return products_df, output_df, lhs_to_rhs

    except Exception as e:
        st.error(f"🚩 Error loading data: {e}")
        st.stop()

products_df, output_df, lhs_to_rhs = load_data()

eligible_input_ids = set().union(*[lhs for lhs in lhs_to_rhs.keys()])
eligible_products_df = products_df[products_df['product_id'].isin(eligible_input_ids)]

@st.cache_data
def get_product_name_list():
    return eligible_products_df['product_name'].tolist()

product_names_list = get_product_name_list()

# -------------------------------
# ✅ Matching Functions
def fuzzy_match_optimized(name, limit=5, cutoff=60):
    matches = process.extract(
        name,
        product_names_list,
        scorer=fuzz.WRatio,
        limit=limit
    )
    return [match[0] for match in matches if match[1] >= cutoff]

def match_baskets_fast(selected_ids):
    selected_set = set(selected_ids)
    subsets = sorted(
        chain.from_iterable(combinations(selected_set, r) for r in range(1, len(selected_set) + 1)),
        key=lambda x: len(x),
        reverse=True
    )
    for subset in subsets:
        rhs = lhs_to_rhs.get(frozenset(subset))
        if rhs:
            return rhs
    return set()

def ids_to_names(ids):
    names = products_df[products_df['product_id'].isin(ids)]['product_name'].tolist()
    return [name.title() for name in names]  # Always display recommendations in Title Case

# -------------------------------
# 🟢 Interactive Recommendation Section (Demo)
st.markdown("## 🧺 Recommendation Engine:")

user_input = st.text_input("📝 What’s in your basket? (Type product names, separated by commas):", "")

if user_input:
    input_names = [name.strip().lower() for name in user_input.split(',')]
    selected_products = []

    st.subheader("🔎 Refine your picks:")
    for name in input_names:
        matches = fuzzy_match_optimized(name)
        matches_display = [match.title() for match in matches]  # Display suggestions in Title Case
        if matches_display:
            selected = st.selectbox(f"Suggestions for '{name}':", matches_display)
            selected_products.append(selected)
        else:
            st.warning(f"No eligible recommendations found for '{name}'.")

    selected_ids = eligible_products_df[eligible_products_df['product_name'].isin([p.lower() for p in selected_products])]['product_id'].tolist()

    if selected_ids:
        matched_rhs_ids = match_baskets_fast(selected_ids)
        if matched_rhs_ids:
            recommended_names = ids_to_names(matched_rhs_ids)
            st.success("✨ You might also love these products:")

            # Use HTML & CSS for beautiful tags
            recommendation_tags = ""
            for product in recommended_names:
                recommendation_tags += f"""
                <span style="
                    background-color: #43B02A;
                    color: white;
                    padding: 8px 16px;
                    margin: 4px;
                    border-radius: 20px;
                    display: inline-block;
                    font-size: 16px;
                ">🛒 {product}</span>
                """

            st.markdown(recommendation_tags, unsafe_allow_html=True)
        else:
            st.info("🤔 No recommendations found for your selection.")

st.markdown("""
## 🚀 Our Solution:
- **Real-time Recommendations** using Market Basket Analysis (FP-Growth / Apriori).
- **No-Code Interface** powered by **Streamlit + Alteryx + Snowflake**.
- **Secure, Scalable Cloud Storage using Big Data** (Snowflake).
""")


# -------------------------------
# 🧑‍💼 Footer (Team Info)
st.markdown("---")
st.markdown("""
**Developed by Team-10**  
Dhiraj Patel, Mehulkumar Patel, Ishaan Bhutada, Tsai-Ning Lin, Yoon Nam, Sahil Sinha
""")
