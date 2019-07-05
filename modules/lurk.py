import re
import requests
from bs4 import BeautifulSoup

base_url = 'http://lurkmore.to/'
search_url = 'http://lurkmore.to/index.php?title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F%3ASearch&profile=default&fulltext=Search&search='

class Handler:

    list_triggers = [4]
    regexp_patterns = ['!lurk .*', 'Рут, лурк .*']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"

    def responder(self, bot, update):
        message_text = update[5]
        message_peer = update[3]

        if re.match(self.regexp_pattern, message_text):
            request = message_text.replace('!lurk ', '').replace('Рут, лурк ', '')
            print(' [Lurk]Request accepted. Trying to get page directly...')
            bot.api.messages.setActivity(peer_id=message_peer, type='typing')
            link = base_url + request.replace(' ', '_')
            response = requests.get(link)
            if response.status_code == 404:
                print(' [Lurk]Page not found. Trying to search...')
                search_result = ''
                response = requests.get(search_url + request)
                soup = BeautifulSoup(response.text, 'html.parser')
                for div in soup.find_all('div', {'class': 'mw-search-result-heading'}):
                    for a in div.find_all('a'):
                        search_result = a['href']
                        break
                if search_result == '':
                    print(' [Lurk]Page not found. Returning error...')
                    bot.tx(message_peer, txt='Страница не найдена, попробуйте изменить запрос')
                    return
                else:
                    print(' [Lurk]Seach done.')
                    link = base_url + search_result
                    targetpage = requests.get(link)
            else:
                print(' [Lurk]Page found. Processing...')
                targetpage = response
            soup = BeautifulSoup(targetpage.text, 'html.parser')
            for div in soup.find_all('div', {'id': 'mw-content-text'}):
                for p in div.find_all('p', {'class': None}):
                    response_text = p.text
                    break
                break
            if response == '':
                print(' [Lurk]Text not found. Returning error...')
                bot.tx(message_peer, txt='Произошла ошибка при парсинге страницы')
                return
            else:
                print(' [Lurk]Parse success, sending response...')
                response_text += '\nСсылка на статью: ' + link
                bot.tx(message_peer, txt=response_text, safe=True)