import grok
from zope.component import Interface, getMultiAdapter
from layout import ILayout, Content
from zope.schema import List, Object, TextLine, Password, Choice
from zope.pluggableauth.plugins.principalfolder import IInternalPrincipal, IInternalPrincipalContainer
from zope.pluggableauth.plugins.principalfolder import InternalPrincipal
from menu import MenuItem
import permissions as gfn
import resource as rc

BATCH_SIZE = 10

#____________________________________________________________________________________
class IAccount(Interface):
    login       = TextLine(title=u'Login', description=u'A login/user Name')
    title       = TextLine(title=u"Title", description=u"Provides a title for the principal.", required=False)
    password    = Password(title=u"Password", description=u"The password for the principal.", required=False)
    role        = Choice(title=u'Role', vocabulary=u'gfn.AccountRoles',
                         description=u'The kind role the user plays',
                         default='gfn.Visitor')

#_____________________________________________________________
class Account(grok.Model):
    grok.implements(IAccount)
    login = u''
    password = u''
    title = u''
    role = 'gfn.Visitor'

    def __init__(self, user=None):
        self.user = user
        if user:
            self.login = user.login
            self.password = user.password
            self.title = user.title
            self.role = getattr(user, 'role', self.role)

#_____________________________________________________________
class InternalPrincipalAccount(grok.Adapter):
    grok.context(IInternalPrincipal)
    grok.implements(IAccount)

    def __new__(cls, principal):
        return Account(principal)

#____________________________________________________________________________________
class IUsers(Interface):
    """ A user management interface
    """
    users    = List(title=u'Accounts', required=True,
                    value_type=Object(title=u"User", schema=IAccount))
    search   = TextLine(title=u'Search:', required=False, default=u'')

    def nItems(self):
        ''' Returns the number of items in the complete search result '''

    def fromItem(self, setPos=None):
        ''' Optionally sets and returns the position from which to display items '''


#_____________________________________________________________________________________
class Users(grok.Model):
    """ The list of users matching the _search filter is cached in _accounts.  We limit
        the number of cached users to BATCH_SIZE, also the number of users actually
        displayed at any time.  The page offset is counted from <pos>.
        The principals folder for the site looks somewhat like a dict, and is passed
        as an argument when instantiating this object.  We keep a reference in
        <principals>.
        The users property setter takes a look at the cached list and compares the new
        list.  From this it determines the set of deleted, inserted or changed items,
        allowing us to update several principals details at once.
    """
    grok.implements(ILayout, IUsers)
    title      = u'User Management'
    principals = {}
    pos        = 0
    _accounts  = []
    _search    = None

    def __init__(self, principals):
        self.principals = principals
        self.do_search()

    def do_search(self):
        p = self.principals
        gen = p.search({'search':self.search or ''}, start=self.pos, batch_size=BATCH_SIZE)
        self._accounts = [IAccount(p[p.principalInfo(i).login]) for i in gen]

    @property
    def search(self):
        return self._search
    @search.setter
    def search(self, value):
        if self._search != value:
            self._search = value
            self.do_search()

    @property
    def users(self):
        return self._accounts
    @users.setter
    def users(self, values):
        vdict = {account.login:account for account in values}
        a = set([account.login for account in self._accounts])
        v = set([account.login for account in values])
        deleted = a.difference(v)
        added = v.difference(a)
        updated = a.intersection(v)
        p = self.principals

        for user in deleted:
            del p[user]
        for user in added:
            account = vdict[user]
            if account.login:
                account = vdict[user]
                p[user] = InternalPrincipal(login=account.login, title=account.title, password=account.password)
                p[user].role = account.role
        for user in updated:
            u = p[user]
            account = vdict[user]
            if account.login and u.login != account.login: u.login=account.login
            u.title=account.title or ''
            if account.password: u.password=account.password
            u.role = account.role
        self.do_search()

    @property
    def nItems(self):
        ''' Returns the number of items in the complete search result '''
        return len(list(self.principals.search({'search':self._search or ''})))

    def fromItem(self, setPos=None):
        ''' Optionally sets and returns the position from which to display items '''
        if setPos: self.pos = setPos
        return self.pos

#____________________________________________________________________________________
from zope.formlib.widget import CustomWidgetFactory
from zope.formlib.objectwidget import ObjectWidget
from zope.formlib.sequencewidget import ListSequenceWidget

#_____________________________________________________________
def AccountWidget():
    '''  An ObjectWidget produces a 'sub-form' for an object, in this case an Account.  If our
           data field happens to be a list of accounts, we can wrap the account widget in a
           list sequence widget.  The CustomWidgetFactory produces widgets by calling the
           appropriate factory with the configured arguments.
    '''
    ow = CustomWidgetFactory(ObjectWidget, Account)    # Show accounts in the list as object widgets (sub-forms)
    return CustomWidgetFactory(ListSequenceWidget, subwidget=ow)

#_____________________________________________________________
class EditPrincipalForm(grok.EditForm):
    ''' A form that allows creation, editing and deletion of principals. '''
    grok.context(Users)          # view available as URL: 'appname/editprincipal'

    grok.require(gfn.Administering)    # Permission requirement
    form_fields = grok.Fields(IUsers)  # Present a search form
    form_fields['users'].custom_widget = AccountWidget()  # The current list of principals

    def update(self):
        rc.tabular.need()

    @grok.action(u"Search")
    def search(self, **data):
        self.context.search = data['search']

    @grok.action(u"Apply")
    def apply(self, **data):
        self.applyData(self.context, **data)

    @grok.action(u"First Page")
    def firstPage(self, **data):
        self.context.fromItem(0)

    @grok.action(u"Next Page")
    def nextPage(self, **data):
        if self.context.fromItem() + BATCH_SIZE < self.context.nItems():
            self.context.fromItem(self.context.fromItem()+BATCH_SIZE)

    @grok.action(u"Prev Page")
    def prevPage(self, **data):
        if self.context.fromItem() - BATCH_SIZE >= 0:
            self.context.fromItem(self.context.fromItem()-BATCH_SIZE)
        else:
            self.context.fromItem(0)

    @grok.action(u"Last Page")
    def lastPage(self, **data):
        n = self.context.fromItem() / BATCH_SIZE
        if n % BATCH_SIZE == 0: n -= 1
        if n < 0: n = 0
        self.context.fromItem(n * BATCH_SIZE)

#_____________________________________________________________________________________
class EditPrincipals(grok.Viewlet):
    """ Renders the user management interface within the Content Area
    """
    grok.context(Users)
    grok.require(gfn.Administering)
    grok.viewletmanager(Content)


class EditPrincipalsNoAccess(grok.Viewlet):
    """  Renders in the event where the user cannot access the management interface
    """
    grok.context(Users)
    grok.require('zope.Public')
    grok.viewletmanager(Content)

    def render(self):
        i = self.request.interaction
        if not i.checkPermission('gfn.administering', self.context):
            login = getMultiAdapter((self.context, self.request), name='login')
            return login()
        return ''

#_____________________________________________________________________________________
class PrincipalUsers(grok.Adapter):
    """ Adapts our PrincipalFolder to a user management interface
    """
    grok.context(IInternalPrincipalContainer)
    grok.implements(IUsers)

    def __new__(cls, principals):
        return Users(principals)

#_____________________________________________________________________________________
class BackButtonMenuEntry(MenuItem):
    '''  A menu item for articles with parent articles. IOW NoobsArticle
    '''
    grok.context(Users)
    title = u'Back to Main'
    link = u'..'
    mclass = 'nav buttons'

