import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# =====================================================
# CONFIG
# =====================================================

SHEET_ID = st.secrets["sheet_id"]

# =====================================================
# URL HELPERS
# =====================================================

def get_sheet_url(sheet_name):

    return (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    )

# =====================================================
# LOAD MASTER RECIPES
# =====================================================

@st.cache_data(ttl=300)
def load_master_recipes():

    df = pd.read_csv(
        get_sheet_url("Master")
    )

    df.columns = df.columns.str.strip()

    return df

# =====================================================
# LOAD GUEST PLANNER
# =====================================================

@st.cache_data(ttl=300)
def load_guest_planner():

    df = pd.read_csv(
        get_sheet_url("GuestPlanner")
    )

    df.columns = df.columns.str.strip()

    return df


def get_day_row(day):

    df = load_guest_planner()

    matches = df[
        df["Day"]
        .astype(str)
        .str.strip()
        .str.lower()
        == day.lower()
    ]

    if matches.empty:
        return None

    return matches.index[0] + 2

def get_existing_meal(day, meal_type):

    df = load_guest_planner()

    matches = df[
        df["Day"]
        .astype(str)
        .str.strip()
        .str.lower()
        == day.lower()
    ]

    if matches.empty:
        return ""

    value = matches.iloc[0][meal_type]

    if str(value) == "nan":
        return ""

    return str(value).strip()

@st.cache_resource
def get_gspread_client():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=scopes
    )

    return gspread.authorize(creds)

def save_guest_meal(day, meal_type, recipe):

    client = get_gspread_client()

    sheet = client.open_by_key(SHEET_ID)

    worksheet = sheet.worksheet("GuestPlanner")

    row_number = get_day_row(day)

    column_map = {
        "Breakfast": "B",
        "Lunch": "C",
        "Dinner": "D",
        "Snacks": "E"
    }

    cell = f"{column_map[meal_type]}{row_number}"

    worksheet.update(
        cell,
        [[recipe]]
    )

def get_recipe_link(recipe_name):

    recipes_df = load_master_recipes()

    match = recipes_df[
        recipes_df["Recipe Name"]
        .astype(str)
        .str.strip()
        == recipe_name.strip()
    ]

    if match.empty:
        return None

    link = match.iloc[0]["Recipe Link"]

    if str(link) == "nan":
        return None

    return str(link).strip()