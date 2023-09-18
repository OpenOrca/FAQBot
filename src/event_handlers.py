from src.utils import get_message_id, cleaned_message, get_answer_rating
from src.database import (create_question, create_answer, vector_search,
                      update_answer_rating, pb)
from src.llm import get_llm_message

async def create_reply(message):
    clean_content = cleaned_message(message.content)
    message_id = get_message_id(message)

    if len(clean_content) < 1:
        return

    create_question(clean_content, message_id)
    response_message = await get_llm_message(message)
    response_message_id = get_message_id(response_message)
    create_answer(response_message.content, response_message_id, message_id, 'llm')


async def get_parent_message(message):
    if message.reference:
        return await message.channel.fetch_message(message.reference.message_id)
    return None


async def handle_reaction(type, reaction, user, client):
    if user == client.user:
        return

    cleaned_text = cleaned_message(reaction.message.content)
    if str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎":
        try:
            answer_row = pb.collection('answers').get_first_list_item(f"text = '{cleaned_text}'")
            rating = get_answer_rating(reaction, type)
            update_answer_rating(answer_row.id, rating)
        except:
            print('Row not found')

    if str(reaction.emoji) == "❓":
        await create_reply(reaction.message)


async def handle_on_message(message, client):
    parent_message = await get_parent_message(message)
    message_id = get_message_id(message)

    if client.user in message.mentions:
        if not parent_message:
            await handle_bot_mention_in_new_message(message, client)
        else:
            await handle_bot_mention_in_reply(message, client, parent_message, message_id)


async def handle_bot_mention_in_new_message(message, client):
    vector_db_question, vector_db_answer = vector_search(message.content)
    if vector_db_question and vector_db_question.similarity > 0.8:
        response = vector_db_answer.text
        pb.collection('questions').update(vector_db_question.id, {"times_asked+": 1})
        bot_message = await message.reply(content=response)
        await bot_message.add_reaction("👍")
        await bot_message.add_reaction("👎")
    else:
        await create_reply(message)


async def handle_bot_mention_in_reply(message, client, parent_message, message_id):
    parent_id = get_message_id(parent_message)
    if client.user in parent_message.mentions:
        create_answer(message.content, message_id, parent_id, 'user')
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    if client.user in message.mentions:
        create_question(parent_message.content, parent_id)
        create_answer(message.content, message_id, parent_id, 'user')
        await message.add_reaction("👍")
        await message.add_reaction("👎")
