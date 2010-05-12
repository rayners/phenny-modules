
def sandwich(phenny, input):
  print input.group(1)
  if input.group(1) == 'sudo ':
    phenny.say('Okay')
  else:
    phenny.say('What?  Make it yourself.')
sandwich.name = 'sandwich'
sandwich.rule = ('$nick', r'(sudo )?make me a sandwich')
sandwich.priority = 'low'
