import datetime
import pymongo
import pprint
from pymongo import MongoClient


# Connect to the database and collection
client = pymongo.MongoClient("mongodb+srv://danielAgro:GtqV7UmRMwSBilrS@cluster0.qmjsaat.mongodb.net/?retryWrites=true&w=majority")
db = client.assistant_db #verificar
conversationhistory = db.conversationhistory

def insert_conversation_history(id_message, messageType, remoteJid, msg_tstamp, knowed_person, name, surname, business_type, cliente_role, client_entite, from_user, from_bot, utterance, format, context_category, seq, stage):
    # Create a dictionary with the conversation history data
    conversation_history = {
        "tsmessage": datetime.datetime.utcnow(),
        "id_message": id_message,
        "msg_type": messageType,
        "remoteJid": remoteJid,
        "msg_timestamp": msg_tstamp,
        "knowed_person": knowed_person,
        "name": name,
        "surname": surname,
        "business_type": business_type,
        "cliente_role": cliente_role,
        "client_entite": client_entite,
        "from_user": from_user,
        "from_bot": from_bot,
        "utterance": utterance,
        "format": format,
        "context_category": context_category,
        "seq": seq,
        "stage": stage
    }
    
    # Insert the conversation history into the collection
    result = conversationhistory.insert_one(conversation_history)
    
    # Return the ID of the inserted document
    return result.inserted_id

