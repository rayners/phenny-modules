
import random
import os
import sqlite3
import sys
import types

taunts = [
    "You don't frighten us, English pig-dogs!  Go and boil your bottom, sons of a silly person.  I blow my nose at you, so-called Arthur King, you and all your silly English k-nnnnniggets.  Thpppppt!  Thppt!  Thppt!",
    "I don't wanna talk to you no more, you empty headed animal food trough wiper!  I fart in your general direction!  You mother was a hamster and your father smelt of elderberries!",
    "Allo, dappy English k-niggets and Monsieur Arthur King, who has the brain of a duck, you know.  So, we French fellows outwit you a second time!",
    "How you English say, 'I one more time, mac, unclog my nose in your direction', sons of a window-dresser!  So, you think you could out-clever us French folk with your silly knees-bent running about advancing behavior?!  I wave my private parts at your aunties, you cheesy lot of second hand electric donkey-bottom biters.",
    "No chance, English bed-wetting types.  I burst my pimples at you and call your door-opening request a silly thing, you tiny-brained wipers of other people's bottoms!",
    "And now, remain gone, illegitimate-faced bugger-folk!  And, if you think you got a nasty taunting this time, you ain't heard nothing yet, dappy English k-nnniggets!  Thpppt!"
]

def act(msg):
    """docstring for act"""
    action = '\x01ACTION %s\x01' % msg
    return action

def f_slap(phenny, input):
    verb = random.choice(phenny.config.slap_verbs)
    area = random.choice(phenny.config.slap_areas)
    size = random.choice(phenny.config.slap_sizes)
    tool = random.choice(phenny.config.slap_tools)
    
    thing = input.group(2)
    action = "%s %s %s with a %s %s" % (verb, thing.rstrip(), area, size, tool)
    msg = act(action)
    phenny.say(msg)
f_slap.commands = ['slap']

def _curse_string(phenny):
    number_of_swears = random.randint(1, 6)
    cur = phenny.swears_db.cursor()
    cur.execute('select swear from swears order by random() limit %s' % (number_of_swears))
    swears = map(lambda x: x[0], cur)
    return ' '.join(swears)

def _praise_string(phenny):
    number_of_swears = random.randint(1, 6)
    cur = phenny.swears_db.cursor()
    cur.execute('select praise from praises order by random() limit %s' % (number_of_swears))
    swears = map(lambda x: x[0], cur)
    return ' '.join(swears)

def f_curseout(phenny, input):
    target = input.group(2)
    swears = _curse_string(phenny)
    phenny.say('%s %s!!' % (swears, target))
f_curseout.commands = ['curseout']
f_curseout.thread = False

def f_blame(phenny, input):
    target = input.group(2)
    swears = _curse_string(phenny)
    if not target:
        phenny.say(act('blames it on the rain'))
    else:
        phenny.say("It's all %s %s's fault!!" % (swears, target.rstrip()))
f_blame.commands = ['blame']
f_blame.thread = False

#def f_praise(phenny, input):
#    target = input.group(2)
#    praises = _praise_string(phenny)
#    phenny.say('%s %s' % (praises, target))
#f_praise.commands = ['praise']
#f_praise.thread = False

def setup(phenny):
    if not hasattr(phenny, 'swears_db'):
        fn = phenny.nick + '-' + phenny.config.host + '.swears.db'
        swear_filename = os.path.join(os.path.expanduser('~/.phenny'), fn)
        phenny.swears_db = sqlite3.connect(swear_filename)
        with phenny.swears_db:
            phenny.swears_db.execute('''CREATE TABLE IF NOT EXISTS swears ( id INTEGER PRIMARY KEY,swear VARCHAR NOT NULL );''')
            phenny.swears_db.execute('''CREATE TABLE IF NOT EXISTS praises (id INTEGER PRIMARY KEY,praise VARCHAR NOT NULL );''')

# ( 'command', 'verb string', 'default target' )

def __praise__(phenny, input):
    praises = _praise_string(phenny)
    return praises + ' %s'

