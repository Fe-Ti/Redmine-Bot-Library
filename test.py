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
                Properties : [Say_anyway, Lexeme_preserving]
        },
        "reset_user":{
            Type    : Say,
            Next    : "start",
            Functions: ["reset_user"],
            Properties : [Lexeme_preserving]
        },
        "start" : {
            Type    : Ask,
            Info    : "start",
            Phrase  : "Введи команду.",
            Next    : {
                        "create"    : ["создай"],
                        # ~ "update"    : ["обнови","измени"],
                        "show"      : ["покажи"],
                        # ~ "delete"    : ["удали"],
                        # ~ "select"    : ["выбери", "в"],
                        "settings"  : ["запомни", "настрой"]
                    },
        },
        "create" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Какой тип объекта ты хочешь создать?""",
            Next    : {
                            "create_project_init_vars":["проект"],
                            "create_issue_init_vars":["задачу"],
                        },
            # ~ Properties : []
        },
        "create_project_init_vars" : {
            Type    : Say,
            Error   : None,
            Info    : None,
            Phrase  : """Инициализирую переменные...""",
            Next    : "create_project_set_identifier",
            Set     :   {
                            Storage  : { Context : Project },
                            Data     : {
                                "name"          : "",
                                "identifier"    : "",
                                "description"   : ""
                            }
                        },
            Properties : [Lexeme_preserving]
        },
        "create_project_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь задать в проекте?""",
            Next    : {
                            "create_project_set_name":["название","имя"],
                            "create_project_set_identifier":["идентификатор", "id"],
                            "create_project_set_description":["описание"],
                            # ~ "create_project_set_parent_nop":["родительский"],
                            "create_call":["готово", ".", "!"]
                        },
        },
        "draft_show_project" : {
            Type    : Say,
            Phrase  : """Черновик проекта""",
            Next    : "create_project_menu",
            Functions: ["show_project_draft"],
            Properties : [Lexeme_preserving]
        },
        "create_project_set_identifier" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'identifier'},
        },
        "create_project_set_name" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи название проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'name'},
        },
        "create_project_set_description" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи описание проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'description'},
        },
        "create_issue_init_vars" : {
            Type    : Ask,
            Info    : "no_help",
            Phrase  : """Инициализирую переменные... """,
            Next    :   {
                        "create_issue_in_project_prep" : ["в"],
                        "create_issue_set_project_id" : ["проект"],
                        "create_issue_set_subject" : ["тема"]
                        },
            Set     :   {
                            Storage  : { Context : Issue },
                            Data     : {
                                "project_id"    : "",
                                "subject"       : "",
                                "description"   : "",
                                "start_date" : "",
                                "due_date" : "",
                                "status" : "",
                                "assigned_to" : None,
                                "tracker" : "",
                                # ~ "" : "",
                            }
                        },
            Properties : [Lexeme_preserving]
        },
        "create_issue_in_project_prep":{
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """В чём?""",
            Next    :   {
                            "create_issue_set_project_id": ["проекте"]
                        },
        },
        "create_issue_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь поменять в задаче?""",
            Next    : {
                            "create_issue_set_project_id" : ["проект"],
                            "create_issue_set_subject":["тему","тема"],
                            "create_issue_set_description":["описание"],
                            "create_issue_set_date":["дату","дата", "срок"],
                            "create_issue_set_assign":["исполнителя","исполнитель"],
                            "create_issue_set_tracker":["трекер"],
                            "create_call":["готово", "."]
                        },
        },
        "draft_show_issue" : {
            Type    : Say,
            Phrase  : """Черновик задачи""",
            Next    : "create_issue_menu",
            Functions: ["show_issue_draft"],
            Properties : [Lexeme_preserving]
        },
        "create_issue_set_date":{
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """В чём?""",
            Next    :   {
                            "create_issue_set_date_start": ["начала"],
                            "create_issue_set_date_due" : ["завершения"]
                        },
            # ~ Properties : []
        },
        "create_issue_set_project_id" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "draft_show_issue",
            Input   : {Data:'project_id'},
        },
        "create_issue_set_subject" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи тему.""",
            Next    : "draft_show_issue",
            Input   : {Data:'subject'},
        },
        "create_issue_set_description" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи описание.""",
            Next    : "draft_show_issue",
            Input   : {Data:'description'},
        },
        "create_issue_set_date_start" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи дату начала. Например, 2023-08-02""",
            Next    : "draft_show_issue",
            Input   : {Data:'start_date'},
        },
        "create_issue_set_date_due" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи срок завершения. Например, 2023-08-02""",
            Next    : "draft_show_issue",
            Input   : {Data:'due_date'},
        },
        "create_issue_set_assign" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи id пользователя, которому хочешь назначить задачу.""",
            Next    : "draft_show_issue",
            Functions:["show_project_memberships"],
            Input   : {Data:'assigned_to'},
        },
        "create_issue_set_tracker" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи трекер.""",
            Next    : "draft_show_issue",
            Functions:["show_issue_trackers"],
            Input   : {Data:'assigned_to'},
        },
        "create_call" : {
            Type     : Say,
            Error    : "Мне не удалось отправить данные.",
            Info     : "start",
            Phrase   : """""",
            Next     : "reset_user",
            Functions: ["create"],
            Properties : [Lexeme_preserving]
        },
        
        "update" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Какой тип объекта ты хочешь создать?""",
            Next    : {
                            "update_project_init_vars":["проект"],
                            "update_issue_init_vars":["задачу"],
                        },
        },
        "update_project_init_vars" : {
            Type    : Get,
            Error   : "data_get_error",
            Phrase  : """Какой проект? Введи идентификатор или номер.""",
            Next    : "update_project_menu",
            Set     :   {
                            Storage  : { Context : Project },
                        },
            Input   : {Parameters: "id"},
            Functions   : ["get_data", ["reset_to_start","""user.variables[Storage][Success]"""]],
            Properties  : [Lexeme_preserving]
        },
        "update_project_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь задать в проекте?""",
            Next    : {
                            "update_project_set_name":["название","имя"],
                            "update_project_set_identifier":["идентификатор", "id"],
                            "update_project_set_description":["описание"],
                            "update_call":["готово", ".", "!"]
                        },
        },
        "draft_show_project" : {
            Type    : Say,
            Next    : "update_project_menu",
            Functions: ["show_project_draft"],
            Properties : [Lexeme_preserving]
        },
        "update_project_set_identifier" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'identifier'},
        },
        "update_project_set_name" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи название проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'name'},
        },
        "update_project_set_description" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи описание проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'description'},
        },
        "update_issue_init_vars" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Инициализирую переменные... """,
            Next    : "update_issue_menu",
            Set     :   {
                            Storage  : { Context : Issue }
                        },
            Input   : {Parameters: "id"},
            Functions   : ["get_data", ["reset_to_start","""user.variables[Storage][Success]"""]],
            Properties : [Lexeme_preserving]
        },
        "update_issue_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь поменять в задаче?""",
            Next    : {
                            "update_issue_set_project_id" : ["проект"],
                            "update_issue_set_subject":["тему","тема"],
                            "update_issue_set_description":["описание"],
                            "update_issue_set_date":["дату","дата", "срок"],
                            "update_issue_set_assign":["исполнителя","исполнитель"],
                            # ~ "update_issue_set_tracker":["трекер"],
                            "update_call":["готово", "."]
                        },
        },
        "update_issue_set_date":{
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """В чём?""",
            Next    :   {
                            "update_issue_set_date_start": ["начала"],
                            "update_issue_set_date_due" : ["завершения"]
                        },
        },
        "update_issue_set_project_id" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "draft_show_issue",
            Input   : {Data:'project_id'},
        },
        "update_issue_set_subject" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи тему.""",
            Next    : "draft_show_issue",
            Input   : {Data:'subject'},
        },
        "update_issue_set_description" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи описание.""",
            Next    : "draft_show_issue",
            Input   : {Data:'description'},
        },
        "update_issue_set_date_start" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи дату начала. Например, 2023-08-02""",
            Next    : "draft_show_issue",
            Input   : {Data:'start_date'},
        },
        "update_issue_set_date_due" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи срок завершения. Например, 2023-08-02""",
            Next    : "draft_show_issue",
            Input   : {Data:'due_date'},
        },
        "update_issue_set_assign" : {
            Type    : Get,
            Info    : "start",
            Phrase  : """Введи id пользователя, которому хочешь назначить задачу.""",
            Next    : "draft_show_issue",
            Functions:["get_project_memberships"],
            Input   : {Data:'assigned_to'},
        },
        "update_call" : {
            Type     : Say,
            Error    : "Мне не удалось отправить данные.",
            Info     : "start",
            Phrase   : """""",
            Next     : "reset_user",
            Functions: ["update"],
            Properties : [Lexeme_preserving]
        },
        "show" : {
            Type    : Ask,
            Phrase  : """Что ты хочешь посмотреть?""",
            Next    : {
                        "show_list":["список"],
                        "show_project_get_id":["проект"],
                        "show_issue_get_id":["задачу"],
                        "show_list_of_projects":["проекты"],
                        "show_list_of_issues":["задачи"],
                        "show_set_me_param":["мои"],
                        }
        },
        "show_set_me_param" : {
            Type    : Ask,
            Phrase  : """Список чего ты хочешь увидеть?""",
            Next    : {
                        "show_list_of_projects":["проекты"],
                        "show_list_of_issues":["задачи"]
            },
            Set     : { Parameters : { "assigned_to_id" : "me" } }
        },
        "show_list" : {
            Type    : Ask,
            Info    : "start",
            Phrase  : """Список чего ты хочешь увидеть?""",
            Next    : {
                        "show_list_of_projects":["проектов"],
                        "show_list_of_issues":["задач"]
            }
        },
        "show_list_of_projects" : {
            Type    : Say,
            Error   : "Мне не удалось получить список проектов",
            Next    : "start",
            Functions: ["get_project_list"],
            Properties : [Lexeme_preserving]
        },
        "show_list_of_issues" : {
            Type     : Say,
            Error    : "Мне не удалось получить список задач",
            Next     : "start",
            Functions: ["get_issue_list"],
            Properties : [Lexeme_preserving]
        },
        "show_project_get_id" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Какой проект ты хочешь посмотреть?""",
            Next    : "show_call",
            Input   : {Parameters:'id'},
            Set     :   {
                            Storage     : { Context : Project },
                            Parameters  : {"include": "trackers"},
                        },
        },
        "show_issue_get_id" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Какую задачу ты хочешь посмотреть?""",
            Next    : "show_call",
            Input   : {Parameters:'id'},
            Set     : { Storage  : { Context : Issue } }
        },
        "show_call" : {
            Type     : Say,
            Error    : "data_get_error",
            Info     : "no_help",
            Phrase   : """""",
            Next     : "reset_user",
            Functions: ["show"],
            Properties : [Lexeme_preserving]
        },
        "settings" : {
            Type    : Ask,
            Info    : "settings",
            Phrase  : "Что ты хочешь настроить? ('ничего' или '.' - выход из режима настройки)",
            Next    :   {
                        "set_key" : ["ключ"],
                        # ~ "set_approve_mode" : ["подтверждение"],
                        # ~ "set_behaviour" : ["поведение"],
                        "start" : ["ничего", "."]
                        }
        },
        "set_key" : {
            Type    : Get,
            Info    : "settings",
            Phrase  : "Введи свой ключ API.",
            Input   : {Settings : Key},
            Next    : "set_key_feedback"
        },
        "set_key_feedback" : {
            Type    : Say,
            Info    : "settings",
            Phrase  : "Я запомнила твой ключ ({Settings[Key]}). Перехожу в режим настройки.",
            Next    : "settings",
            Properties: [Phrase_formatting, Lexeme_preserving, Say_anyway]
        },


    },
    "phrases": {
        Default : "...",
        "set_approve_mode_phrase":"""Подтверждать изменения? (да/нет, сейчас установлено '{Settings[Approve_changes]}')""",
        "setted_approve_mode":"Установила подтверждение изменений: '{Settings[Approve_changes]}'",
    },
    "errors" : {
        Default : "Запрос некорректен, проверь его.",
        "data_get_error" : "Мне не удалось получить данные.",
    },
    "infos" : {
        "no_help" : """По данному разделу справочная информация отсутствует.""",
        Default : """Команды строятся из глагола в повелительном наклонении и объекта над которым необходимо произвести действие.
В ответ на незавершенную команду я выдам наводящую фразу.

Замечу, что все лексемы я разбираю аналогично командной строке, т.е. если записать в кавычках "В чащах юга жил-был цитрус...", то я интерпретирую это не как отдельные слова, а как целую строку.

Если тебе нужна будет справка, то в любой момент ты можешь получить её с помощью слов "!справка" и "!помощь".
Для возврата в начальное состояние - "!отмена". Чтобы сбросить не только состояние, но и настройки, отправь "!сброс".

P.S.
@Fe_Ti просил передать, что я пока не разучилась падать. Поэтому при неполадках со мной обращаться к нему.
""",
        "select"    : """Задание контекста нужно для того, чтобы я понимала в каком объекте я работаю.""",
        "settings"  : """Здесь ты можешь настроить ключ API.
И другие переменные, когда они появятся."""
    },
    "commands" : {
        "info"      : ["!справка", "!помощь"],
        "reset"     : ["!сброс"],
        "cancel"    : ["!отмена"],
        "repeat"    : ["!повтори"]
    },
}

