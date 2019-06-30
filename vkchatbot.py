import vk
import datetime
import os
import requests
import json
import traceback
import sys
import random
from threading import Thread

disallowed_words = []


def get_time_date_string():
    now_time = datetime.datetime.now()
    current_time = now_time.strftime('%H-%M-%S')
    current_date = now_time.strftime('%d.%m.%y')
    return '{} {}'.format(current_date, current_time)


class Bot:

    boot_timestamp = None
    log_path = None
    api = None
    modules_loaded = []
    listeners = []
    admins = []
    banlist = []
    conflict_regexps = []

    def init(self, token):
        self.boot_timestamp = datetime.datetime.now()
        self.api = vk.API(vk.AuthSession(access_token=token), v=5.68)
        if not os.path.exists('temp'):
            os.makedirs('temp')
        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.log_path = 'logs/' + str(datetime.date.today()) + '_' + self.boot_timestamp.strftime('%H-%M-%S') + '.log'
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        open(self.log_path, 'w').close()
        if os.path.exists('config.json'):
            with open('config.json', 'r') as configfile:
                config = json.load(configfile)
            self.admins = config['admins']
            self.banlist = config['banlist']
        else:
            config = {'admins': [], 'banlist': []}
            with open('config.json', 'w') as configfile:
                json.dump(config, configfile)

    def save_config(self):
        config = {'admins': self.admins, 'banlist': self.banlist}
        with open('config.json', 'w') as configfile:
            json.dump(config, configfile)

    def write_to_log(self, message):
        with open(self.log_path, 'a') as logfile:
            logfile.write(message)

    def log_traceback(self, module_name, traceback_data):
        self.write_to_log('''
        [{}, TS: {}]
        {}
        '''.format(module_name, get_time_date_string(), traceback_data))

    def refresh_long_poll(self):
        print('[LongPollProvider]Refreshing longpoll...')
        longpoll_data = self.api.messages.getLongPollServer(lp_version=3)
        longpoll_key = longpoll_data['key']
        longpoll_server = longpoll_data['server']
        longpoll_ts = longpoll_data['ts']
        return longpoll_key, longpoll_server, longpoll_ts

    def lp_listener(self):
        print('[{}][LongPollHandler]Started'.format(get_time_date_string()))
        print('[{}][LongPollHandler]Getting LongPoll data...'.format(get_time_date_string()))
        long_poll_key, long_poll_server, long_poll_ts = self.refresh_long_poll()
        while True:
            try:
                response = requests.get(
                    'https://{}?act=a_check&key={}&ts={}&wait=25&version=3&mode=74'.format(long_poll_server,
                                                                                           long_poll_key, long_poll_ts))
                long_poll_response = json.loads(response.text)
                try:
                    long_poll_ts = long_poll_response['ts']
                except KeyError:
                    print('[LongPollHandler]LongPoll Error, initializing refreshment...')
                    long_poll_key, long_poll_server, long_poll_ts = self.refresh_long_poll()
                    continue
                print(long_poll_response)
                for update in long_poll_response['updates']:
                    if len(update) >= 4:
                        if update[3] < 2000000000:
                            message_from_id = update[3]
                        else:
                            message_from_id = int(update[6]['from'])
                    else:
                        message_from_id = 0
                    if message_from_id not in self.banlist:
                        for listener in self.listeners[:]:
                            if update[0] in listener['triggers']:
                                print(update)
                                Thread(target=listener['responder'], args=(self, update)).start()
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                traceback_str = ''.join(line for line in lines)
                self.log_traceback('Longpoll Listener', traceback_str)
                print(traceback_str)

    def start_polling(self):
        Thread(target=self.lp_listener).start()

    def convert_longpoll_message(self, message_id):
        return self.api.messages.getById(message_ids=message_id)

    def load_module(self, filename):
        print('[Bot][Module Loader]Requested module load with {}.py filename!'.format(filename))
        module = __import__('modules.{}'.format(filename), fromlist=[filename])
        handler = module.Handler()
        triggers = handler.list_triggers
        if hasattr(handler, 'regexp_patterns'):
            self.conflict_regexps += handler.regexp_patterns
        self.listeners.append(
            {'triggers': triggers, 'handler': handler, 'responder': handler.responder, 'module': filename})
        self.modules_loaded.append('{}.py'.format(filename))
        return True

    def unload_module(self, filename):
        print('[Bot][Module Unloader]Requested module unload {}.py'.format(filename))
        try:
            for listener in self.listeners:
                if listener['module'] == filename:
                    self.listeners.remove(listener)
            self.modules_loaded.remove('{}.py'.format(filename))
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            traceback_str = ''.join(line for line in lines)
            print(traceback_str)
            return False
        return True

    def module_loaded(self, filename):
        if filename[-3:] != '.py':
            filename += '.py'
        if '{}'.format(filename) in self.modules_loaded:
            return True
        return False

    def get_listeners(self):
        return self.listeners

    def get_admins(self):
        return self.admins

    def get_banlist(self):
        return self.banlist

    def add_admin(self, admin_id):
        self.admins.append(admin_id)
        self.save_config()
        return True

    def rem_admin(self, admin_id):
        try:
            self.admins.remove(admin_id)
            self.save_config()
            return True
        except ValueError:
            return False

    def ban_user(self, user_id):
        self.banlist.append(user_id)
        self.save_config()
        return True

    def unban_user(self, user_id):
        try:
            self.banlist.remove(user_id)
            self.save_config()
            return True
        except ValueError:
            return False

    def get_conflict_regexps(self):
        return "(" + ")|(".join(self.conflict_regexps) + ")"

    def tx(self, peer, safe=False, txt=None, ats=None):
        if txt:
            txt = str(txt)
            if not safe:
                txt = txt.replace('&#', '')
                splitted_message = txt.split('.')
                txt = '.&#8206;'.join(splitted_message)
                txt += '\n'
                txt += '&#8206;' * random.randint(1, 8)
            for word in disallowed_words:
                if word in txt.lower():
                    txt = txt.lower().replace(word, '<deleted>')
        self.api.messages.send(peer_id=peer, message=txt, attachment=ats)
