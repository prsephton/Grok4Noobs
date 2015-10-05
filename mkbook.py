#______________________________________________________________________________
# Turn our site into a pdf printable document using princexml
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import grok

from interfaces import ISiteRoot, IArticle, IArticleSorter
from menu import MenuItem
from resource import style, textLight
import subprocess

try:  # Figure if we have prince (http://www.princexml.com) installed
    has_prince = subprocess.call(['prince', '--version']) >= 0
except:
    has_prince = False


class PageSimpleHTML(grok.View):
    ''' Render this IArticle as a simple page, then do the same
        for each of the sub-articles
    '''
    grok.context(IArticle)
    grok.require('zope.Public')

    def articleContent(self):
        baseUrl = self.url(self.context) + "/"
        text = self.context.text
        if self.context.attachments is not None: 
            for a in self.context.attachments:
                st = 'attachments/{}'.format(a)
                text = text.replace(st, baseUrl+st)
        return text
    
    def sortedItems(self):
        sorter = IArticleSorter(self.context)
        return sorter.sortedItems()        


class FullPageHTML(grok.View):
    ''' Return the site as a single HTML page
    '''
    grok.context(ISiteRoot)
    grok.require('zope.Public')

    def update(self):
        style.need()
        textLight.need()

class MkBook(grok.View):
    '''  Turn the content of this site into a book
    '''
    grok.context(ISiteRoot)
    grok.require('zope.Public')
    
    def render(self):
        url = self.url(self.context, name='fullpagehtml')

        try:
            result = subprocess.check_output(['prince', url, '-o', '-'])
        except:
            return
        
        response = self.request.response
        response.setHeader('content-type', 'application/pdf')
        response.addHeader('content-disposition', 'inline;filename="gfn.pdf"')
        return result


class MkBookButton(MenuItem):
    '''  A menu item that turns the site into a book
    '''
    grok.context(ISiteRoot)
    grok.require('zope.Public')
    grok.order(-9)
    title = u'Create Book'
    link = 'mkbook'
    mclass = 'nav buttons'

    def condition(self):  # Depends on the 'prince' app being installed
        return has_prince
