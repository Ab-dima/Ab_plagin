#-*- coding: utf-8 -*-

__title__ = "Выключатели\n(Удалить это)"
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
from Autodesk.Revit.Exceptions import *

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
from rpw.ui.forms import FlexForm,TextBox,Separator,Button, Label, CheckBox, Alert

from math import degrees, radians, cos, sin, tan

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


def get_angle(cable_tray, axis):
    angle = get_vector(cable_tray).AngleTo(axis)
    return angle

def get_vector(cable_tray):
    pt_start = cable_tray.Location.Curve.GetEndPoint(0)
    pt_end = cable_tray.Location.Curve.GetEndPoint(1)
    vector = (pt_end - pt_start).Normalize()
    return vector

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# =========================================

uidoc        = __revit__.ActiveUIDocument
doc          = uidoc.Document
app          = __revit__.Application

active_view  = doc.ActiveView
active_level = doc.ActiveView.GenLevel

elements_av = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds()]
my_dict = {}


group_element_param = []

proverka_1 = ['TSL_2D автоматический выключатель_ВРУ','TSL_Резервный автомат для ВРУ','TSL_2D автоматический выключатель_Щит','TSL_Резервный автомат для щитов']
proverka_2 = ['TSL_Вводной автомат для щитов','TSL_Любой автомат для схем']

for elem in elements_av:
    param_type = elem.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
    if param_type == 'TSL_Щит распределительный' or param_type == 'TSL_Панель распределительная':
        name_sheild = elem.LookupParameter('Имя панели').AsValueString()
        break


vvodnoy_avtomat = ''
for elem in elements_av:
    if elem.LookupParameter('Принадлежность щиту') and elem.LookupParameter('Принадлежность щиту').AsValueString() == name_sheild:
        if elem.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString() in proverka_1:
            param_phase   = elem.LookupParameter('3-фазный аппарат').AsValueString()
            param_diff    = elem.LookupParameter('Дифф.автомат').AsValueString()
            param_ust     = elem.LookupParameter('Уставка аппарата').AsValueString()
            param_appType = elem.LookupParameter('Тип аппарата').AsValueString()
            param_mark    = elem.LookupParameter('ADSK_Марка').AsValueString()
            group_element_param.append([3 if param_phase == 'Да' else 1, 'ДИФ' if param_diff == 'Да' else 'АВ', float(param_ust), param_appType])
        elif elem.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString() in proverka_2:
            param_phase = elem.LookupParameter('3-фазный аппарат').AsValueString()
            param_diff = elem.LookupParameter('Дифф.автомат').AsValueString()
            param_ust = elem.LookupParameter('Уставка аппарата').AsValueString()
            param_appType = elem.LookupParameter('Тип аппарата').AsValueString()
            param_mark = elem.LookupParameter('ADSK_Марка').AsValueString()
            vvodnoy_avtomat = "Тип: {3} {2}А / {0}P - 1".format(3 if param_phase == 'Да' else 1, 'ДИФ' if param_diff == 'Да' else 'АВ', float(param_ust), param_appType + " " * (15 - len(param_appType)))




group_element_param = sorted(group_element_param, key=lambda x: (x[0],x[1], x[3]))
for group in group_element_param:
    itog = "Тип: {3} {2}А / {0}P /".format( group[0], group[1],group[2], group[3]+" "*(15-len(group[3])))
    if itog not in my_dict:
        my_dict.setdefault(itog, 1)
    else:
        my_dict[itog] += 1

print('Панель: '+name_sheild)
print('_ '*30)

print('Вводной автомат:')
print(vvodnoy_avtomat if len(vvodnoy_avtomat) != 0 else 'Вводной автомат отсутсвует')
print('_ '*30)
counter = 0
for k,v in my_dict.items():
    print('{0} - {1}'.format(k,v))
    counter += v
print('_ '*30)
print('Всего автоматов: ' + str(counter+1 if len(vvodnoy_avtomat) != 0 else counter) + ' шт.')

