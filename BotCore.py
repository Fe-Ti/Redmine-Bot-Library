# (Yet another) Redmine Bot Library

# Goals for the first version:
# - use Redmine JSON REST API (maybe in future supoort XML)
# - provide a simple bot logic which will be able to:
#     - create/delete:
#         - projects
#         - issues
#     - assign issues to user
#     - add watchers to issues
#     - get:
#       - project list
#       - issues:
#           - by number
#           - listed in project (with filtering);
#           - assigned to user
#           - which are watched by user

# Goals for early Alpha:
# +- Run test scenery without api calls
# - Run test scenery with functions
# - Write 'prod' scenery
# - Run 'prod' scenery

# Then think about next goals

import shlex
import time

from threading import Thread, Lock, current_thread
from dataclasses import dataclass

from ServerControlUnit import *

# Keywords of states
Type = "Type"
Error = "Error"
Info = "Info" # help message
Phrase = "Phrase" # short help. sort of  tl:dr
Next = "Next"
Set = "Set" # Set variables {"name" : value}
Input = "Input"
#Function = "Function" # function to run


# Types
Say = 0 # Just say and go further
Get = 1 # Get the value of something
Ask = 2 # Ask and choose next

#
Context = "context" # Context, e.g. project, issue... used as type of object
Data = "data" # JSON data
Parameters = "parameters" # HTTP params

# Contexts
Issue = "issue"
Project = "project"

class SceneryNode:
    def __init__(self, params_dict):
        self.type = params_dict[Type] #????
        self.phrase = params_dict[Phrase]
        self.error = params_dict[Error]
        self.info = params_dict[Info]
        self.vars_to_set = None
        if Set in params_dict:
            self.vars_to_set = params_dict[Set]
        self.var_to_input = None
        if (Input in params_dict) or (self.type == Get):
            self.var_to_input = params_dict[Input]
        self.next = dict()

    def input_var(self, variables_dict : dict, user_input):
        if not self.var_to_input:
            return
        for category in self.var_to_input.keys():
            name = self.var_to_input[category]
            if category in variables_dict:
                variables_dict[category][name] = user_input

    def set_vars(self, variables_dict : dict):
        if not self.vars_to_set:
            return
        for category in self.vars_to_set:
            if category in variables_dict:
                if category == Context:
                    variables_dict[category] = self.vars_to_set[category]
                else:
                    for name, value in self.vars_to_set[category].items():
                        variables_dict[category][name] = value

    def add_next(self, next_node, lexemes):
        for lexeme in lexemes:
            self.next[lexeme] = next_node

    def get_next(self, lexeme):
        return self.next[lexeme]

    def is_valid_next(self, lexeme):
        if lexeme in self.next:
            return True
        else:
            return False

class SceneryNode_Ask(SceneryNode):
    pass

class SceneryNode_Say(SceneryNode):
    def add_next(self, next_node, lexemes = None):
        self.next = next_node

    def get_next(self, lexeme = None):
        return self.next

    def is_valid_next(self, lexeme):
        return True

class SceneryNode_Get(SceneryNode_Say):
    pass


class SceneryGraph:
    def __init__(self, nodes : dict, errors, infos):
        self.nodes = dict()
        for node_name, node_params in nodes.items():
            if node_name not in self.nodes:
                self._create_node(node_name, node_params, errors, infos)
            # Get next nodes
            next_nodes = node_params[Next]
            if not(type(next_nodes) is dict):
                next_nodes = { next_nodes : None }
            # Iterate adding next nodes
            for next_node, lexemes in next_nodes.items():
                if next_node not in self.nodes: # Check existance
                    self._create_node(next_node, nodes[next_node], errors, infos)
                node = self[node_name]
                node.add_next(self[next_node], lexemes)

    def _create_node(self, node_name, params, errors, infos):
        if params[Error] in errors:
            params[Error] = errors[params[Error]]
        if params[Info] in infos:
            params[Info] = infos[params[Info]]
        ntype = params[Type]
        if ntype == Ask:
            self[node_name] = SceneryNode_Ask(params)
        elif ntype == Get:
            self[node_name] = SceneryNode_Get(params)
        elif ntype == Say:
            self[node_name] = SceneryNode_Say(params)
        else:
            raise TypeError(f"Can't use type {ntype} for node.")

    def __getitem__(self, key):
        return self.nodes[key]

    def __setitem__(self, key, value):
        self.nodes[key] = value

@dataclass
class User:
    uid = None
    key : str = None
    reset_if_error : bool = False # reset state when error occurs
    # ~ approve_changes : bool = True # ask user for approving

    # ~ context_obj_id : int = None # object ID of current context (i.e. project or issue i)
    state = None # A reference to actual state
    variables : dict() = None
    # ~ context : str = GLOBAL_CXT # current context, i.e. global, certain project (issue)
    # ~ data : dict = None
    # ~ parameters : dict = None

    is_busy : bool = False # some sort of a lock

@dataclass
class Message:
    user_id : str
    content : str

