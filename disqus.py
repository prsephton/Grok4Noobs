import grok
from interfaces import IArticle
from layout import Content

class Disqus(grok.Viewlet):
    '''  A viewlet to display a Disqus section with every article
    '''
    grok.context(IArticle)
    grok.viewletmanager(Content)
    grok.order(99)

    def namespace(self):
        ns = {}
        ns['PAGE_URL'] = self.view.url()
        ns['PAGE_IDENTIFIER'] = self.context.title
        return ns
