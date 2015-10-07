'''
   Handling of attachments such as images or text snippits
'''
import grok
from zope.component import getUtility, getMultiAdapter
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from interfaces import IArticle, IAttachments, IAttachment
from resource import textStyle, popups, style
from layout import Content, ILayout
from colorise import ISourceHighlight
from menu import UtilItem
from permissions import Editing

#____________________________________________________________________________________
class ResourceTypes(grok.GlobalUtility):
    """  The types of resources which may be included in our articles
            *** NOTE *** Unsure why, but vocabularies defined like this
               need zope.app.schema in setup.py
    """
    grok.implements(IVocabularyFactory)
    grok.name('gfn.resourceTypes')

    formats = [
        ('image',      u'A png, gif or jpeg image'),
        ('html',       u'HTML Source'),
        ('javascript', u'Javascript Code'),
        ('python',     u'Python Sources'),
        ('css',        u'CSS Source')]

    def __call__(self, context):
        self.context = context
        terms = []
        for value, title in self.formats:
            token  = str(value)
            terms.append(SimpleVocabulary.createTerm(value,token,title))
        return SimpleVocabulary(terms)

#____________________________________________________________________________________
class Attachments(grok.Container):
    ''' Holds things which implement IAttachment
    '''
    grok.implements(IAttachments, ILayout)
    title = u'Managing Attachments'

#____________________________________________________________________________________
class BackButton(UtilItem):
    grok.context(IAttachments)
    grok.order(0)
    title = u'Back to article'
    mclass = 'buttons'
    @property
    def link(self):
        return self.context.__parent__

#____________________________________________________________________________________
class ManageAttachments(UtilItem):
    grok.context(IArticle)
    grok.require(Editing)
    grok.order(-1)
    title = u'Manage Attachments'
    link = u'attachments'
    mclass = 'buttons'

    def condition(self):
        a = self.context.attachments
        return a is not None and len(a)

#____________________________________________________________________________________
class Image(grok.Model):
    '''  An attachment being an image
    '''
    grok.implements(IAttachment)

    def __init__(self, name, description, fmt, fdata, text):
        self.name = name
        self.description = description
        self.fmt  = fmt
        self.fdata = fdata
        self.text = text
    def link(self):
        return '''<img src="attachments/{}" />'''.format(self.name)

#____________________________________________________________________________________
class ShowImage(grok.View):
    grok.context(Image)
    grok.name('index')
    grok.require('zope.Public')

    def render(self):
        return self.context.fdata or self.context.text

#____________________________________________________________________________________
class Source(grok.Model):
    '''  An attachment being a text item
    '''
    grok.implements(IAttachment)

    def __init__(self, name, description, fmt, fdata, text):
        self.name = name
        self.description = description
        self.fmt  = fmt
        self.fdata = fdata
        self.text = text
        if fdata:
            self.text = fdata.replace('\r\n', '\n')

    def highlight(self):
        pygments = getUtility(ISourceHighlight, name="Pygments")
        return pygments(self.text, self.fmt)  # Returns highlighted text

    def link(self):
        return '''<div class='attachment' name="%s" src="attachments/%s" />''' % (self.name, self.name)

#____________________________________________________________________________________
class ShowSource(grok.View):
    grok.context(Source)
    grok.name('index')
    grok.require('zope.Public')
    html = ''

    def update(self):
        self.html = self.context.highlight()  # Set highlighted text
        style.need()
        textStyle.need()

#____________________________________________________________________________________
class Highlight(grok.View):
    grok.context(Source)
    grok.require('zope.Public')

    def render(self):
        return self.context.highlight()  # Get highlighted text

#____________________________________________________________________________________
class ListAttachments(grok.Viewlet):
    ''' Displays a list of attachments and allows edit/delete on each item
    '''
    grok.context(IAttachments)
    grok.viewletmanager(Content)

    def update(self):
        popups.need()

