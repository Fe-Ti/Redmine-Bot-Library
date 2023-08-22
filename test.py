from BotCore import *
scenery_v2 = {
    "start_state" : "start",
    "states":{
        "start" : {
            Type    : Ask,
            Error   : "start",
            Info    : "start",
            Phrase  : "Введи команду.",
            Next    : { # "state" : [keywords]
                        "create"    : ["создай"],
                        # ~ "update"    : ["обнови","измени"],
                        # ~ "show"      : ["покажи"],
                        # ~ "delete"    : ["удали"],
                        "select"    : ["выбери", "в"],
                        # ~ "settings"  : ["запомни"]
                        }
        },
        "create" : {
            Type    : Say,
            Error   : "start",
            Info    : "Ошибка 404: помощь для состояния 'create' не найдена",
            Phrase  : """Какой тип объекта ты хочешь создать? Хотя погоди... я этого пока ещё не умею :)
Так что введи что-нибудь для возвращения назад.""",
            Next    : "start"
        },
        "select" : {
            Type    : Ask,
            Error   : "start",
            Info    : "select",
            Phrase  : "С каким типом объектов ты хочешь работать? С проектом или задачей?",
            Next    : {
                "select_issue"  : ["задачу", "задаче", "задачей"],
                "select_project": ["проект", "проекте", "проектом"],
                "select":["с"]
            }
        },
        "select_issue" : {
            Type    : Get,
            Error   : "start",
            Info    : "select",
            Phrase  : "Введи идентификатор задачи.",
            Set     : {Context:Issue},
            Input   : {Data:'id'},
            Next    : "start"
        },
        "select_project" : {
            Type    : Get,
            Error   : "start",
            Info    : "select",
            Phrase  : "Введи идентификатор проекта.",
            Set     : {Context:Project},
            Input   : {Data:'id'},
            Next    : "start"
        },

    },
    "errors" : {
        "start" : "ERRRORORORORORO!!!!1!!!111!"
    },
    "infos" : {
        "start" : """Команды строятся из глагола в повелительном наклонении и объекта над которым необходимо произвести действие.
Для этого мне нужно знать контекст. Чтобы его задать перед командой можно написать "в <объекте> <id> <команда>" или "выбери <объект>..."
Например, "в проекте 1 создай задачу". Если выбран контекст, то хватит обычной команды. Напиши одно из следующих слов:
 - создай
 - в
 - выбери
В ответ я выдам наводящую фразу. Если нужна будет справка, то в любой момент ты можешь получить её с помощью команд "!справка" и "!помощь".

Чтобы я вернулась к началу и сбросила контекст и все временные переменные введи "!сброс" или "!отмена".
Замечу, что все лексемы я разбираю аналогично командной строке, т.е. если записать в кавычках "В чащах юга жил-был цитрус...", то я интерпретирую это не как отдельные слова, а как целую строку.

@Fe_Ti просил передать, что я пока умею только разбирать запросы и иногда могу падать. Поэтому при неполадках со мной обращаться к нему.
""",
        "select":"""Задание контекста нужно для того, чтобы я понимала в каком объекте я работаю."""
    },
    "commands" : {
        "info"      : ["!справка", "!помощь"],
        "reset"     : ["!сброс", "!отмена"],
        # ~ "cancel"    : ["!отмена"]
    }
}
config = {
    "use_https"         : False,#True,
    "refresh_period"    : 5, # in seconds
    "sleep_timeout"     : 10,
    "redmine_root_url"  : "localhost/redmine",
    "bot_user_key"      : "8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6",
}


from sys import argv
from time import sleep

from origamibot import OrigamiBot as Bot
from origamibot.listener import Listener



START_MSG = """Привет, {first_name}! Меня зовут Тасфия ‒ я бот таск-трекера Искры.
Введи "!справка" для получения справочной информации."""
def get_start_msg(message):
    return START_MSG.format(first_name = message.chat.first_name)

def get_info_msg():
    return """Я могла бы много рассказать, но пока я ничего не знаю.
Разве только команды:
 - /start
 - /info
 - /echo <текст>
"""

class BotsCommands:
    def __init__(self, bot: Bot, scenery_bot):  # Can initialize however you like
        self.bot = bot
        self.scenery_bot = scenery_bot

    def start(self, message):   # /start command
        if message.chat.id not in self.scenery_bot.user_db:
            self.scenery_bot.add_user(message.chat.id)
            self.bot.send_message(
                message.chat.id,
                get_start_msg(message))
        else:
            self.bot.send_message(
                message.chat.id,
                "А я вас знаю!(с)")


    # ~ def info(self, message):
        # ~ self.bot.send_message(
            # ~ message.chat.id,
            # ~ get_info_msg())

    # ~ def echo(self, message, value: str):  # /echo [value: str] command
        # ~ print(message)
        # ~ print(value)
        # ~ self.bot.send_message(
            # ~ message.chat.id,
            # ~ value
            # ~ )

    # ~ def add(self, message, a: float, b: float):  # /add [a: float] [b: float]
        # ~ self.bot.send_message(
            # ~ message.chat.id,
            # ~ str(a + b)
            # ~ )


    def _not_a_command(self):   # This method not considered a command
        print('???')


class MessageListener(Listener):  # Event listener must inherit Listener
    def __init__(self, bot, scenery_bot):
        self.bot = bot
        self.scenery_bot = scenery_bot
        self.scenery_bot.set_reply_function(self.__reply_user)
        self.m_count = 0

    def __reply_user(self, message):
        self.bot.send_message(message.user_id, message.content)

    def on_message(self, message):   # called on every message
        self.m_count += 1
        print(f'Total messages: {self.m_count}')
        # Here should be some message processing
        # ~ self.bot.send_message(
            # ~ message.chat.id,
            # ~ "Сообщение получила!")
        if (message.chat.id not in self.scenery_bot.user_db) and not(message.text.startswith("/start")):
            self.bot.send_message (
            message.chat.id,
            "Без /start я работать не буду!")
            return
        elif message.text.startswith("/"):
            pass
        else:
            self.scenery_bot.process_user_message(Message(
                message.chat.id,
                message.text
                ))


    def on_command_failure(self, message, err=None):  # When command fails
        if err is None:
            self.bot.send_message(message.chat.id,
                                  'Э-э-эм... не поняла')
        else:
            self.bot.send_message(message.chat.id,
                                  f"В команде есть ошибка:\n{err}")


# ~ if __name__ == '__main__':
token = (argv[1] if len(argv) > 1 else input('Enter bot token: '))
bot = Bot(token)   # Create instance of OrigamiBot class
scbot = BotCore(scenery_v2, config)   # Create instance of scenery bot

# Add an event listener
bot.add_listener(MessageListener(bot,scbot))

# Add a command holder
bot.add_commands(BotsCommands(bot, scbot))

# We can add as many command holders
# and event listeners as we like

bot.start()   # start bot's threads
scbot.start()   # start bot's threads
# ~ print(dir(bot))
try:
    while True:
        sleep(1)
        # Can also do some useful work i main thread
        # Like autoposting to channels for example
except KeyboardInterrupt:
    while scbot.is_running:
        try:
            scbot.stop()
        except KeyboardInterrupt as kbip:
            print(kbip)
