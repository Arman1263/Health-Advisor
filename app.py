import os
import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is not set in the environment variables. Please add it to your .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# Set page configuration
st.set_page_config(
    page_title="AI Health Advisor",
    page_icon="❤️‍🩹",
    layout="wide",
)

# App title and description
st.title("AI Health Advisor")
st.markdown("""
This application provides personalized health recommendations based on your inputs.
Fill out the form below to receive tailored health advice from our AI assistant.
""")

# Create a form for user inputs
with st.form("health_form"):
    st.subheader("Personal Health Information")
    
    # Basic information
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
    with col2:
        height = st.number_input("Height (cm)", min_value=50, max_value=250, step=1)
        weight = st.number_input("Weight (kg)", min_value=20, max_value=300, step=1)
    
    # Stress level
    stress_level = st.slider("Stress Level (1-10)", min_value=1, max_value=10, value=5, 
                            help="1 = Very Low Stress, 10 = Extremely High Stress")
    
    # Physical activity
    st.subheader("Physical Activity")
    activity_status = st.radio("Activity Status", ["Inactive", "Somewhat Active", "Active", "Very Active"])
    
    activity_frequency = st.selectbox("Activity Frequency", 
                                    ["None", "1-2 times per week", "3-4 times per week", "5+ times per week"])
    
    activity_types = st.multiselect("Types of Physical Activities", 
                                    ["Walking", "Running", "Swimming", "Cycling", "Weight Training", 
                                     "Yoga", "Team Sports", "HIIT", "Dancing", "Other"])
    
    if "Other" in activity_types:
        other_activity = st.text_input("Please specify other activities")
    else:
        other_activity = ""
    
    # Social context
    st.subheader("Social Context")
    living_situation = st.selectbox("Living Situation", 
                                    ["Alone", "With partner", "With family", "With roommates/friends", "Other"])
    
    social_support = st.slider("Social Support Network (1-10)", min_value=1, max_value=10, value=5,
                              help="1 = Very Limited Support, 10 = Extensive Support Network")
    
    # Diet preferences
    st.subheader("Diet & Nutrition")
    diet_preference = st.multiselect("Diet Preferences", 
                                    ["No specific diet", "Vegetarian", "Vegan", "Pescatarian", 
                                     "Paleo", "Keto", "Gluten-free", "Dairy-free", "Other"])
    
    if "Other" in diet_preference:
        diet_other = st.text_input("Please specify other diet preferences")
    else:
        diet_other = ""
    
    daily_water = st.selectbox("Daily Water Intake", 
                              ["Less than 1 liter", "1-2 liters", "2-3 liters", "3+ liters"])
    
    meal_regularity = st.selectbox("Meal Regularity", 
                                  ["Regular meals at set times", "Somewhat regular", "Irregular eating patterns"])
    
    # Sleep
    st.subheader("Sleep Patterns")
    sleep_hours = st.slider("Average Hours of Sleep per Night", min_value=1, max_value=12, value=7)
    
    sleep_quality = st.radio("Sleep Quality", ["Poor", "Fair", "Good", "Excellent"])
    
    # Medical conditions
    st.subheader("Medical Information (Optional)")
    medical_conditions = st.text_area("Existing Medical Conditions (if any)", 
                                     help="E.g., diabetes, hypertension, asthma, etc.")
    
    medications = st.text_area("Current Medications (if any)", 
                              help="Please list any medications you're currently taking")
    
    # Goals
    st.subheader("Health Goals")
    health_goals = st.multiselect("What are your health goals?", 
                                 ["Weight loss", "Muscle gain", "Improved fitness", 
                                  "Better sleep", "Stress reduction", "Disease management", 
                                  "Overall wellness", "Other"])
    
    if "Other" in health_goals:
        goals_other = st.text_input("Please specify other health goals")
    else:
        goals_other = ""
    
    # Additional information
    additional_info = st.text_area("Any additional information you'd like to share?", 
                                  help="Anything else that might be relevant to your health consultation")
    
    # Submit button
    submitted = st.form_submit_button("Get Health Recommendations")

# Process the form when submitted
if submitted:
    # Validate required inputs
    if not age or not gender or not height or not weight:
        st.error("Please fill in all required fields (Age, Gender, Height, Weight)")
    else:
        # Display a spinner while waiting for the API response
        with st.spinner("Generating your personalized health recommendations..."):
            try:
                # Format user data for the prompt
                user_data = {
                    "Age": age,
                    "Gender": gender,
                    "Height (cm)": height,
                    "Weight (kg)": weight,
                    "BMI": round(weight / ((height/100) ** 2), 1),
                    "Stress Level": stress_level,
                    "Activity Status": activity_status,
                    "Activity Frequency": activity_frequency,
                    "Activity Types": ", ".join(activity_types) + (f", {other_activity}" if other_activity else ""),
                    "Living Situation": living_situation,
                    "Social Support (1-10)": social_support,
                    "Diet Preferences": ", ".join(diet_preference) + (f", {diet_other}" if diet_other else ""),
                    "Daily Water Intake": daily_water,
                    "Meal Regularity": meal_regularity,
                    "Sleep Hours": sleep_hours,
                    "Sleep Quality": sleep_quality,
                    "Medical Conditions": medical_conditions if medical_conditions else "None reported",
                    "Medications": medications if medications else "None reported",
                    "Health Goals": ", ".join(health_goals) + (f", {goals_other}" if goals_other else ""),
                    "Additional Information": additional_info if additional_info else "None provided"
                }
                
                # Create prompt for Gemini API
                prompt = f"""
                You are a professional health advisor with expertise in providing personalized health recommendations.
                Based on the following user health profile, provide detailed, personalized health recommendations.
                
                USER HEALTH PROFILE:
                {user_data}
                
                Please provide recommendations in the following format:
                1. Summary of Health Status
                2. Diet Recommendations (specific foods, meal timing, hydration advice)
                3. Exercise Recommendations (types, frequency, duration based on their current activity level)
                4. Sleep Improvement Suggestions
                5. Stress Management Techniques
                6. Social Health Suggestions
                7. Additional Personalized Advice (based on their specific conditions/goals)
                
                For each section, provide 3-5 specific, actionable recommendations. Be detailed but concise.
                Ensure all advice is evidence-based and appropriate for their specific health profile.
                Do not prescribe medications or make specific medical treatment recommendations.
                If there are serious health concerns, recommend consulting with a healthcare professional.
                
                Important: If insufficient information is provided for any section, indicate this and provide general
                best practices instead.
                """
                
                # Get response from Gemini
                response = model.generate_content(prompt)
                recommendations = response.text
                
                # Display user profile and recommendations
                st.success("Health recommendations generated successfully!")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("Your Health Profile")
                    profile_df = pd.DataFrame(list(user_data.items()), columns=["Factor", "Value"])
                    st.dataframe(profile_df, use_container_width=True)
                
                with col2:
                    st.subheader("Your Personalized Health Recommendations")
                    st.markdown(recommendations)
                
                # Disclaimer
                st.info("""
                **Disclaimer**: These recommendations are generated by AI and should not be considered medical advice. 
                Always consult with qualified healthcare professionals before making significant changes to your health routine, 
                especially if you have existing medical conditions.
                """)
                
            except Exception as e:
                st.error(f"An error occurred while generating recommendations: {str(e)}")
                st.info("Please try again later or contact support if the problem persists.")
