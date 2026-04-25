import streamlit as st
import pandas as pd

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="My Recipe Vault",
    page_icon="☕",
    layout="wide"
)

# ---------------------------------------------------
# LOAD CSS
# ---------------------------------------------------

def load_css():
    with open("styles/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

# ---------------------------------------------------
# GOOGLE SHEETS CONNECTION
# ---------------------------------------------------

sheet_id = "15UfbwoR9p8_8iz1eEU54iQuLvojOb7h91YHi4TrR-Y4"
sheet_name = "Master"

csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(csv_url)
df.columns = df.columns.str.strip()

# ---------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------

text_columns = [
    "Recipe Name",
    "Category",
    "Tags",
    "Recipe Link",
    "Source",
    "Notes"
]

for col in text_columns:
    if col in df.columns:
        df[col] = df[col].fillna("")

macro_columns = [
    "Calories",
    "Protein",
    "Carbs",
    "Fats"
]

for col in macro_columns:
    if col in df.columns:
        df[col] = df[col].fillna(0)

# ---------------------------------------------------
# EXTRACT UNIQUE CATEGORIES
# ---------------------------------------------------

all_categories = set()

for row in df["Category"]:
    categories = str(row).split(",")

    for category in categories:
        cleaned = category.strip()

        if cleaned:
            all_categories.add(cleaned)

all_categories = sorted(list(all_categories))

# ---------------------------------------------------
# EXTRACT UNIQUE TAGS
# ---------------------------------------------------

all_tags = set()

for row in df["Tags"]:
    tags = str(row).split(",")

    for tag in tags:
        cleaned = tag.strip()

        if cleaned:
            all_tags.add(cleaned)

all_tags = sorted(list(all_tags))

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("☕ Categories")

selected_category = st.sidebar.radio(
    "Browse",
    ["All Recipes"] + all_categories
)

# ---------------------------------------------------
# TOP SECTION
# ---------------------------------------------------

st.title("My Recipe Vault")
st.caption("Luxury café style recipe library")

search = st.text_input(
    "Search recipes",
    placeholder="Search by recipe name..."
)

# ---------------------------------------------------
# FILTER + SORT SECTION
# ---------------------------------------------------

filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])

# Sort by
with filter_col1:
    sort_by = st.selectbox(
        "Sort By",
        [
            "Recipe Name",
            "Protein",
            "Carbs",
            "Fats",
            "Calories"
        ]
    )

# Sort order
with filter_col2:
    sort_order = st.selectbox(
        "Order",
        [
            "Ascending",
            "Descending"
        ]
    )

# Tag filter
with filter_col3:
    tag_filter = st.selectbox(
        "Filter by Tag",
        ["All Tags"] + all_tags
    )

# ---------------------------------------------------
# FILTER LOGIC
# ---------------------------------------------------

filtered_df = df.copy()

# Search filter
if search:
    filtered_df = filtered_df[
        filtered_df["Recipe Name"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# Category filter
if selected_category != "All Recipes":
    filtered_df = filtered_df[
        filtered_df["Category"].str.contains(
            selected_category,
            case=False,
            na=False
        )
    ]

# Tag filter (works WITH category filter)
if tag_filter != "All Tags":
    filtered_df = filtered_df[
        filtered_df["Tags"].str.contains(
            tag_filter,
            case=False,
            na=False
        )
    ]

# Sort order logic
ascending_order = True if sort_order == "Ascending" else False

filtered_df = filtered_df.sort_values(
    by=sort_by,
    ascending=ascending_order
)

# ---------------------------------------------------
# TABLE HEADER
# ---------------------------------------------------

st.markdown("---")

header_cols = st.columns([3, 2, 1, 1, 1, 1, 1])

headers = [
    "Recipe Name",
    "Category",
    "Protein",
    "Carbs",
    "Fats",
    "Calories",
    "Open"
]

for col, header in zip(header_cols, headers):
    col.markdown(f"**{header}**")

st.markdown(
    """
    <hr style="
        margin: 6px 0;
        border: none;
        border-top: 1px solid #E5DED3;
    ">
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# TABLE ROWS
# ---------------------------------------------------

for _, row in filtered_df.iterrows():

    cols = st.columns([3, 2, 1, 1, 1, 1, 1])

    # Recipe Name
    cols[0].markdown(
        f"""
        <div style="
            font-size: 24px;
            color: #2F2A24;
            line-height: 1.2;
            padding-top: 4px;
        ">
            {row['Recipe Name']}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Category
    cols[1].markdown(
        f"""
        <div style="
            font-size: 24px;
            color: #6B6258;
            padding-top: 6px;
        ">
            {row['Category']}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Protein
    cols[2].markdown(
        f"{row['Protein']}g"
    )

    # Carbs
    cols[3].markdown(
        f"{row['Carbs']}g"
    )

    # Fats
    cols[4].markdown(
        f"{row['Fats']}g"
    )

    # Calories
    cols[5].markdown(
        f"{row['Calories']}"
    )

    # Recipe Link
    if row["Recipe Link"]:
        cols[6].markdown(
            f"[Open →]({row['Recipe Link']})"
        )
    else:
        cols[6].markdown("-")

    st.markdown(
        """
        <div style="margin-top: 10px; margin-bottom: 10px;"></div>
        """,
        unsafe_allow_html=True
    )