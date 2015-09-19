#_____________________________________________________________________________________________
#  The code below defines a new HiddenText schema field type and associates a widget
# with it that renders as a hidden input type.
#  A HiddenText schema field may be used to persist state in forms between the server
# and the browser.
import grok
from zope.schema import TextLine
from zope.publisher.browser import IBrowserRequest
from zope.formlib.interfaces import IInputWidget
from zope.formlib.widget import SimpleInputWidget

#________________________________________________________________
class HiddenText(TextLine):
    ''' We register an adapter for this new schema field which renders a hidden text field '''

#________________________________________________________________
class HiddenTextWidget(SimpleInputWidget):
    ''' Our hidden text widget is easily derived from SimpleInputWidget.  We override
        the __call__ to render as a hidden input
    '''
    def _toFieldValue(self, aInput):
        return unicode(aInput)

    def __call__(self):
        return self.hidden()

#________________________________________________________________
class HiddenTextAdapter(grok.MultiAdapter):
    '''  Define an adapter for our schema field which selects our hidden text widget
    '''
    grok.adapts(HiddenText, IBrowserRequest)
    grok.implements(IInputWidget)

    def __new__(cls, field, request):
        return HiddenTextWidget(field, request)
