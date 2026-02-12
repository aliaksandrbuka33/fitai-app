import streamlit as st
st.markdown("""
    <style>
        /* Force dark background on this page */
        [data-testid="stAppViewContainer"] {
            background-color: #0a0c10 !important;
        }

        /* Target ALL input wrappers and elements - focused or unfocused */
        div[data-testid="stNumberInput"],
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stNumberInput"] > div > div,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] > div > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"],
        div[data-testid="stTextArea"] > div,
        div[data-testid="stTextArea"] > div > div,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"],
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stSelectbox"] > div > div,
        div[data-testid="stSelectbox"] select {
            background-color: #11151c !important;
            color: #f1f5f9 !important;
            border: 1px solid #2a3241 !important;
            border-radius: 10px !important;
        }

        /* Force placeholder color */
        input::placeholder, textarea::placeholder {
            color: #94a3b8 !important;
        }

        /* Focus ring */
        input:focus, textarea:focus, select:focus {
            border-color: #00ff9d !important;
            box-shadow: 0 0 0 3px rgba(0,255,157,0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)
    
# Force dark mode on this page
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117 !important;
            color: #e0e0e0 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #161b22 !important;
        }
        .stButton > button {
            background-color: #00cc66 !important;
            color: black !important;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #1e1e1e !important;
            color: white !important;
        }
        h1, h2, h3 {
            color: #00cc66 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Your existing code below...
st.title("Log Workout")
# ... rest of your page
from huggingface_hub import InferenceClient
from datetime import datetime

st.title("Log Workout")

# Load token from secrets
api_token = st.secrets["HF_TOKEN"]

# Simple storage for logs (exercise -> list of (date, sets, reps, weight))
if "logged_workouts" not in st.session_state:
    st.session_state.logged_workouts = {}

# Example plan (in real app, pull from home or save in session)
# For now, hard-coded — later we'll share from home page
example_plan = [
    {"exercise": "Squats", "sets": 3, "reps": "8-12"},
    {"exercise": "Bench Press", "sets": 4, "reps": "6-10"},
    {"exercise": "Pull-ups", "sets": 3, "reps": "max"},
]

st.subheader("Today's Exercises")
for ex in example_plan:
    exercise = ex["exercise"]
    target = f"{ex['sets']} sets of {ex['reps']}"

    st.markdown(f"**{exercise}** — Target: {target}")

    # Show last logged performance
    last_perf = None
    if exercise in st.session_state.logged_workouts and st.session_state.logged_workouts[exercise]:
        last = st.session_state.logged_workouts[exercise][-1]
        last_date, sets, reps, weight = last
        last_perf = f"{sets}x{reps} @ {weight}kg ({last_date})"
        st.caption(f"Last: {last_perf}")
    else:
        st.caption("No previous log")

    col1, col2 = st.columns([5, 1])
    with col1:
        # Log form
        with st.form(key=f"log_{exercise}"):
            sets = st.number_input("Sets", min_value=1, value=ex["sets"])
            reps = st.number_input("Reps", min_value=1, value=10)
            weight = st.number_input("Weight (kg)", min_value=0.0, value=50.0, step=2.5)
            submitted = st.form_submit_button("Log this set")

            if submitted:
                date = datetime.now().strftime("%Y-%m-%d")
                entry = (date, sets, reps, weight)
                if exercise not in st.session_state.logged_workouts:
                    st.session_state.logged_workouts[exercise] = []
                st.session_state.logged_workouts[exercise].append(entry)
                st.success(f"Logged {exercise}: {sets}x{reps} @ {weight}kg")

    with col2:
        # Subtle ? suggestion button
        if last_perf and st.button("?", key=f"suggest_{exercise}", help="AI suggestion for next session"):
            with st.spinner("..."):
                client = InferenceClient(token=api_token)
                suggestion_prompt = f"""
                User last did {exercise}: {last_perf}.
                Suggest next session weight/reps for progressive overload.
                Use linear progression and NSCA hypertrophy guidelines (increase 2-5% if 8-12 reps achieved with good form).
                Keep response short, subtle and encouraging, e.g. "+2.5kg" or "keep same - focus on form".
                """
                response = client.chat_completion(
                    messages=[{"role": "user", "content": suggestion_prompt}],
                    model="meta-llama/Llama-3.1-8B-Instruct",
                    max_tokens=100,
                    temperature=0.5,
                )
                suggestion = response.choices[0].message.content.strip()
                st.info(suggestion)
