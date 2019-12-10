import os
import json
import requests
import random
import re
from wit import Wit

wit_ai = Wit('') #


def wit_recognize(audiomsg_link):
    print('[Wit.AI]Downloading link...')
    response = None
    filename = 'temp/audiomsg{}.mp3'.format(random.randint(1, 10000))
    if os.path.exists(filename):
        print(' [Warn]temp.mp3 already exists. Deleting...')
        os.remove(filename)
    audiomsg = requests.get(audiomsg_link)
    with open(filename, 'wb') as audiomsg_file:
        audiomsg_file.write(audiomsg.content)
    print('[Wit.AI]Decoding message...')
    with open(filename, 'rb') as audiomsg_file:
        try:
            response = wit_ai.speech(audiomsg_file, None, {'Content-Type': 'audio/mpeg3'})['_text']
        except Exception:
            response = '[Голосовое сообщение слишком длинное, или сервер не ответил на запрос]'
    os.remove(filename)
    return response


class Handler:

    list_triggers = [4]
    auto_recognition_peers = []
    regexp_patterns = ['!stt', '!autostt']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"

    def __init__(self):
        if os.path.exists('wit_ai_config.json'):
            with open('wit_ai_config.json', 'r') as configfile:
                self.auto_recognition_peers = json.load(configfile)
        else:
            with open('wit_ai_config.json', 'w') as configfile:
                json.dump([], configfile)

    def save_config(self):
        with open('wit_ai_config.json', 'w') as configfile:
            json.dump(self.auto_recognition_peers, configfile)

    def responder(self, bot, update):
        message_text = update[5]
        message_peer = update[3]
        recognition_results = []
        if re.match(self.regexp_pattern, message_text):
            if re.match(self.regexp_patterns[0], message_text):
                print('[Wit.AI]Decode of fwd_message requested, processing...')
                bot.api.messages.setActivity(peer_id=message_peer, type='typing')
                if 'fwd' in update[7].keys():
                    message = bot.convert_longpoll_message(update[1])
                    for fwd_message in message['items'][0]['fwd_messages']:
                        if ('attachments' in fwd_message) and (
                                'doc' in fwd_message['attachments'][0]) and (
                                'preview' in fwd_message['attachments'][0]['doc']) and (
                                'audio_msg' in fwd_message['attachments'][0]['doc']['preview']):
                            try:
                                recognition_results.append(wit_recognize(fwd_message['attachments'][0]['doc']['preview']['audio_msg']['link_mp3']))
                            except Exception:
                                bot.tx(message_peer, txt='Ошибка при обработке аудиосообщения')
                                return
                    if recognition_results:
                        reply = '=====[Речь -> Текст]=====\n'
                        reply += '\n'.join(recognition_results)
                        reply += '\n======================'
                else:
                    reply = 'Не удалось найти аудиосообщения для распознавания.'
            elif re.match(self.regexp_patterns[1], message_text):
                if message_peer in self.auto_recognition_peers:
                    self.auto_recognition_peers.remove(message_peer)
                    self.save_config()
                    reply = '[❌] Функция автоматического распознавания сообщений отключена.'
                else:
                    self.auto_recognition_peers.append(message_peer)
                    self.save_config()
                    reply = '[✅] Функция автоматического распознавания сообщений включена.'
            bot.tx(message_peer, txt=reply)
        elif message_peer in self.auto_recognition_peers:
            if len(update) > 7:
                if ('attach1_kind' in update[7]) and (update[7]['attach1_kind'] == 'audiomsg'):
                    print('[Wit.AI]Auto recognition triggered, processing...')
                    bot.api.messages.setActivity(peer_id=message_peer, type='typing')
                    message = bot.convert_longpoll_message(update[1])
                    recognition_results.append(wit_recognize(message['items'][0]['attachments'][0]['doc']['preview']['audio_msg']['link_mp3']))
                    if recognition_results:
                        reply = '=====[Речь -> Текст]=====\n'
                        reply += '\n'.join(recognition_results)
                        reply += '\n======================'
                    else:
                        reply = 'Ошибка при обработке аудиосообщений.'
                    bot.tx(message_peer, txt=reply)
