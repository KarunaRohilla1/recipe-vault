import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="My Recipe Vault",
    page_icon="☕",
    layout="wide"
)

# =====================================================
# LOAD CSS
# =====================================================

with open("styles/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# =====================================================
# CONFIG
# =====================================================

PIN = st.secrets["planner_pin"]
sheet_id = st.secrets["sheet_id"]

# =====================================================
# LOAD MASTER SHEET
# =====================================================

master_sheet = "Master"

master_url = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{sheet_id}/gviz/tq?tqx=out:csv&sheet={master_sheet}"
)

df = pd.read_csv(master_url)

df.columns = df.columns.str.strip()

# =====================================================
# CLEAN DATA
# =====================================================

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

# =====================================================
# UNIQUE CATEGORIES
# =====================================================

all_categories = set()

for row in df["Category"]:

    categories = str(row).split(",")

    for category in categories:

        cleaned = category.strip()

        if cleaned:
            all_categories.add(cleaned)

all_categories = sorted(list(all_categories))

# =====================================================
# UNIQUE TAGS
# =====================================================

all_tags = set()

for row in df["Tags"]:

    tags = str(row).split(",")

    for tag in tags:

        cleaned = tag.strip()

        if cleaned:
            all_tags.add(cleaned)

all_tags = sorted(list(all_tags))

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Kitchen")
st.sidebar.caption("Luxury café style recipe library")

page = st.sidebar.radio(
    "",
    [
        "Recipes",
        "Meal Planner 🔒"
    ]
)

selected_category = st.sidebar.radio(
    "Browse",
    ["All Recipes"] + all_categories
)

# =====================================================
# FILTER RECIPES
# =====================================================

filtered_df = df.copy()

if selected_category != "All Recipes":

    filtered_df = filtered_df[
        filtered_df["Category"].str.contains(
            selected_category,
            case=False,
            na=False
        )
    ]

# =====================================================
# MEAL PLANNER PAGE
# =====================================================

