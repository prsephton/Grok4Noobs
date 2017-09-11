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
        url = str(self.view.url())
        url.replace('gfn.aptrackers.com', 'www.aptrackers.com/gfn')
        ns['PAGE_URL'] = url
        ns['PAGE_IDENTIFIER'] = self.context.title
        return ns
