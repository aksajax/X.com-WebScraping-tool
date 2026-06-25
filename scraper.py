import asyncio
import os
from browser_use import Agent, Browser, BrowserConfig
from langchain_groq import ChatGroq  # Groq ke liye special import

# Groq API Key set karein
os.environ["GROQ_API_KEY"] = "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"

async def main():
    # 1. Setup Groq Model (Vision wala model use karna zaroori hai)
    # 'llama-3.2-11b-vision-preview' screenshots ko achhe se samajhta hai
    llm = ChatGroq(
        model_name="llama-3.2-11b-vision-preview", 
        temperature=0.0 
    )

    browser = Browser(config=BrowserConfig(headless=False))

    # 2. Task define karein
    task = (
        "Go to x.com, login with my credentials, "
        "and find the top trending topic in India."
    )

    # 3. Agent initialize karein
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        use_vision=True  # Groq Vision model screenshots dekh kar kaam karega
    )

    print("🚀 Groq AI Agent kaam shuru kar raha hai...")
    result = await agent.run()
    
    print("\n--- FINAL RESULT ---")
    print(result.final_result())
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())