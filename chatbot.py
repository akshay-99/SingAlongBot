from flask import Flask, request, jsonify, render_template
import json
import requests
import os
import random
import string

from protobuf_to_dict import protobuf_to_dict

from bs4 import BeautifulSoup
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['SECRET_KEY'] = ''

PAT = ''

randomspace = string.ascii_letters+'0123456789'
project_id = 'test-chatbot-53656'

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

    replyformatted = {
        'msgs':messages,
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
        return handle_bored(req)
    elif intent == 'song':
        return jsonify({"fulfillmentMessages": [{
                    "text": {
                        "text":["jam"],
                    }
                }],
                "followupEventInput": {
                "name": "songin",
                "languageCode": "en-US"
                }
        })
    elif intent == 'songin':
        return handle_song(req)
        # return handle_song(req)

def handle_song(req):
    lyr = req['queryResult']['queryText']
    songname, content = getsongname(lyr)
    return jsonify({"fulfillmentMessages": [{
                    "text": {
                        "text":[content],
                    }
                }, {
                    "text": {
                        "text":[songname+'! I love this song!'],
                    }
                }],
        })
def handle_bored(req):
    rch = random.randint(1, 2)
    if rch == 1:
        reddit = requests.get('https://www.reddit.com/r/programmerhumor/top.json?t=week',  headers = {'User-agent': 'your bot 0.1'})
        data = reddit.json()
        rno = random.randint(0, len(data['data']['children']))-1
        url = data['data']['children'][rno]['data']['url']
        title = data['data']['children'][rno]['data']['title']
        return jsonify({ "fulfillmentMessages": [{
                    "text": {
                        "text":["Here's a hilarious post I found on reddit"],
                    }
                },{
                    "text": {
                        "text": ["<h3>"+title+"</h3><img src =\""+url+"\" width=250 height=250></img>"],
                    }
                }]
        })
    else:
        return jsonify({"fulfillmentMessages": [{
                    "text": {
                        "text":["So am I"],
                    }
                }]
        })


    
def handle_cats(req):
    animal = req['queryResult']['parameters']['animals']
    animal_dict = {'Cat':'kittens', 'Dog':'puppies','Panda':'redpandas','Rabbit':'rabbits','Horse':'horses'} 
    reddit = requests.get('https://www.reddit.com/r/'+animal_dict[animal]+'/top.json?t=week',  headers = {'User-agent': 'your bot 0.1'})
    data = reddit.json()
    rno = random.randint(0, len(data['data']['children'])-1)
    url = data['data']['children'][rno]['data']['url']
    title = data['data']['children'][rno]['data']['title']
    return jsonify({
        "fulfillmentMessages": [
            {
                "text": {
                    "text":[animal+"s are amazing! Here's a recent reddit post"],
                }
            },
            {
                "text": {
                    "text": ["<h3>"+title+"</h3><img src =\""+url+"\" width=250 height=250></img>"],
                }
            }
        ]
        
    })

def getsongname(lyrics):
    
    try:
       
        r2 = requests.get('https://www.googleapis.com/customsearch/v1/siterestrict?q='+lyrics +
                          '&cx={}&num=1&key={}'.format(os.environ.get('CSE_CX'), os.environ.get('CSE_KEY')))
        print('here 1,1')
        d = eval(r2.text)
        url2 = d['items'][0]['link']
        print('here 1,2')
        title = d['items'][0]['pagemap']['metatags'][0]['og:title']

        #scrape first search result
        t = requests.get(url2).text
        soup = BeautifulSoup(t)
        song = soup.find_all('div', attrs={'class': 'lyrics'})[
            0].find('p').text
        lines = song.split('\n')
        lines = [i for i in lines if (i != '' and i[0] != '[')]
        lno = matches(lyrics, lines)
        print('here 1,3')
        print(len(lines))
        if lno >= len(lines):
            conti = '...'
        else:
            conti = lines[lno+1]
        # title = soup.find_all('h1', attrs={'class':'header_with_cover_art-primary_info-title'})[0].text.split('(')[0]
        print('1 runs')
    except:
        r = requests.get('https://songsear.ch/q/'+lyrics)
        soup = BeautifulSoup(r.text)
        l = soup.find_all(
            'h2', attrs={'title': 'Click to view just this song'})
        li = soup.find_all('div', attrs={'class': 'fragments'})
        print((l[0].find('a').text.split('(')[0], str(
            li[0].find('p')).split('</mark>')[-1][:-4].replace('\n', '')))
        re = str(li[0].find('p')).split(
            '</mark>')[-1][:-4].replace('\n', '').split('..')[0]
        rer = re[0]
        for e in re[1:]:
            if e in string.ascii_uppercase and e != 'I':
                break
            rer += e
        title = l[0].find('a').text.split('(')[0]
        conti = rer
        print('2 runs')

    print('title', title)
    print('conti', conti)
    return title, conti

def get_cosine_sim(*strs): 
    vectors = [t for t in get_vectors(*strs)]
    return cosine_similarity(vectors)
    
def get_vectors(*strs):
    text = [t for t in strs]
    vectorizer = CountVectorizer(text)
    vectorizer.fit(text)
    return vectorizer.transform(text).toarray()
def matches(inp, lines):
    inp = inp.lower()
    inp = inp.translate(str.maketrans('', '', string.punctuation))
    gcls = []
    count = 0
    for line in lines:
        line = line.lower()
        line = line.translate(str.maketrans('', '', string.punctuation))
        gcl = get_cosine_sim(line, inp)[0,1]
        gcls.append(int(gcl*1000000))
        # print('START', count,' :\n', line, '\n', gcl, end='\n\n')
        count+=1
    print(gcls.index(max(gcls)))
    return gcls.index(max(gcls))
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

@app.route('/')
def chatbot():
    return render_template('chatbot.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)