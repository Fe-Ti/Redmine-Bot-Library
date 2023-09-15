# Copyright 2023 Fe-Ti aka T.Kravchenko

from .constants import *
from .data_structs import User, Message

def get_string_from_enum_list(enum_list, template_list_entry):
    string = str()
    for entry in enum_list:
        string += template_list_entry.format_map(entry)
    return string


def get_empty_scenery():
    return {
            Start_state   : "",
            Hint_template : "\n\n>>{}",
            States   :{
            },
            Phrases : {
                Default : "",
                Notification : "",
            },
            Errors  : {
                Default : "",
                Notification : "",
            },
            Infos   : {
                Default : "",
                },
            Commands : {
                Info      : [],
                Reset     : [],
                Cancel    : [],
                Repeat    : []
            },
        }

class DefaultApiRealisationTemplates:
    pass

class DefaultSceneryApiRealisation:
    def __init__(self, bot = None, templates = DefaultApiRealisationTemplates()):
        self.bot = bot
        self.templates = templates

    def _change_bot(self, bot):
        self.bot = bot

    def _report_failure(self, user):
        self.bot.reply_function(Message(user.uid, user.state.error))
        # ~ user.state = self.bot.scenery_states[self.bot.scenery_start_state]

    def _clear_nulls(self, dictionary, clear_zeros=False):
        keys = list(dictionary.keys())[:]
        for k in keys:
            if not dictionary[k]:
                if (type(dictionary[k]) is int) and not clear_zeros:
                    continue
                else:
                    del dictionary[k]

    def _notify(self, user):
        pass
