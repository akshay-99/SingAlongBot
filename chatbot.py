from flask import Flask, request, jsonify, render_template
import json
import requests

import random
import string
app = Flask(__name__)

PAT = 'EAAElanWHWs0BAGrlESwCtGH6C4ZAtfGtINDVPgcWiuUQo3ZAeY0O7H4ic1b1lPmVgcmqpjYPxom0V80cZBD4K5tvdaiwQB3dnFVUvZAgJQlSo1rLEmxHH8Ojuq1LAkoyM300upWo9HZAlRNO91LZBURLJsRDOQH3pnBNjZBOYQKK1cQ95ZA9TNyg'
print('rerun')

user_lists = {}
randomspace = string.ascii_letters+'0123456789'
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
def handle_messages():
    print ("Handling Messages")
    payload = request.get_data()
    print (payload)
    
    for sender, message in messaging_events(payload):
        print ("Incoming from %s: %s" % (sender, message))
        send_message(PAT, sender, message)
    return "ok"

@app.route('/send', methods=['POST'])
def send():
    print ("Handling Messages")
    payload = request.json
    print (payload)
    
    sender = payload['sender_id']
    msg = payload['msg']
    send_message(PAT, sender, msg, facebook=False)
    return "ok"

@app.route('/initiate', methods=['POST'])
def initiate():
    rid = ''
    for i in range(64):
        rid+=randomspace[random.randint(0, len(randomspace)-1)]
    d={'sender_id':rid}
    global user_lists
    user_lists[rid]=[]
    print('init: \n\n\n', user_lists, '\n\n\n')
    return jsonify(d)

def handle_def(sender):
    if sender not in user_lists:
        user_lists[sender]=[]


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
@app.route('/get_pending', methods=['POST'])
def get_pending():
    content = request.json
    sender = content['sender_id']
    global user_lists
    print(user_lists, sender, sender in user_lists)

    if sender in user_lists:
        mresponse = {}
        mresponse['count']=len(user_lists[sender])
        mresponse['msgs']=user_lists[sender]
        user_lists[sender]=[]
        return jsonify(mresponse)
    else:
        return jsonify({'err':'sender id invalid'})

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

def send_def(recipient, text):
    try:
        user_lists[recipient].append(text)
    except:
        pass

def send_message(token, recipient, text, facebook=True):
    """Send the message text to recipient with id recipient.
    """
    if not facebook:
        send_def(recipient, text)
    else:
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": token},
            data=json.dumps({
                "recipient": {"id": recipient},
                "message": {"text": text.decode('unicode_escape')}
            }),
            headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print (r.text)

if __name__ == '__main__':
    app.run()

