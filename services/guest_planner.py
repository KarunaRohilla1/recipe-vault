import streamlit as st
from datetime import date

from services.sheets import (
    load_master_recipes,
    load_guest_planner,
    save_guest_meal,
    get_existing_meal,
    get_recipe_link
)

def show_guest_planner():

    # =====================================================
    # PIN
    # =====================================================

    GUEST_PIN = st.secrets["guest_pin"]

    # =====================================================
    # SESSION
    # =====================================================

    if "guest_unlocked" not in st.session_state:
        st.session_state.guest_unlocked = False

    if "pending_replace" not in st.session_state:
        st.session_state.pending_replace = None

    if "guest_banner_dismissed_date" not in st.session_state:
        st.session_state.guest_banner_dismissed_date = None

    today = str(date.today())  

    # =====================================================
    # TITLE
    # =====================================================

    st.title("Guest Planner")

    # =====================================================
    # PIN LOCK
    # =====================================================

    if not st.session_state.guest_unlocked:

        entered_pin = st.text_input(
            "Enter Guest PIN",
            type="password"
        )

        if entered_pin == GUEST_PIN:
            st.session_state.guest_unlocked = True
            st.rerun()

        elif entered_pin:
            st.error("Wrong PIN")

        st.stop()

    # =====================================================
    # WELCOME BANNER
    # =====================================================

    if st.session_state.guest_banner_dismissed_date != today:

        if "guest_banner_shown" not in st.session_state:
            st.balloons()
            st.session_state.guest_banner_shown = True

        st.markdown("""<div style="background: #FFF8F2;
                border: 1px solid #F0DCC8;
                border-radius: 24px;
                padding: 24px;
                margin-bottom: 25px;">
                <h3 style="
                    margin-top:0;
                    color:#2F2A24;">
                    ❤️ A Quick Reminder
                </h3>
                <p style="font-size:22px;
                    color:#4A433C;
                    margin-bottom:0;">Hi! ✨ 
                    Just a reminder: Your girlfriend loves you and is super proud of you. 
                    Now go eat your protein. 😌</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        hide_today = st.checkbox("Don't show again today",key="guest_banner_hide")

        if hide_today:
            st.session_state.guest_banner_dismissed_date = today
            st.rerun()

    # =====================================================
    # LOAD DATA
    # =====================================================

    recipes_df = load_master_recipes()

    planner_df = load_guest_planner()

    # =====================================================
    # ADD MEAL
    # =====================================================

    st.subheader("Add Meal")

    days = [
        "Saturday",
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]

    meal_types = [
        "Breakfast",
        "Lunch",
        "Dinner",
        "Snacks"
    ]

    recipe_names = sorted(
        recipes_df["Recipe Name"]
        .dropna()
        .astype(str)
        .unique()
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_day = st.selectbox(
            "Day",
            days
        )

    with col2:
        selected_meal = st.selectbox(
            "Meal Type",
            meal_types
        )

    with col3:

        recipe_search = st.text_input(
            "Search Recipe",
            placeholder="Start typing..."
        )

        filtered_recipes = [
            recipe
            for recipe in recipe_names
            if recipe_search.lower() in recipe.lower()
        ]

        if filtered_recipes:

            selected_recipe = st.selectbox(
                "Recipe",
                filtered_recipes,
                index=None,
                placeholder="Select a recipe..."
            )

        else:

            st.warning("No recipes found")
            selected_recipe = None

    if st.button("Add Meal") and selected_recipe:

        existing = get_existing_meal(
            selected_day,
            selected_meal
        )

        if existing:

            st.session_state.pending_replace = {
                "day": selected_day,
                "meal_type": selected_meal,
                "recipe": selected_recipe,
                "existing": existing
            }

        else:

            save_guest_meal(
                selected_day,
                selected_meal,
                selected_recipe
            )
            load_guest_planner.clear()

            st.success("Meal added!")

            st.rerun()

    pending = st.session_state.pending_replace

    if pending:

        st.warning(
            f"{pending['day']} "
            f"{pending['meal_type']} "
            f"already contains: "
            f"{pending['existing']}"
        )

        st.write(
            f"Replace with: "
            f"**{pending['recipe']}** ?"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Replace Meal",
                type="primary"
            ):

                save_guest_meal(
                    pending["day"],
                    pending["meal_type"],
                    pending["recipe"]
                )

                load_guest_planner.clear()

                st.session_state.pending_replace = None

                st.success("Meal replaced!")

                st.rerun()

        with col2:

            if st.button("Cancel"):

                st.session_state.pending_replace = None

                st.rerun()

    # =====================================================
    # WEEKLY VIEW
    # =====================================================

    st.divider()

    st.subheader("Weekly Planner")

    for i in range(0, len(days), 2):

        col1, col2 = st.columns(2)

        pair = days[i:i+2]

        for idx, day in enumerate(pair):

            column = col1 if idx == 0 else col2

            with column:

                st.markdown(f"## {day}")

                day_row = planner_df[
                    planner_df["Day"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == day.lower()
                ]

                if day_row.empty:
                    continue

                day_row = day_row.iloc[0]

                for meal_type in meal_types:

                    meal = day_row.get(meal_type, "")

                    if meal is None:
                        continue

                    if str(meal) == "nan":
                        continue

                    meal = str(meal).strip()

                    if not meal:
                        continue

                    recipe_link = get_recipe_link(meal)

                    st.markdown(
                        f"<div class='meal-label'>{meal_type}</div>",
                        unsafe_allow_html=True
                    )

                    if recipe_link:

                        st.markdown(
                            f"""
                            <div class="meal-item">
                                <a href="{recipe_link}"
                                target="_blank"
                                class="meal-link">
                                {meal}
                                </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"""
                            <div class="meal-item">
                                {meal}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )