import grok
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

#_________________________________________________________________________________________
# Permissions defined
class Administering(grok.Permission):
    grok.name('gfn.administering')

class Authenticated(grok.Permission):
    grok.name('gfn.authenticated')

class Editing(grok.Permission):
    grok.name('gfn.editing')

class Viewing(grok.Permission):
    grok.name('gfn.viewing')

#_________________________________________________________________________________________
# Roles defined
class Administrator(grok.Role):
    grok.name('gfn.Administrator')
    grok.title(u'Administrator')
    grok.permissions(Authenticated, Administering, Editing, Viewing)

class Editor(grok.Role):
    grok.name('gfn.Editor')
    grok.title(u'Editor')
    grok.permissions(Authenticated, Editing, Viewing)

class Visitor(grok.Role):
    grok.name('gfn.Visitor')
    grok.title(u'Visitor')
    grok.permissions(Authenticated, Viewing)

#_________________________________________________________________________________________
# A vocabulary for our defined roles
class Roles(grok.GlobalUtility):
    grok.name('gfn.AccountRoles')
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        for role in [Administrator, Editor, Visitor]:
            name  = role.__dict__['grokcore.component.directive.name']
            title = role.__dict__['grokcore.component.directive.title']
            terms.append(SimpleVocabulary.createTerm(name, name, title))
        return SimpleVocabulary(terms)


