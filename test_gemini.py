import asyncio
import google.generativeai as genai

# ✅ Replace with your actual API key
genai.configure(api_key="AIzaSyC-M_9hrVelx9mefSNNfiAk7JK5uq9hO0w")

async def main():
    # ✅ Use correct model name
    model = genai.GenerativeModel("gemini-2.5-pro")

    # ✅ Use the async call correctly
    response = await model.generate_content_async("Say hello from Gemini!")

    print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
