from BotCore import *
scenery_v2 = {
    "start_state"   : "start",
    "hint_template" : "\n\n>>{}",
    "states":{
        "init1":{ # dummy
                Type    : Say,
                Error   : None,
                Info    : None,
                Phrase  : """""",
                Next    : "init2",
                # ~ Properties : [Lexeme_preserving]
        },
        "init2":{
                Type    : Say,
                Error   : None,
                Info    : None,
                Phrase  : """А пока, как сказано в Слове, "Почнёмъ же, братие, повѣсть сию" c ключа к API.""",
                Next    : "set_key",
                Properties : [Lexeme_preserving]
        },
        "start" : {
            Type    : Ask,
            Error   : "start",
            Info    : "start",
            Phrase  : "Введи команду.",
            Next    : {
                        # ~ "create"    : ["создай"],
                        # ~ "update"    : ["обнови","измени"],
                        "show"      : ["покажи"],
                        # ~ "delete"    : ["удали"],
                        "select"    : ["выбери", "в"],
                        "settings"  : ["запомни", "настрой"]
                        }
        },
        "create" : {
            Type    : Say,
            Error   : "start",
            Info    : "Ошибка 404: помощь для состояния 'create' не найдена",
            Phrase  : """Какой тип объекта ты хочешь создать? Хотя погоди... я этого пока ещё не умею :)""",
            Next    : "start",
            Properties : [Lexeme_preserving]
        },
        "show" : {
            Type    : Ask,
            Error   : "start",
            Info    : "Ошибка 404: помощь для состояния 'create' не найдена",
            Phrase  : """Что ты хочешь посмотреть?""",
            Next    : {
                        "show_list":["список"],
                        # ~ "show_project":["проект"],
                        # ~ "show_issue":["задачу"],
                        }
        },
        "show_list" : {
            Type    : Ask,
            Error   : "start",
            Info    : "start",
            Phrase  : """Список чего ты хочешь увидеть?""",
            Next    : {
                        "show_list_of_projects":["проектов"],
                        "show_list_of_issues":["задач"]
            }
        },
        "show_list_of_projects" : {
            Type    : Say,
            Error   : "start",
            Info    : "start",
            Phrase  : """Вот список проектов:""",
            Next    : "start",
            Functions: ["get_project_list"],
            Properties : [Lexeme_preserving]
        },
        "show_list_of_issues" : {
            Type     : Say,
            Error    : "start",
            Info     : "start",
            Phrase   : """Вот список задач:""",
            Next     : "start",
            Functions: ["get_issue_list"],
            Properties : [Lexeme_preserving]
        },
        "show_project" : {
            Type    : Ask,
            Error   : "start",
            Info    : "start",
            Phrase  : """Какой проект ты хочешь посмотреть?""",
            Next    : {
                        "":[""]
                        }
        },
        # ~ "show_issue" : {
            # ~ Type    : Ask,
            # ~ Error   : "start",
            # ~ Info    : "Ошибка 404: помощь для состояния 'create' не найдена",
            # ~ Phrase  : """Что ты хочешь посмотреть?""",
            # ~ Next    : {
                        # ~ "":[""]
                        # ~ }
        # ~ },
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
            Set     : {Settings : {Context:Issue}},
            Input   : {Data:'id'},
            Next    : "start"
        },
        "select_project" : {
            Type    : Get,
            Error   : "start",
            Info    : "select",
            Phrase  : "Введи идентификатор проекта.",
            Set     : {Settings : {Context:Project}},
            Input   : {Data:'id'},
            Next    : "start"
        },
        "settings" : {
            Type    : Ask,
            Error   : "start",
            Info    : "settings",
            Phrase  : "Что ты хочешь настроить? (ответ 'ничего' или '.' отправит тебя к нормальному режиму работы)",
            Next    :   {
                        "set_key" : ["ключ"],
                        "set_approve_mode" : ["подтверждение"],
                        "set_behaviour" : ["поведение"],
                        "start" : ["ничего", "."]
                        }
        },
        "set_key" : {
            Type    : Get,
            Error   : "start",
            Info    : "settings",
            Phrase  : "Введи свой ключ API.",
            Input   : {Settings : Key},
            Next    : "set_key_feedback"
        },
        "set_key_feedback" : {
            Type    : Say,
            Error   : "start",
            Info    : "settings",
            Phrase  : "Я запомнила твой ключ. Переходим в меню настроек.",
            Next    : "settings",
            Properties: [Phrase_formatting, Lexeme_preserving]
        },
        "set_behaviour" : {
            Type    : Ask,
            Error   : "start",
            Info    : "settings",
            Phrase  : "Поведение чего ты хочешь настроить?",
            Next    :   {
                        "set_approve_mode"   : ["подтверждения"],
                        "set_reset_if_error" : ["сброса"]
                        }
        },
        "set_approve_mode"   : {
            Type    : Ask,
            Error   : "start",
            Info    : "settings",
            Phrase  : "set_approve_mode_phrase",
            Next    :   {
                        "set_approve_mode_true" : ["да"],
                        "set_approve_mode_false": ["нет"]
                        },
            Properties:[Phrase_formatting]
        },
        "set_approve_mode_true" : {
            Type    : Say,
            Error   : "start",
            Info    : "Ошибка",
            Phrase  : "setted_approve_mode",
            Set     : {Settings : {Approve_changes:True}},
            Next    : "settings",
            Properties:[Lexeme_preserving,Phrase_formatting]
        },
        "set_approve_mode_false": {
            Type    : Say,
            Error   : "start",
            Info    : "Ошибка",
            Phrase  : "setted_approve_mode",
            Set     : {Settings : {Approve_changes:False}},
            Next    : "settings",
            Properties:[Lexeme_preserving,Phrase_formatting]
        },
        "set_reset_if_error" : {
            Type    : Say,
            Error   : "start",
            Info    : "Ошибка 404",
            Phrase  : """rrr""",
            Next    : "settings",
        }

    },
    "phrases": {
        "set_approve_mode_phrase":"""Подтверждать изменения? (да/нет, сейчас установлено '{Settings[Approve_changes]}')""",
        "setted_approve_mode":"Установила подтверждение изменений: '{Settings[Approve_changes]}'",
    },
    "errors" : {
        "start" : "Запрос некорректен, проверь его."
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

@Fe_Ti просил передать, что я пока умею только падать. Поэтому при неполадках со мной обращаться к нему.
""",
        "select"    : """Задание контекста нужно для того, чтобы я понимала в каком объекте я работаю.""",
        "settings"  : """Здесь ты можешь настроить ключ API и некоторые аспекты моего поведения (например, отключить подсказки)."""
    },
    "commands" : {
        "info"      : ["!справка", "!помощь"],
        "reset"     : ["!сброс"],
        "cancel"    : ["!отмена"],
        "repeat"    : ["!повтори"]
    }
}

config = {
    "use_https"             : False,#True,
    "refresh_period"        : 5, # in seconds
    "sleep_timeout"         : 10,
    "redmine_root_url"      : "localhost/redmine",
    "bot_user_key"          : "8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6",
    "user_db_path"          : "./localbase.json",
    "allowed_api_functions" : [
                                "reset_user",
                                "create",
                                "show",
                                "update",
                                "delete",
                                "get_project_list",
                                "get_issue_list",
                                "show_issue_statuses",
                                "show_issue_priorities",
                                "add_watcher",
                                "delete_watcher",
                                # ~ "set"
                                ]
}


import signal
from sys import argv
from time import sleep

from origamibot import OrigamiBot as Bot
from origamibot.listener import Listener



START_MSG = """Привет, {first_name}. Меня зовут Тасфия ‒ я бот таск-трекера Искры.
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
        uid = str(message.chat.id)
        if uid not in self.scenery_bot.user_db:
            self.scenery_bot.add_user(uid)
            self.bot.send_message(
                message.chat.id,
                get_start_msg(message))
            self.scenery_bot.user_db[uid].state = self.scenery_bot.scenery_states["init1"]
            self.scenery_bot.process_user_message(Message(uid,"nothing"))
        else:
            self.bot.send_message(
                message.chat.id,
                f"""{message.chat.first_name}, на тебя дело уже заведено.
Отправь мне "!справка", если не помнишь как со мной работать.""")


    def _not_a_command(self):   # This method not considered a command
        print('???')


class MessageListener(Listener):  # Event listener must inherit Listener
    def __init__(self, bot, scenery_bot):
        self.bot = bot
        self.scenery_bot = scenery_bot
        self.scenery_bot.set_reply_function(self.__reply_user)
        self.m_count = 0

    def __reply_user(self, message):
        self.bot.send_message(int(message.user_id), message.content)

    def on_message(self, message):   # called on every message
        self.m_count += 1
        print(f'Total messages: {self.m_count}')

        user_id = str(message.chat.id)
        if (user_id not in self.scenery_bot.user_db) and not(message.text.startswith("/start")):
            self.bot.send_message (
            message.chat.id,
            "Без /start я работать не буду!")
            return
        elif message.text.startswith("/"):
            pass
        else:
            self.scenery_bot.process_user_message(Message(
                user_id,
                message.text
                ))


    def on_command_failure(self, message, err=None):  # When command fails
        if err is None:
            self.bot.send_message(message.chat.id,
                                  'Э-э-эм... не поняла')
        else:
            self.bot.send_message(message.chat.id,
                                  f"В команде есть ошибка:\n{err}")
        raise err


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



def handler(signum, frame):
    global scbot
    scbot.shutdown()
    raise KeyboardInterrupt
signal.signal(signal.SIGINT, handler)



bot.start()   # start bot's threads
scbot.start()   # start bot's threads
# ~ print(dir(bot))

while True:
    sleep(1)
    # Can also do some useful work i main thread
    # Like autoposting to channels for example
