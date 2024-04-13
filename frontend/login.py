import streamlit as st
from user_auth import userAuth as user_auth
from streamlit_option_menu import option_menu
from fetch_data_w_api import fetch_api_data
import api_payloads as ap


def login():
    st.write("Login")
    user_name = st.text_input("User Name")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        auth = user_auth(user_name, password)
        access_token = auth.login()
        if access_token:
            st.write("Logged in")
            return access_token
    else:
        st.write("Invalid Credentials")


def set_exercise_preference(level, type, eq, body_part):
    excercise_search_payload = ap.excercise_search_payload
    excercise_search_payload["Level_Beginner"] = "1" if level == "Beginer" else "0"
    excercise_search_payload["Level_Intermediate"] = "1" if level == "Intermediate" else "0"
    excercise_search_payload["Level_Expert"] = "1" if level == "Advanced" else "0"
    excercise_search_payload["Type_Cardio"] = "1" if type == "Endurance" else "0"
    excercise_search_payload["Type_Strength"] = "1" if type == "Strength" else "0"
    excercise_search_payload["Type_Stretching"] = "1" if type == "Flexibility" else "0"
    excercise_search_payload['Equipment_Gym'] = "1" if eq == "Gym" else "0"
    excercise_search_payload['Equipment_Body_Only'] = "1" if eq == "Body Weight" else "0"
    excercise_search_payload["BodyPart_Abdominals"] = "1" if body_part == "Abdominals" else "0"
    excercise_search_payload["BodyPart_Biceps"] = "1" if body_part == "Biceps" else "0"
    excercise_search_payload["BodyPart_Chest"] = "1" if body_part == "Chest" else "0"
    excercise_search_payload["BodyPart_Forearms"] = "1" if body_part == "Forearms" else "0"
    excercise_search_payload["BodyPart_Neck"] = "1" if body_part == "Neck" else "0"
    excercise_search_payload["BodyPart_Shoulders"] = "1" if body_part == "Shoulders" else "0"
    excercise_search_payload["BodyPart_Triceps"] = "1" if body_part == "Triceps" else "0"
    excercise_search_payload["BodyPart_Legs"] = "1" if body_part == "Legs" else "0"
    excercise_search_payload["BodyPart_Back"] = "1" if body_part == "Back" else "0"
    excercise_search_payload["BodyPart_FullBody"] = "1" if body_part == "Full body" else "0"
    return excercise_search_payload


def side_bar_exercise_search():
    st.sidebar.title("Search Exercises")
    level = st.sidebar.selectbox("Activity Level", ["Beginer", "Intermediate", "Advanced"])
    type = st.sidebar.selectbox("Goal", ["Endurance", "Strength", "Flexibility", ])
    eq = st.sidebar.selectbox("Equipment", ["Gym", "Body Weight", "Bands"])
    body_part = st.sidebar.selectbox("Body Part",
                             ["Abdominals", "Biceps", "Chest", "Forearms", "Neck", "Shoulders", "Triceps", "Legs",
                              "Back", "FullBody"])
    submit = st.sidebar.button("Submit")

    if submit:
        st.divider()
        st.sidebar.subheader("Your Exercise Search Results")
        excercise_search_payload = set_exercise_preference(level, type, eq, body_part)
        fetch_api_data_obj = fetch_api_data(access_token)
        data = fetch_api_data_obj.fetch_data("http://127.0.0.1:8080/exercise/search", request_type="POST",
                                             data=excercise_search_payload)
        for item_data in data:
            workout_search_item(item_data)

        for k, v in excercise_search_payload.items():
            excercise_search_payload[k] = '0'


def side_bar_diet_search():
    st.sidebar.title("Search Diets")
    age = st.sidebar.selectbox("Age", [i for i in range(1, 100)])
    gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
    ht = st.sidebar.selectbox("Height (cm)", [i for i in range(100, 250)])
    wt = st.sidebar.selectbox("Weight (kg)", [i for i in range(30, 200)])

    submit = st.sidebar.button("Submit")

    if submit:
        ...


def add_workout_search_item(exercise_id):
    fetch_api_data_obj = fetch_api_data(access_token)
    response = fetch_api_data_obj.fetch_data(
        "http://127.0.0.1:8080/exercise/log",
        request_type="POST",
        data={"exercise_id": exercise_id}
    )


def workout_search_item(item_data):
    st.sidebar.subheader(item_data["title"])
    st.sidebar.write(item_data["desc"])

    st.sidebar.button(f"Add", key=item_data['exercise_id'], on_click=add_workout_search_item, args=(item_data['exercise_id'],))


def dashboard_workout():
    side_bar_exercise_search()
    st.title("Workout Plan")

    # fetched logged workout exercises
    fetch_api_data_obj = fetch_api_data(access_token)
    data = fetch_api_data_obj.fetch_data("http://127.0.0.1:8080/exercise/history", request_type="GET")

    icons = {
        "Level_Beginner": "🟢",
        "Level_Intermediate": "🟠",
        "Level_Expert": "🔴",
        "Type_Cardio": "🏃",
        "Type_Strength": "💪",
        "Type_Stretching": "🤸",
        "Equipment_Gym": "🏋️",
        "Equipment_Body_Only": "🧍"
    }

    # st.sidebar.write(df)
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    col1.subheader("Exercise")
    col2.subheader("Difficulty Level")
    col3.subheader("Type")
    col4.subheader("Body Part")

    for item in data:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(item['details']['title'])
            encoded_values = item['details']['encoded_values']
            # Display in each column
            for key, value in encoded_values.items():
                if value == 1:  # Only display if the value is 1
                    if 'Level' in key:
                        col2.write(icons.get(key, key.replace("Level_", "")))
                    elif 'Type' in key:
                        col3.write(icons.get(key, key.replace("Type_", "")))
                    elif 'BodyPart' in key:
                        col4.write(icons.get(key, key.replace("BodyPart_", "")))

    # fetch workout recommendations
    st.divider()
    st.title("Workout Recommendations")
    fetch_api_data_obj = fetch_api_data(access_token)
    data = fetch_api_data_obj.fetch_data("http://127.0.0.1:8080/exercise/recommendations/history", request_type="GET")
    if data:
        for item_data in data:
            st.subheader(item_data["title"])
            st.write(item_data["desc"])

            st.button(f"Add", key=item_data['exercise_id'], on_click=add_workout_search_item,
                      args=(item_data['exercise_id'],))
    else:
        st.write("No recommendations available based on your workout.")


def dashboard_diet():
    side_bar_diet_search()


def dashboard_content():
    ms = option_menu(None, ["Workout", "Nutrition"],
        icons=['bi-person-arms-up', 'bi-cup-hot-fill'],
        menu_icon="cast", default_index=0, orientation="horizontal",
        styles={
            "container": {"padding": "1px", "background-color": "#fafafa", "color": "black"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px",
                         "--hover-color": "#FFEBEE", "color": "black"},
            "nav-link-selected": {"background-color": "#C62828", "color": "white"},
        }
    )
    if ms == "Workout":
        dashboard_workout()
    else:
        dashboard_diet()


if __name__ == "__main__":
    st.set_page_config(layout='wide', initial_sidebar_state='expanded')
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzczMDUxMDcxfQ.AVXFYHc0UzrFfM5tPtZEQCe5-W1VC5AKLTsEI6DhsPE"
    if access_token:
        dashboard_content()
