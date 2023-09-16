from pocketbase import PocketBase
from utils import cleaned_message
from config import POCKETBASE_URL

pb = PocketBase(POCKETBASE_URL)

def create_question(question, id):
    cleaned_text = cleaned_message(question)
    pb.collection('questions').create({
        'text': cleaned_text,
        'id': id
    })

def create_answer(answer, id, question_id, source):
    cleaned_text = cleaned_message(answer)
    pb.collection('answers').create({
        'text': cleaned_text,
        'source': source,
        'question': question_id,
        'id': id
    })

def update_answer_rating(id, rating):
    pb.collection('answers').update(id, {
        "rating+": rating
    })

def vector_search(question):
    cleaned_question = cleaned_message(question)
    results = pb.collection("questions").get_list(per_page=10000000, query_params={
        "search": cleaned_question,
        "expand": "answers(question)"
    })
    if not results.items:
        return
    first_question = results.items[0]

    del first_question.embedding
    first_answer = pb.collection('answers').get_first_list_item(f"question = '{first_question.id}'", query_params= {
       "sort":"-rating"
    })
    return first_question, first_answer
