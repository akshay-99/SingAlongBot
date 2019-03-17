from flask import Flask, request, jsonify, render_template
import json
import requests

import random
import string

from protobuf_to_dict import protobuf_to_dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ghrg4854yn754ct5cvrtgtAS'

PAT = 'EAAElanWHWs0BAGrlESwCtGH6C4ZAtfGtINDVPgcWiuUQo3ZAeY0O7H4ic1b1lPmVgcmqpjYPxom0V80cZBD4K5tvdaiwQB3dnFVUvZAgJQlSo1rLEmxHH8Ojuq1LAkoyM300upWo9HZAlRNO91LZBURLJsRDOQH3pnBNjZBOYQKK1cQ95ZA9TNyg'
print('rerun')

randomspace = string.ascii_letters+'0123456789'
project_id = 'test-chatbot-53656'
# session_id = '83ebfe95-d844-1525-de20-9d15059ec6a8'


@app.route('/send',methods=['POST'])
def receive_message():
    data = request.json
    if not data.get('sid'):
        sid = randomstring(32)
        reply = generate_reply(data['msg'], sid)
    else:
        reply = generate_reply(data['msg'], data['sid'])

    return jsonify(reply)

def generate_reply(msg, sid):
    '''
    Process and reply
    '''
    reply = detect_intent_texts(project_id, sid, [msg], 'en')
    
    return reply

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
    
    reply = protobuf_to_dict(response.query_result)
    print(reply)
    messages = []
    output_contexts = []
    for rep in reply['fulfillment_messages']:
        if 'text' in rep:
            messages.append(rep['text']['text'])
    # if 'output_contexts' in reply:
    #     for con in reply['output_contexts']:
    #         output_contexts.append(con)
    replyformatted = {
        'msgs':messages,
        # 'output_contexts':output_contexts,
        'sid': session_id
    }
    return replyformatted

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    intent = req['queryResult']['intent']['displayName']
    if intent == 'cats':
        return handle_cats(req)
        
    elif intent == 'bored':
        rch = random.randint(1, 3)
        if rch == 1:
            reddit = requests.get('https://www.reddit.com/r/programmerhumor/top.json?t=week',  headers = {'User-agent': 'your bot 0.1'})
            data = reddit.json()
            rno = random.randint(0, len(data['data']['children']))-1
            url = data['data']['children'][rno]['data']['url']
            title = data['data']['children'][rno]['data']['title']
            return jsonify({
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text":["Here's a hilarious post I found on reddit"],
                        }
                    },
                    {
                        "text": {
                            "text": ["<h3>"+title+"</h3><img src =\""+url+"\" width=250 height=250></img>"],
                        }
                    }
                ]
            })
        else:
            return jsonify({
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text":["So am I"],
                        }
                    }
                ]
            })

    
def handle_cats(req):
    reddit = requests.get('https://www.reddit.com/r/kittens/top.json?t=week',  headers = {'User-agent': 'your bot 0.1'})
    data = reddit.json()
    rno = random.randint(0, len(data['data']['children']))-1
    url = data['data']['children'][rno]['data']['url']
    title = data['data']['children'][rno]['data']['title']
    return jsonify({
        "fulfillmentMessages": [
            {
                "text": {
                    "text":["Cats are amazing! Here's a recent reddit post"],
                }
            },
            {
                "text": {
                    "text": ["<h3>"+title+"</h3><img src =\""+url+"\" width=250 height=250></img>"],
                }
            }
        ]
        
    })
# ------------------------- Facebook stuff ------------------------------------
def randomstring(size):
    s = ''
    for i in range(size):
        s+=randomspace[random.randint(0, len(randomspace)-1)]
    return s
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