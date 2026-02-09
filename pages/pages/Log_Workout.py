import streamlit as st
from huggingface_hub import InferenceClient
from datetime import datetime

st.title("Log Workout")

# Simple storage in session state (later we can use database)
if "logged_workouts" not in st.session_state:
    st.session_state.logged_workouts = {}  # exercise -> list of (date, sets, reps, weight)

# Load token from secrets
api_token = st.secrets["HF_TOKEN"]

# Example plan (in real app, pull from home page or save in session)
example_plan = [
    {"exercise": "Squats", "sets": 3, "reps": "8-12"},
    {"exercise": "Bench Press", "sets": 4, "reps": "6-10"},
    {"exercise": "Pull-ups", "sets": 3, "reps": "max"},
]

st.subheader("Today's Workout")
for ex in example_plan:
    exercise = ex["exercise"]
    st.write(f"**{exercise}** - {ex['sets']} sets of {ex['reps']}")

    # Show last logged
    if exercise in st.session_state.logged_workouts:
        last = st.session_state.logged_workouts[exercise][-1]
        last_date, sets, reps, weight = last
        st.caption(f"Last: {sets}x{reps} @ {weight}kg ({last_date})")

        # Tiny ? icon for suggestion
        if st.button("?", key=f"suggest_{exercise}", help="Get AI suggestion for next session"):
            with st.spinner("Thinking..."):
                client = InferenceClient(token=api_token)
                suggestion_prompt = f"""
                User last did {exercise}: {sets} sets of {reps} reps at {weight}kg.
                Suggest next session weight/reps for progressive overload.
                Base on linear progression and NSCA hypertrophy guidelines (increase 2-5% if 8-12 reps achieved).
                Keep it short and subtle, e.g. "+2.5kg" or "keep same - focus on form".
                """
                response = client.chat_completion(
                    messages=[{"role": "user", "content": suggestion_prompt}],
                    model="meta-llama/Llama-3.1-8B-Instruct",
                    max_tokens=100,
                    temperature=0.5,
                )
                suggestion = response.choices[0].message.content.strip()
                st.info(suggestion)
    else:
        st.caption("No previous log")

    # Log form for this exercise
    with st.form(key=f"log_{exercise}"):
        sets = st.number_input("Sets", min_value=1, value=ex["sets"])
        reps = st.number_input("Reps", min_value=1, value=10)
        weight = st.number_input("Weight (kg)", min_value=0.0, value=50.0, step=2.5)
        submitted = st.form_submit_button("Log this exercise")

        if submitted:
            date = datetime.now().strftime("%Y-%m-%d")
            entry = (date, sets, reps, weight)
            if exercise not in st.session_state.logged_workouts:
                st.session_state.logged_workouts[exercise] = []
            st.session_state.logged_workouts[exercise].append(entry)
            st.success(f"Logged {exercise}: {sets}x{reps} @ {weight}kg")
