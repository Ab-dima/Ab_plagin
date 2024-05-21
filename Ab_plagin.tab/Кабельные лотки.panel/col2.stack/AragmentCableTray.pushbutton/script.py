#-*- coding: utf-8 -*-

__title__ = "Переименовать\nсоед. детали лотков"
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


def fittingsRename():
    typesize = ['ZH_Шарнирное изменение угла трассы', 'ZH_Угол горизонтальный', 'ZH_Ответвитель Х-образный', 'ZH_Ответвитель Т-образный']

    cable_aragment = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CableTrayFitting).WhereElementIsNotElementType().ToElements()

    cable_aragment = [i for i in cable_aragment if i.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() in typesize]


    t = Transaction(doc, __title__)
    t.Start()
    for aragment in cable_aragment:
        family_name = aragment.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
        if family_name in typesize:
            if family_name == 'ZH_Шарнирное изменение угла трассы':
                height    = str(round(decimal_to_mm(aragment.LookupParameter('Высота лотка').AsDouble()),2))[:-2]
                weight    = str(round(decimal_to_mm(aragment.LookupParameter('Ширина лотка').AsDouble()),2))[:-2]
                thickness = str(round(decimal_to_mm(aragment.LookupParameter('Толщина').AsDouble()),2))
                angle     = aragment.LookupParameter('Угол поворота').AsValueString()
                name = ' {0} градусов {1}х{2}, {3} мм, в комплекте с крепежными элементами и соединительными пластинами, необходимыми для монтажа'.format(angle, weight, height, thickness)
                if aragment.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString() == 'Вертикальный изгиб внутренний':
                    sublement = 'Изгиб вертикальный внутренний'
                else:
                    sublement = 'Изгиб вертикальный внешний'
            elif family_name == 'ZH_Угол горизонтальный':
                height = str(round(decimal_to_mm(aragment.LookupParameter('Высота лотка').AsDouble()), 2))[:-2]
                weight = str(round(decimal_to_mm(aragment.LookupParameter('Ширина лотка').AsDouble()), 2))[:-2]
                thickness = str(round(decimal_to_mm(aragment.LookupParameter('Толщина').AsDouble()), 2))
                angle = aragment.LookupParameter('Угол').AsValueString()
                sublement = 'Угол горизонтальный'
                name = ' {0} градусов {1}х{2}, {3} мм, в комплекте с крепежными элементами и соединительными пластинами, необходимыми для монтажа'.format(
                    angle, weight, height, thickness)

            if family_name == 'ZH_Ответвитель Х-образный' or family_name == 'ZH_Ответвитель Т-образный':
                height     = str(round(decimal_to_mm(aragment.LookupParameter('Высота лотка').AsDouble()), 2))[:-2]
                weight     = str(round(decimal_to_mm(aragment.LookupParameter('Ширина лотка 1').AsDouble()), 2))[:-2]
                thickness  = str(round(decimal_to_mm(aragment.LookupParameter('Толщина').AsDouble()), 2))
                angle      = ''
                name = ' {0}х{1}, {2} мм, в комплекте с крепежными элементами и соединительными пластинами, необходимыми для монтажа'.format(
                    weight, height, thickness)
                if family_name == 'ZH_Ответвитель Х-образный':
                    sublement = 'Ответвитель X-образный'
                else:
                    sublement = 'Ответвитель T-образный'



            if aragment.LookupParameter('ZH_Крышка').AsInteger():
                aragment.LookupParameter('Крышка').Set(1)
                aragment.LookupParameter('Крышка наименование').Set('Крышка на ' + (sublement[0].lower() + sublement[1:]) + ' {0}'.format((angle)) + ' осн.{0}'.format(weight) + ' в комплекте с крепежными элементами и соединительными пластинами, необходимыми для монтажа')
                aragment.LookupParameter('Крышка марка').Set('---')
            else:
                aragment.LookupParameter('Крышка').Set(0)
                aragment.LookupParameter('Крышка наименование').Set('')
                aragment.LookupParameter('Крышка марка').Set('')



        aragment.LookupParameter('ADSK_Наименование').Set((sublement + name))
    t.Commit()

fittingsRename()