class BotCore:
    def __init__(self,
                    bot_scenery : dict,
                    bot_config : dict,
                    reply_function = None):
        """
        bot_user_key    -   is used for fetching enumerations and other
                            non-confidential data.
        """
        # From scenery:
        self.scenery_errors = bot_scenery["errors"].copy()
        self.scenery_infos = bot_scenery["infos"].copy()
        self.scenery_commands = bot_scenery["commands"].copy()
        self.scenery_states = SceneryGraph(bot_scenery["states"].copy(),
                                            self.scenery_errors,
                                            self.scenery_infos)
        self.scenery_start_state = bot_scenery["start_state"]

        # From config:
        self.scu = ServerControlUnit(   server_root=bot_config["redmine_root_url"],
                                        use_https=bot_config["use_https"])
        self.bot_user_key = bot_config["bot_user_key"]
        self.refresh_period = bot_config["refresh_period"]
        self.sleep_timeout = bot_config["sleep_timeout"]

        self.reply_function =reply_function

        # Loading stuff from server or local database
        self.issue_statuses = self.scu.get_issue_statuses(self.bot_user_key)
        self.issue_priorities = self.scu.get_issue_priorities(self.bot_user_key)
        self.user_db : dict[str, User] = dict()
        # TODO: load user db

        # Initializing multithreading stuff
        self.enum_lock = Lock()
        self.user_db_lock = Lock()
        self.last_msg_timestamp = 0
        self.is_running = False
        self.enum_updater = None

    def reset_user(self, user):
        user.variables =    {
                            Context : None,
                            Data : dict(),
                            Parameters : dict()
                            }
        user.state = self.scenery_states[self.scenery_start_state]
        # ~ user.context_obj_id = None

    def _set_user_lock(self, user, is_locked):
        self.user_db_lock.acquire()
        try:
            user.is_busy = is_locked
        finally:
            self.user_db_lock.release()

    def _process_user_message(self, message : Message):
        ## TODO: programmatically define via scenery

        # Initial checks and other stuff
        content_array = shlex.split(message.content)
        logging.warning(str(content_array))
        if not content_array:
            logging.warning("Empty content array")
            return
        user = self.user_db[message.user_id]
        if content_array[0] in self.scenery_commands["reset"]:
            logging.warning(f"Resetting user {user.uid}")
            self.reset_user(user)
            return
        if content_array[0] in self.scenery_commands["info"]:
            self.reply_function(Message(user.uid, user.state.info))
            return
        # Check and lock the user (locking may not work properly)

        if user.is_busy:
            logging.warning(f"User {user.uid} is busy")
            return # Just forget about spammers :)
        self._set_user_lock(user=user, is_locked=True)
        try:
            # Here parsing magic happens
            for lex in content_array:
                if user.state.is_valid_next(lex):
                    user.state.set_vars(user.variables)
                    user.state.input_var(user.variables, lex)
                    self._call_function(user)
                    user.state = user.state.get_next(lex)
                    reply = Message(user.uid, user.state.phrase)
                else:
                    reply = Message(user.uid, user.state.error)
                    break

            logging.warning(f"Reply ready for {user.uid}")
            # Reply and unlock user for further conversation
            self.reply_function(reply)
            logging.warning(f"Replied {user.uid}")
            self._set_user_lock(user=user, is_locked=False)
            logging.warning(f"User {user.uid} is free")
        except Exception as error:
            logging.error(error)
            self._set_user_lock(user=user, is_locked=False)
            raise error

    def _call_function(self, user):
        pass

    def process_user_message(self, message : Message):
        if self.is_running:
            p_thread = Thread(  target=self._process_user_message,
                                args=(message,),
                                daemon=True)
            self.last_msg_timestamp = time.time()
            p_thread.start()
        else:
            raise RuntimeError("Bot is not running.")

    def reply_user(self, message: Message):
        self.reply_function(message.user_id, message.content)

    def add_user(self, user_id):
        if user_id not in self.user_db:
            new_user = User()
            new_user.uid = user_id
            self.reset_user(new_user)
            self.user_db[user_id] = new_user
        else:
            raise ValueError(f"User with id={user_id} already exists.")

    def _safe_update_enums(self, new_statuses, new_priorities):
        self.enum_lock.acquire()
        try:
            self.issue_statuses = new_statuses
            self.issue_priorities = new_priorities
        finally:
            self.enum_lock.release()

    def update_enumerations_cycle(self):
        while self.is_running:
            time.sleep(self.refresh_period)
            if (time.time() - self.last_msg_timestamp) < self.sleep_timeout:
                new_statuses = self.scu.get_issue_statuses(self.bot_user_key)
                new_priorities = self.scu.get_issue_priorities(self.bot_user_key)
                self._safe_update_enums(new_statuses, new_priorities)
            else:
                while (time.time() - self.last_msg_timestamp) > self.sleep_timeout:
                    time.sleep(0.1)

    def start(self):
        if not self.reply_function:
            raise RuntimeError("Reply function is not set")
        if not self.is_running:
            self.last_msg_timestamp = time.time()
            self.is_running = True
            self.enum_updater = Thread(target=self.update_enumerations_cycle, daemon=False)
            self.enum_updater.start()
        else:
            raise RuntimeError("Bot is already running.")

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.last_msg_timestamp = time.time()
            self.enum_updater.join()
        else:
            raise RuntimeError("Bot has already been stopped.")

    def set_reply_function(self, new_reply_func):
        self.reply_function = new_reply_func

    def restart(self):
        stop()
        start()

    def shutdown(self):
        pass

    def _save_db(self):
        pass

