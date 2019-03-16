from flask import Flask, request, jsonify, render_template
import json
import requests

import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ghrg4854yn754ct5cvrtgtAS'

PAT = 'EAAElanWHWs0BAGrlESwCtGH6C4ZAtfGtINDVPgcWiuUQo3ZAeY0O7H4ic1b1lPmVgcmqpjYPxom0V80cZBD4K5tvdaiwQB3dnFVUvZAgJQlSo1rLEmxHH8Ojuq1LAkoyM300upWo9HZAlRNO91LZBURLJsRDOQH3pnBNjZBOYQKK1cQ95ZA9TNyg'
print('rerun')

randomspace = string.ascii_letters+'0123456789'
project_id = 'test-chatbot-53656'
session_id = '83ebfe95-d844-1525-de20-9d15059ec6a8'


@app.route('/send',methods=['POST'])
def receive_message():
    data = request.json
    replies = generate_reply(data['msg'])
    return jsonify({'count': len(replies), 'msgs': replies })

def generate_reply(msg):
    '''
    Process and reply
    '''
    replies = detect_intent_texts(project_id, session_id, [msg], 'en')
    return replies

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# ------------------------- calls to and from Dialog flow ------------------------------
def detect_intent_texts(project_id, session_id, texts, language_code):
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    for text in texts:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = session_client.detect_intent(
            session=session, query_input=query_input)
         
    return [response.query_result.fulfillment_text]

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    return jsonify({
        "fulfillmentText": "This is a text response"
    })

# ------------------------- Facebook stuff ------------------------------------

def sendfacebookmessage(recipient, text, token):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": token},
        data=json.dumps({
            "recipient": {"id": recipient},
            "message": {"text": text.decode('unicode_escape')}
        }),
        headers={'Content-type': 'application/json'}
    )
    if r.status_code != requests.codes.ok:
        print (r.text)

def messaging_events(payload):
    """Generate tuples of (sender_id, message_text) from the
    provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
        else:
            yield event["sender"]["id"], "I can't echo this"

@app.route('/', methods=['GET'])
def handle_verification():
    print ("Handling Verification.")
    if request.args.get('hub.verify_token', '') == 'Hatel-is-amazingg':
        print ("Verification successful!")
        return request.args.get('hub.challenge', '')
    else:
        print ("Verification failed!")
        return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages_fb():
    print ("Handling Messages")
    payload = request.get_data()
    print (payload)
    
    for sender, message in messaging_events(payload):
        print ("Incoming from %s: %s" % (sender, message))
        # send_message(PAT, sender, message)
        
        sendfacebookmessage(sender, message, PAT)
    return "ok"


if __name__ == '__main__':
    app.run(debug=True, threaded=True)