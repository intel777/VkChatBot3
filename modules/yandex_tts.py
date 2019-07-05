import re
import requests
import random
import os

yandex_token = '' #Your Yandex TTS token here


class Handler:

    list_triggers = [4]
    regexp_patterns = ['!tts .*', 'Рут, скажи .*']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"

    def responder(self, bot, update):
        message_text = update[5]
        message_peer = update[3]

        if re.match(self.regexp_pattern, message_text):
            print('[YandexTTS]Request accepted, processing...')
            bot.api.messages.setActivity(peer_id=message_peer, type='audiomessage')
            request = message_text.replace('!tts ', '').replace('Рут, скажи ', '')
            print('[YandexTTS]Asking Yandex to say a word...')
            response = requests.get('https://tts.voicetech.yandex.net/generate?text='
                                    + request + '&format=mp3&lang=ru&key=' + yandex_token, timeout=10)
            filename = 'temp/tts{}.mp3'.format(random.randint(1, 10000))
            if os.path.exists(filename):
                os.remove(filename)
            with open(filename, 'wb') as audiomessagefile:
                audiomessagefile.write(response.content)
            print('[YandexTTS]Uploading audiomessage to VK...')
            data = bot.api.docs.getUploadServer(type='audio_message')
            response = requests.post(data['upload_url'], files={'file': open(filename, 'rb')})
            audiomessage = bot.api.docs.save(file=response.json()['file'])
            bot.tx(message_peer, ats='doc{}_{}'.format(audiomessage[0]['owner_id'], audiomessage[0]['id']))
