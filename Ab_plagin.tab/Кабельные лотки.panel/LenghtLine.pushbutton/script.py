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


elementIds = []
host_element = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds()][0]

filter1 = ElementClassFilter(FamilyInstance)
sub1 = host_element.GetDependentElements(filter1)
for s1 in sub1:
    elementIds.append(s1)
    filter1_1 = ElementClassFilter(FamilyInstance)
    sub1_1 = doc.GetElement(s1).GetDependentElements(filter1_1)
    for s1_1 in sub1_1:
        elementIds.append(s1_1)

t = Transaction(doc, __title__)
t.Start()

members = List[ElementId](elementIds)
cat_id = doc.GetElement(elementIds[0]).Category.Id
# cat_id = ElementId(BuiltInCategory.OST_Windows)
assembly = AssemblyInstance.Create(doc, members, cat_id)
t.Commit()

t.Start()
name = "OK1"
assembly.AssemblyTypeName = name
t.Commit()


t.Start()
# view3d   = AssemblyViewUtils.Create3DOrthographic(doc, assembly.Id)

enumerate_view = [AssemblyDetailViewOrientation.HorizontalDetail,AssemblyDetailViewOrientation.DetailSectionA,AssemblyDetailViewOrientation.DetailSectionB,
                  AssemblyDetailViewOrientation.ElevationLeft,AssemblyDetailViewOrientation.ElevationRight,
                  AssemblyDetailViewOrientation.ElevationFront,AssemblyDetailViewOrientation.ElevationBack]
for i in enumerate_view:
    view = AssemblyViewUtils.CreateDetailSection(doc, assembly.Id, i)
    view.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(name)




t.Commit()


