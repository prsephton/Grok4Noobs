#__________________________________________________________________________________________________
# A small module to allow registration of local utilities after the site has been created
# and added via the management UI
import grok
from zope.component import Interface
from zope.location.interfaces import ISite

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
        util = sm.queryUtility(provided, name=name)
        if util is not None:
            print 'delete %s' % util
            sm.unregisterUtility(provided=provided, name=name)
            del util
            # del sm.utilities._adapters[0][provided]
            # del sm.utilities._subscribers[0][provided]
            # sm.utilities.unsubscribe((), provided)
            # del sm.utilities.__dict__['_provided'][provided]

    def registerUtility(self, factory, provided, name='', setup=None):
        ''' Register a new local utility with the site.  If it already exists
            we remove the old one first
        '''
        sm = self.context.getSiteManager()
        old = sm.queryUtility(provided, name=name)
        if old: sm.unregisterUtility(provided=provided, name=name)
        try:
            obj = factory()
        except:
            obj = factory
        sm.registerUtility(obj, provided=provided, name=name)
        if setup: setup(obj)
