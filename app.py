import streamlit as st
import asyncio
import os
from playwright.async_api import async_playwright
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Credentials
X_EMAIL = os.getenv("EMAIL")
X_USERNAME = os.getenv("USERNAME")
X_PASSWORD = os.getenv("PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def scrape_x(search_term):
    async with async_playwright() as p:
        # Browser launch (Headless=False taaki aap live dekh sakein)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        # 1. Login Page par jana
        st.info("X Login page par ja rahe hain...")
        await page.goto("https://x.com/i/flow/login")
        
        # Step: Email Input
        await page.wait_for_selector('input[autocomplete="username"]')
        await page.screenshot(path="step1_email.png") # Screenshot liya verify karne ke liye
        await page.click('input[autocomplete="username"]') # Pehle click karo
        await page.fill('input[autocomplete="username"]', X_EMAIL) # Fill karo
        await page.keyboard.press("Enter")
        st.write("Email fill kar diya...")

        # Step: Username Verification (Agar X maange toh)
        try:
            # X kabhi kabhi "Suspicious activity" bol kar username maangta hai
            await page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=5000)
            await page.screenshot(path="step2_username.png")
            await page.fill('input[data-testid="ocfEnterTextTextInput"]', X_USERNAME)
            await page.keyboard.press("Enter")
            st.write("Username verification done...")
        except:
            st.write("Username verification nahi maanga, skipping...")

        # Step: Password Input
        await page.wait_for_selector('input[name="password"]')
        await page.screenshot(path="step3_password.png")
        await page.click('input[name="password"]')
        await page.fill('input[name="password"]', X_PASSWORD)
        await page.keyboard.press("Enter")
        st.write("Password fill kar diya...")

        # Home page load hone ka wait karein
        await page.wait_for_selector('[data-testid="AppTabBar_Home_Link"]', timeout=20000)
        st.success("Login Successful!")

        # 2. Search Logic
        await page.goto(f"https://x.com/search?q={search_term}&src=typed_query")
        await page.wait_for_selector('[data-testid="tweet"]', timeout=15000)
        
        # Final Data Screenshot
        await page.screenshot(path="final_result.png")
        
        content = await page.content()
        await browser.close()
        
        # 3. AI Processing (New Model: llama-3.3-70b-specdec)
        llm = ChatGroq(model_name="llama-3.3-70b-specdec", groq_api_key=GROQ_API_KEY)
        prompt = f"Analyze this HTML and give me top 5 tweets (User: Text). HTML: {content[:10000]}"
        
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

# --- Streamlit UI ---
st.title("🐦 X Scraper (Human-Like Auto Fill)")

query = st.text_input("Enter your search topic:")

if st.button("Run Agent"):
    if query:
        with st.spinner("Processing... Check your project folder for screenshots!"):
            try:
                result = asyncio.run(scrape_x(query))
                st.markdown("### Search Results:")
                st.write(result)
                
                # Streamlit mein screenshots dikhana
                if os.path.exists("final_result.png"):
                    st.image("final_result.png", caption="Last Captured Screenshot")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# llm = ChatGroq(model_name="groq/compound-mini")