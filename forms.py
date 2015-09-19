"""  A small shim over grok.formlib forms to add a default hidden() method and
     replace the default form template
"""
import grok

class EditForm(grok.EditForm):
    grok.template('edit')
    grok.baseclass()

    def hidden(self): return []

class AddForm(grok.AddForm):
    grok.template('edit')
    grok.baseclass()

    def hidden(self): return []

