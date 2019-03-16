from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import json
import requests
import time
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ghrg4854yn754ct5cvrtgtAS'
socketio = SocketIO(app)
PAT = 'EAAElanWHWs0BAGrlESwCtGH6C4ZAtfGtINDVPgcWiuUQo3ZAeY0O7H4ic1b1lPmVgcmqpjYPxom0V80cZBD4K5tvdaiwQB3dnFVUvZAgJQlSo1rLEmxHH8Ojuq1LAkoyM300upWo9HZAlRNO91LZBURLJsRDOQH3pnBNjZBOYQKK1cQ95ZA9TNyg'
print('rerun')

randomspace = string.ascii_letters+'0123456789'
project_id = 'test-chatbot-53656'
session_id = '83ebfe95-d844-1525-de20-9d15059ec6a8'


@socketio.on('user sent')
def receive_message(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    print(request.namespace)
    contents = {'sender':request.sid, 'body':json['msg']}
    print(contents)
    reply(contents)

def reply(msg, facebook=False):
    '''
    Process and reply
    '''
    msg_body = msg['body']
    my_reply = detect_intent_texts(project_id, session_id, [msg_body], 'en')
    sender = msg['sender']
    send_message(sender, my_reply, facebook=facebook, token=PAT)

def sent_success():
    print('client received the response')
def send_message(recipient, text, facebook=False, token=None):
    """Send the message text to recipient with id recipient.
    """
    if not facebook:
        print('\n\nresponding...\n')
        socketio.emit('reply', {'msg':text},room=recipient,namesplace='/', callback=sent_success)
    else:
        sendfacebookmessage(recipient, text, token)


@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')



# ------------------------- calls to Dialog flow ------------------------------
def detect_intent_texts(project_id, session_id, texts, language_code):
    import dialogflow_v2 as dialogflow
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    for text in texts:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = session_client.detect_intent(
            session=session, query_input=query_input)

        print('=' * 20)
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text)) 
    return response.query_result.fulfillment_text

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
        msg = {'sender':sender, 'body':message}
        reply(msg, facebook=True)
    return "ok"

@app.route('/sleep')
def long():
    time.sleep(10)
    return 'done'

if __name__ == '__main__':
    socketio.run(app, debug=True)