'''
    This application implements a wiki-like interface to write up documents
    about the grok web framework.  It packs in as many concepts as it can to
    demonstrate how to use Grok.
'''
import grok
from interfaces import IArticle, IArticleSorter, ISiteRoot
from permissions import Editing
from users import IUsers
from layout import ILayout, Navigation, Content
from menu import UtilItem
from urllib import quote_plus
import forms

class ArticleContainer(grok.Container):
    '''  An article container is a generic container (a dict-like object) which
        also provides a sorter for the articles it contains    '''
    prev = None
    next = None
    attachments = None

    grok.traversable('attachments')
    grok.traversable('sorter')

    def getArticleId(self):  # Only used in producing a book
        section = getattr(self, "section", None)
        if section is None:
            return "sn_main"
        else:
            return u'sn_'+section.replace('.', '_')

    def sorter(self):
        '''  Find an adapter which adapts self to an IArticleSorter, and return an instance
        '''
        return IArticleSorter(self)

class NoobsArticle(ArticleContainer):
    ''' Contains the detail for a navigable article in the site
    '''
    grok.implements(IArticle, ILayout)
    title = u''
    navTitle = u''
    text = u''

class Grok4Noobs(grok.Application, ArticleContainer):
    ''' The Grok4Noobs application is a content wiki-like application which contains examples
        explaining how to use the Grok framework for trivial and non-trivial applications.
    '''
    grok.implements(IArticle, ILayout, ISiteRoot)
    title = u'A gentle introduction to using the Grok web framework'
    navTitle = u'Introduction'
    text = u''

    grok.traversable('attachments')
    grok.traversable('sorter')
    grok.traversable('users')

    def users(self):
        sm = self.getSiteManager()
        if 'users' in sm:
            return IUsers(sm['users'])


class TextViewlet(grok.Viewlet):
    ''' Render the article content
    '''
    grok.context(IArticle)
    grok.viewletmanager(Content)


class PreviousLevelMenuEntry(UtilItem):
    '''  A menu item for articles with parent articles. IOW NoobsArticle
    '''
    grok.context(NoobsArticle)
    grok.order(-4)
    title = mtitle = u'Up a level'
    link = u'..'
    mclass = 'nav buttons'
    def condition(self):
        self.title = self.context.__parent__.navTitle
        self.image = self.static['up.png']
        return True

class PrevMenuEntry(UtilItem):
    '''  A menu item for previous articles in the list
    '''
    grok.context(NoobsArticle)
    grok.order(-3)
    title = mtitle = u'Prev Page'
    mclass = 'nav buttons'
    @property
    def link(self):
        title = quote_plus(self.context.prev)
        return self.context.__parent__[title]
    def condition(self):
        if getattr(self.context, 'prev', None) is not None:
            self.title = self.context.prev
            self.image = self.static['left.png']
            return True

class NextMenuEntry(UtilItem):
    '''  A menu item for articles next in the list
    '''
    grok.context(NoobsArticle)
    grok.order(-2)
    title = mtitle = u'Next Page'
    mclass = 'nav buttons'
    @property
    def link(self):
        title = quote_plus(self.context.next)
        return self.context.__parent__[title]
    def condition(self):
        if getattr(self.context, 'next', None) is not None:
            self.title = self.context.next
            self.image = self.static['right.png']
            return True

class SorterLink(UtilItem):
    ''' A conditional menu item which shows for articles with more than one child
    '''
    grok.context(IArticle)
    grok.require(Editing)
    grok.order(-1)
    title = u'Change menu order'
    link = u'sorter'
    mclass = 'nav buttons'

    def condition(self):
        return len(self.context) > 1

class DeleteButton(grok.Viewlet):
    '''  Renders a delete button into the navigation area
    '''
    grok.viewletmanager(Navigation)  # Render into the Navigation area
    grok.context(NoobsArticle)       # for normal articles
    grok.require(Editing)

class Edit(forms.EditForm):
    '''  Renders the article editor. This includes the tinyMCE HTML editor
    '''
    grok.context(IArticle)
    grok.require(Editing)

    def hidden(self):  # persists the request 'edit' form variable
        return [dict(name='edit', value='')]

    def setUpWidgets(self, ignore_request=False):
        super(Edit, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth=50
        self.widgets['navTitle'].displayWidth=12

    @grok.action(u'Change this page')
    def changeItem(self, **data):
        title = data['navTitle']
        if self.context.navTitle==title:
            self.applyData(self.context, **data)
            self.redirect(self.url(self.context))
        else:   # to change it we must create new and remove old
            ntitle = quote_plus(title)
            self.context.__parent__[ntitle] = self.context
            navTitle = quote_plus(self.context.navTitle)
            del self.context.__parent__[navTitle]

            self.applyData(self.context, **data)
            self.redirect(self.url(self.context.__parent__[ntitle]))

class Add(forms.AddForm):
    ''' Renders the article add form, which is similar to the edit form
    '''
    grok.context(IArticle)
    form_fields = grok.Fields(IArticle).omit('text')
    grok.require(Editing)

    def hidden(self): # persists the request 'add' form variable
        return [dict(name='add', value='')]

    def setUpWidgets(self, ignore_request=False):
        super(Add, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth=50
        self.widgets['navTitle'].displayWidth=12

    @grok.action(u'Add this page')
    def addItem(self, **data):
        ntitle = quote_plus(data['navTitle'])
        item = self.context[ntitle] = NoobsArticle()
        self.applyData(item, **data)
        self.redirect(self.url(self.context))

class Delete(forms.EditForm):
    '''  A Delete confirmation form and action
    '''
    grok.context(NoobsArticle)       # for normal articles
    form_fields = grok.AutoFields(NoobsArticle).omit('text')
    grok.require(Editing)

    def setUpWidgets(self, ignore_request=False):
        self.form_fields['title'].field.readonly = True
        self.form_fields['navTitle'].field.readonly = True
        super(Delete, self).setUpWidgets(ignore_request)
        self.form_fields['title'].field.readonly = False
        self.form_fields['navTitle'].field.readonly = False


    def hidden(self): # persists the request 'delete' form variable
        return [dict(name='delete', value='')]

    @grok.action(u'Delete this page (cannot be undone)')
    def delPage(self):
        title = self.context.navTitle
        parent = self.context.__parent__
        url = self.url(parent, name='deleting', data={'dtitle':title})
        self.redirect(url)

class Deleting(grok.View):
    grok.context(IArticle)       # Container for deleted item
    grok.require(Editing)

    def render(self, dtitle=None):
        if dtitle is not None:
            dtitle = quote_plus(dtitle)
            if dtitle in self.context:
                try:
                    del self.context[dtitle]
                except Exception, e:
                    print 'There was an error deleting %s:\n\t%s' % (dtitle, str(e))
                    raise e
        self.redirect(self.url(self.context))

