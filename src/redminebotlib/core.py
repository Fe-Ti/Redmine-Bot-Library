# (Yet another) Redmine Bot Library
# Copyright 2023 Fe-Ti aka T.Kravchenko

import json
import logging
import shlex
import time

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)
    
from pathlib import Path
from threading import Thread, Lock, current_thread
from dataclasses import dataclass, asdict

from .server_control_unit import RedmineServerControlUnit #, GreenboardServerControlUnit
from .constants import *
from .data_structs import User, Message
from .default_scenery_api_realisation import DefaultSceneryApiRealisation, DefaultApiRealisationTemplates

ServerControlUnit = RedmineServerControlUnit # TODO: implement different task server 

@dataclass
class PropertyStruct:
    format_phrase   : bool = False # use formatting
    preserve_lexeme : bool = False # don't change lexeme when going to next
    say_anyway      : bool = False # ignore muting
    check_input     : bool = False # check input against hint
    dynamic_hint    : bool = False # generate hint by some function
    alter_next      : bool = False # only for Get

class SceneryNode:
    def __init__(self, name, params_dict, api_realisation):
        self.name = name
        self.type = params_dict[Type]
        self.phrase = params_dict[Phrase]
        self.error = params_dict[Error]
        self.info = params_dict[Info]
        self.api_realisation = api_realisation

        self.next = dict()
        self.alter_next = dict() # Should be used in Get... but maybe we will 
        self.alter_hint = list() # have fun with undefined behaviour :)

        self.vars_to_set = None
        if Set in params_dict:
            self.vars_to_set = params_dict[Set]
        self.var_to_input = None
        if (Input in params_dict) or (self.type == Get):
            self.var_to_input = params_dict[Input]
        self.function_list = list()
        if Functions in params_dict:
            self.function_list = params_dict[Functions][:]

        self.properties = PropertyStruct()
        if Properties in params_dict:
            if Phrase_formatting in params_dict[Properties]:
                self.properties.format_phrase = True
            if Lexeme_preserving in params_dict[Properties]:
                self.properties.preserve_lexeme = True
            if Input_checking in params_dict[Properties]:
                self.properties.check_input = True
            if Say_anyway in params_dict[Properties]:
                self.properties.say_anyway = True
            if Dynamic_hint in params_dict[Properties] and Hint in params_dict:
                self.properties.dynamic_hint = True
            if Alter_next in params_dict[Properties] and Hint in params_dict:
                self.properties.alter_next = True
        if self.properties.dynamic_hint: 
            self._next_lexemes_hint : str = params_dict[Hint]
                                    # params_dict[Hint] is callable api function
                                    # i.e. it is dynamic
        else:
            self._next_lexemes_hint : list = list() # hint is just a list (default)
                                                    # i.e. it is set only once per reload
            if Hint in params_dict:
                if type(params_dict[Hint]) is list: # as we need lists, then
                    self._next_lexemes_hint = params_dict[Hint]
                else:
                    logger.warning(f"Found static hint: {params_dict[Hint]}. But it is not list.")

    def __repr__(self):
        return f"[{self.name}]"

    def input_var(self, variables_dict : dict, user_input):
        if user_input in self.alter_hint:
            return
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
                for name, value in self.vars_to_set[category].items():
                    variables_dict[category][name] = value

    def add_next(self, next_node, lexemes):
        """
        Adds next node which corresponds to lexemes
        """
        for lexeme in lexemes:
            lexeme = lexeme.lower()
            self.next[lexeme] = next_node

    def get_next(self, lexeme):
        """
        Returns node depending on lexeme
        """
        return self.next[lexeme.lower()]

    def get_hint(self, user) -> list:
        """
        Returns list of possible next lexemes, e.g. [first, second, third]
        """
        if self.properties.dynamic_hint: # note this may be slower if function is accessing remote host
            function = self._next_lexemes_hint
            if self.properties.alter_next:
                return getattr(self.api_realisation, function)(user)+self.alter_hint
            return getattr(self.api_realisation, function)(user)
        if not self._next_lexemes_hint: # If hint is empty then cache lexeme list
            if type(self.next) is dict: # if it exists.
                lexemes = self.next.keys()
                for lexeme in lexemes:
                    self._next_lexemes_hint.append(lexeme)
    #            self._next_lexemes_hint = self._next_lexemes_hint[:-1]
        return self._next_lexemes_hint # else produce whatever set in scenery 

    def is_valid_next(self, lexeme, user = None):
        if lexeme.lower() in self.next:
            return True
        else:
            return False

    def get_phrase(self, user):
        """
        Format and/or just return string.
        """
        if self.properties.format_phrase:
            return self.phrase.format(**user.variables)
        else:
            return self.phrase

    def get_error(self, lexeme):
        return self.error + f"\n -> {lexeme}"

    def preserve_lexeme(self):
        return self.properties.preserve_lexeme

    def say_anyway(self):
        return self.properties.say_anyway

