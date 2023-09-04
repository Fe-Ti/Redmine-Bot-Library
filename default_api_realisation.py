import json
import logging

from bot_lib_constants import *
from bot_data_structs import User, Message

def get_string_from_enum_list(enum_list, template_list_entry):
    string = str()
    for entry in enum_list:
        string += template_list_entry.format_map(entry)
    return string

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

    project_custom_field = """{name}: {value}\n"""
    project_member_field = """{user[name]} (id:{user[id]}): {role_names}\n"""

    issue_custom_field = project_custom_field

    project_list_entry = """№{id} "{name}" ({identifier})\n"""

    issue_list_entry = """№{id} "{subject}"\n"""
    
    issue_statuses = """Статусы: {}"""
    issue_statuses_list_entry = """\n{id} "{name}" """
    issue_trackers = """Трекеры: {}"""
    issue_trackers_list_entry = issue_statuses_list_entry
    issue_priorities = """Приоритеты: {}"""
    issue_priorities_list_entry = issue_statuses_list_entry

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

    ### Functions which don't use redmine API
    def reset_user(self, user):
        print(user.state)
        self.bot.reset_user(user, keep_settings=True, reset_state=False)
        print(user.state)

    def push_state_to_stack(self, user):
        storage = user.variables[Storage]
        if State_stack not in storage:
            storage[State_stack] = list()
        if JMP_state in storage:
            storage[State_stack].append(user.state.name)
            user.state = self.bot.scenery_states[storage[JMP_state]]

    def pop_state_from_tack(self, user):
        storage = user.variables[Storage]
        if State_stack not in storage:
            logging.warning("No stack initialized. (User:{user.uid})")
            return
        if not storage[State_stack]:
            logging.warning(f"Stack is empty. (User:{user.uid})")
            return
        state_name = storage[State_stack].pop()
        user.state = self.bot.scenery_states[state_name]

    def call_state(self, user):
        push_state_to_stack()
        self.bot._run_state(user)
        pop_state_from_stack()

    def reset_to_start(self, user):
        self.bot.reset_user(user, keep_settings=True, reset_state=True)

    ### Functions which call ServerControlUnit functions (i.e. use RM API)

    def create(self, user):
        self._clear_nulls(user.variables[Data])
        if user.variables[Storage][Context] is Project:
            self.bot.scu.create_project(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
        elif user.variables[Storage][Context] is Issue:
            self.bot.scu.create_issue(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])

    def _project_to_str(self, user, resp_data):
        if resp_data[Success]:
            project = resp_data["data"]["project"]
            string = self.templates.project.format_map(project)
            if "custom_fields" in project:
                for custom_field in project["custom_fields"]:
                    string += self.templates.project_custom_field.format_map(custom_field)
            string += self._get_project_memberships(user, project["id"])
            return string
        return str()

    def _issue_to_str(self, user, resp_data):
        if resp_data[Success]:
            issue = resp_data["data"]["issue"]
            string = self.templates.issue.format_map(issue)
            if "assigned_to" in issue:
                string += self.templates.issue_assigned_to.format_map(issue)
            if "custom_fields" in issue:
                for custom_field in issue["custom_fields"]:
                    string += self.templates.project_custom_field.format_map(custom_field)
            return string
        return str()

    def show(self, user):
        if user.variables[Storage][Context] is Project:
            resp_data = self.bot.scu.show_project(user.variables[Parameters],
                                    user.variables[Settings][Key])
            string = self._project_to_str(user, resp_data)
        elif user.variables[Storage][Context] is Issue:
            resp_data = self.bot.scu.show_issue(user.variables[Parameters],
                                    user.variables[Settings][Key])
            string = self._issue_to_str(user, resp_data)
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        if not resp_data[Success]:
            self._report_failure(user)
        else:
            self.bot.reply_function(Message(user.uid, string))

    def get_data(self, user):
        if user.variables[Storage][Context] == Project:
            resp_data = self.bot.scu.show_project(user.variables[Parameters],
                                                user.variables[Settings][Key])
        elif user.variables[Storage][Context] == Issue:
            resp_data = self.bot.scu.show_issue(user.variables[Parameters],
                                                user.variables[Settings][Key])
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        if resp_data[Success]:
            user.variables[Storage]["data"] = resp_data["data"]
            user.variables[Storage][Success] = resp_data[Success]
        else:
            self._report_failure(user)
            user.variables[Storage][Success] = False

    def update(self, user):
        self._clear_nulls(user.variables[Data])
        if user.variables[Storage][Context] is Project:
            self.bot.scu.update_project(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
        elif user.variables[Storage][Context] is Issue:
            self.bot.scu.update_issue(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])

    def delete(self, user):
        if user.variables[Storage][Context] is Project:
            self.bot.scu.delete_project(user.variables[Data]["id"],
                                    user.variables[Settings][Key])
        elif user.variables[Storage][Context] is Issue:
            self.bot.scu.delete_issue(user.variables[Data]["id"],
                                    user.variables[Settings][Key])

    def get_project_list(self, user):
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = self.bot.scu.get_project_list(parameters, key)
        if resp_data[Success]:
            msg_string = str()
            for project in resp_data["data"]["projects"]:
                msg_string += self.templates.project_list_entry.format_map(project)

            if not msg_string:
                self.bot.reply_function(Message(user.uid, "Проектов нет."))
            else:
                self.bot.reply_function(Message(user.uid, msg_string))
        else:
            self._report_failure(user)


    def get_issue_list(self, user):
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = self.bot.scu.get_issue_list(parameters, key)
        if resp_data[Success]:
            msg_string = str()
            for issue in resp_data["data"]["issues"]:
                msg_string += self.templates.issue_list_entry.format_map(issue)
            if not msg_string:
                self.bot.reply_function(Message(user.uid, "Задач нет."))
            else:
                self.bot.reply_function(Message(user.uid, msg_string))
        else:
            self._report_failure(user)

    def show_project_draft(self, user):
        self.bot.reply_function(Message(
                                    user.uid, 
                                    self.templates.project_draft.format_map(user.variables[Data])
                                    ))

    def show_issue_draft(self, user):
        self.bot.reply_function(Message(
                                    user.uid, 
                                    self.templates.issue_draft.format_map(user.variables[Data])
                                    ))

    def log_to_user(self, user, log_msg):
        self.bot.reply_function(Message(user.uid, log_msg))
        
    def _get_project_memberships(self, user, project_id):
        string = str()
        resp_data = self.bot.scu.get_project_memberships(project_id,
                                                    user.variables[Settings][Key])
        if resp_data[Success]:
            member = dict()
            for mship in resp_data["data"]["memberships"]:
                member["role_names"] = str({ role["name"] for role in mship["roles"] })[1:-1].replace("'","")
                member["user"] = mship["user"]
                string += self.templates.project_member_field.format_map(member)
        return string

    def show_project_memberships(self, user):
        string = self._get_project_memberships(user, user.variables[Data]["identifier"])
        if not string:
            return
        self.bot.reply_function(Message(user.uid, string))

    def _show_enumeration(self, user, enum_list, template, template_list_entry):
        if user.variables[Storage][Context] in [Project, Global, Issue]:
            self.bot.reply_function(Message(
                user.uid,
                template.format(get_string_from_enum_list(enum_list, template_list_entry))
                ))
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        
    def show_issue_statuses(self, user):
        self._show_enumeration(
            user = user,
            enum_list = self.bot.issue_statuses,
            template = self.templates.issue_statuses,
            template_list_entry = self.templates.issue_statuses_list_entry,
        )

    def show_issue_trackers(self, user):
        self._show_enumeration(
            user = user,
            enum_list = self.bot.issue_trackers,
            template = self.templates.issue_trackers,
            template_list_entry = self.templates.issue_trackers_list_entry,
        )

    def show_issue_priorities(self, user):
        self._show_enumeration(
            user = user,
            enum_list = self.bot.issue_priorities,
            template = self.templates.issue_priorities,
            template_list_entry = self.templates.issue_priorities_list_entry,
        )

    def add_watcher(self, user):
        pass
    def delete_watcher(self, user):
        pass
