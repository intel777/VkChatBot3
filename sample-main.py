from vkchatbot import Bot

print('VkChatBot version 3.0.0 starting...')
vkToken = 'YOUR_ACCESS_TOKEN_HERE'

modules_to_load = ['loader', 'admin_tools', 'simple_chat', 'intel_ark', 'wallhaven', 'wit_ai', 'wikipedia', 'lurk',
                   'yandex_tts']

print('[VKCB][Boot]Initializing Bot...')
bot = Bot()
bot.init(vkToken)
for module in modules_to_load:
    bot.load_module(module)
bot.start_polling()
