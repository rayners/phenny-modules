
import typepad

def f_tpuser(phenny, input):
    typepad.client.batch_request()
    u = typepad.User.get_by_url_id(input.group(2))
    typepad.client.complete_batch()
    phenny.say("%s's about me: %s" % (input.group(2), u.about_me))
f_tpuser.commands = ['tpuser']

def f_tpelsewhere(phenny, input):
    typepad.client.batch_request()
    u = typepad.User.get_by_url_id(input.group(2))
    typepad.client.complete_batch()

    for account in u.elsewhere_accounts:
        if account.provider_name:
            if account.username:
                phenny.say('%s at %s (%s)' % (account.username, account.provider_name, account.url))
            else:
                phenny.say( '%s at %s (%s)' % (account.user_id, account.provider_name, account.url))
        elif account.url:
            phenny.say( account.url)
f_tpelsewhere.commands = ['tpelsewhere']

def setup(self):
    typepad.TypePadObject.batch_requests = False
