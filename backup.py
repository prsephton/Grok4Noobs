import grok
from io import FileIO
from grok4noobs import Grok4Noobs, NoobsArticle
from attachments import Attachments, Source, Image
from urllib import quote_plus
from permissions import Administering
from interfaces import ISiteRoot, IStatus
from menu import UtilItem
from zope import component

def dbPath():
    from os.path import dirname
    return dirname(__file__)+"/db/backup.dat"

def write_objs(f, objs):
    '''  Just write the objects in a way that lets us read them again
    '''
    for o in objs:
        if o:
            f.write("%i\n"%len(o))
            f.write(o)
        else:
            f.write("0\n")


def read_objs(f, n):
    ''' Read <n> objects back and return them
    '''
    objs = []
    while n > 0:
        sz = int(f.readline())
        objs.append(f.read(sz))
        n -= 1
    return objs


def do_backup(f, node):
    '''
        First save current node information,
            title, navtitle, text.
            attachments
        then for each contained item, process recursively.
    '''
    write_objs(f, [node.title, node.navTitle, node.text])
    if node.attachments:
        f.write("%i\n"%len(node.attachments))
        for a in node.attachments.values():
            t = 'Image' if type(a) is Image else 'Source'
            write_objs(f, [t, a.name, a.description, a.fmt, a.fdata, a.text])
    else:
        f.write("0\n")

    f.write("%i\n"%len(node.keys()))
    sorter = node.sorter()
    for item in sorter.sortedItems():
        do_backup(f, item)


def do_restore(f, node):
    '''
       Performs the opposite of the backup function, reading all data back into
       the container structure.
    '''
    [node.title, node.navTitle, node.text] = read_objs(f, 3)
    nAttachments = int(f.readline())
    if nAttachments > 0:
        att = node.attachments = Attachments()
        while nAttachments > 0:
            [t, name, desc, fmt, fdata, text] = read_objs(f, 6)
            if t == 'Image':
                att[name] = Image(name, desc, fmt, fdata, text)
            elif t == 'Source':
                att[name] = Source(name, desc, fmt, fdata, text)
            nAttachments -= 1
    nChildren = int(f.readline())

    for order in range(nChildren):
        art = NoobsArticle()
        art.order = order
        do_restore(f, art)
        nTitle = quote_plus(art.navTitle)
        if nTitle in node: del node[nTitle]
        node[nTitle] = art


class backup(grok.View):
    ''' A view which executes the backup function
    '''
    grok.context(Grok4Noobs)
    grok.require(Administering)

    def update(self):
        self.context.status = None
        sts = component.getUtility(IStatus)
        try:
            with FileIO(dbPath(), 'w') as f:
                do_backup(f, self.context)
            sts('backup_ok', 'Success')
        except Exception, e:
            sts('backup_fail', str(e))


    def render(self):
        self.redirect(self.url(self.context))


class restore(grok.View):
    ''' A view which executes the restore function
    '''
    grok.context(Grok4Noobs)
    grok.require(Administering)

    def update(self):
        sts = component.getUtility(IStatus)
        try:
            with FileIO(dbPath(), 'r') as f:
                do_restore(f, self.context)
            sts('restore_ok', 'Success')
        except Exception, e:
            sts('restore_fail', str(e))

    def render(self):
        self.redirect(self.url(self.context))


class BackupButton(UtilItem):
    '''  A menu item for making a data backup
    '''
    grok.context(ISiteRoot)
    grok.require(Administering)
    grok.order(-7)
    title = u'Backup Data'
    link = 'backup'
    mclass = 'nav buttons'


class RestoreButton(UtilItem):
    '''  A menu item for restoring from backup
    '''
    grok.context(ISiteRoot)
    grok.require(Administering)
    grok.order(-6)
    title = u'Restore Data'
    link = 'restore'
    mclass = 'nav buttons'