def __thank__(phenny, input):
    praises = _praise_string(phenny)
    return "It's all thanks to " + praises + ' %s!!'

def __stab__(input):
    t = [ 'wildly', input.nick ]
    return random.choice(t)

def __taunt__(input):
    t = random.choice(taunts)
    if input.group(2):
        t = input.group(2).rstrip() + ': ' + t
    return t

def __high5__(input):
    return input.nick

acronyms = ( ('ym', 'Your mom'), 
             ('rimshot', 'Ba-dum-pish!'),
             ('twss', 'That\'s what she said!'),
             ('mole', 'IT\'S MOLE!'),
             ('taunt', __taunt__),
             ('whe{2,}!?', "wheeeee!"),
             ('sadtrombone', "waa waaa waaaaaa"),
             ('sque(?:al|e+)!?', "squeeee!"))

actions = ( ('thank', __thank__, 'rayners'),
            ('giggle', 'giggles at %s', 'nothing'),
            ('stab', 'stabs', __stab__), 
            ( ['fstab', 'facestab'], 'stabs %s in the face', 'wildly'),
            ( ['kill', 'fkill', 'facekill'], 'kills %s in the face', 'stabbers'),
            ( [ 'murder', 'fmurder' ], 'murders %s in the face', 'Monday'),
            ('burn', 'burns', 'bridges'),
            ('burninate', 'burninates', ''),
            ('smite', 'smites', 'the unholy'),
            ('tickle', 'tickles', ''),
            ('cuddle', 'cuddles', ['fluffy bunnies', 'puppies', 'fuzzy kittens']),
            ('snuggle', 'snuggles', ''),
            ('frolick', 'frolicks with', 'bunnies'),
            ('scratch', 'scratches', 'itself'),
            ('dig', 'digs', 'deep'),
            ('slime', 'slimes', 'Dr. Venkman'),
            ([ '\^5', 'high-?(?:5|five)'], 'high fives', __high5__),
            ('goo', 'makes %s GOO', 'it'),
            ('pity', 'pities %s', 'the fool'),
            ('asplode', 'asplodes', ''),
            ('tackle', 'tackles', ''),
            ('badger', 'puts a rabid badger in %s\'s shorts', 'sivy'),
            ('sacrifice', 'sacrifices %s to Baal', [ 'puppies', 'kittens' ]))

def __action__((command, verb_str, def_target)):
    if type(verb_str) == types.StringType:
        v = verb_str
        if not '%s' in v:
            v = v + ' %s'
        def verb_str(phenny, input):
            return act(v)
    if type(command) == types.StringType:
        command = [command]
    if type(def_target) == types.StringType:
        s = def_target
        def def_target(input):
            return s
    elif type(def_target) == types.ListType or type(def_target) == types.TupleType:
        s = def_target
        def def_target(input):
            return random.choice(s)
    def action(phenny, input):
        target = input.group(2)
        if not target:
            target = def_target(input)
        msg = verb_str(phenny, input) % (target.rstrip())
        phenny.say(msg)
    action.commands = command
    action.thread = False
    return action

def __acronym__((short, lng)):
    if type(lng) == types.StringType:
        s = lng
        def lng(input):
            return s
    def acronym(phenny, input):
        phenny.say(lng(input))
    acronym.commands = [short]
    return acronym

i = 0
for a in actions:
    i = i + 1
    setattr(sys.modules[__name__], 'f_action_' + str(i), __action__(a))

j = 0
for a in acronyms:
    j = j + 1
    setattr(sys.modules[__name__], 'f_acronym_' + str(j), __acronym__(a))

def f_actions(phenny, input):
    acts = ['slap', 'thank', 'praise', 'curseout', 'blame']
    for a in actions:
        if type(a[0]) == types.StringType:
            acts.append(a[0])
        else:
            acts.extend(a[0])
    phenny.say("I know how to do the following actions: " + ', '.join(acts))
f_actions.commands = ['actions']
