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
# - Run test scenery without api calls
# - Run test scenery with functions
# - Write 'prod' scenery
# - Run 'prod' scenery

# Then think about next goals

import shlex
import time

from threading import Thread, Lock, current_thread
from dataclasses import dataclass

from ServerControlUnit import *

# Contexts
GLOBAL_CXT = "global"
PROJECT_CXT = "project"
ISSUE_CXT = "issue"

DEFAULT_CXT = GLOBAL_CXT

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
say = 0 # Just say and go further
get = 1 # Get the value of something
ask = 2 # Ask and choose next

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
        if Input in params_dict:
            self.var_to_input = params_dict[Input]
        self.next = dict()

    def add_next(self, next_node, lexemes):
        for lexeme in lexemes:
            self.next[lexeme] = next_node

    def get_next(self, lexeme):
        return self.next[lexeme]

class SceneryNode_Ask(SceneryNode):
    pass

class SceneryNode_Say(SceneryNode):
    def add_next(self, next_node, lexemes = None):
        self.next = next_node
    def get_next(self, lexeme = None):
        return self.next
class SceneryNode_Get(SceneryNode_Say):
    pass

        
class SceneryGraph:
    def __init__(self, nodes : dict):
        self.nodes = dict()
        for node_name in nodes:
            if node_name not in self.nodes:
                self.__create_Node(node_name, nodes[node_name])
            # Get next nodes
            next_nodes = nodes[node_name][Next]
            if not(type(next_nodes) is dict):
                next_nodes = { next_nodes : None }
            # Iterate adding next nodes
            for next_node, lexemes in next_nodes.items():
                if next_node not in self.nodes: # Check existance
                    self.__create_Node(next_node, nodes[next_node])
                node = self[node_name]
                node.add_next(self[next_node], lexemes)
                
    def __create_node(self, node_name, params):
        ntype = params[Type]
        if ntype == ask:
            self[node_name] = SceneryNode_Ask(params)
        elif ntype == get:
            self[node_name] = SceneryNode_Get(params)
        elif ntype == say:
            self[node_name] = SceneryNode_Say(params)
        else:
            raise TypeError(f"Can't use type {ntype} for node.")

    def __getitem__(self, key):
        return self.nodes[key]

@dataclass
class User:
    key : str = None
    reset_if_error : bool = True # reset state when error occurs
    approve_changes : bool = True # ask user for approving 
    
    context : str = GLOBAL_CXT # current context, i.e. global, certain project (issue)
    context_obj_id : int = None # object ID of current context (i.e. project or issue i)
    state = None # A reference to actual state
    
    is_busy : bool = True # some sort of a lock

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
        self.scenery_states = SceneryGraph(bot_scenery["states"])
        self.scenery_errors = bot_scenery["errors"]
        self.scenery_infos = bot_scenery["infos"]
        self.scenery_commands = bot_scenery["commands"]
        self.scenery_start_state = bot_scenery["start_state"]

        # From config:
        self.scu = ServerControlUnit(   server_root=bot_config["redmine_root_url"],
                                        use_https=bot_config["use_https"])
        self.bot_user_key = bot_config["bot_user_key"]
        self.refresh_period = bot_config["refresh_period"]
        self.sleep_timeout = bot_config["sleep_timeout"]
        self.reply_function = bot_config["reply_function"]

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

    def _reset_user(self, user):
        user.context = DEFAULT_CXT
        user.state = self.scenery_states[self.scenery_start_state]
        user.context_obj_id = None
    
    def _set_user_lock(self, user, is_locked):
        self.user_db_lock.aquire()
        try:
            user.is_busy = is_locked
        finally:
            self.user_db_lock.release()

    def _process_user_message(self, message : Message):
        ## TODO: programmatically define via scenery 
        
        # Initial checks and other stuff
        content_array = shlex.split(message.content)
        if not content_array:
            return
        user = self.user_db[message.user_id]
        if content_array[0] in self.scenery_commands["reset"]:
            self._reset_user(user)
            return
        if content_array[0] in self.scenery_commands["info"]:
            self.reply_function(Message(message.user_id, user.state.info))
            return
        # Check and lock the user (locking may not work properly)
        if user.is_busy:
            return # Just forget about spammers :)
        self._set_user_lock(user=user, is_locked=True)
        
        # Here parsing magic happens
        
        reply = Message(user_id, "Reply!!!")
        
        # Reply and unlock user for further conversation
        self.reply_function(reply)
        self._set_user_lock(user=user, is_locked=False)

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
            self.user_db[user_id] = User
        else:
            raise ValueError(f"User with id={user_id} already exists.")

    def _safe_update_enums(self, new_statuses, new_priorities):
        self.enum_lock.aquire()
        try:
            self.issue_statuses = new_statuses
            self.issue_priorities = new_priorities
        finally:
            self.enum_lock.release()

    def update_enumerations_cycle(self):
        while self.is_running:
            time.sleep(self.refresh_period)
            if (time.time() - self.last_msg_timestamp) < self.sleep_timeout():
                new_statuses = self.scu.get_issue_statuses(self.bot_user_key)
                new_priorities = self.scu.get_issue_priorities(self.bot_user_key)
                self._safe_update_enums(new_statuses, new_priorities)
            else:
                while (time.time() - self.last_msg_timestamp) > self.sleep_timeout():
                    time.sleep(0.1)
        
    def _save_db(self):
        pass
        
    def start(self):
        if not self.reply_function:
            raise RuntimeError("Reply function is not set")
        if not self.is_running:
            self.last_msg_timestamp = time.time()
            self.is_running = True
            self.enum_updater = Thread(target=update_enumerations_cycle, daemon=False)
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
