#______________________________________________________________________________
# Turn our site into a pdf printable document using princexml
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import grok

from interfaces import ISiteRoot, IArticle, IArticleSorter
from menu import UtilItem
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

    def articleNumber(self):
        order = getattr(self.context, "order", None)
        if order is None:
            self.context.section = ""
        else:
            order = int(order) + 1
            parent = getattr(self.context, "__parent__", None)
            if parent and len(parent.section):
                section = "{}.{}".format(parent.section, order)
            else:
                section = "{}".format(order)
            self.context.section = section
            return section + ": "
        return ""

    def articleId(self, item):
        if self.context.section:
            section = "{}.{}".format(self.context.section, item.order+1)
        else:
            section = "{}".format(item.order+1)
        return u'sn_'+section.replace('.', '_')

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


class MkBookButton(UtilItem):
    '''  A menu item that turns the site into a book
    '''
    grok.context(ISiteRoot)
    grok.require('zope.Public')
    grok.order(-1)
    title = u'Create Book'
    link = 'mkbook'
    mclass = 'nav buttons'

    def condition(self):  # Depends on the 'prince' app being installed
        return has_prince