if page == "Meal Planner 🔒":

    st.title("Weekly Meal Planner")

    if "planner_unlocked" not in st.session_state:
        st.session_state.planner_unlocked = False

    # =====================================================
    # PIN LOCK
    # =====================================================

    if not st.session_state.planner_unlocked:

        col1, col2, col3 = st.columns([1, 1.1, 1])

        with col2:

            st.markdown(
                """
                <div class="pin-card">
                    <div class="pin-title">
                        Private Planner
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            entered_pin = st.text_input(
                "Enter PIN",
                type="password",
                label_visibility="collapsed"
            )

            if entered_pin == PIN:
                st.session_state.planner_unlocked = True
                st.rerun()

            elif entered_pin:
                st.error("Wrong PIN")

        st.stop()

    # =====================================================
    # LOAD PLANNER SHEET
    # =====================================================

    planner_sheet = "MealPlanner"

    planner_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/gviz/tq?tqx=out:csv&sheet={planner_sheet}"
    )

    planner_df = pd.read_csv(planner_url)

    planner_df.columns = planner_df.columns.str.strip()

    planner_df = planner_df.fillna("")

    # =====================================================
    # DAYS
    # =====================================================

    days = [
        "Saturday",
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]

    meal_columns = [
        "Breakfast",
        "Lunch",
        "Dinner",
        "Snacks"
    ]

    # =====================================================
    # PLANNER DISPLAY
    # =====================================================

    for i in range(0, len(days), 2):

        col1, col2 = st.columns(2)

        pair = days[i:i+2]

        for idx, day in enumerate(pair):

            column = col1 if idx == 0 else col2

            with column:

                st.markdown(f"## {day}")

                day_row = planner_df[
                    planner_df["Day"].str.strip().str.lower()
                    == day.lower()
                ]

                if day_row.empty:
                    continue

                day_row = day_row.iloc[0]

                for meal_type in meal_columns:

                    meal = str(day_row.get(meal_type, "")).strip()

                    if not meal:
                        continue

                    st.markdown(
                        f"<div class='meal-label'>{meal_type}</div>",
                        unsafe_allow_html=True
                    )

                    meal_parts = [
                        part.strip()
                        for part in meal.split("+")
                    ]

                    linked_parts = []

                    for part in meal_parts:

                        recipe_match = df[
                            df["Recipe Name"]
                            .str.strip()
                            .str.lower()
                            == part.lower()
                        ]

                        if not recipe_match.empty:

                            recipe_link = recipe_match.iloc[0]["Recipe Link"]

                            linked_parts.append(
                                f'''
                                <a href="{recipe_link}"
                                   target="_blank"
                                   class="meal-link">
                                   {part}
                                </a>
                                '''
                            )

                        else:
                            linked_parts.append(part)

                    final_meal = " + ".join(linked_parts)

                    st.markdown(
                        f"""
                        <div class="meal-item">
                            {final_meal}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# =====================================================
# RECIPES PAGE
# =====================================================

else:

    st.title("My Recipe Vault")
    st.caption("Luxury café style recipe library")

    # =====================================================
    # SEARCH
    # =====================================================

    search = st.text_input(
        "Search recipes",
        placeholder="Search by recipe name..."
    )

    if search:

        filtered_df = filtered_df[
            filtered_df["Recipe Name"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # =====================================================
    # FILTERS
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        sort_by = st.selectbox(
            "Sort By",
            [
                "Recipe Name",
                "Protein",
                "Calories"
            ]
        )

    with col2:
        order = st.selectbox(
            "Order",
            ["Ascending", "Descending"]
        )

    with col3:
        selected_tag = st.selectbox(
            "Filter By Tag",
            ["All Tags"] + all_tags
        )

    # =====================================================
    # TAG FILTER
    # =====================================================

    if selected_tag != "All Tags":

        filtered_df = filtered_df[
            filtered_df["Tags"].str.contains(
                selected_tag,
                case=False,
                na=False
            )
        ]

    # =====================================================
    # SORT
    # =====================================================

    ascending = order == "Ascending"

    filtered_df = filtered_df.sort_values(
        by=sort_by,
        ascending=ascending
    )

    # =====================================================
# MOBILE DETECTION
# =====================================================

st.markdown("""
<style>
@media (max-width: 768px) {
    .desktop-table {
        display: none;
    }
}

@media (min-width: 769px) {
    .mobile-cards {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# MOBILE CARDS
# =====================================================

for _, row in filtered_df.iterrows():

    st.markdown(f"""<div class="mobile-recipe-card"><h3>{row['Recipe Name']}</h3><div class="mobile-category">{row['Category']}</div>
                <div class="mobile-macros">Protein: {row['Protein']}g • Carbs: {row['Carbs']}g • Fats: {row['Fats']}g • {row['Calories']} kcal</div>
                <a href="{row['Recipe Link']}" target="_blank">Open Recipe →</a></div>""",unsafe_allow_html=True)

# =====================================================
# DESKTOP TABLE
# =====================================================

st.markdown('<div class="desktop-table">', unsafe_allow_html=True)

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

for col, title in zip(header_cols, headers):

    col.markdown(
        f"<div class='table-header'>{title}</div>",
        unsafe_allow_html=True
    )

st.markdown("<hr>", unsafe_allow_html=True)

for _, row in filtered_df.iterrows():

    cols = st.columns([3, 2, 1, 1, 1, 1, 1])

    cols[0].markdown(
        f"<div class='table-cell'>{row['Recipe Name']}</div>",
        unsafe_allow_html=True
    )

    cols[1].markdown(
        f"<div class='table-cell'>{row['Category']}</div>",
        unsafe_allow_html=True
    )

    cols[2].markdown(
        f"<div class='table-cell'>{row['Protein']}g</div>",
        unsafe_allow_html=True
    )

    cols[3].markdown(
        f"<div class='table-cell'>{row['Carbs']}g</div>",
        unsafe_allow_html=True
    )

    cols[4].markdown(
        f"<div class='table-cell'>{row['Fats']}g</div>",
        unsafe_allow_html=True
    )

    cols[5].markdown(
        f"<div class='table-cell'>{row['Calories']}</div>",
        unsafe_allow_html=True
    )

    cols[6].markdown(
        f"""
        <a href="{row['Recipe Link']}"
           target="_blank"
           class="open-link">
           Open →
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)