class SceneryNode_Ask(SceneryNode):
    pass

class SceneryNode_Say(SceneryNode):
    def add_next(self, next_node, lexemes = None):
        self.next = next_node

    def get_next(self, lexeme = None):
        return self.next

    def is_valid_next(self, lexeme, user):
        return True

class SceneryNode_Get(SceneryNode):
    def add_next(self, next_node, lexemes = None):
        if not lexemes:
            self.next = next_node
        elif self.properties.alter_next:
            for lexeme in lexemes:
                lexeme = lexeme.lower()
                self.alter_next[lexeme] = next_node
            self.alter_hint = list(self.alter_next.keys())
        else:
            raise ValueError("Recieved not None without Alter_next property in node.")

    def get_next(self, lexeme):
        lexeme = lexeme.lower()
        if self.properties.alter_next:
            if lexeme in self.alter_next:
                return self.alter_next[lexeme]
        return self.next
    
    def is_valid_next(self, lexeme, user):
        if self.properties.alter_next and lexeme in self.alter_hint:
            return True
        if self.properties.check_input:
            return (lexeme in self.get_hint())
        return True

class SceneryGraph:
    def __init__(self, nodes : dict, phrases, errors, infos, root_node_name, api_realisation):
        self.node_count : int = 0
        self.nodes = dict()
        defaults = dict()

        if Default in phrases:
            defaults[Phrase] = phrases[Default]
        else:
            raise ValueError("No default phrase in scenery.")
        if Default in errors:
            defaults[Error] = errors[Default]
        else:
            raise ValueError("No default error in scenery.")
        if Default in infos:
            defaults[Info] = infos[Default]
        else:
            raise ValueError("No default info in scenery.")

        for node_name, node_params in nodes.items():
            if node_name not in self.nodes:
                self._create_node(node_name, node_params, phrases, errors, infos, defaults, api_realisation)
            # Get next nodes
            next_nodes = node_params[Next]
            if not(type(next_nodes) is dict):
                next_nodes = { next_nodes : None }
            if Alter_next in node_params:
                for node,lexemes in node_params[Alter_next].items():
                    next_nodes[node] = lexemes
            # Iterate adding next nodes
            for next_node, lexemes in next_nodes.items():
                if next_node not in self.nodes: # Check existance
                    self._create_node(next_node, nodes[next_node], phrases, errors, infos, defaults, api_realisation)
                node = self[node_name]
                node.add_next(self[next_node], lexemes)

    def _create_node(self, node_name, params, phrases, errors, infos, defaults, api_realisation):
        self.node_count += 1
        if Phrase not in params:
            params[Phrase] = defaults[Phrase]
        if Error not in params:
            params[Error] = defaults[Error]
        if Info not in params:
            params[Info] = defaults[Info]

        if params[Phrase] in phrases:
            params[Phrase] = phrases[params[Phrase]]
        if params[Error] in errors:
            params[Error] = errors[params[Error]]
        if params[Info] in infos:
            params[Info] = infos[params[Info]]
        ntype = params[Type]
        if ntype == Ask:
            self[node_name] = SceneryNode_Ask(node_name, params, api_realisation)
        elif ntype == Get:
            self[node_name] = SceneryNode_Get(node_name, params, api_realisation)
        elif ntype == Say:
            self[node_name] = SceneryNode_Say(node_name, params, api_realisation)
        else:
            raise TypeError(f"Can't use type {ntype} for node.")

    def __getitem__(self, key):
        return self.nodes[key]

    def __setitem__(self, key, value):
        self.nodes[key] = value


