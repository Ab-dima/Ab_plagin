#-*- coding: utf-8 -*-

__title__ = "Длины линий\n детализации"
__doc__   = "Это бомба"
__highlight__ = 'new'


import pyrevit.forms
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ========================================
import sys,math,clr
clr.AddReference('System')
from System.Collections.Generic import List
clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB.Structure import *
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

from Autodesk.Revit.DB.Electrical import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import ElementId
from Autodesk.Revit.UI import *
from pyrevit import revit, forms
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB import BoundingBoxXYZ
from Autodesk.Revit.DB import Line, XYZ
from Autodesk.Revit.DB.Structure import StructuralType

from Autodesk.Revit.UI import Selection

from math import degrees
from rpw.ui.forms import FlexForm,TextBox,Separator,Button, Label, CheckBox

def decimal_to_mm(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertFromInternalUnits(value,
                                                  UnitTypeId.Millimeters)
def mm_to_decimal(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertToInternalUnits(value,
                                                  UnitTypeId.Millimeters)

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# =========================================

uidoc        = __revit__.ActiveUIDocument
doc          = uidoc.Document
app          = __revit__.Application

active_view  = doc.ActiveView
active_level = doc.ActiveView.GenLevel


lenght = 0

for i in [doc.GetElement(k) for k in uidoc.Selection.GetElementIds()]:
    lenght += decimal_to_mm(i.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble())

print(lenght)


