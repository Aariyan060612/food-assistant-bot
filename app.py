import sys
import subprocess

# 1. Force install missing packages automatically
try:
    import groq
    from PIL import Image
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq", "pillow", "streamlit"])
    import groq
    from PIL import Image

import streamlit as st
import os
import base64

# 2. Configure Layout and Header
st.set_page_config(page_title="AI Sous Chef", page_icon="🍳", layout="centered")
st.title("🍳 Groq AI Sous Chef Bot")
st.write("Type a dish name or drop an image of food below, and I'll walk you through how to cook it!")

# 3. CRITICAL FIX: Initialize Session State for the API Key so it doesn't vanish
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("GROQ_API_KEY") or ""

# 4. Sidebar configuration
st.sidebar.title("Settings")

# If it's not found in Windows, show the manual entry box
if not st.session_state.api_key:
    st.sidebar.warning("🔑 Groq API Key not detected in Windows.")
    user_key = st.sidebar.text_input("Enter your Groq API Key manually:", type="password", key="manual_key_input")
    if user_key:
        st.session_state.api_key = user_key
        st.rerun()  # Instantly refresh the app to register the key
else:
    st.sidebar.success("🔒 Connected & Authenticated!")
    if st.sidebar.button("Clear Saved Key"):
        st.session_state.api_key = ""
        st.rerun()

# 5. Main Application Logic (Runs only when api_key exists)
if st.session_state.api_key:
    from groq import Groq
    
    # Create the client using the secured session state key
    client = Groq(api_key=st.session_state.api_key)

    # UI Inputs
    dish_name = st.text_input("What would you like to cook today?", placeholder="e.g., Butter Chicken, Pasta Carbonara...")
    uploaded_file = st.file_uploader("Or upload an image of ingredients/food:", type=["jpg", "jpeg", "png"])

    def encode_image(image_file):
        return base64.b64encode(image_file.read()).decode('utf-8')

    # Trigger analysis when user submits an input
    if st.button("Get Recipe & Instructions 🚀"):
        with st.spinner("Thinking... Chef Bot is writing your recipe! 🥣"):
            try:
                messages = []
                
                if uploaded_file:
                    base64_image = encode_image(uploaded_file)
                    st.image(uploaded_file, caption="Your Uploaded Food/Ingredients", width=300)
                    
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this food image or ingredients and provide a step-by-step recipe, including prep time, ingredients list, and clear cooking instructions."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ]
                    model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct"
                elif dish_name:
                    messages = [
                        {"role": "user", "content": f"Provide a complete, step-by-step recipe for {dish_name}. Include prep time, exact ingredients, and easy instructions."}
                    ]
                    model_to_use = "llama-3.1-8b-instant"
                else:
                    st.warning("Please type a dish name or upload an image first!")
                    st.stop()

                # Call Groq API
                completion = client.chat.completions.create(
                    model=model_to_use,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                # Output response to the screen
                st.markdown("---")
                st.subheader("📋 Your Personalized Recipe")
                st.write(completion.choices[0].message.content)

            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("💡 Please enter your Groq API Key (`gsk_...`) in the left sidebar to unlock the cooking assistant.")