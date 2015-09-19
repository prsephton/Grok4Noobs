"""_____________________________________________________________________________

    Source text highlighting is tricky.  JavaScript text highlighters may involve
    having to download considerable volumes of JavaScript to the browser, and these
    source formatters may do a less than sterling job.

    We will instead build a TinyMCE plug-in which will use AJAX to show a form, submit
    the content to the server, and to fill whatever the server returns in place. This
    unfortunately means that we will not be able to edit the highlighted text directly
    inside of the tinyMCE editor, but will need to replace the text as a whole.

    We would like to define the source highlighter as a plugin point, so we will define
    it as a global utility.
"""

import grok

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
from interfaces import ISourceHighlight

#____________________________________________________________________________________
class Pygments(grok.GlobalUtility):
    """ Implements a source code highlighter as a utility
    """
    grok.implements(ISourceHighlight)
    grok.name('Pygments')
    def __call__(self, data, fmt='python'):
        """  A highlighted version of the data is returned
        """
        lexer = get_lexer_by_name(fmt)
        formatter = get_formatter_by_name('html')
        return highlight(data, lexer, formatter)

#____________________________________________________________________________________
class PygmentFormats(grok.GlobalUtility):
    """  The supported formats for our <pygmentize> based conversions
            *** NOTE *** Unsure why, but vocabularies defined like this
               need zope.app.schema in setup.py
    """
    grok.implements(IVocabularyFactory)
    grok.name('gfn.pygmentFormats')

    formats = [('html',       u'HTML Source'),
               ('javascript', u'Javascript Code'),
               ('python',     u'Python Sources'),
               ('css',        u'CSS Source'),
               ('xml',        u'Generic XML Source')]

    def __call__(self, context):
        self.context = context
        terms = []
        for value, title in self.formats:
            token  = str(value)
            terms.append(SimpleVocabulary.createTerm(value,token,title))
        return SimpleVocabulary(terms)
