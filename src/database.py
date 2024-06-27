from pocketbase import PocketBase
from src.utils import cleaned_message
from src.config import POCKETBASE_URL

pb = PocketBase(POCKETBASE_URL)

def create_related_question(text, id, guild_id, channel_id, message_id, author_id, parent_question_id):
    cleaned_text = cleaned_message(text)
    pb.collection('questions').create({
        'text': cleaned_text,
        'id': id,
        'guild_id': str(guild_id),
        'channel_id': str(channel_id),
        'message_id': str(message_id),
        'author_id': str(author_id),
        "parent_question_id": str(parent_question_id)
    })

def create_question(message, id, parent_question_id=""):
    cleaned_text = cleaned_message(message.content)
    pb.collection('questions').create({
        'text': cleaned_text,
        'id': id,
        'guild_id': str(message.guild.id),
        'channel_id': str(message.channel.id),
        'message_id': str(message.id),
        'author_id': str(message.author.id),
        "parent_question_id": str(parent_question_id)
    })

def create_answer(message, id, question_id, source, parent_answer_id = ""):
    cleaned_text = cleaned_message(message.content)
    if parent_answer_id:
        parent_answer_id = parent_answer_id[:15]
    pb.collection('answers').create({
        'text': cleaned_text,
        'id': id,
        "parent_answer_id": parent_answer_id,
        'source': source,
        'question': str(question_id),
        'guild_id': str(message.guild.id),
        'channel_id': str(message.channel.id),
        'message_id': str(message.id),
        'author_id': str(message.author.id)
    })

def update_answer_rating(id, rating):
    pb.collection('answers').update(id, {
        "rating+": rating
    })

def vector_search(message):
    cleaned_question = cleaned_message(message.content)
    results = pb.collection("questions").get_list(per_page=10000000, query_params={
        "search": cleaned_question,
        "filter": f'parent_question_id = "" && guild_id = "{str(message.guild.id)}"',
        "expand": "answers(question)"
    })
    if not results.items:
        return None, None
    first_question = results.items[0]

    del first_question.embedding
    first_answer = pb.collection('answers').get_first_list_item(f"question = '{first_question.id}' && parent_answer_id = ''", query_params= {
       "sort":"-rating",
    })
    if first_answer:
        return first_question, first_answer
    else:
        return first_answer, None
