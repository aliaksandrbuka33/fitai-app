import streamlit as st
from huggingface_hub import InferenceClient

# Load token from secrets (no visible input anymore)
api_token = st.secrets["HF_TOKEN"]

# Global dark mode + fitness styling (applies to all pages)
st.markdown("""
    <style>
        /* Dark background for the whole app */
        [data-testid="stAppViewContainer"] {
            background-color: #0a0c10 !important;
        }
        .main .block-container {
            background-color: #0a0c10 !important;
            max-width: 900px !important;
            margin: 0 auto !important;
            padding: 1.5rem !important;
        }

        /* Sidebar dark */
        [data-testid="stSidebar"] {
            background-color: #11151c !important;
        }

        /* Buttons: bright green, high contrast, subtle shadow */
        .stButton > button {
            background-color: #00ff88 !important;
            color: #000000 !important;
            border-radius: 12px !important;
            padding: 14px 28px !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(0, 255, 136, 0.25) !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
            margin: 12px 0 !important;
        }
        .stButton > button:hover {
            background-color: #33ffaa !important;
            box-shadow: 0 8px 20px rgba(0, 255, 136, 0.4) !important;
            transform: translateY(-2px) !important;
        }

        /* Inputs / selects / textareas - clean dark */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background-color: #1a1f28 !important;
            color: #ffffff !important;
            border: 1px solid #444c5a !important;
            border-radius: 10px !important;
            padding: 14px !important;
            font-size: 16px !important;
        }

        /* Slider - green track */
        .stSlider > div {
            background-color: #00ff88 !important;
        }

        /* Text & headers - clean contrast */
        h1, h2, h3, h4 {
            color: #66ffcc !important;
            font-weight: 600 !important;
        }
        p, span, div, label {
            color: #d0d7e0 !important;
            font-size: 16px !important;
        }

        /* Success / info boxes */
        .stSuccess, .stInfo, .stAlert {
            background-color: #0d2b1a !important;
            border-color: #00ff88 !important;
            color: #e0ffe0 !important;
            border-radius: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Page config (wide layout for better mobile)
st.set_page_config(
    page_title="FitAI - Your Personal Workout Planner",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"  # hides sidebar on phone by default
)

# Title
st.title("💪 FitAI - Personalized Workout Planner")
st.markdown("Tell me about yourself and your goals, and I'll create a custom workout plan!")

# User inputs
with st.form("user_form"):
    name = st.text_input("Your name (optional)")
    age = st.slider("Age", 15, 80, 30)
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
    fitness_level = st.selectbox("Current fitness level", ["Beginner", "Intermediate", "Advanced"])
    goals = st.multiselect("Fitness goals", ["Lose weight", "Build muscle", "Improve endurance", "General health", "Tone up"])
    equipment = st.multiselect("Available equipment", ["None (bodyweight)", "Dumbbells", "Barbell", "Gym machines", "Resistance bands", "Kettlebell"])
    days_per_week = st.slider("Days per week you can train", 1, 7, 4)
    minutes_per_session = st.slider("Minutes per workout session", 15, 90, 45)
    preferences = st.text_area("Any preferences, injuries, or special requests? (e.g., no jumping, focus on arms)")
    
    submitted = st.form_submit_button("Generate My Workout Plan!")

if submitted:
    try:
        # Set up Hugging Face client
        client = InferenceClient(token=api_token)
        
        # Create prompt (correct indentation)
        prompt = f"""
Create a personalized weekly workout plan for someone named {name or 'user'}.
Details:
- Age: {age}
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Fitness level: {fitness_level}
- Goals: {', '.join(goals)}
- Available equipment: {', '.join(equipment) or 'bodyweight only'}
- Training days per week: {days_per_week}
- Session length: about {minutes_per_session} minutes
- Special notes: {preferences or 'none'}

Format the plan nicely with:
- Warm-up (5-10 min)
- Main exercises (sets, reps, rest)
- Cool-down
- One rest or active recovery day suggestion
Make it motivating and safe for their level.
Respond ONLY with the workout plan, no extra text.
"""
        
        with st.spinner("Generating your custom plan..."):
            messages = [{"role": "user", "content": prompt}]
            
            response = client.chat_completion(
                messages=messages,
                model="meta-llama/Llama-3.1-8B-Instruct",  # Free & supported model
                max_tokens=1500,
                temperature=0.7,
            )
            
            plan = response.choices[0].message.content
        
        st.success("Here's your personalized workout plan!")
        st.markdown(plan)
        
        # Optional regenerate button
        if st.button("Generate a different version"):
            st.rerun()
            
    except Exception as e:
        st.error(f"Something went wrong: {str(e)}. Please try again or check your token.")