#____________________________________________________________________________________
class ModifySource(grok.EditForm):
    grok.context(Source)
    grok.name('modify')
    grok.require(Editing)

    def setUpWidgets(self, ignore_request=False):
        super(ModifySource, self).setUpWidgets(ignore_request)
        self.widgets['text'].cssClass = 'pre'

    @grok.action(u'Update')
    def Change(self, **data):
        attachments = self.context.__parent__
        name = data['name']
        if name in attachments: del attachments[name]
        if data['fmt']=='image':
            src = attachments[name] = Image(**data)
        else:
            src = attachments[name] = Source(**data)
        content = getMultiAdapter((src, self.request), name='index')
        return content()

    @grok.action(u'Cancel action', validator=lambda *_a, **_k: {})
    def cancel(self):
        attachments = self.context.__parent__
        name = self.context.name
        src = attachments[name]
        content = getMultiAdapter((src, self.request), name='index')
        return content()

#____________________________________________________________________________________
class ModifyImage(grok.EditForm):
    grok.context(Image)
    grok.name('modify')
    grok.require(Editing)

    form_fields = grok.AutoFields(Image).omit('text', 'fmt')

    @grok.action(u'Update')
    def Change(self, **data):
        attachments = self.context.__parent__
        name = data['name']
        if name in attachments: del attachments[name]
        src = attachments[name] = Image(**data)
        return src.link()

    @grok.action(u'Cancel action', validator=lambda *_a, **_k: {})
    def cancel(self):
        attachments = self.context.__parent__
        name = self.context.name
        src = attachments[name]
        return src.link()

#____________________________________________________________________________________
class EditAttachment(grok.EditForm):
    grok.context(IAttachment)
    grok.name('edit')
    grok.require(Editing)

    camefrom = None

    def update(self, camefrom = None):
        self.camefrom = camefrom or self.url(self.context.__parent__)

    @grok.action(u'Update')
    def Change(self, **data):
        attachments = self.context.__parent__
        name = data['name']
        if name in attachments: del attachments[name]
        if data['fmt']=='image':
            attachments[name] = Image(**data)
        else:
            attachments[name] = Source(**data)
        self.redirect(self.camefrom)

    @grok.action(u'Cancel action', validator=lambda *_a, **_k: {})
    def cancel(self):
        self.redirect(self.camefrom)

#____________________________________________________________________________________
class DeleteAttachment(grok.EditForm):
    grok.context(IAttachment)
    grok.name('delete')
    grok.require(Editing)
    form_fields = grok.Fields(IAttachment).omit('fdata', 'text')

    @grok.action(u'Yes, Delete this attachment')
    def Delete(self, **data):
        attachments = self.context.__parent__
        name = data['name']
        if name in attachments: del attachments[name]
        self.redirect(self.url(attachments))

    @grok.action(u'No, get me out of here', validator=lambda *_a, **_k: {})
    def cancel(self):
        attachments = self.context.__parent__
        self.redirect(self.url(attachments))

#____________________________________________________________________________________
class ArticleAttachment(grok.Adapter):
    ''' An adapter which creates an IAttachment for an IArticle
    '''
    grok.context(IArticle)
    grok.implements(IAttachment)

    name  = None
    description = None
    fmt   = u'python'
    text  = u''
    fdata = None

#____________________________________________________________________________________
class AddAttachment(grok.EditForm):
    '''  This is an edit form for resources.  These are stored with the article.  We
        return HTML which will insert the appropriate resource.  For images, we
        return an image tag.  For source text, we return a div linking the
        formatted text.
    '''

    grok.context(IArticle)
    form_fields = grok.Fields(IAttachment)    # Use the ArticleAttachment adapter
    grok.name('attach')
    grok.require(Editing)

    def setUpWidgets(self, ignore_request=False):
        super(AddAttachment, self).setUpWidgets(ignore_request)
        self.widgets['text'].cssClass = 'pre'

    def update(self):
        ''' As this view is called directly and displayed in a dialog window, we need to add the
            css style explicitly.  Also, grok.EditForm includes the HTML header.
        '''
        style.need()

    @grok.action(u'Add this resource')
    def addResource(self, **data):

        if self.context.attachments is None:
            attachments = self.context.attachments = Attachments()
        else:
            attachments = self.context.attachments
        name = data['name']
        if name in attachments: del attachments[name]
        if data['fmt']=='image':
            src = attachments[name] = Image(**data)
            return src.link()
        else:
            src = attachments[name] = Source(**data)
            content = getMultiAdapter((src, self.request), name='index')
            return content()

    @grok.action(u'Cancel action', validator=lambda *_a, **_k: {})
    def cancel(self):
        return ''
