from src.utils import get_message_id, cleaned_message, get_answer_rating
from src.database import (create_question, create_answer, vector_search, create_related_question,
                      update_answer_rating, pb)
from src.llm import get_llm_message
import lilac as ll
ll.set_project_dir('/home/epentland/ai/lilac')
from datetime import datetime

async def create_reply(message):
    clean_content = cleaned_message(message.content)
    question_id = get_message_id(message)

    if len(clean_content) < 1:
        return

    create_question(message, question_id)
    response_message = await get_llm_message(message)
    response_message_id = get_message_id(response_message)
    create_answer(response_message, response_message_id, question_id, 'llm')


async def get_parent_message(message):
    if message.reference:
        return await message.channel.fetch_message(message.reference.message_id)
    return None


async def handle_reaction(type, reaction, user, client):
    if user == client.user:
        return

    if str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎":
        message_id = get_message_id(reaction.message)
        answer_row = pb.collection('answers').get_one(message_id)
        rating = get_answer_rating(reaction, type)
        answer_id = answer_row.id
        if answer_row.parent_answer_id:
            answer_id = answer_row.parent_answer_id
        update_answer_rating(answer_id, rating)

    if str(reaction.emoji) == "❓":
        await handle_bot_mention_in_new_message(reaction.message, client)


async def handle_on_message(message, client):
    parent_message = await get_parent_message(message)
    message_id = get_message_id(message)

    if not parent_message:
    # Generates a reply from the model or pulls from vector database
        #if client.user in message.mentions:
        await handle_bot_mention_in_new_message(message, client)
    else:
        # Adds reaction to users answers for voting
        await handle_bot_mention_in_reply(message, client, parent_message, message_id)

def get_or_create_concept(guild):
    concept_name = f'{guild.name}_{guild.id}'
    namespace = 'local'
    db = ll.DiskConceptDB()
    # Checks to see if the concept exists
    concept = db.get(
        namespace=namespace,
        name=concept_name
    )
    if concept:
        return concept
    else:
        # Creates a concept if one doesn't already exist
        concept = db.create(
            namespace='local',
            name=concept_name
        )
        examples = [
        ll.concepts.ExampleIn(label=False, text='How do I do this?'),
        ll.concepts.ExampleIn(label=True, text='How can I install axolotl?'),
        ]
        db.edit(namespace, concept_name, ll.concepts.ConceptUpdate(insert=examples))
        return concept
        


async def handle_bot_mention_in_new_message(message, client):
    # Only looks at message with a question mark in it
    if not "?" in message.content:
        return
    
    # Uses a classifier first to identify if its a question
    messages = [message.content]
    start_time = datetime.now()
    concept = get_or_create_concept(message.guild)
    
    signal = ll.signals.ConceptSignal(
        namespace=concept.namespace,
        concept_name=concept.concept_name,
        embedding='gte-small')
    
    score = list(signal.compute(messages))[0][0]['score']
    duration = datetime.now() - start_time
    print('Runtime:', duration)
    print(score)
    # Only goes to vectordb if its a valid question
    if score > 0.09 or client.user in message.mentions:
        vector_db_question, vector_db_answer = vector_search(message)
        # When the question is similar to something its seen before
        if vector_db_question and vector_db_question.similarity > 0.8:
            response = vector_db_answer.text
            pb.collection('questions').update(vector_db_question.id, {"times_asked+": 1})
            bot_message = await message.reply(content=response)
            message_id = get_message_id(bot_message)
            # Checks if there is a parent
            base_message_id = get_message_id(message)
            create_related_question(vector_db_question.text, base_message_id, vector_db_question.guild_id, vector_db_question.channel_id, vector_db_question.message_id, vector_db_question.author_id, vector_db_question.id)
            create_answer(bot_message, message_id, vector_db_answer.question, vector_db_answer.source, vector_db_answer.id)
            await bot_message.add_reaction("👍")
            await bot_message.add_reaction("👎")
        # When the model is being used to generate the output
        else:
            # Put a grey question mark if its not similar to any previously asked questions
            await message.add_reaction("❔")
            await message.add_reaction("❌")
            #await create_reply(message)


async def handle_bot_mention_in_reply(message, client, parent_message, message_id):
    #Checks to see if there is a parent question
    question_id = get_message_id(parent_message)
    id = message_id

    # When the user replies to a question with @bot
    if client.user in parent_message.mentions:
        db_question = pb.collection('questions').get_one(question_id)
        if db_question.parent_question_id:
            question_id = db_question.parent_question_id
        # Check to see if the parent message has parent
        create_answer(message, id, question_id, 'user')
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    # When the user provides an answer and adds the bot to the message
    is_question = any(reaction.emoji == '❔' for reaction in parent_message.reactions)
    if client.user in message.mentions or is_question:
        create_question(parent_message, question_id)
        create_answer(message, id, question_id, 'user')
        await message.add_reaction("👍")
        await message.add_reaction("👎")
