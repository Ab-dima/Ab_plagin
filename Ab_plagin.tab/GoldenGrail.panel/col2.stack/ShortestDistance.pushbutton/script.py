#-*- coding: utf-8 -*-

__title__ = "Наикротчайшее\nрасстояние кабеля"
__doc__   = "Это бомба"

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


import subprocess
import json
import sys

points_xyz = [doc.GetElement(i).Location.Point for i in uidoc.Selection.GetElementIds()]
points = [i.ToString() for i in points_xyz]

try:
    result_file_path = r'C:\Dima\Revit\S\Shablon\data.json'
    with open(result_file_path, 'w') as file:
        json.dump(points, file)
except Exception as e:
    print(e)
    sys.exit()

open_file = r'C:\Dima\Скрипты\External_scripts\external_script.py'
subprocess.call(['python', open_file])

result_file_path = r'C:\Dima\Revit\S\Shablon\result.json'
with open(result_file_path, 'r') as file:
    mst_edges = json.load(file)

mst_edges = [eval(i) for i in mst_edges]

points_xy = {k:i for k,i in enumerate(points_xyz, start= 1)}

curves = []
for start, end in mst_edges:
    z  = 0
    x1 = points_xy[start].X
    y1 = points_xy[start].Y

    x2 = points_xy[end].X
    y2 = points_xy[end].Y

    pt1 = XYZ(x1, y1, z)
    pt2 = XYZ(x2, y1, z)
    pt4 = XYZ(x2, y2, z)

    if decimal_to_mm(pt1.DistanceTo(pt2)) > 1:
        curve1          = Line.CreateBound(pt1, pt2)
        curves.append(curve1)
        # newDetailCurve1 = doc.Create.NewDetailCurve(active_view, curve1)

    if decimal_to_mm(pt2.DistanceTo(pt4)) > 1:
        curve2 = Line.CreateBound(pt2, pt4)
        curves.append(curve2)
        # newDetailCurve2 = doc.Create.NewDetailCurve(active_view, curve2)


###------------------------------------------------------------------------------------------------------
###------------------------------------------------------------------------------------------------------
###------------------------------------------------------------------------------------------------------

curves_to_delete = []

curves_points = {}

digit = 0
for i in curves:
    digit += 1
    print('Линия {}'.format(digit))
    if i in curves_to_delete:
        continue
    for j in curves:
        if i is j or j in curves_to_delete:
            continue
        else:
            if j not in curves_points:

                pt2s = j.GetEndPoint(0)
                pt2e = j.GetEndPoint(1)
                pt2s = XYZ(pt2s.X, pt2s.Y, 0)
                pt2e = XYZ(pt2e.X, pt2e.Y, 0)

                curves_points[j.Id] = pt2s,pt2e
            else:
                pt2s, pt2e = curves_points[j.Id]

            counter = 0
            value_to_check = mm_to_decimal(0.2)

            if i.Distance(pt2s) <= value_to_check:
                counter += 1
            if i.Distance(pt2e) <= value_to_check:
                counter += 1
            if counter == 1:
                vector = pt2e - pt2s
                vector.Normalize()
                pt2_1s = pt2s + vector * (mm_to_decimal(0.1))
                pt2_1e = pt2e - vector * (mm_to_decimal(0.1))
                if i.Distance(pt2_1s) <= value_to_check:
                    counter += 1
                elif i.Distance(pt2_1e) <= value_to_check:
                    counter += 1
            try:
                if counter == 2:
                    print(counter)
                    line_to_del = i if i.Length < i.Length else j
                    curves_to_delete.append(line_to_del)
                    print('Линию {0} удалили'.format(digit))
                    continue
            except Exception as e:
                print(e)

            print(counter)


result_curves = [i for i in curves if i not in curves_to_delete]
print(len(result_curves))
result_curves = curves
try:
    t = Transaction(doc, __title__)
    t.Start()

    for c in result_curves:

        newDetailCurve = doc.Create.NewDetailCurve(active_view, c)

    t.Commit()
except Exception as e:
    print(e)

