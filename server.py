#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import datetime
import json
import io
import base64
import time
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

"""
TODO: logger module to clean logger code for each file
logging level
asyncoronize
"""

connected = set()


def audio(ws):
    while True:
        in_data = ws.recv()
        d = json.loads(in_data)
        data = []
        if 'audio' in d['data']:
            data.append(base64.b64decode(d['data']['audio']))


def print_response(r):
    for response in r:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        for result in response.results:
            print('Finished: {}'.format(result.is_final))
            print('Stability: {}'.format(result.stability))
            alternatives = result.alternatives
            # The alternatives are ordered from most likely to least.
            for alternative in alternatives:
                print('Confidence: {}'.format(alternative.confidence))
                print(u'Transcript: {}'.format(alternative.transcript))


async def ws_server(ws, path):

    connected.add(ws)
    print('current: ')
    print(connected)

    stream = []
#    with open(f"output/{datetime.datetime.now():%Y-%m-%dT%H%M%S}.pcm", mode='bx') as f:
    while True:
        try:
            in_data = await ws.recv()
            d = json.loads(in_data)
            #with io.open('/Users/xiajimu/Documents/test/googleAsr/test.wav', 'rb') as audio_file:
                #content = audio_file.read()

            if 'audio' in d['data']:
                stream.append(base64.b64decode(d['data']['audio']))
            else:
                pass

            if len(d['header']) == 6:
                break
                
            if d['header'][6] == 0:
                client = speech.SpeechClient()
                print(stream)
                requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                            for chunk in stream)
                config = types.RecognitionConfig(
                    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code='en-US')

                streaming_config = types.StreamingRecognitionConfig(config=config)
                responses = client.streaming_recognize(streaming_config, requests)

                print_response(responses)
                stream = []
            #f.write(base64.b64decode(d['data']['audio']))
            # try:
            #     out['data']['result'] = recognize_google(wav)
            # excecpt UnknownValueError:
            #     out['data']['result'] = 'Unknown'

    #            stop = time.time()
    #            out['data']['response_time'] = round(stop - start, 5)
    #            del out['data']['audio']
            await ws.send("Done")

        except websockets.exceptions.ConnectionClosed:
            '''
            TODO: Logging.info
            '''
            print('{}: user disconnected'.format(int(time.time())))
            connected.remove(ws)
            print(connected)
            break

start_server = websockets.serve(ws_server, 'localhost', 3456)
print('Start listening:')

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

