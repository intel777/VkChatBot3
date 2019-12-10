import re


def get_numberic_userid(api, userid):
    try:
        return int(userid)
    except ValueError:
        user_data = api.utils.resolveScreenName(screen_name=userid)
        return user_data['object_id']


def get_fwd_ment_user_id(bot, update):
    user_id = None
    if 'fwd' in update[7].keys():
        message = bot.convert_longpoll_message(update[1])
        user_id = message['items'][0]['fwd_messages'][0]['user_id']
    elif 'mentions' in update[6]:
        user_id = update[6]['mentions'][0]
    else:
        mentions = re.findall("(\[id+\d+\|@+\w+\])", update[5])
        for mention in mentions:
            user_id = int(re.findall('\d+', mention)[0])
    return user_id


class Handler:

    list_triggers = [4]
    regexp_patterns = ['!ban.*', '!unban.*', '!addadm.*', '!rmadm.*', '!isbanned.*', '!isadmin.*']
    regexp_pattern = "(" + ")|(".join(regexp_patterns) + ")"

    def responder(self, bot, update):
        message_text = update[5]
        if re.match(self.regexp_pattern, message_text):
            if update[3] < 2000000000:
                message_from_id = update[3]
            else:
                message_from_id = int(update[6]['from'])
            if message_from_id in bot.get_admins():
                user_id = get_fwd_ment_user_id(bot, update)
                reply = ''
                if re.match(self.regexp_patterns[0], message_text):
                    if not user_id:
                        user_id = message_text.replace('!ban ', '')
                        user_id = get_numberic_userid(bot.api, user_id)
                    if user_id not in bot.get_banlist():
                        bot.ban_user(user_id)
                        reply = 'Пользователь с идентификатором *id{} внесен в черный список.'.format(user_id)
                    else:
                        reply = 'Пользователь уже в черном списке.'
                elif re.match(self.regexp_patterns[1], message_text):
                    if not user_id:
                        user_id = message_text.replace('!unban ', '')
                        user_id = get_numberic_userid(bot.api, user_id)
                    if user_id in bot.get_banlist():
                        bot.unban_user(user_id)
                        reply = 'Пользователь с идентификатором *id{} удален из черного списка'.format(user_id)
                    else:
                        reply = 'Пользователь не найден в черном списке.'
                elif re.match(self.regexp_patterns[2], message_text):
                    if not user_id:
                        user_id = message_text.replace('!addadm ', '')
                        user_id = get_numberic_userid(bot.api, user_id)
                    if user_id not in bot.get_admins():
                        bot.add_admin(user_id)
                        reply = 'Привилегии пользователя *id{} повышены до уровня администратора.'.format(user_id)
                    else:
                        reply = 'Пользователь уже администратор.'
                elif re.match(self.regexp_patterns[3], message_text):
                    if not user_id:
                        user_id = message_text.replace('!rmadm ', '')
                        user_id = get_numberic_userid(bot.api, user_id)
                    if user_id in bot.get_admins():
                        bot.rem_admin(user_id)
                        reply = 'Привилегии пользователя *id{} понижены до уровня пользователя.'.format(user_id)
                    else:
                        reply = 'Пользователь не является администратором.'
                elif re.match(self.regexp_patterns[4], message_text):
                    if not user_id:
                        user_id = message_text.replace('!isbanned ', '')
                        user_id = get_numberic_userid(bot.api, user_id)
                    if user_id in bot.get_banlist():
                        reply = 'Пользователь *id{} найден в черном списке.'.format(user_id)
                    else:
                        reply = 'Пользователь *id{} не найден в черном списке.'.format(user_id)
                elif re.match(self.regexp_patterns[5], message_text):
                    if not user_id:
                        user_id = message_text.replace('!isadmin ', '')
                        user_id = get_numberic_userid(bot.api, user_id)
                    if user_id in bot.get_admins():
                        reply = 'Пользователь *id{} найден в списке администраторов.'.format(user_id)
                    else:
                        reply = 'Пользователь *id{} не найден в списке администраторов.'.format(user_id)
                bot.tx(update[3], txt=reply)
