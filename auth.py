#________________________________________________________________
# Authentication based upon PAU.
# BALogout  link to https://log:out@example.com/.

import grok
from grok4noobs import Grok4Noobs
from sitelocal import ISiteLocalInstaller

from zope import schema
from zope.component import Interface, queryUtility, getUtilitiesFor, IComponentLookup
from zope.authentication.interfaces import IAuthentication, IUnauthenticatedPrincipal, ILogout
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from zope.pluggableauth import PluggableAuthentication

from zope.pluggableauth.interfaces import ICredentialsPlugin, IAuthenticatorPlugin
from zope.pluggableauth.plugins.session import SessionCredentialsPlugin
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder, InternalPrincipal

from permissions import Administering

from layout import ILayout, AuthSection
import forms

#_____________________________________________________________________________________
def isLoggedIn(request):
    ''' Convenience function tells us if we are logged in
    '''
    return not IUnauthenticatedPrincipal.providedBy(request.principal)


#_____________________________________________________________________________________
class ILoginForm(Interface):
    ''' Our login form implements login and password schema fields.
    '''
    login = schema.BytesLine(title=u'Username', required=True)
    password = schema.Password(title=u'Password', required=True)


#_____________________________________________________________________________________
class Login(forms.AddForm):
    ''' This is our login form.  It will render when and where we need it.
    '''
    grok.context(Interface)
    grok.require('zope.Public')

    form_fields = grok.Fields(ILoginForm)

    @grok.action('login')
    def handle_login(self, **data):
        ''' If the authentication plugins are not yet installed, install them
        '''
        pau = queryUtility(IAuthentication)
        if pau is None or type(pau) is not PluggableAuthenticatorPlugin:
            installer = ISiteLocalInstaller(grok.getSite())

            installer.registerUtility(PluggableAuthenticatorPlugin,
                                      provided=IAuthentication,
                                      name_in_container='pau')

            installer.registerUtility(AuthenticatorPlugin,
                                      provided=IAuthenticatorPlugin,
                                      name='users')
            pau = queryUtility(IAuthentication)
            if pau is not None: pau.authenticate(self.request)
            self.redirect(self.url(self.context, data=data))


#_____________________________________________________________________________________
class Logout(grok.View):
    ''' We can call this view to log out from the cookie based login session.
    '''
    grok.context(Interface)
    grok.require('zope.Public')

    def update(self):
        if isLoggedIn(self.request):
            auth = queryUtility(IAuthentication)
            ILogout(auth).logout(self.request)

    def render(self):
        self.redirect(self.url(self.context))


#_____________________________________________________________________________________
class Status(grok.Viewlet):
    ''' Renders the login form in Authentication area for layout
    '''
    grok.context(ILayout)
    grok.viewletmanager(AuthSection)
    grok.require('zope.Public')

    def loggedIn(self):
        ''' Tries to authenticate if not already authenticated. Returns status.
        '''
        if not isLoggedIn(self.request):
            auth = queryUtility(IAuthentication)
            if auth is not None:
                auth.authenticate(self.request)
        return isLoggedIn(self.request)

    def greeting(self):
        ''' Returns a greeting depending on the time of day
        '''
        from datetime import datetime as dt
        hour = dt.now().hour
        tod = "Morning" if hour < 12 else "Afternoon" if hour < 18 else "Evening"
        return "Good %s, %s" % (tod, self.request.principal.title)

    def zopeLogin(self):
        ''' Zope management by default uses a Basic Auth login with a 'zope' prefix
        '''
        if self.loggedIn():
            ns = self.request.principal.id.split('.')
            if len(ns) > 1: ns = ns[0]
            if ns=='zope': return True
        return False

    def logoutLink(self):
        ''' If this is a Basic Auth login, redirect to challenge site,
            otherwise to our own logout view
        '''
        if self.zopeLogin():
            site = self.view.url("/").split("//")[1].split("/")[0]
            return "http://log:out@%s/." % site
        else:
            return self.view.url(self.context, "logout")


