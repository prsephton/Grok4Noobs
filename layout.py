import grok
from resource import style, favicon, tinymce, textdivs, nolabels
from interfaces import Interface
from zope.session.interfaces import ISession
from urllib import quote_plus
class ILayout(Interface):
    ''' This is an interface for the main site layout

            All a model has to do to inherit the Layout view, is to say that it
            implements this interface.

            The Layout view defines a basic HTML document shell consisting of a
            number of parts; the viewlet managers below are place holders for your
            site implementation to fill in the blanks.  What goes in those sections
            will depend on the context.
    '''

# We specify the renderable areas of the page as viewlet managers.
# These areas will always render for instances of ILayout
class MastHead(grok.ViewletManager):
    grok.context(ILayout)

class AuthSection(grok.ViewletManager):
    grok.context(ILayout)

class Navigation(grok.ViewletManager):
    grok.context(ILayout)

class Content(grok.ViewletManager):
    grok.context(ILayout)

class SideBar(grok.ViewletManager):
    grok.context(ILayout)

class Footer(grok.ViewletManager):
    grok.context(ILayout)

# We define a few viewlets which always render for specific areas
# of the page.  These render because the template for the Layout
# view (below) does tal:content='structure provider:masthead' etc.
# The appropriate viewletmanager collects up all the viewlets
# registered for itself and renders them.  No magic involved.
class MastHeadViewlet(grok.Viewlet):
    ''' Render layout masthead
    '''
    grok.context(ILayout)
    grok.viewletmanager(MastHead)

class FooterViewlet(grok.Viewlet):
    ''' Render the layout footer
    '''
    grok.context(ILayout)
    grok.viewletmanager(Footer)


# Finally, the page layout itself is a view which renders the html
# skeleton.  It also includes any resources such as css and javascript
# which would be required by the content.
class Layout(grok.View):
    ''' Renders the base HTML page layout for the site.
        Since for this site, editing, adding and deleting are
        going to be common actions, we provide for these actions as
        URL arguments.  Another approach would have been to use
        traversers, and make the operations part of the URL itself.
    '''
    grok.context(ILayout)
    grok.name('index')
    grok.require('zope.Public')

    editing = False
    adding = False
    deleting = False
    moving = False
    viewing = True

    def process_moving(self, move, moved, cancel):
        moving = False
        session = ISession(self.request)['package.gfn']
        if moved is not None and 'moving' in session:
            item = session['moving']
            nTitle = quote_plus(item.navTitle)
            self.context[nTitle] = item
            del session['moving']
        elif move is not None:
            moving = self.context.navTitle
            nTitle = quote_plus(moving)
            cont = self.context.__parent__
            session['moving'] = self.context
            del cont[nTitle]
            self.redirect(self.url(cont))
        elif 'moving' in session:
            if cancel is not None:
                del session['moving']
            else:
                moving = self.context.navTitle
        return moving

    def update(self, edit=None, add=None, delete=None, move=None, moved=None,
               nomce=None, cancel=None):
        self.editing = edit is not None
        self.adding = add is not None
        self.deleting = delete is not None
        self.moving = self.process_moving(move, moved, cancel)
        self.viewing = not (self.editing or self.adding or self.deleting or self.moving)
        style.need()
        favicon.need()
        nolabels.need()
        if nomce is None:  # Switch includes or omits tinyMCE
            tinymce.need()
        textdivs.need()
