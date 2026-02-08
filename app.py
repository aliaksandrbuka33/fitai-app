import streamlit as st
from huggingface_hub import InferenceClient

api_token = st.secrets["HF_TOKEN"]

# Page config
st.set_page_config(page_title="FitAI - Your Personal Workout Planner", page_icon="💪")

# Title
st.title("💪 FitAI - Personalized Workout Planner")
st.markdown("Tell me about yourself and your goals, and I'll create a custom workout plan!")

# User inputs (form)
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
        
        # Create prompt
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
            # Wrap prompt as chat message (required by Featherless / current routing)
            messages = [{"role": "user", "content": prompt}]
            
            response = client.chat_completion(
                messages=messages,
                model="mistralai/Mistral-7B-Instruct-v0.2",
                max_tokens=1500,
                temperature=0.7,
            )
            
            plan = response.choices[0].message.content
        
        st.success("Here's your personalized workout plan!")
        st.markdown(plan)
        
        if st.button("Generate a different version"):
            st.rerun()
    
    except Exception as e:
        st.error(f"Something went wrong: {str(e)}. Double-check your token or try again.")