config = {
    "refresh_period"        : 1000, # in seconds
    "sleep_timeout"         : 10,
    "use_https"             : False,
    "redmine_root_url"      : "localhost/redmine",
    "bot_user_key"          : "8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6",
    "user_db_path"          : "./localbase.json",
    "allowed_api_functions" : []# All Functions are allowed if empty list specified
                                # Specify None to disable function calling
                                # ~ "reset_user",
                                # ~ "create",
                                # ~ "show",
                                # ~ "update",
                                # ~ "delete",
                                # ~ "get_project_list",
                                # ~ "get_issue_list",
                                # ~ "show_issue_statuses",
                                # ~ "show_issue_priorities",
                                # ~ "add_watcher",
                                # ~ "delete_watcher",
                                # ~ "show_project_draft",
                                # ~ "show_issue_draft",
                                # ~ "get_project_memberships"
                                # ~ "show_project_draft",
                                # ~ "show_issue_draft"
                                # ~ ]
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
        self.bot.send_message(int(message.user_id), message.content)#, parse_mode="Markdown")

    def on_message(self, message):   # called on every message
        self.m_count += 1
        print(f'Total messages: {self.m_count}')

        user_id = str(message.chat.id)
        if type (message.text) is str:
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

api_realisation = DefaultApiRealisation(templates=DefaultTemplates())
scbot = BotCore(scenery_v2, config, api_realisation=api_realisation)   # Create instance of scenery bot

# Add an event listener
bot.add_listener(MessageListener(bot,scbot))

# Add a command holder
bot.add_commands(BotsCommands(bot, scbot))

# We can add as many command holders
# and event listeners as we like



def handler(signum, frame):
    global scbot, bot
    scbot.shutdown()
    # ~ bot.stop()
    raise KeyboardInterrupt
signal.signal(signal.SIGINT, handler)



bot.start()   # start bot's threads
scbot.start()   # start bot's threads
# ~ print(dir(bot))

while True:
    sleep(1)
    # Can also do some useful work i main thread
    # Like autoposting to channels for example



        # ~ "select" : {
            # ~ Type    : Ask,
            # ~ Error   : "start",
            # ~ Info    : "select",
            # ~ Phrase  : "С каким типом объектов ты хочешь работать? С проектом или задачей?",
            # ~ Next    : {
                # ~ "select_issue"  : ["задачу", "задаче", "задачей"],
                # ~ "select_project": ["проект", "проекте", "проектом"],
                # ~ "select":["с"]
            # ~ }
        # ~ },
        # ~ "select_issue" : {
            # ~ Type    : Get,
            # ~ Error   : "start",
            # ~ Info    : "select",
            # ~ Phrase  : "Введи идентификатор задачи.",
            # ~ Set     : {Storage : {Context:Issue}},
            # ~ Input   : {Data:'id'},
            # ~ Next    : "start"
        # ~ },
        # ~ "select_project" : {
            # ~ Type    : Get,
            # ~ Error   : "start",
            # ~ Info    : "select",
            # ~ Phrase  : "Введи идентификатор проекта.",
            # ~ Set     : {Storage : {Context:Project}},
            # ~ Input   : {Data:'id'},
            # ~ Next    : "start"
        # ~ },
        # ~ "set_behaviour" : {
            # ~ Type    : Ask,
            # ~ Error   : "start",
            # ~ Info    : "settings",
            # ~ Phrase  : "Поведение чего ты хочешь настроить?",
            # ~ Next    :   {
                        # ~ "set_approve_mode"   : ["подтверждения"],
                        # ~ "set_reset_if_error" : ["сброса"]
                        # ~ }
        # ~ },
        # ~ "set_approve_mode"   : {
            # ~ Type    : Ask,
            # ~ Error   : "start",
            # ~ Info    : "settings",
            # ~ Phrase  : "set_approve_mode_phrase",
            # ~ Next    :   {
                        # ~ "set_approve_mode_true" : ["да"],
                        # ~ "set_approve_mode_false": ["нет"]
                        # ~ },
            # ~ Properties:[Phrase_formatting]
        # ~ },
        # ~ "set_approve_mode_true" : {
            # ~ Type    : Say,
            # ~ Error   : "start",
            # ~ Info    : "Ошибка",
            # ~ Phrase  : "setted_approve_mode",
            # ~ Set     : {Settings : {Approve_changes:True}},
            # ~ Next    : "settings",
            # ~ Properties: [Phrase_formatting, Lexeme_preserving, Say_anyway]
        # ~ },
        # ~ "set_approve_mode_false": {
            # ~ Type    : Say,
            # ~ Error   : "start",
            # ~ Info    : "Ошибка",
            # ~ Phrase  : "setted_approve_mode",
            # ~ Set     : {Settings : {Approve_changes:False}},
            # ~ Next    : "settings",
            # ~ Properties: [Phrase_formatting, Lexeme_preserving, Say_anyway]
        # ~ },
        # ~ "set_reset_if_error" : {
            # ~ Type    : Say,
            # ~ Error   : "start",
            # ~ Info    : "Ошибка 404",
            # ~ Phrase  : """rrr""",
            # ~ Next    : "settings",
        # ~ }
