import re

# Pocketbase only supports ids of length 15
def get_message_id(message):
    return str(message.id)[:15]

def cleaned_message(text):
    # Removes any @ mentions and metadata from the string
    return re.sub(r'<@!?[0-9]+>|<<<.*?>>>', '', text).strip()

def get_answer_rating(reaction, type):
    multiplier = 1 if type == 'add' else -1 
    if str(reaction.emoji) == "👍":
        return 1 * multiplier
    elif str(reaction.emoji) == "👎":
        return -1 * multiplier