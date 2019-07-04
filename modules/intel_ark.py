import re
import requests
from bs4 import BeautifulSoup

state_aftersearch = {}


def parse_sheet(text):
    reply = ''
    soup = BeautifulSoup(text, 'html.parser')
    specs_sheet = soup.find('div', {'id': 'tab-blade-1-0'})
    if specs_sheet:
        for spec_subsheet in specs_sheet.find_all('section', {'class': 'blade specs-blade specifications'}):
            title = spec_subsheet.find('h2', {'class': 'h2'}).text
            reply += '===============\n{}\n===============\n'.format(title)
            for spec in spec_subsheet.find_all('ul', {'class': 'specs-list'}):
                for li in spec.find_all('li'):
                    label = li.find('span', {'class': 'label'}).text.replace('\n', '').replace(' ' * 49, '') \
                        .replace('‡', '')
                    value = li.find('span', {'class': 'value'}).text.replace('\n', '').replace(' ' * 49, '')
                    reply += '{}: {}\n'.format(label, value)
    else:
        return None
    return reply


class Handler:

    list_triggers = [4]
    regexp_patterns = ['!ark *.']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"

    def responder(self, bot, update):
        message_text = update[5]
        message_peer = update[3]

        if re.match(self.regexp_pattern, message_text):
            print('[IntelARK]Responding on request from {}'.format(message_peer))
            query = message_text.replace('!ark ', '')
            reply = ''
            print(query)
            if message_peer not in state_aftersearch:
                print('[IntelARK]Peer not found in db, stage 1 begin...')
                response = requests.get('https://ark.intel.com/content/www/ru/ru/ark/search.html?_charset_=UTF-8&q='
                                        + query)
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('h4', {'class': 'result-title'})
                if results:
                    print('[IntelARK]Search complete, parsing response...')
                    state_aftersearch[message_peer] = results
                    i = 0
                    reply += 'Результаты поиска по запросу {}:\n'.format(query)
                    for result in results:
                        reply += '{}. {}\n'.format(i, result.text)
                        i += 1
                else:
                    print('[IntelARK]Search returned 404, searching for RedirectURL')
                    redirect_input = soup.find('input', {'id': 'FormRedirectUrl'})
                    if redirect_input:
                        print('[IntelARK]RedirectURL found, parsing...')
                        response = requests.get('https://ark.intel.com' + redirect_input['value'])
                        response.encoding = 'utf-8'
                        reply = parse_sheet(response.text)
                    else:
                        print('[IntelARK]Nothing found, giving up...')
                        reply = 'Не найдено процессоров по запросу {}.'.format(query)
            else:
                print('[IntelARK]Peer found in db, acting like it is search result selector...')
                try:
                    query = int(query)
                    soup = state_aftersearch[message_peer][int(query)]
                    a = soup.find_all('a')[0]
                    link = a['href']
                    print('[IntelARK]Parsing response...')
                    response = requests.get('https://ark.intel.com' + link)
                    response.encoding = 'utf-8'
                    reply = parse_sheet(response.text)
                    del state_aftersearch[message_peer]
                except ValueError:
                    reply = 'Вам необходимо ввести цифру от 0 до {}, чтобы продолжить.'.format(
                        len(state_aftersearch[message_peer]) - 1)
            bot.tx(message_peer, txt=reply)
