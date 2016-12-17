# This is made for Python3

import pygame
import time
import requests
import uuid
from xml.etree import ElementTree

pygame.mixer.pre_init(16000, -16, 2, 2048) # setup mixer to avoid sound to be too fast
pygame.mixer.init() 

_search_id = '<SOME_RANDOM_UUID>' # without dashes
_client_id = '<SOME_RANDOM_UUID>' # without dashes
_client_name = '<SOME_RANDOM_APP_NAME>'

_speech_key = '<SPEECH_API_KEY>'
_vision_key = '<VISION_API_KEY>'
_trans_key = '<TRANSLATOR_API_KEY>' # This requires Azure subscription

_ssml_template = "<speak version='1.0' xml:lang='en-us'><voice xml:lang='{0}' xml:gender='{1}' name='{2}'>{3}</voice></speak>"

def play_sound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    time.sleep(10)

def authenticate(key):
    auth_url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {} 
    headers['Ocp-Apim-Subscription-Key'] = key
    response = requests.request('post', auth_url, headers = headers)
    print('Got JWT token')
    return response.text

def synthesis_phrase(jwt, phrase):
    url = 'https://speech.platform.bing.com/synthesize'
    headers = {} 
    headers['Authorization'] = 'Bearer ' + jwt
    headers['Content-Type'] = 'application/ssml+xml'
    headers['X-Microsoft-OutputFormat'] = 'audio-16khz-64kbitrate-mono-mp3'
    headers['X-Search-AppId'] = _search_id
    headers['X-Search-ClientID'] = _client_id
    headers['User-Agent'] = _client_name
    
    phrase = 'я думаю что это ' + phrase
    
    #content = _ssml_template.format('en-US', 'Female', 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)', phrase)
    content = _ssml_template.format('ru-RU', 'Female', "Microsoft Server Speech Text to Speech Voice (ru-RU, Irina, Apollo)", phrase)
    response = requests.request('post', url, data=content.encode('utf-8'), headers = headers)
    print('Got synthesis response')

    with open('output.mp3', 'wb') as fd:
        for chunk in response.iter_content(2000):
            fd.write(chunk)
    return     

def translate(jwt, text):
    url = 'https://api.microsofttranslator.com/v2/http.svc/Translate'
    headers = {} 
    headers['Authorization'] = 'Bearer ' + jwt
    params = {}
    params["text"] = text
    params["to"] = 'ru-RU'

    response = requests.request('get', url, headers = headers, params=params)
    print('Got translation response')
    print(response.content)
    tree = ElementTree.fromstring(response.content)
    return tree.text

def analyze_image(image_address):
    url = 'https://api.projectoxford.ai/vision/v1.0/describe'
    headers = {} 
    headers['Ocp-Apim-Subscription-Key'] = _vision_key

    json = {}
    json['url'] = image_address
    print(json)
    response = requests.request('post', url, json=json, headers=headers)
    print('Got image analysis response')
    result = response.json()
    print(result)
    return result["description"]["captions"][0]["text"]


# Reading URL from input
url = input().strip()

# Doing image analysis
phrase = analyze_image(url)

# Dirty hack to improve translation. Do not repeat! Ever.
phrase = phrase.replace('et al.', 'and someone')

# Getting access key for translation
jwt = authenticate(_trans_key)

# Doing translation
trans_phrase = translate(jwt, phrase)
print(trans_phrase)

# Getting access key for text-to-speech
jwt = authenticate(_speech_key)

# Requesting audio file 
synthesis_phrase(jwt, trans_phrase)

# Playing the response
play_sound('output.mp3')
