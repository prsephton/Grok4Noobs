from zope.component import Interface
from zope.interface import invariant, Invalid
from zope.schema import Choice, Text, TextLine, Bytes, DottedName

#____________________________________________________________________________________
class ISourceHighlight(Interface):
    """ A utility which returns a formatted string highlighting syntax
    """

class IAccount(Interface):
    pass

#____________________________________________________________________________________
class IAttachments(Interface):
    """  A bin holding attachments
    """

#____________________________________________________________________________________
class IAttachment(Interface):
    """ Schema for resources which we intend to store alongside articles
    """
    name  = DottedName(title=u'Resource Name:', description=u'The name of the resource being defined')
    description = TextLine(title=u'Description', description=u'A description for the resource')
    fmt   = Choice(title=u'Format:', description=u'The format of the source',
                 vocabulary='gfn.resourceTypes', required=True, default='python')
    fdata = Bytes(title=u'Upload file:', description=u'Upload source', required=False)
    text  = Text(title=u'or type Text:', description=u'Source Text', required=False)

    @invariant
    def file_or_text(self):
        if self.fdata or self.text: return True
        raise Invalid('You must either upload the source or type it in')

#____________________________________________________________________________________
class IArticle(Interface):
    ''' Identifies an article, and defines a data schema for it
    '''
    title = TextLine(title=u'Page Title:', description=u'The title of the displayed page')
    navTitle = TextLine(title=u'Nav Title:', description=u'A title for the navigation area')
    text  = Text(title=u'Display Text:', description=u'Text to display on this page')

#____________________________________________________________________________________
class IArticleSorter(Interface):
    ''' This defines an interface into an article sorter.  We use this approach rather
        than using grok.OrderedContainer for articles, in order to demonstrate the
        extensibility of the grok web framework.
    '''
    def sortedItems(self):
        ''' Returns a sorted list of articles, and maintains sorting order'''
        return []

