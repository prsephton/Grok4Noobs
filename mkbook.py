#______________________________________________________________________________
# Turn our site into a pdf printable document using princexml
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import grok, re

from interfaces import ISiteRoot, IArticle, IArticleSorter
from menu import UtilItem
from resource import style, textLight
from zope.traversing.api import traverse
from urlparse import urlparse
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

        def host_from(netloc):
            if type(netloc) is str and len(netloc):
                return netloc.split(":")[0]

        baseUrl = self.url(self.context) + "/"
        host = host_from(urlparse(baseUrl).netloc)

        text = self.context.text
        c = re.compile(r'<a\s*title="([^"]*)"\s*href="([^"]*)">([^<])</a>')

        pos = 0
        new_text = u""
        while True:               # Replace URLs inline
            s = c.search(text, pos=pos)
            if s is None:
                new_text += text[pos:]
                break
            else:
                new_text += text[pos:s.start()]  # Add text up to start
                pos = s.end()+1
                url = urlparse(s.group(2))
                if (url.netloc is None or len(url.netloc)==0 or
                    host == host_from(url.netloc)):  # local link. replace with section anchor
                    if url.netloc is None:
                        try:
                            ob = traverse(self.context, url.path)
                        except:
                            try:
                                ob = traverse(self.context, baseUrl+url.path)
                            except:
                                ob = None
                    else:
                        try:
                            ob = traverse(grok.getSite(), url.path)
                        except:
                            ob = None
                    if ob is None or not IArticle.providedBy(ob):
                        new_text += s.group()
                    else:
                        fmt = '<a title="{}" href="#{}">{}</a>'
                        new_text += fmt.format(s.group(1),
                                               ob.getArticleId(),
                                               s.group(3))
                else:                       # Replace global links with footnotes
                    fmt = u"<em>{}</em><span class='fn'>{}: {}</span>"
                    new_text += fmt.format(s.group(3), s.group(1), s.group(2))
        text = new_text

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


class IdView(grok.View):
    '''  Give all articles an ID
    '''
    grok.context(IArticle)
    grok.require('zope.Public')
    grok.name("id")

    def render(self):
        return self.context.getArticleId()


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
