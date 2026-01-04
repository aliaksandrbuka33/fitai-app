import streamlit as st
from huggingface_hub import InferenceClient

# Page setup with dark mode
st.set_page_config(
    page_title="FitAI - AI Workout Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
    <style>
    .stApp {background-color: #0e1117; color: white;}
    section[data-testid="stSidebar"] {background-color: #1a1a1a;}
    .stButton>button {background-color: #1f8a6e; color: white; border: none;}
    .stButton>button:hover {background-color: #2aa07f;}
    </style>
""", unsafe_allow_html=True)

# Load HF token from secrets (already set up)
api_token = st.secrets["HF_TOKEN"]
client = InferenceClient(token=api_token)

# Sidebar navigation
st.sidebar.title("FitAI")
page = st.sidebar.radio("Go to", ["Home - Generate Plan", "Workout Log", "Progress Stats"])

# Home Page: Quick Plan Generator
if page == "Home - Generate Plan":
    st.title("💪 FitAI - Your AI Coach")
    st.markdown("Answer 4 quick questions for a custom weekly plan.")

    with st.form("quick_plan"):
        level = st.selectbox("Your fitness level", ["Beginner", "Intermediate", "Advanced"])
        goals = st.multiselect("Main goals", ["Lose weight", "Build muscle", "Improve strength", "Endurance", "General health"])
        days = st.slider("Training days per week", 1, 7, 4)
        equipment = st.multiselect("Available equipment", ["Bodyweight only", "Dumbbells", "Barbell", "Gym machines", "Resistance bands"])
        submitted = st.form_submit_button("Generate My Plan")

    if submitted:
        prompt = f"""
        Create a simple, safe weekly workout plan for a {level} person training {days} days per week.
        Goals: {', '.join(goals)}
        Equipment: {', '.join(equipment) or 'bodyweight only'}
        Keep it motivating, clear format: Day 1: ..., Warm-up, Exercises (sets/reps), Cool-down.
        Respond ONLY with the plan.
        """

        with st.spinner("AI generating your plan..."):
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/Llama-3.2-3B-Instruct",
                max_tokens=1500,
                temperature=0.7,
            )
            plan = response.choices[0].message.content

        st.success("Here's your personalized plan!")
        st.markdown(plan)

        # Save plan for later use in Workout page
        st.session_state.current_plan = plan

# Placeholder pages (we'll fill them next)
elif page == "Workout Log":
    st.title("🏋️‍♂️ Workout Log")
    st.info("This page is coming in the next step...")

elif page == "Progress Stats":
    st.title("📈 Progress Stats")
    st.info("Charts coming soon...")
