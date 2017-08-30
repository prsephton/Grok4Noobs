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

class PageView(grok.View):
    grok.context(ISiteRoot)
    grok.name('indexpage')
    grok.require('zope.Public')

    def render(self):
        page = IndexPage()
        page = location.located(page, self.context, 'indexpage')
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

    def articleNumber(self):
        order = getattr(self.context, "order", None)
        if order is None:
            self.context.section = ""
        else:
            order = int(order) + 1
            parent = getattr(self.context, "__parent__", None)
            if parent and len(parent.section):
                section = "{}.{}".format(parent.section, order)
            else:
                section = "{}".format(order)
            self.context.section = section
            return section + ": "
        return ""

    def sortedItems(self):
        sorter = IArticleSorter(self.context)
        return sorter.sortedItems()

class PreviousLevelMenuEntry(UtilItem):
    '''  Make a button to navigate to the introduction
    '''
    grok.context(IndexPage)
    title = mtitle = u'Up a level'
    link = u'..'
    mclass = 'nav buttons'
    def condition(self):
        self.title = self.context.__parent__.navTitle
        self.image = self.static['up.png']
        return True

class IndexButton(UtilItem):
    '''  A menu item to navigate to the index
    '''
    grok.context(ISiteRoot)
    grok.require('zope.Public')
    grok.order(-1)
    title = u'Index'
    link = 'indexpage'
    mclass = 'nav buttons'

