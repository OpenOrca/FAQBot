import openai
from config import OPENAI_API_BASE, OPENAI_API_KEY
from utils import cleaned_message

openai.api_base = OPENAI_API_BASE
openai.api_key = OPENAI_API_KEY

async def get_llm_message(message):
    clean_content = cleaned_message(message.content)
    # Make the bot appear as if it's typing
    async with message.channel.typing():
        prompt = f"### System: Below is an instruction that describes a task. Write a response that appropriately completes the request. \n### Instruction: {clean_content}\n### Response: "
        response = openai.Completion.create(
                model="llm",
                prompt=prompt,
                max_tokens=256,
                temperature=1,
                )
        response_text = response.choices[0].text
        #embed.add_field(name="Times Asked", value=str(1), inline=True)
        response_message = await message.reply(response_text)
        # Adds thumbs up/down so users can rate the answer
        await response_message.add_reaction("👍")
        await response_message.add_reaction("👎")

        return response_message

