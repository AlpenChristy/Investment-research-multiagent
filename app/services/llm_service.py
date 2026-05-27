import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,       # low temp = more consistent JSON output
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()