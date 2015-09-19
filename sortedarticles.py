'''
    This module deals with ordering articles and managing article order.
    Grok does include a OrderedContainer type which could have formed
    a better basis for our IArticle implementation, but the code below
    demonstrates numerous features quite well.
'''
import grok

from interfaces import IArticle, IArticleSorter
from layout import ILayout, Content
from resource import ordermenu
from menu import MenuItem

class SorterBackLink(MenuItem):
    grok.context(IArticleSorter)
    grok.order(0)
    title = u'Back to article'
    link = u'..'
    mclass = 'nav buttons'

class SorterAccept(MenuItem):
    grok.context(IArticleSorter)
    grok.order(1)
    title = u'Accept this menu order'
    link = u''
    mclass = 'setItemOrder buttons'

class Sorter(grok.Model):
    ''' Implements an order for items in a normal grok.Container.  Not terribly efficient
        since it sorts every time we extract the items, but there won't really be that
        many items anyway, and this demonstrates a transient object.
    '''
    grok.implements(IArticleSorter, ILayout)
    grok.provides(IArticleSorter)
    title = u'Ordering the navigation menu'

    def __init__(self, context):
        self.context = context
    def renumber(self, items):
        prev = None
        for i, ob in enumerate(items):
            if prev is not None:             # Simultaneously build a doubly linked list
                prev.next = ob.navTitle      # while assigning an object order
                ob.prev = prev.navTitle
            else:
                ob.prev = None
            ob.next = None
            ob.order = i  # Re-assign order numbers
            prev = ob
    def itemKey(self, value):
        return getattr(value, 'order', 9999)  # by default insert items at the end
    def sortedItems(self):
        items = [v for v in self.context.values()]
        items.sort(key=lambda value: self.itemKey(value))
        self.renumber(items)   # We ensure a renumber of ordered items every time we render
        return items

class LayoutArticleSorter(grok.Adapter):
    ''' Adapts an IArticle and returns an IArticleSorter.  Uses a factory pattern to return
        an instance of a Sorter.  Since the Sorter implements ILayout, the site's index view
        will be rendered as the default view for such objects.  This means that our viewlet
        below will be called for the Content area.
    '''
    grok.context(IArticle)
    grok.implements(IArticleSorter)

    def __new__(cls, context):
        return Sorter(context)

class ReOrderViewlet(grok.Viewlet):
    ''' Renders an interface for re-ordering items in the IArticle container
    '''
    grok.context(IArticleSorter)
    grok.viewletmanager(Content)

    items = []
    def update(self):
        ordermenu.need()                             # Include Javascript
        self.items = self.context.sortedItems()      # Get the items

class OrderSetter(grok.JSON):
    '''  Any method declared below becomes a JSON callable
    '''
    grok.context(IArticleSorter)

    def setOrder(self, new_order=None):
        '''  Accepts an array of navTitle elements in the required order.
            Normally, we would not have to use JSON.stringify and
            simplejson.loads on arguments, but array arguments get
            names which are not compatible with Python.
        '''
        from simplejson import loads
        from urllib import quote_plus

        if new_order is not None:
            new_order = loads(new_order)   # Unescape stringified json
            container = self.context.context
            for nth, navTitle in enumerate(new_order):
                container[quote_plus(navTitle)].order = nth
            return 'ok'
