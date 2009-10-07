
import twitter
import threading

def update_all_dms(self):
    for account in self.config.twitter_accounts:
        update_dms(self, account)
    
    self.twitter_thread = new_timer(self)
    self.twitter_thread.start()

def update_dms(self, account):
    api = twitter.Api(username=account, password=self.config.twitter_accounts[account]['password'])
    since = self.twitter_since[account]
    recips = self.config.twitter_accounts[account]['channels']
    
    dm_msgs = api.GetDirectMessages(since_id=since)
    if len(dm_msgs) > 0:
        self.twitter_since[account] = dm_msgs[0].GetId()
        for dm in dm_msgs:
            for recip in recips:
                self.msg(recip, "New DM from %s: %s" % (dm.GetSenderScreenName(), dm.GetText()))    

def new_timer(self):
    return threading.Timer(120.0, update_all_dms, args=[self])

def setup(self):
    if not hasattr(self, 'twitter_thread'):
        self.twitter_api = {}
        self.twitter_since = {}
        for account in self.config.twitter_accounts:
            api = twitter.Api(username=account, password=self.config.twitter_accounts[account]['password'])
            dms = api.GetDirectMessages()
            if len(dms) > 0:
                self.twitter_since[account] = dms[0].GetId()
        self.twitter_thread = new_timer(self)
        self.twitter_thread.start()
