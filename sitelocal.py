#__________________________________________________________________________________________________
# A small module to allow registration of local utilities after the site has been created
# and added via the management UI
import grok
from zope.component import Interface
from zope.location.interfaces import ISite

class ISiteLocalInstaller(Interface):
    '''  Describes the registration interface
    '''
    def unregisterUtility(self, provided, name=None, name_in_container=None):
        '''  Unregister a local utility
        '''
    def registerUtility(self, factory, provided, name=None, name_in_container=None, setup=None):
        '''  Register a local utility
        '''

class SiteLocalInstaller(grok.Adapter):
    '''  An adapter which adapts an ISite (or grok.Application) to return
         a local utility installer
    '''
    grok.context(ISite)
    grok.implements(ISiteLocalInstaller)

    def unregisterUtility(self, provided, name='', name_in_container=None):
        ''' Unregister a local utility from the site
        '''
        if name_in_container is None:
            if name and len(name):
                name_in_container = name
            else:
                raise Exception(u'We need either a name, or a name_in_container to unregister local components')

        sm = self.context.getSiteManager()

        util = sm.queryUtility(provided, name=name)
        if util is not None:
            print 'delete %s' % util
            sm.unregisterUtility(provided=provided)
            del util


    def registerUtility(self, factory, provided, name='', name_in_container=None, setup=None):
        ''' Register a new local utility with the site.  If it already exists
            we remove the old one first
        '''
        if name_in_container is None:
            if name and len(name):
                name_in_container = name
            else:
                raise Exception(u'We need either a name or a name_in_container to register local components')

        sm = self.context.getSiteManager()
        old = sm.queryUtility(provided, name=name)
        if old is not None:
            sm.unregisterUtility(component=old, provided=provided)
            del old

        if name_in_container in sm: del sm[name_in_container]
        try:
            obj = factory()
        except:
            obj = factory

        sm[name_in_container] = obj
        sm.registerUtility(obj, provided=provided, name=name)
        if setup: setup(obj)
