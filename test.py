import os
import re
import discord
import openai
openai.api_key = "YOUR_API_KEY"  # Replace with your OpenAI API key
openai.api_base = "http://localhost:8001/v1"
from dotenv import load_dotenv
clean_context = " To use axolotl, what versions of Python and Pytorch do I need?"
prompt = f"### System: Below is an instruction that describes a task. Write a response that appropriately completes the request. \n### Instruction: {clean_context}\n### Response: \n"
response = openai.Completion.create(
        model="llm",
        prompt=prompt,
        max_tokens=256,
        temperature=0.7,
        )
print(response)