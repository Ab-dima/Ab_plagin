#-*- coding: utf-8 -*-

__title__ = "Расчет трубы"
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

from math import pi, degrees, radians


def get_el_fix_by_name(name_circuit):
    param_type  = ElementId(BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER)
    f_param     = ParameterValueProvider(param_type)
    evaluator   = FilterStringEquals()
    f_rule      = FilterStringRule(f_param, evaluator, name_circuit)
    filter_type_name = ElementParameterFilter(f_rule)
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ElectricalFixtures).WherePasses(filter_type_name).WhereElementIsNotElementType().ToElements()

def get_el_fix_by_id(id_panel):
    collector        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ElectricalFixtures).WhereElementIsNotElementType().ToElements()
    lst_el_fixctures = []
    for i in collector:
        lst_MEPModel = i.MEPModel.GetElectricalSystems()
        for l in lst_MEPModel:
            if l.BaseEquipment.Id.ToString() == id_panel:
                lst_el_fixctures.append(i)

    return lst_el_fixctures

counter_el_circuit = 0
electrical_circuits = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds() if doc.GetElement(i).Category.Name == 'Электрические цепи']

z_axis = XYZ(0, 0, 1)

t = Transaction(doc, __title__)
t.Start()

for electrical_circuit in electrical_circuits:
    lenght_truba = 0
    points = electrical_circuit.GetCircuitPath()
    for point in range(len(points)):
        if point == len(points)-1:
            break
        else:
            point_end              = points[point+1]
            point_start            = points[point]
            str_point_end          = point_end.ToString()
            vector                 = point_end-point_start
            angle_betwen_z_axis    = degrees(vector.AngleTo(z_axis))

            if angle_betwen_z_axis > 89 and angle_betwen_z_axis < 91:
                lenght_truba += point_start.DistanceTo(point_end)

    lenght_truba = (lenght_truba / 1000) *1.15
    electrical_circuit.LookupParameter('ZH_Длина трубы').Set(lenght_truba)

t.Commit()


