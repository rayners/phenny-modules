
import random

def act(msg):
    """docstring for act"""
    action = '\x01ACTION %s\x01' % msg
    return action

def f_stab(phenny, input):
    msg = act("stabs %s" % input.group(2))
    phenny.say(msg)    
f_stab.commands = ['stab']

def f_slap(phenny, input):
    verb = random.choice(phenny.config.slap_verbs)
    area = random.choice(phenny.config.slap_areas)
    size = random.choice(phenny.config.slap_sizes)
    tool = random.choice(phenny.config.slap_tools)
    
    thing = input.group(2)
    action = "%s %s %s with a %s %s" % (verb, thing, area, size, tool)
    msg = act(action)
    phenny.say(msg)
f_slap.commands = ['slap']