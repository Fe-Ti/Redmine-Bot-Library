from BotCore import *
Issue = "issue"
Project = "project"
scenery_v2 = {
    "start_state" : "start",
    "states":{
        "start" : {
            Type    : ask,
            Error   : "start",
            Info    : "start",
            Phrase  : "Введи команду :)",
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
            Type    : say,
            Error   : "start",
            Info    : "create",
            Phrase  : "/Creating state entered... But going back to start state",
            Next    : "start"
        },
        "select" : {
            Type    : ask,
            Error   : "start",
            Info    : "select",
            Phrase  : "Введи тип объекта",
            Next    : {
                "select_issue"  : ["задачу", "задаче"],
                "select_project": ["проект", "проекте"]
            }
        },
        "select_issue" : {
            Type    : get,
            Error   : "start",
            Info    : "start",
            Phrase  : "/Creating state entered... But going back to start state",
            Set     : {"user.context":Issue},
            Input   : "data['id']",
            Next    : "start"
        },
        "select_project" : {
            Type    : get,
            Error   : "start",
            Info    : "start",
            Phrase  : "/Creating state entered... But going back to start state",
            Set     : {"user.context":Project},
            Input   : "data['id']",
            Next    : "start"
        },
        
    },
    "errors" : {
        "start" : "ERRRORORORORORORORORORO!!!!!!!1!!!111!"
    },
    "infos" : { 
        "start" : "Тестовая справка"
    },
    "commands" : {
        "info"      : ["!справка", "!помощь"],
        "reset"     : ["!сброс"],
        "cancel"    : ["!отмена"]
    }
}
config = {
    "use_https"         : True,
    "refresh_period"    : 60, # in seconds
    "sleep_timeout"     : 3600,
    "redmine_root_url"  : "localhost/redmine",
    "bot_user_key"      : "8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6",
}


from sys import argv
from time import sleep

from origamibot import OrigamiBot as Bot
from origamibot.listener import Listener



START_MSG = "Привет, {first_name}! Меня зовут Тасфия ‒ я бот таск-трекера Искры."
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
    def __init__(self, bot: Bot):  # Can initialize however you like
        self.bot = bot

    def start(self, message):   # /start command
        self.bot.send_message(
            message.chat.id,
            get_start_msg(message))

    def info(self, message):
        self.bot.send_message(
            message.chat.id,
            get_info_msg())

    def echo(self, message, value: str):  # /echo [value: str] command
        # ~ print(message)
        # ~ print(value)
        self.bot.send_message(
            message.chat.id,
            value
            )

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
        self.bot.send_message(
            message.chat.id,
            "Сообщение получила!")
        self.scenery_bot.process_user_message(Message(
            message.chat.id,
            message.content
            ))


    def on_command_failure(self, message, err=None):  # When command fails
        if err is None:
            self.bot.send_message(message.chat.id,
                                  'Э-э-эм... не поняла')
        else:
            self.bot.send_message(message.chat.id,
                                  'В команде есть ошибка:\n{err}')


if __name__ == '__main__':
    token = (argv[1] if len(argv) > 1 else input('Enter bot token: '))
    bot = Bot(token)   # Create instance of OrigamiBot class
    scbot = BotCore(scenery_v2, config)   # Create instance of scenery bot
    
    # Add an event listener
    bot.add_listener(MessageListener(bot))

    # Add a command holder
    bot.add_commands(BotsCommands(bot))

    # We can add as many command holders
    # and event listeners as we like

    bot.start()   # start bot's threads
    print(dir(bot))
    while True:
        sleep(1)
        # Can also do some useful work i main thread
        # Like autoposting to channels for example
