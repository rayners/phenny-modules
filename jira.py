#!/usr/bin/env python
"""
jira.py - Phenny Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import xmlrpclib
import time
import re
import modules.activecollab

recent_tickets = {}
min_age = 60 * 5

def get_status(self):
    server = xmlrpclib.ServerProxy(self.config.jira_baseurl)
    try:
        # self.jira = {}
        auth = server.jira1.login(self.config.jira_username, self.config.jira_password)
        server_statuses = server.jira1.getStatuses(auth)
        jira_statuses = {}
        for status in server_statuses:
            if self.config.jira_mappings['status'].has_key(status['name']):
                jira_statuses[status['id']] = self.config.jira_mappings['status'][status['name']]
            else:
                jira_statuses[status['id']] = status['name']
        self.jira_statuses = jira_statuses
        server_priorities = server.jira1.getPriorities(auth)
        jira_priorities = {}
        for priority in server_priorities:
            if self.config.jira_mappings['priority'].has_key(priority['name']):
                jira_priorities[priority['id']] = self.config.jira_mappings['priority'][priority['name']]
            else:
                jira_priorities[priority['id']] = priority['name']
        self.jira_priorities = jira_priorities
        
        info = server.jira1.getServerInfo(auth)
        self.jira_baseurl = info['baseUrl']
    except xmlrpclib.Error, v:
        print "XMLRPC ERROR: ", v

def _ticket_lookup(self, ticket):
    server = xmlrpclib.ServerProxy(self.config.jira_baseurl)
    try:
        auth = server.jira1.login(self.config.jira_username, self.config.jira_password)
        info = server.jira1.getIssue(auth, ticket)
        return info
    except xmlrpclib.Error, v:
        print "XMLRPC ERROR:", v
    return None
    
def ticket_lookup(self, ticket):
    """docstring for ticket_lookup"""
    info = _ticket_lookup(self, ticket)
    if info:
        self.say( "%s: Summary:     %s" % (info['key'], info['summary']))
        if info.has_key('assignee'):
            self.say( "%s: Assigned To: %s" % (info['key'], info['assignee']))
        else:
            self.say( "%s: Assigned To: Unassigned" % (info['key']))            
        self.say( "%s: Priority:    %s" % (info['key'], self.jira_priorities[info['priority']]))
        self.say( "%s: Status:      %s" % (info['key'], self.jira_statuses[info['status']]))
        self.say( "%s: %s/browse/%s" % (info['key'], self.jira_baseurl, info['key']))

def f_jira(phenny, input):
    """JIRA stuff"""
    if not input.sender in phenny.config.jira_channels and not input.owner:
        return
    for ticket in phenny.jira_re.findall(input.bytes):
        if ticket not in recent_tickets or recent_tickets[ticket] < time.time() - min_age:
            recent_tickets[ticket] = time.time()
            ticket_lookup(phenny, ticket)
f_jira.priority = 'low'

def f_jiratoac(phenny, input):
    """docstring for f_jiratoac"""
    ticket = input.group(2)
    info = _ticket_lookup(phenny, ticket)
    if info:
        project = modules.activecollab.current_project(phenny, input.sender)
        if project:
            summary = '(%s) %s' % (ticket, info['summary'])
            js = modules.activecollab.create_ticket(phenny, project, summary)
            phenny.say('Created ticket %s-%s: %s' % (project, js['id'], js['permalink']))
f_jiratoac.commands = [ 'jiratoac' ]
f_jiratoac.priority = 'medium'

def setup(self):
    get_status(self)
    re_str = r'((?:' + '|'.join(self.config.jira_projects) + ')-(?:\d+))'
    self.jira_re = re.compile(re_str)
    f_jira.rule = r'.*' + re_str
