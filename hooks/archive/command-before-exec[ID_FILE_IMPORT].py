# -*- coding: utf-8 -*-


from  pyrevit import revit, EXEC_PARAMS
from Autodesk.Revit.UI import TaskDialog

sender = __eventsender__
args   = __eventargs__

doc = revit.doc

if not doc.IsFamilyDocument:
    TaskDialog.Show('Big Brother is Watching',
                    'Import CAD is not Allowed! Use LinkCAD Instead')

    from pyrevit.forms import ask_for_string
    password = 'LearRevitAPI'
    user_input = ask_for_string(prompt='Only users with a password can Import CAD files',
                                title='Import CAD Blocked')

    if user_input != password:
        args.Cancel = True
else:
    TaskDialog.Show('Family CAD Import',
                    'Import CAD is Allowed in families!')