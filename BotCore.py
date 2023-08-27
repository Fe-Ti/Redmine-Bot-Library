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
from dataclasses import dataclass, asdict

from ServerControlUnit import *

# Keywords of states
Type = "Type"
Error = "Error"
Info = "Info" # help message
Phrase = "Phrase" # short help. sort of  tl:dr
Next = "Next"
Set = "Set" # Set variables {"name" : value}
Input = "Input"
Functions = "Functions" # A list of functions to run, e.g.:
                        # Functions: [["create","not user.approve"], reset_user]
                        # The first will run only when expression is true
                        # and if the function is allowed to be called.
                        # Note: the expression is currently evaluated by eval()
                        # Note 2: allowed functions are defined in config

Properties = "Properties"   # Determines how the state is interpreted.
                            # Is an array (list) of strings, e.g.:
                            # Properties: [Lexeme_preserving, Phrase_formatting]
# Property list
Phrase_formatting = "Phrase_formatting" # If present, then phrase is formatted like f"..."
Lexeme_preserving = "Lexeme_preserving" # If present, then lexeme is preserved for the next state

# Types
Say = 0 # Just say and go further
Get = 1 # Get the value of something
Ask = 2 # Ask and choose next

#
Settings = "Settings"
Context = "Context" # Context, e.g. project, issue... used as type of object
Key = "Key"
Show_hints = "Show_hints"
Approve_changes = "Approve_changes"
Reset_if_error = "Reset_if_error"

Data = "Data" # JSON data
Parameters = "Parameters" # HTTP params

# Contexts
Issue = "Issue"
Project = "Project"

@dataclass
class PropertyStruct:
    format_phrase : bool = False
    preserve_lexeme : bool = False

class SceneryNode:
    def __init__(self, name, params_dict):
        self.name = name
        self.type = params_dict[Type]
        self.phrase = params_dict[Phrase]
        self.error = params_dict[Error]
        self.info = params_dict[Info]
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
        self.next : dict = dict()
        self._next_lexemes_hint : str = str() # is used in returning hint

    def __repr__(self):
        return f"[{self.name}]"

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
                for name, value in self.vars_to_set[category].items():
                    variables_dict[category][name] = value

    def add_next(self, next_node, lexemes):
        for lexeme in lexemes:
            lexeme = lexeme.lower()
            self.next[lexeme] = next_node

    def get_next(self, lexeme):
        return self.next[lexeme.lower()]

    def get_hint_string(self) -> str:
        """
        Returns string with list of possible next lexemes, e.g. "first, second, third"
        """
        if not self._next_lexemes_hint:
            for lexeme in self.next.keys():
                self._next_lexemes_hint += f" {lexeme},"
            self._next_lexemes_hint = self._next_lexemes_hint[:-1]
        return self._next_lexemes_hint

    def is_valid_next(self, lexeme):
        if lexeme.lower() in self.next:
            return True
        else:
            return False

    def get_phrase(self, user):
        if self.properties.format_phrase:
            return self.phrase.format(**user.variables)
        else:
            return self.phrase

    def preserve_lexeme(self):
        return self.properties.preserve_lexeme


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
    def __init__(self, nodes : dict, phrases, errors, infos):
        self.nodes = dict()
        for node_name, node_params in nodes.items():
            if node_name not in self.nodes:
                self._create_node(node_name, node_params, phrases, errors, infos)
            # Get next nodes
            next_nodes = node_params[Next]
            if not(type(next_nodes) is dict):
                next_nodes = { next_nodes : None }
            # Iterate adding next nodes
            for next_node, lexemes in next_nodes.items():
                if next_node not in self.nodes: # Check existance
                    self._create_node(next_node, nodes[next_node], phrases, errors, infos)
                node = self[node_name]
                node.add_next(self[next_node], lexemes)

    def _create_node(self, node_name, params, phrases, errors, infos):
        if params[Phrase] in phrases:
            params[Phrase] = phrases[params[Phrase]]
        if params[Error] in errors:
            params[Error] = errors[params[Error]]
        if params[Info] in infos:
            params[Info] = infos[params[Info]]
        ntype = params[Type]
        if ntype == Ask:
            self[node_name] = SceneryNode_Ask(node_name, params)
        elif ntype == Get:
            self[node_name] = SceneryNode_Get(node_name, params)
        elif ntype == Say:
            self[node_name] = SceneryNode_Say(node_name, params)
        else:
            raise TypeError(f"Can't use type {ntype} for node.")

    def __getitem__(self, key):
        return self.nodes[key]

    def __setitem__(self, key, value):
        self.nodes[key] = value