#_____________________________________________________________________________________
class PluggableAuthenticatorPlugin(PluggableAuthentication, grok.LocalUtility):
    ''' The Pluggable Authentication Utility mechanism provided by the
        Zope Toolkit is very flexible.  It allows registration of utilities
        which retrieve credentials from the request, or provide authentication.
        One way to use it, is to use component lookup via the ZCA by name.
        Another way is to simply include instances of the plugins directly
        inside the PluggableAuthentication, as it is a persistent container
        in it's own right.
    '''
    grok.provides(IAuthentication)
    grok.name('pau')

    def __init__(self, *args, **kwargs):
        super(PluggableAuthenticatorPlugin, self).__init__(*args, **kwargs)
        self.credentialsPlugins = ['credentials']       # Name of utility for ICredentialsPlugin
        self.authenticatorPlugins = ['users']           # Name of utility for IAuthenticatorPlugin
        self.prefix = 'gfn.'


#_____________________________________________________________________________________
class PluginSiteFinder(grok.Adapter):
    ''' To allow the our PluggableAuthentication to find the site where our
        plugins reside, the utility is adapted internally to a IComponentLookup.
        If we are installing the local utility manually, we need to provide
        an adapter ourselves.
    '''
    grok.context(PluggableAuthenticatorPlugin)
    grok.provides(IComponentLookup)

    def __new__(cls, context):
        site = grok.getSite()
        return site.getSiteManager()


#_____________________________________________________________________________________
class AuthenticatorPlugin(PrincipalFolder, grok.LocalUtility):
    ''' The Zope toolkit provides a few folder based authenticator plugins.
        Here, we build a PAU plugin as a local utility based on the PrincipalFolder,
        which already implements IAuthenticatorPlugin.
        To use an external authenticator, eg. LDAP, one would implement the
        IAuthenticatorPlugin interface directly.
    '''
    grok.provides(IAuthenticatorPlugin)
    grok.name('users')

    def __init__(self, *args, **kwargs):
        ''' Create an administrator with default login and password
        '''
        super(AuthenticatorPlugin, self).__init__(*args, **kwargs)

        su = InternalPrincipal(login='admin', password='Admin', title=u'Administrator', 
                               description=u'The SuperUser')
        self['admin'] = su

        roleMgr = IPrincipalRoleManager(grok.getSite())
        for uid, _setting in roleMgr.getPrincipalsForRole('gfn.Administrator'):
            roleMgr.unsetRoleForPrincipal('gfn.Administrator', 'gfn.'+uid)

        uid = self.getIdByLogin('admin')
        roleMgr.assignRoleToPrincipal('gfn.Administrator', 'gfn.'+uid)


#_____________________________________________________________________________________
class CredentialsPlugin(grok.GlobalUtility, SessionCredentialsPlugin):
    ''' Define the credentials plugin and challenge form fields
    '''
    grok.provides(ICredentialsPlugin)
    grok.name('credentials')

    loginpagename = 'login'
    loginfield = 'form.login'
    passwordfield = 'form.password'


#_____________________________________________________________________________________
# Calling this view will reinstall our authenticator and PAU.
class InstallAuth(grok.View):
    ''' If we call this view, we want to reinstall authentication
    '''
    grok.context(Grok4Noobs)
#    grok.require('zope.Public')
    grok.require(Administering)

    def update(self):
        # Register the PAU as a local utility
        installer = ISiteLocalInstaller(self.context)

        installer.registerUtility(PluggableAuthenticatorPlugin,
                                  provided=IAuthentication,
                                  name_in_container='pau')

        installer.registerUtility(AuthenticatorPlugin,
                                  provided=IAuthenticatorPlugin,
                                  name='users')

    def render(self):
        # Test that our installation was successful
        pau = queryUtility(IAuthentication)
        if pau is None or type(pau) is not PluggableAuthenticatorPlugin:
            if pau is not None:
                st = "PAU not installed correctly: %s" % pau
                utilities = getUtilitiesFor(IAuthentication)
                st += "\n Available utilities are: %s" % [u for u in utilities]
                return st
            else:
                return "PAU Utility not found"

        st = ('Success: Credentials plugins= %s; Authenticator plugins= %s' %
                (pau.credentialsPlugins, pau.authenticatorPlugins))
        roleMgr = IPrincipalRoleManager(self.context)
        p = roleMgr.getPrincipalsForRole('gfn.Administrator')
        st += "\n  Administrators: %s" %p
        for ut in pau.credentialsPlugins:
            if queryUtility(ICredentialsPlugin, name=ut) is None:
                st += '\n     Could not find credentials plugin for %s' % ut
        for ut in pau.authenticatorPlugins:
            if queryUtility(IAuthenticatorPlugin, name=ut) is None:
                st += '\n     Could not find authenticator plugin for %s' % ut

        return st

