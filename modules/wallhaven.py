import re
import requests
from threading import Thread

api_key = ''  # Your API key here


def download_image(url, images):
    response = requests.get(url)
    filename = 'temp/' + url.split('/')[-1]
    with open(filename, 'wb') as image:
        image.write(response.content)
    images.append(filename)


class Handler:

    list_triggers = [4]
    regexp_patterns = ['!wh*.']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"

    def responder(self, bot, update):
        message_text = update[5]
        message_peer = update[3]

        if re.match(self.regexp_pattern, message_text):
            print('[Wallhaven]Processing request from {}'.format(message_peer))
            bot.api.messages.setActivity(peer_id=message_peer, type='typing')
            q = None
            nsfw = False
            anime = False
            amount = 1
            links = []
            images = []
            threads = [None] * 10

            reply = ''
            request = message_text.lower().replace('!wh ', '').replace(' пикч ', '')
            try:
                amount = int(re.findall('\d+', request)[0])
                if 0 > amount or 10 < amount:
                    bot.tx(message_peer, txt='Ошибка. Количество запрашиваемых изображений должно быть от 1 до 10')
                    return
                buf = request
                request = ''.join([i for i in buf if not i.isdigit()])
            except Exception:
                pass
            if 'anime' in request or 'аниме' in request:
                anime = True
                request = request.replace(' аниме ', '').replace(' anime ', '')
            if 'nsfw' in request or 'порно' in request:
                nsfw = True
                request = request.replace(' nsfw ', '').replace(' порно ', '')
            buf = request.replace(' ', '')
            if buf != 'anime' and buf != 'аниме' and buf != 'nsfw' and buf != 'порно' and buf != '!wh':
                q = request
            query = '&categories='
            if anime:
                query += '010'
            else:
                query += '111'
            query += '&purity='
            if nsfw:
                query += '001'
            else:
                query += '110'
            query += '&sorting=random'
            if q:
                query += '&q={}'.format(q)
            print('[Wallhaven]Sending request to wallhaven...')
            response = requests.get('https://wallhaven.cc/api/v1/search?apikey=' + api_key + query)
            response = response.json()
            for i in range(0, amount):
                try:
                    links.append(response['data'][i]['path'])
                except IndexError:
                    print('[Wallhaven]Warn: not enough images in response')
                    break
            print('[Wallhaven]Downloading images...')
            for i in range(0, len(links)):
                threads[i] = Thread(target=download_image, args=(links[i], images))
                threads[i].start()
            for thread in threads:
                try:
                    thread.join()
                except Exception:
                    pass
            vk_images = bot.mass_upload_message_images(images)
            attachments = []
            for image in vk_images:
                attachments.append('photo{}_{}'.format(image['owner_id'], image['id']))
            bot.tx(peer=message_peer, txt='Ну, как-то так', ats=attachments)