@dataclass
class User:
    uid : str = None
    is_busy : bool = False # some sort of a lock

    state = None # A reference to actual state
    variables : dict() = None

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
        self.scenery_phrases = bot_scenery["phrases"].copy()
        self.scenery_errors = bot_scenery["errors"].copy()
        self.scenery_infos = bot_scenery["infos"].copy()
        self.scenery_commands = bot_scenery["commands"].copy()
        self.scenery_states = SceneryGraph(bot_scenery["states"].copy(),
                                            self.scenery_phrases,
                                            self.scenery_errors,
                                            self.scenery_infos)
        self.scenery_start_state = bot_scenery["start_state"]
        self.hint_template = bot_scenery["hint_template"]

        # From config:
        self.scu = ServerControlUnit(   server_root=bot_config["redmine_root_url"],
                                        use_https=bot_config["use_https"])
        self.bot_user_key = bot_config["bot_user_key"]
        self.refresh_period = bot_config["refresh_period"]
        self.sleep_timeout = bot_config["sleep_timeout"]
        self.user_db_path = Path(bot_config["user_db_path"])
        self.allowed_api_functions = bot_config["allowed_api_functions"][:]

        self.reply_function = reply_function

        # Loading stuff from server or local database
        self.issue_statuses = self.scu.get_issue_statuses(self.bot_user_key)
        self.issue_priorities = self.scu.get_issue_priorities(self.bot_user_key)
        self.user_db : dict[str, User] = dict()
        self._load_user_db() # TODO: improve security of database

        # Initializing multithreading stuff
        self.enum_lock = Lock()
        self.user_db_lock = Lock()
        self.last_msg_timestamp = 0
        self.is_running = False
        self.enum_updater = None

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
            logging.warning(f"Fully resetting user {user.uid}")
            self.reset_user(user, keep_settings=False)
            self.reply_function(self._get_prompt_message(user))
            return
        elif content_array[0] in self.scenery_commands["cancel"]:
            logging.warning(f"Resetting state and variables of user {user.uid}")
            self.reset_user(user, keep_settings=True)
            self.reply_function(self._get_prompt_message(user))
            return
        elif content_array[0] in self.scenery_commands["info"]:
            self.reply_function(Message(user.uid, user.state.info))
            self.reply_function(self._get_prompt_message(user))
            return
        elif content_array[0] in self.scenery_commands["repeat"]:
            self.reply_function(self._get_prompt_message(user))
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
                    self._run_state(user, lex)
                    reply = self._get_prompt_message(user)
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

    def _get_prompt_message(self, user):
        if user.state.type == Ask and user.variables[Settings][Show_hints]:
            return Message( user.uid,
                        user.state.get_phrase(user) +
                        self.hint_template.format(user.state.get_hint_string()
                        ))
        else:
            return Message( user.uid,
                        user.state.get_phrase(user)
                        )

    def _run_state(self, user, lex):
        while True: # TODO: Think abot limiting the cycle
            user.state.set_vars(user.variables)
            user.state.input_var(user.variables, lex)
            self._call_function(user)
            user.state = user.state.get_next(lex)
            if not user.state.preserve_lexeme():
                break
            else:
                self.reply_function(Message(user.uid, user.state.get_phrase(user)))

    def _call_function(self, user):
        state = user.state
        # ~ self.log_to_user(user, f"Start calling functions in state {state}")
        logging.info(f"Start calling functions in state {state}")
        for function in state.function_list:
            # ~ self.log_to_user(user, f"Function is {function}")
            logging.info(f"Function is {function}")
            if type(function) is list:
                if (function[0] in self.allowed_api_functions) and (eval(function[1])):
                    # Note: the code above is sort of insecure, but scenery
                    # is owned by bot owner so if he want's to steal keys
                    # he can just edit the code and get the dictionary
                    getattr(self, function[0])(user)
            elif type(function) is str:
                if function in self.allowed_api_functions:
                    getattr(self, function)(user)

    def reset_user(self, user, keep_settings=True):
        u_settings = {
                        Reset_if_error      : False,
                        Approve_changes     : False,
                        Show_hints          : True,
                        Key                 : None,
                        Context             : None
                    }
        if keep_settings and user.variables:
            u_settings = user.variables[Settings]
        user.variables =    {
                            Settings : u_settings,
                            Data : dict(),
                                # ~ {
                                # ~ "project_id": 1,
                                # ~ "subject": "Example Пример",
                                # ~ "priority_id": 4,
                                # ~ "tracker_id": 1,
                                # ~ "status_id":1
                                # ~ },
                            Parameters : dict()
                            }
        user.state = self.scenery_states[self.scenery_start_state]
        # ~ user.context_obj_id = None

    def create(self, user):
        if user.variables[Settings][Context] is Project:
            user.variables[Data] = json.loads(self.scu.create_project(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key]))
        elif user.variables[Settings][Context] is Issue:
            user.variables[Data] = json.loads(self.scu.create_issue(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key]))
    def show(self, user):
        if user.variables[Settings][Context] is Project:
            user.variables[Data] = json.loads(self.scu.show_project(user.variables[Parameters],
                                    user.variables[Settings][Key]))
        elif user.variables[Settings][Context] is Issue:
            user.variables[Data] = json.loads(self.scu.show_issue(user.variables[Parameters],
                                    user.variables[Settings][Key]))

    def update(self, user):
        if user.variables[Settings][Context] is Project:
            user.variables[Data] = json.loads(self.scu.update_project(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key]))
        elif user.variables[Settings][Context] is Issue:
            user.variables[Data] = json.loads(self.scu.update_issue(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key]))
    def delete(self, user):
        if user.variables[Settings][Context] is Project:
            self.scu.delete_project(user.variables[Data]["id"],
                                    user.variables[Settings][Key])
        elif user.variables[Settings][Context] is Issue:
            self.scu.delete_issue(user.variables[Data]["id"],
                                    user.variables[Settings][Key])

    def get_project_list(self, user): # Todo: make userdefinable (sort of)
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = self.scu.get_project_list(parameters, key)
        if resp_data["success"]:
            for project in resp_data["data"]["projects"]:
                self.reply_function(Message(user.uid,
                                f"""№{project['id']} "{project['name']}" ({project['identifier']})"""))
        else:
            self.reply_function(Message(user.uid,
                                    "Мне не удалось получить список проектов"))
            user.state = self.scenery_states[self.scenery_start_state]

    def get_issue_list(self, user): # Todo: make userdefinable (sort of)
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = self.scu.get_issue_list(parameters, key)
        if resp_data["success"]:
            for issue in resp_data["data"]["issues"]:
                self.reply_function(Message(user.uid, f"""№{issue['id']} "{issue['subject']}" """))
        else:
            self.reply_function(Message(user.uid,
                                    "Мне не удалось получить список задач"))
            user.state = self.scenery_states[self.scenery_start_state]

    def show_issue_statuses(self, user):
        pass
    def show_issue_priorities(self, user):
        pass
    def add_watcher(self, user):
        pass
    def delete_watcher(self, user):
        pass

    # ~ def log_to_user(self, user, log_msg):
        # ~ self.reply_function(Message(user.uid, log_msg))

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
        self.stop()
        self.start()

    def shutdown(self):
        self.stop()
        self._save_user_db()

    def _save_user_db(self):
        plain_udb = dict()
        for uid, user in self.user_db.items():
            plain_udb[uid] = asdict(user)
            plain_udb[uid]["state"] = user.state.name
        with open(self.user_db_path, 'w') as udb_file:
            udb_file.write(json.dumps(plain_udb))

    def _load_user_db(self):
        try:
            with open(self.user_db_path, 'r') as udb_file:
                raw_data = json.loads(udb_file.read())
            for uid, udata in raw_data.items():
                state_name = udata.pop("state")
                self.user_db[uid] = User(**udata)
                self.user_db[uid].state = self.scenery_states[state_name]
        except OSError:
            pass

