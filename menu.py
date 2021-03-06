import grok
from layout import ILayout, Navigation
from interfaces import IArticle, IArticleSorter


class Menu(grok.Viewlet):
    grok.viewletmanager(Navigation)  # Render into the Navigation area
    grok.context(ILayout)            # for all instances of ILayout

    def isEditable(self):
        if not hasattr(self.context, 'navTitle'): return False
        if self.context.navTitle is None: return False
        i = self.request.interaction
        if not i.checkPermission('gfn.editing', self.context):
            return False
        return True


class MenuItems(grok.ViewletManager):
    grok.context(ILayout)            # This will be a list of <li /> elements


class UtilItems(grok.ViewletManager):
    grok.context(ILayout)            # As with the normal menu items, but utilities


class MenuItem(grok.Viewlet):
    ''' A base class for ad-hoc navigation menu items.
    '''
    grok.viewletmanager(MenuItems)   # Render into the MenuItems area
    grok.context(ILayout)            # for all instances of ILayout
    grok.baseclass()                 # This is not a concrete class

    title = u''
    link  = u''
    mclass = ''
    mtitle = ''
    image = None
    
    def condition(self):
        return True

    def selected(self):
        return self.title == getattr(self.context, 'navTitle', None)

    def href(self):
        return self.view.url(self.link)

    def render(self):
        if self.condition():
            img = ''
            if self.image is not None:
                img = '''<img src="{}" />'''.format(self.image)
                
            return ("""<li class="menuItem%s%s" title="%s"><a href="%s">%s%s</a></li>""" %
                    (' selected' if self.selected() else '',
                     ' %s'%self.mclass if len(self.mclass) else '', self.mtitle,
                     self.href(), img, self.title))
        else:
            return ''

class UtilItem(MenuItem):
    ''' A utility menu item
    '''
    grok.viewletmanager(UtilItems)   # Render into the MenuItems area


class ContainerMenu(grok.Viewlet):
    ''' Render the items contained inside self.context.  The container menu must
        always be rendered in the same order
    '''
    grok.viewletmanager(MenuItems)   # Render into the MenuItems area
    grok.context(IArticle)            # for all instances of ILayout

    def sortedItems(self):
        sorter = IArticleSorter(self.context)
        return sorter.sortedItems()
