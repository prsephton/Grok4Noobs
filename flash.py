import grok
from zope.component import Interface
from grokcore.message.utils import receive

class FlashMgr(grok.ViewletManager):
    grok.context(Interface)

class FlashViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.viewletmanager(FlashMgr)
    grok.require('zope.Public')

    def update(self):
        mlist = receive()
        self.messages = list(mlist) if mlist else []
