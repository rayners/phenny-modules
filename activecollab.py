
from xml.dom.minidom import parseString
import json
import web

def activecollab_request(self, command, args={}, data={}):
    """docstring for activecollab_request"""
    url = self.config.activecollab_url
    url += "?path_info=%s" % command
    args['token'] = self.config.activecollab_key
    args['format'] = 'json'
    for (key, value) in args.items():
        url += "&%s=%s" % (key, value)
    if len(data) > 0:
        bytes = web.post(url, data)
        js = json.loads(bytes)
        return js
    else:        
        bytes = web.get(url)
        js = json.loads(bytes)
        return js

def setup_projects(self):
    """docstring for setup_projects"""
    self.activecollab_projects = {}
    dom = activecollab_request(self, 'projects')
    for project in dom:
        self.activecollab_projects[project['id']] = project['name']
    
def setup_users(self):
    """docstring for setup_users"""
    self.activecollab_companies = {}
    self.activecollab_users = {}
    dom = activecollab_request(self, 'people')
    for company in dom:
        self.activecollab_companies[company['id']] = company['name']
        if company['id'] == 21:            
            users = activecollab_request(self, "people/%s" % (company['id']))
            if users['users']:
                for user in users['users']:
                    self.activecollab_users[user['id']] = "%s %s (%s)" % (user['first_name'], user['last_name'], user['email'])

def setup(self):
    setup_projects(self)
    setup_users(self)

def current_project(self, sender, project=0):
    """docstring for current_project"""
    if not hasattr(self.bot, 'activecollab_current_projects'):
        self.bot.activecollab_current_projects = {}
    if not project:
        if self.activecollab_current_projects.has_key(sender):
            return self.activecollab_current_projects[sender]
        elif self.config.activecollab_channels[sender]:
            return self.config.activecollab_channels[sender]
        else:
            return 0
    else:
        self.activecollab_current_projects[sender] = project

def f_project(self, input):
    project_id = input.group(2)
    if not project_id:
        project = current_project(self, input.sender)
        if project:
            self.say("Current project: %s" % (self.activecollab_projects[project]))
        else:
            self.say("No current project")
    else:
        project_id = int(project_id)
        if self.activecollab_projects.has_key(project_id):
            self.say(self.activecollab_projects[project_id])
            current_project(self, input.sender, project_id)
        else:
            self.say('Unknown project')
f_project.commands = ['acproject']
    
def f_ticket(self, input):
    project = current_project(self, input.sender)
    ticket = input.group(2)
    if project:
        dom = activecollab_request(self, "projects/%s/tickets/%s" % (project, ticket))
        self.say("%s-%s: Summary: %s" % (project, ticket, dom['name']))
        if dom['assignees']:
            for assignee in dom['assignees']:
                self.say("%s-%s: Assignee: %s" % (project, ticket, self.activecollab_users[assignee['user_id']]))
        else:
            self.say('%s-%s: Assignee: Unassigned' % (project, ticket))
        self.say("%s-%s: %s" % (project, ticket, dom['permalink']))
        
f_ticket.commands = ['acticket']

def create_ticket(self, project, summary):
    data = {'submitted': 'submitted', 'ticket[name]': summary}
    command_path = 'projects/%s/tickets/add' % (project)
    return activecollab_request(self, command_path, data=data)
    
def f_createticket(self, input):
    project = current_project(self, input.sender)
    summary = input.group(2)
    if project:
        dom = create_ticket(self, project, summary)
        self.say('Created ticket %s-%s: %s' % (project, dom['id'], dom['permalink']))
f_createticket.commands = ['accreateticket']
