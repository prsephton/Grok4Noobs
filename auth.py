#________________________________________________________________
# Authentication based upon PAU.
# BALogout  link to https://log:out@example.com/.

import grok
from grok4noobs import Grok4Noobs
from sitelocal import ISiteLocalInstaller

from zope import schema
from zope.component import Interface, queryUtility, getUtilitiesFor
from zope.authentication.interfaces import IAuthentication, IUnauthenticatedPrincipal, ILogout
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder, InternalPrincipal

from zope.pluggableauth.interfaces import ICredentialsPlugin, IAuthenticatorPlugin
from zope.pluggableauth.plugins.session import SessionCredentialsPlugin
from permissions import Administering

from layout import ILayout, AuthSection
import forms

#_____________________________________________________________________________________
# Define the credentials plugin and challenge form
class CredentialsPlugin(grok.GlobalUtility, SessionCredentialsPlugin):
    grok.provides(ICredentialsPlugin)
    grok.name('credentials')

    loginpagename = 'login'
    loginfield = 'form.login'
    passwordfield = 'form.password'


#_____________________________________________________________________________________
# Our login form implements login and password schema fields.
class ILoginForm(Interface):
    login = schema.BytesLine(title=u'Username', required=True)
    password = schema.Password(title=u'Password', required=True)


#_____________________________________________________________________________________
# Convenience function tells us if we are logged in
def loggedIn(request):
    return not IUnauthenticatedPrincipal.providedBy(request.principal)


#_____________________________________________________________________________________
# This is our login form.  It will render when and where we need it.
class Login(forms.AddForm):
    grok.context(Interface)
    grok.require('zope.Public')

    form_fields = grok.Fields(ILoginForm)

    @grok.action('login')
    def handle_login(self, **data):
        auth = queryUtility(IAuthentication)
        auth.authenticate(self.request)
        self.redirect(self.url(self.context))
#        self.redirect(self.request.form.get('camefrom', ''))


#_____________________________________________________________________________________
# We can call this view to log out.
class Logout(grok.View):
    grok.context(Interface)
    grok.require('zope.Public')

    def update(self):
        if loggedIn(self.request):
            auth = queryUtility(IAuthentication)
            ILogout(auth).logout(self.request)

    def render(self):
        return '<p>You have been logged out</p>'

#_____________________________________________________________________________________
class Status(grok.Viewlet):
    ''' Auth area for layout
    '''
    grok.context(ILayout)
    grok.viewletmanager(AuthSection)
    grok.require('zope.Public')

    def loggedIn(self):
        return loggedIn(self.request)

    def greeting(self):
        from datetime import datetime as dt
        hour = dt.now().hour
        tod = "Morning" if hour < 12 else "Afternoon" if hour < 18 else "Evening"
        return "Good %s, %s" % (tod, self.request.principal.title)

    def zopeLogin(self):
        if self.loggedIn():
            ns = self.request.principal.id.split('.')
            if len(ns) > 1: ns = ns[0]
            if ns=='zope': return True
        return False

    def logoutLink(self):
        if self.zopeLogin():
            site = self.view.url("/").split("//")[1].split("/")[0]
            return "http://log:out@%s/." % site
        else:
            return self.view.url(self.context, "logout")

#_____________________________________________________________________________________
# Install a Pluggable Authentication Utility as a local utility in the
# Grok4Noobs application.  We have to jump through a few hoops if we want to
# support installing local utilities without reinstalling our application.
def setup_authentication(ob):
    """ Set up pluggable authentication utility.
    """
    ob.credentialsPlugins = ['credentials']       # Name of utility for ICredentialsPlugin
    ob.authenticatorPlugins = ['users']           # Name of utility for IAuthenticatorPlugin
    ob.prefix = 'gfn.'


#_____________________________________________________________________________________
# Calling this view will reinstall our authenticator and PAU.
class InstallAuth(grok.View):
    ''' If we call this view, we want to reinstall authentication
    '''
    grok.context(Grok4Noobs)
    grok.require('zope.Public')
#    grok.require(Administering)

    def update(self):
        # Install a new principals folder and provide it as a global utility
        if not hasattr(self.context, 'principals'):
            self.context.principals = PrincipalFolder(u'principal.')
            # Register principals folder as a local utility

        # Install a default superuser
            if 'admin' in self.context.principals: del self.context.principals['admin']
            su = InternalPrincipal(login='admin', password='Admin', title=u'Administrator', description=u'The SuperUser')
            self.context.principals['admin'] = su
            roleMgr = IPrincipalRoleManager(self.context)
            for uid, _setting in roleMgr.getPrincipalsForRole('gfn.Administrator'):
                roleMgr.unsetRoleForPrincipal('gfn.Administrator', uid)
            uid = self.context.principals.getIdByLogin('admin')
            roleMgr.assignRoleToPrincipal('gfn.Administrator', 'gfn.'+uid)

            # Register the PAU as a local utility
            installer = ISiteLocalInstaller(self.context)
            installer.registerUtility(PluggableAuthentication,
                                      provided=IAuthentication,
                                      setup=setup_authentication)

        installer = ISiteLocalInstaller(self.context)
        installer.registerUtility(self.context.principals,
                                  provided=IAuthenticatorPlugin,
                                  name='users')

    def render(self):
        # Test that our installation was successful
        pau = queryUtility(IAuthentication)
        if pau is None or type(pau) is not PluggableAuthentication:
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

