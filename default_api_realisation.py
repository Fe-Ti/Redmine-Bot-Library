import json
import logging

from bot_lib_constants import *
from bot_data_structs import User, Message

class DefaultTemplates:
    issue = """№{id} {subject}

Описание: {description}
Статус: {status[name]}

Автор: {author[name]} ({author[id]})
Трекер: {tracker[name]}
    
Дата начала: {start_date}
Срок завершения: {due_date}
"""
    issue_assigned_to = "Назначена: {assigned_to[name]} ({assigned_to[id]})"


    issue_draft = """Черновик задачи:
Тема: {subject}
ID проекта: {project_id}

Описание: {description}

Дата начала: {start_date}
Дедлайн: {due_date}
Статус: {status}

Назначена: {assigned_to}
Трекер: {tracker}"""

    project = """{name} ({identifier})

Описание:   {description}

Участники:
"""
    project_draft = """Черновик проекта:
Название: {name}
Идентификатор: {identifier}
Описание: {description}
"""

    project_custom_field = """{name}: {value}
"""
    project_member_field = """{user[name]} (id:{user[id]}): {role_names}
"""

    issue_custom_field = project_custom_field

    project_list_entry = """№{id} "{name}" ({identifier})\n"""

    issue_list_entry = """№{id} "{subject}"\n"""

class DefaultApiRealisation:
    def __init__(self, bot = None, templates = DefaultTemplates()):
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

    def reset_user(self, user):
        print(user.state)
        self.bot.reset_user(user, keep_settings=True)
        print(user.state)

    def create(self, user):
        bot = self.bot
        self._clear_nulls(user.variables[Data])
        if user.variables[Settings][Context] is Project:
            bot.scu.create_project(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
        elif user.variables[Settings][Context] is Issue:
            bot.scu.create_issue(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
    def show(self, user):
        bot = self.bot
        resp_data : dict = dict()
        template : str = None
        resp_data = dict()
        if user.variables[Settings][Context] is Project:
            resp_data = bot.scu.show_project(user.variables[Parameters],
                                    user.variables[Settings][Key])
            if resp_data["success"]:
                project = resp_data["data"]["project"]
                string = self.templates.project.format_map(project)
                if "custom_fields" in project:
                    for custom_field in project["custom_fields"]:
                        string += self.templates.project_custom_field.format_map(custom_field)
                string += self._get_project_memberships(user, project["id"])
        
        elif user.variables[Settings][Context] is Issue:
            resp_data = bot.scu.show_issue(user.variables[Parameters],
                                    user.variables[Settings][Key])
            if resp_data["success"]:
                issue = resp_data["data"]["issue"]
                string = self.templates.issue.format_map(issue)
                if "assigned_to" in issue:
                    string += self.templates.issue_assigned_to.format_map(issue)
                if "custom_fields" in issue:
                    for custom_field in issue["custom_fields"]:
                        string += self.templates.project_custom_field.format_map(custom_field)
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        if not resp_data["success"]:
            self._report_failure(user)
        else:
            bot.reply_function(Message(user.uid, string))

    def update(self, user):
        pass
        # ~ bot = self.bot
        # ~ if user.variables[Settings][Context] is Project:
            # ~ resp_data = bot.scu.update_project(user.variables[Parameters],
                                    # ~ user.variables[Data],
                                    # ~ user.variables[Settings][Key])
        # ~ elif user.variables[Settings][Context] is Issue:
            # ~ resp_data = bot.scu.update_issue(user.variables[Parameters],
                                    # ~ user.variables[Data],
                                    # ~ user.variables[Settings][Key])
    def delete(self, user):
        pass
        # ~ bot = self.bot
        # ~ if user.variables[Settings][Context] is Project:
            # ~ bot.scu.delete_project(user.variables[Data]["id"],
                                    # ~ user.variables[Settings][Key])
        # ~ elif user.variables[Settings][Context] is Issue:
            # ~ bot.scu.delete_issue(user.variables[Data]["id"],
                                    # ~ user.variables[Settings][Key])

    def get_project_list(self, user): # Todo: make userdefinable (sort of)
        bot = self.bot
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = bot.scu.get_project_list(parameters, key)
        if resp_data["success"]:
            msg_string = str()
            for project in resp_data["data"]["projects"]:
                msg_string += self.templates.project_list_entry.format_map(project)
            if not msg_string:
                bot.reply_function(Message(user.uid, "Проектов нет."))
            else:
                bot.reply_function(Message(user.uid, msg_string))
        else:
            self._report_failure(user)

    def get_issue_list(self, user): # Todo: make userdefinable (sort of)
        bot = self.bot
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = bot.scu.get_issue_list(parameters, key)
        if resp_data["success"]:
            msg_string = str()
            for issue in resp_data["data"]["issues"]:
                msg_string += self.templates.issue_list_entry.format_map(issue)
            if not msg_string:
                bot.reply_function(Message(user.uid, "Задач нет."))
            else:
                bot.reply_function(Message(user.uid, msg_string))
        else:
            self._report_failure(user)

    def show_issue_statuses(self, user):
        bot = self.bot

    def show_issue_priorities(self, user):
        bot = self.bot
        pass
    def add_watcher(self, user):
        bot = self.bot
        pass
    def delete_watcher(self, user):
        bot = self.bot
        pass

    def show_project_draft(self, user):
        bot = self.bot
        bot.reply_function(Message(
                                    user.uid, 
                                    self.templates.project_draft.format_map(user.variables[Data])
                                    ))

    def show_issue_draft(self, user):
        bot = self.bot
        bot.reply_function(Message(
                                    user.uid, 
                                    self.templates.issue_draft.format_map(user.variables[Data])
                                    ))

    def log_to_user(self, user, log_msg):
        bot = self.bot
        bot.reply_function(Message(user.uid, log_msg))
        
    def _get_project_memberships(self, user, project_id):
        bot = self.bot
        string = str()
        resp_data = bot.scu.get_project_memberships(project_id,
                                                    user.variables[Settings][Key])
        if resp_data["success"]:
            member = dict()
            for mship in resp_data["data"]["memberships"]:
                member["role_names"] = str({ role["name"] for role in mship["roles"] })[1:-1].replace("'","")
                member["user"] = mship["user"]
                string += self.templates.project_member_field.format_map(member)
        return string
    def get_project_memberships(self, user):
        bot = self.bot
        string = self._get_project_memberships(user, user.variables[Data]["identifier"])
        if not string:
            return
        self.bot.reply_function(Message(user.uid, string))

    def push_state_stack(self, user):
        storage = user.variables[Storage]
        if State_stack not in storage:
            storage[State_stack] = list()
        if JMP_state in storage:
            storage[State_stack].append(user.state.name)
            user.state = self.bot.scenery_states[storage[JMP_state]]

    def pop_state_stack(self, user):
        storage = user.variables[Storage]
        if State_stack not in storage:
            logging.warning("No stack initialized. (User:{user.uid})")
            return
        if not storage[State_stack]:
            logging.warning(f"Stack is empty. (User:{user.uid})")
            return
        state_name = storage[State_stack].pop()
        user.state = self.bot.scenery_states[state_name]

