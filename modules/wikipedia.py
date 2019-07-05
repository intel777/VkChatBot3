import re
import wikipedia

class Handler:

    list_triggers = [4]
    regexp_patterns = ['!wiki .*', 'Рут, что такое .*', 'Рут, вики .*']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"
    wikipedia.set_lang('ru')

    def responder(self, bot, update):
        message_text = update[5]
        message_peer = update[3]
        reply = ''

        if re.match(self.regexp_pattern, message_text):
            print('[Wikipedia]Request accepted, processing...')
            bot.api.messages.setActivity(peer_id=message_peer, type='typing')
            request = message_text.replace('!wiki ', '').replace('Рут, что такое ', '').replace('Рут, вики ', '')
            try:
                wiki_page = wikipedia.page(request)
                summary = wiki_page.summary
                page_url = wiki_page.url
                reply = summary + '\n\nСсылка на статью: ' + page_url
            except wikipedia.exceptions.DisambiguationError as e:
                reply = 'Возможно, вы имели в виду:\n{}'.format('\n'.join(e.options))
            except wikipedia.exceptions.PageError:
                reply = 'Такой страницы не существует, попробуйте изменить запрос'
            except Exception:
                reply = 'При обработке запроса произошла ошибка, попробуйте еще раз.'
            bot.tx(message_peer, txt=reply, safe=True)
