import grok

from interfaces import IArticle, IArticleSorter, Interface
from urllib import quote_plus
from resource import textLight
from zope.component.interfaces import Attribute


class Bootstrap(grok.IDefaultBrowserLayer):
    '''  Defines the 'bootstrap' layer
    '''
    grok.skin('bootstrap')


class INavItem(Interface):
    '''  A navigation item
    '''
    id    = Attribute(u'id')     # The label for the menu item
    title = Attribute(u'title')  # The label for the menu item
    items = Attribute(u'items')  # May have sub items in the dropdown


class ArticleNavItem(grok.Adapter):
    ''' Adapts an IArticle to provide an INavItem
    '''
    grok.context(IArticle)
    grok.implements(INavItem)

    def __init__(self, context):
        ''' Gets id, title and items from the IArticle
        '''
        super(ArticleNavItem, self).__init__(context)
        self.id = quote_plus(context.navTitle)
        self.title = context.navTitle
        self.items = []
        sorter = IArticleSorter(self.context)
        for a in sorter.sortedItems():
            self.items.append({'link':  quote_plus(a.navTitle),
                               'title': a.navTitle})


class NavBar_Item(grok.View):
    ''' Represents a single item on the navigation bar
    '''
    grok.context(INavItem)
    grok.layer(Bootstrap)

    def link(self, sub=False):  # Return a url for the article
        if sub: return self.url(self.context.context, name=sub)
        return self.url(self.context.context)


class NavBar_Header(grok.View):
    '''  This view renders as the site header item
    '''
    grok.context(IArticle)
    grok.layer(Bootstrap)

    def hRef(self):  # Returns site root URL
        return self.url(grok.getApplication())


class NavBar(grok.View):
    '''  This view renders as the fixed navigation bar
    '''
    grok.context(IArticle)
    grok.layer(Bootstrap)

    def navItems(self):
        ''' Returns navigation bar items for current IArticle
        '''
        try:
            sorter = IArticleSorter(self.context.__parent__)
            for a in sorter.sortedItems():
                item = NavBar_Item(INavItem(a), self.request)
                yield item()
        except:
            item = NavBar_Item(INavItem(self.context), self.request)
            yield item()


class BreadCrumbs(grok.View):
    '''  Renders the breadcrumbs
    '''
    grok.context(IArticle)
    grok.layer(Bootstrap)

    def crumbs(self):
        ''' Walk the tree up from current context, build crumbs.
        '''
        app = grok.getApplication()
        cl  = []
        curr = self.context

        while curr != app:
            cl.append(curr)
            curr = curr.__parent__
        cl.append(curr)
        cl.reverse()
        return ({'title': a.navTitle,
                 'hRef':self.url(a),
                 'isLast':a==self.context} for a in cl)


class Index(grok.View):
    '''  Renders the main site index
    '''
    grok.context(IArticle)
    grok.layer(Bootstrap)

    editing = False   # content viewlet manager needs these flags
    adding = False
    deleting = False
    viewing = True

    def update(self): # require 'light' text box styling
        textLight.need()