class RedmineBot:
    def __init__(self,
                    bot_scenery : dict,
                    bot_config  : dict,
                    bot_user_key: str,
                    reply_function = None,
                    udb_loading_function = None,
                    udb_saving_function = None,
                    api_realisation = DefaultSceneryApiRealisation(),
                    no_split_on_get = True # don't split when user is on Get node
                    ):
        """
        Parameters:
            bot_scenery : dict  -   scenery graph as dictionary,
            bot_config  : dict  -   bot configuration,
            bot_user_key: str   -   key to be used for fetching enumerations and other
                                    non-confidential data,
            reply_function = None       -   function for replying,
            udb_loading_function = None -   function for loading user DB (optional),
            udb_saving_function = None  -   function for saving user DB (optional),
            api_realisation = DefaultSceneryApiRealisation()    - API realisation used by scenery,
            no_split_on_get = True      -   if set True don't split new input when user is on Get node type.
        """
        self.bot_user_key = bot_user_key
        self.no_split_on_get = no_split_on_get
        # From config:
        self.scu = ServerControlUnit(   server_root=bot_config["redmine_root_url"],
                                        use_https=bot_config["use_https"])
        self.reload(config=bot_config,
                    scenery=bot_scenery,
                    api_realisation=api_realisation)
                    
        self.reply_function = reply_function
        logger.info(f"Reply function set to {self.reply_function}.")
        
        if udb_saving_function:
            if udb_loading_function:
                self._udb_saving_function = udb_saving_function
                self._udb_loading_function = udb_loading_function
            else:
                raise ValueError("You must specify udb_loading_function if you set udb_saving_function.")
        else:
            if udb_loading_function:
                raise ValueError("You must specify udb_saving_function if you set udb_loading_function.")
            else:
                self._udb_saving_function = self._default_udb_saving_function
                self._udb_loading_function = self._default_udb_loading_function
                logger.info("Using default JSON for storing user DB.")

        # Init enumumerations
        self.issue_statuses = list()    # self.scu.get_issue_statuses(self.bot_user_key)
        self.issue_trackers = list()    # self.scu.get_issue_trackers(self.bot_user_key)
        self.issue_priorities = list()  # self.scu.get_issue_priorities(self.bot_user_key)

        self.user_db : dict[str, User] = dict()
        self._udb_loading_function() #load_user_db() # TODO: improve security of database
        logger.info("Loaded user database.")

        # Initializing multithreading stuff
        self.enum_lock = Lock()
        self.user_db_lock = Lock()
        self.last_msg_timestamp = 0
        self.last_notify_timestamp = 0
        self.is_running = False
        self.enum_updater = None
        self.notifier = None
        logger.info("MT stuff init finished.")

    def _set_user_lock(self, user, lock_state : bool):
        self.user_db_lock.acquire()
        try:
            if lock_state and user.is_busy:
                raise ValueError(f"User {user.uid} lock is already acquired by another thread.")
            user.is_busy = lock_state
        except ValueError as error:
            logger.error(Error)
        finally:
            self.user_db_lock.release()

    def _process_user_message(self, message : Message):
        # Initial checks and other stuff
        user = self.user_db[message.user_id]
        content_array = list()
        if user.state.type == Get and self.no_split_on_get:
            content_array = [message.content]
        else:
            content_array = shlex.split(message.content)
        logger.info(str(content_array))
        if not content_array:
            logger.info("Empty content array.")
            return
        if content_array[0] in self.scenery_commands[Reset]:
            logger.info(f"Fully resetting user {user.uid}")
            self.reset_user(user, keep_settings=False)
            self.reply_function(self._get_prompt_message(user))
            return
        elif content_array[0] in self.scenery_commands[Cancel]:
            logger.info(f"Resetting state and variables of user {user.uid}")
            self.reset_user(user, keep_settings=True)
            self.reply_function(self._get_prompt_message(user))
            return
        elif content_array[0] in self.scenery_commands[Info]:
            self.reply_function(Message(user.uid, user.state.info))
            self.reply_function(self._get_prompt_message(user))
            return
        elif content_array[0] in self.scenery_commands[Repeat]:
            self.reply_function(self._get_prompt_message(user))
            return
        # Check and lock the user (locking may not work properly)
        if user.is_busy:
            logger.info(f"User {user.uid} is busy")
            return # Just forget about spammers :)
        logger.info(f"User {user.uid} is locked")
        self._set_user_lock(user=user, lock_state=True)
        try:
            # Here parsing magic happens
            for lex in content_array:
                if not user.is_busy:
                    self.reset_user(user, keep_settings=True)
                    break
                # ~ print(user.state, lex)
                if user.state.is_valid_next(lex, user):
                    self._run_state(user, lex)
                    user.state = user.state.get_next(lex)
                    reply = self._get_prompt_message(user)
                    logger.info(f"Changed state to {user.state}")
                    if user.state.say_anyway() and not user.state.preserve_lexeme():
                        self.reply_function(reply)
                    while user.state.preserve_lexeme(): # Jumping through states which preserve lexeme
                        if user.state.is_valid_next(lex, user):
                            self._run_state(user, lex)
                            if user.state.say_anyway():
                                self.reply_function(reply)
                            user.state = user.state.get_next(lex)
                            reply = self._get_prompt_message(user)
                            logger.info(f"Changed state to {user.state}")
                        else:
                            break
                else:
                    reply = Message(user.uid, user.state.get_error(lex))
                    break
            logger.info(f"Reply ready for {user.uid}")
            # Reply and unlock user for further conversation
            if not user.state.say_anyway(): # Just for eliminating doubles (for Say_enyway states)
                self.reply_function(reply)
            logger.info(f"Replied {user.uid}")
            self._set_user_lock(user=user, lock_state=False)
            logger.info(f"User {user.uid} is free")
        except Exception as error:
            logger.error(error)
            self._set_user_lock(user=user, lock_state=False)
            raise error

    def _get_prompt_message(self, user):
        # ~ if user.state.type == Ask and user.variables[Settings][Show_hints]:
        return Message( user.uid,
                    user.state.get_phrase(user),
                    hint=user.state.get_hint(user)
                        )
        # ~ else:
            # ~ return Message( user.uid,
                        # ~ user.state.get_phrase(user)
                        # ~ )

    def _run_state(self, user, lex=None):
        logger.info(f"Current state is {user.state}")
        user.state.set_vars(user.variables)
        if lex:
            user.state.input_var(user.variables, lex)
        self._call_functions(user)

    def _call_functions(self, user):
        if self.allowed_api_functions == None:
            logger.warning("None functions are allowed.")
            return
        state = user.state
        # ~ self.log_to_user(user, f"Start calling functions in state {state}")
        logger.info(f"Start calling functions in state {state}")
        # ~ print(user.variables)
        is_allowed = True
        for function in state.function_list:
            # ~ self.log_to_user(user, f"Function is {function}")
            logger.info(f"Function is {function}")
            if type(function) is list:
                is_allowed = (function[0] in self.allowed_api_functions) or (self.allowed_api_functions == list())
                if is_allowed and (eval(function[1])):
                    # Note: the code above is sort of insecure, but scenery
                    # is owned by bot owner so if he want's to steal keys
                    # he can just edit the code and get the dictionary
                    getattr(self.api_realisation, function[0])(user)
            elif type(function) is str:
                # ~ print(function)
                is_allowed = (function in self.allowed_api_functions) or (self.allowed_api_functions == list())
                if is_allowed:
                    getattr(self.api_realisation, function)(user)
            if not is_allowed:
                logger.warning(f"{function} is invalid! Check your scenery.")

    def reset_user(self, user, keep_settings=True, reset_state=True):
        u_settings = {
                        Notify              : True,
                        Show_hints          : True,
                        Key                 : None,
                    }
        if keep_settings and user.variables:
            u_settings = user.variables[Settings]
        user.variables =    {
                            Settings : u_settings,
                            Data : dict(),
                            Parameters : dict(),
                            Storage: {Context : Global} ## A storage for API realisation variables
                                                        ## Just for not to interfere with Data and Parameters
                            }
        if reset_state:
            user.state = self.scenery_states[self.scenery_start_state]
            self._set_user_lock(user=user, lock_state=False)

    def process_user_message(self, message : Message):
        if self.is_running:
            p_thread = Thread(  target=self._process_user_message,
                                args=(message,),
                                daemon=True)
            self.last_msg_timestamp = time.time()
            p_thread.start()
        else:
            raise RuntimeError("Bot is not running.")

    def add_user(self, user_id : str):
        if user_id not in self.user_db:
            new_user = User()
            new_user.uid = str(user_id)
            self.reset_user(new_user)
            self.user_db[str(user_id)] = new_user # stringify id for stupid devs
        else:
            raise ValueError(f"User with id={user_id} already exists.")

    def _safe_update_enums(self, new_statuses, new_priorities, new_trackers):
        self.enum_lock.acquire()
        try:
            self.issue_statuses = new_statuses
            self.issue_priorities = new_priorities
            self.issue_trackers = new_trackers
        finally:
            self.enum_lock.release()

    def update_enumerations_cycle(self):
        updated_at = 0
        while self.is_running:
            # ~ print("Running...")
            while (time.time() - updated_at) < self.refresh_period:
                time.sleep(1)
                if not self.is_running:
                    return
            if (time.time() - self.last_msg_timestamp) < self.sleep_timeout:
                new_statuses = self.scu.get_issue_statuses(self.bot_user_key)
                new_priorities = self.scu.get_issue_priorities(self.bot_user_key)
                new_trackers = self.scu.get_issue_trackers(self.bot_user_key)
                # ~ print(new_statuses, new_priorities, new_trackers)
                self._safe_update_enums(new_statuses, new_priorities, new_trackers)
                updated_at = time.time()
            else:
                while (time.time() - self.last_msg_timestamp) > self.sleep_timeout:
                    time.sleep(5)

    def notificating_routine(self):
        for uid,user in self.user_db.items():
            if user.variables[Settings][Notify]:
                self.api_realisation._notify(user)
        self.last_notify_timestamp = time.time()

    def notificating_cycle(self):
        if not self.notify_schedule:
            logger.warning("Switched to external notification trigger.")
            return
        logger.warning("Using internal notification trigger.")
        while self.is_running:
            # ~ print("ncycle begin")
            while time.strftime("%H:%M") not in self.notify_schedule:
                for i in range(5):
                    # ~ print(f"ncycle wait {i}, {self.is_running}")
                    time.sleep(10)
                    if not self.is_running:
                        return
            self.notificating_routine()
            self.last_notify_timestamp = time.time()
            while time.strftime("%H:%M") in self.notify_schedule:
                # ~ print(f"Wait after notify, {self.is_running}")
                time.sleep(10)
                if not self.is_running:
                    return

    def start(self):
        if not self.reply_function:
            raise RuntimeError("Reply function is not set")
        if not self.is_running:
            self.last_msg_timestamp = time.time()
            self.is_running = True
            self.enum_updater = Thread(target=self.update_enumerations_cycle, daemon=False)
            self.enum_updater.start()
            self.notifier = Thread(target=self.notificating_cycle, daemon=False)
            self.notifier.start()
        else:
            raise RuntimeError("Bot is already running.")

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.last_msg_timestamp = time.time()
            self.enum_updater.join()
            self.notifier.join()
        else:
            raise RuntimeError("Bot has already been stopped.")

    def set_reply_function(self, new_reply_func):
        self.reply_function = new_reply_func
        
    def reload(self, config, scenery, api_realisation):
        self.scu.server_root = config["redmine_root_url"]
        self.scu.use_https = config["use_https"]
        self.refresh_period = config["refresh_period"]
        self.notify_schedule = None
        if "notify_schedule" in config:
            self.notify_schedule = config["notify_schedule"]
        self.sleep_timeout = config["sleep_timeout"]
        self.user_db_path = Path(config["user_db_path"])
        self.allowed_api_functions = config["allowed_api_functions"][:]
        logger.info("Config and SCU init finished.")
        # From scenery:
        self.scenery_phrases = scenery[Phrases].copy()
        self.scenery_errors = scenery[Errors].copy()
        self.scenery_infos = scenery[Infos].copy()
        self.scenery_commands = scenery[Commands].copy()
        self.scenery_start_state = scenery[Start_state]
        self.scenery_states = SceneryGraph(scenery[States].copy(),
                                            self.scenery_phrases,
                                            self.scenery_errors,
                                            self.scenery_infos,
                                            self.scenery_start_state,
                                            api_realisation)
        self.hint_template = scenery[Hint_template]
        logger.info(f"Scenery init finished. {self.scenery_states.node_count} nodes have been loaded.")

        # From config:
        self.api_realisation = api_realisation
        logger.info("API realisation is set.")
        self.api_realisation._change_bot(self)
        logger.info("API realisation references current bot.")

    def restart(self):
        self.stop()
        self.start()

    def save(self):
        if self.is_running:
            self.stop()
            restart = True
        else:
            restart = False
        self._udb_saving_function()
        if restart:
            self.start()

    def dump_user_db(self):
        """
        Dump user_db into serializable dictionary. Can be used for customizing
        save/load process.
        
        Returns dictionary which corresponds to user data and state.
        """
        plain_udb = dict()
        for uid, user in self.user_db.items():
            plain_udb[uid] = asdict(user)
            plain_udb[uid]["state"] = user.state.name
        return plain_udb

    def load_user_db(self, raw_data):
        """
        Load data from dictionary (`raw_data`) into RedmineBot instance user_db.
        If you want to customize user DB save/load then use this function for
        loading from dictionary, which was produced by dump_user_db() function.
        """
        for uid, udata in raw_data.items():
            state_name = udata.pop("state")
            self.user_db[uid] = User(**udata)
            self.user_db[uid].state = self.scenery_states[state_name]

    def _default_udb_saving_function(self):
        """
        By default save user DB into JSON... I know, not very secure :)
        """
        plain_udb = self.dump_user_db()
        with open(self.user_db_path, 'w') as udb_file:
            udb_file.write(json.dumps(plain_udb))
    
    def _default_udb_loading_function(self):
        """
        By default load user DB from JSON.
        """
        try:
            with open(self.user_db_path, 'r') as udb_file:
                raw_data = json.loads(udb_file.read())
                self.load_user_db(raw_data)
        except OSError:
            pass
