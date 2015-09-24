#__________________________________________________________________________________________________
# A small module to allow registration of local utilities after the site has been created
# and added via the management UI
import grok
from zope.component import Interface
from zope.location.interfaces import ISite
from zope.site.site import SiteManagementFolder

class ISiteLocalInstaller(Interface):
    '''  Describes the registration interface
    '''
    def unregisterUtility(self, provided, name=None):
        '''  Unregister a local utility
        '''
    def registerUtility(self, factory, provided, name=None, setup=None):
        '''  Register a local utility
        '''

class SiteLocalInstaller(grok.Adapter):
    '''  An adapter which adapts an ISite (or grok.Application) to return
         a local utility installer
    '''
    grok.context(ISite)
    grok.implements(ISiteLocalInstaller)

    def unregisterUtility(self, provided, name=''):
        ''' Unregister a local utility from the site
        '''
        sm = self.context.getSiteManager()
        folder = None
        if 'default' in sm.keys():
            folder = sm['default']

        util = sm.queryUtility(provided, name=name)
        if util is not None:
            print 'delete %s' % util
            sm.unregisterUtility(provided=provided, name=name)
            if folder and name in folder: del folder[name]

            # del sm.utilities._adapters[0][provided]
            # del sm.utilities._subscribers[0][provided]
            # sm.utilities.unsubscribe((), provided)
            # del sm.utilities.__dict__['_provided'][provided]

    def registerUtility(self, factory, provided, name='', setup=None):
        ''' Register a new local utility with the site.  If it already exists
            we remove the old one first
        '''

        sm = self.context.getSiteManager()
        if 'default' in sm.keys():
            folder = sm['default']
        else:
            folder = sm['default'] = SiteManagementFolder()

        old = sm.queryUtility(provided, name=name)
        if old is not None:
            sm.unregisterUtility(provided=provided, name=name)
            if name in folder: del folder[name]
            if name in sm: del sm[name]

        try:
            obj = factory()
        except:
            obj = factory
        if name in folder: del folder[name]
        folder[name] = obj
        sm.registerUtility(obj, provided=provided, name=name)
        if setup: setup(obj)
