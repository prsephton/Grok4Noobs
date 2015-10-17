import grok
from layout import Content
from interfaces import ISiteRoot, IStatus


class StatusData(grok.Model):
    ''' This data gets stored in the site root.  If the
        status is not None we will render a popup dialog.
    '''
    title = u'Status'
    message = ''
    status = None

    def __init__(self, sts, msg, title=u'Status'):
        self.status = sts
        self.message = msg
        self.title = title

        app = grok.getApplication()
        app.status = self

    def read(self):  # "one shot" reader
        if self.status is not None:
            sts = dict(status=self.status,
                       title=self.title,
                       message=self.message)
            self.status = None
            return sts


class Status(grok.GlobalUtility):
    ''' A small utility to set the status message '''
    grok.implements(IStatus)

    def __call__(self, sts, msg, title=u'Status'):
        StatusData(sts, msg, title)


class StatusContent(grok.Viewlet):
    ''' Renders the status into the content area '''
    grok.context(ISiteRoot)
    grok.viewletmanager(Content)
