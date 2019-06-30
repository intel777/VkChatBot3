import re
import os


class Handler:

    list_triggers = [4]
    regexp_patterns = ['Рут, список модулей', 'Рут, загрузи модуль .*', 'Рут, выгрузи модуль .*', '!loader.list',
                       '!loader.load .*', '!loader.unload .*']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"

    def responder(self, bot, update):
        message_text = update[5]

        if re.match(self.regexp_pattern, message_text):
            if update[3] < 2000000000:
                message_from_id = update[3]
            else:
                message_from_id = int(update[6]['from'])
            if message_from_id in bot.get_admins():
                reply = ''
                if re.match(self.regexp_patterns[0], message_text) or re.match(self.regexp_patterns[3], message_text):
                    modules_list = os.listdir('modules')
                    for module in modules_list:
                        if module[-3:] == '.py':
                            if bot.module_loaded(module):
                                reply += '[✅] {}'.format(module)
                            else:
                                reply += '[❌] {}'.format(module)
                            reply += '\n'
                elif re.match(self.regexp_patterns[1], message_text) or re.match(self.regexp_patterns[4], message_text):
                    module_name = message_text.replace('Рут, загрузи модуль ', '').replace('!loader.load ', '')
                    if not bot.module_loaded(module_name):
                        load_result = bot.load_module(module_name)
                        if load_result:
                            reply = 'Модуль {} успешно загружен'.format(module_name)
                        else:
                            reply = 'Ошибка загрузки модуля!'
                    else:
                        reply = 'Модуль {} уже загружен.'.format(module_name)
                elif re.match(self.regexp_patterns[2], message_text) or re.match(self.regexp_patterns[5], message_text):
                    module_name = message_text.replace('Рут, выгрузи модуль ', '').replace('!loader.unload ', '')
                    if bot.module_loaded(module_name):
                        unload_result = bot.unload_module(module_name)
                        if unload_result:
                            reply = 'Модуль {} успешно выгружен'.format(module_name)
                        else:
                            reply = 'Ошибка выгрузки модуля. Проверьте правильность написания имени модуля.'
                    else:
                        reply = 'Модуль {} не загружен, поэтому не может быть выгружен.'.format(module_name)
                bot.tx(update[3], txt=reply)
