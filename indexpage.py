#______________________________________________________________________________
# Produce an index page for the site
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import grok

from interfaces import ISiteRoot, IArticle, IArticleSorter
from menu import UtilItem
from layout import ILayout, Content
from zope.location import location
from zope import component

class IndexPage(grok.Model):
    ''' Return an index page for the site
    '''
    grok.implements(ILayout)
    title = u'Site Index'
    navTitle = u'Index'
    text = u''
    article = None

    def __init__(self, article):
        self.article = article


class PageView(grok.View):
    grok.context(IArticle)
    grok.name('indexpage')
    grok.require('zope.Public')

    def render(self):
        ctx = self.context
        while not ISiteRoot.providedBy(ctx):
            ctx = ctx.__parent__
        page = IndexPage(self.context)
        page = location.located(page, ctx, 'indexpage')
        view = component.getMultiAdapter((page, self.request), name='index')
        return view()

class IndexContent(grok.Viewlet):
    ''' This populates the 'Content' section with the index
    '''
    grok.context(IndexPage)
    grok.require('zope.Public')
    grok.viewletmanager(Content)

    def namespace(self):
        return dict(site=self.context.__parent__)

class IndexOf(grok.View):
    ''' Produces an index entry from the current article
    '''
    grok.context(IArticle)
    grok.require('zope.Public')

    def update(self):
        if not hasattr(self.context, 'section'):
            self.articleNumber()

    def articleNumber(self):
        order = getattr(self.context, "order", None)
        if order is None:
            self.context.section = ""
        else:
            order = int(order) + 1
            parent = getattr(self.context, "__parent__", None)
            if parent and hasattr(parent, 'section') and len(parent.section):
                section = "{}.{}".format(parent.section, order)
            else:
                section = "{}".format(order)
            self.context.section = section
            return section + ": "
        return ""

    def articleId(self):
        if str(self.request.URL).find('fullpage') >= 0:
            section = getattr(self.context, 'section', False)
            if section:
                return u'#sn_'+section.replace('.', '_')
            else:
                return u'#sn_main'
        else:
            return self.url(self.context)

    def sortedItems(self):
        sorter = IArticleSorter(self.context)
        return sorter.sortedItems()

class IntroductionMenuEntry(UtilItem):
    '''  Make a button to navigate to the introduction
    '''
    grok.context(IndexPage)
    title = mtitle = u'Top Level'
    link = u'..'
    mclass = 'nav buttons'
    grok.order(1)
    def condition(self):
        self.title = self.context.__parent__.navTitle
        self.image = self.static['up.png']
        return True

class ArticleMenuEntry(UtilItem):
    '''  Make a button to navigate to the introduction
    '''
    grok.context(IndexPage)
    title = mtitle = u'Back to Article'
    link = None
    mclass = 'nav buttons'
    grok.order(2)
    def condition(self):
        if self.context.article==self.context.__parent__:
            return False
        self.title = self.context.article.navTitle
        self.image = self.static['left.png']
        self.link = self.context.article
        return True

class IndexButton(UtilItem):
    '''  A menu item to navigate to the index
    '''
    grok.context(IArticle)
    grok.require('zope.Public')
    grok.order(-1)
    title = u'Index'
    link = 'indexpage'
    mclass = 'nav buttons'

