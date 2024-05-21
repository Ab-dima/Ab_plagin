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

form_components_sw = [Label('Угол обхода:'),
                      TextBox('textbox1', Text = '45'),
                      Label('Вертикальное расстояние от пересечения, мм:'),
                      TextBox('textbox2', Text = '300'),
                      Separator(),
                      Button('Готово')]

starting_window = FlexForm("Исходные данные", form_components_sw)

if starting_window.show() == False:
    sys.exit()

h = mm_to_decimal(float(starting_window.values['textbox2']))
angle = radians(float(starting_window.values['textbox1']))
adder =  XYZ(0, 0, -h)
z_axis = XYZ(0,0,1)
x_axis = XYZ(1,0,0)

cable_trays = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds() if str(doc.GetElement(i).Category.Name) == 'Кабельные лотки']


t = Transaction(doc, __title__)
t.Start()

for c in cable_trays:

    _Flag = False

    opt = Options()
    opt.ComputeReferences = True
    opt.IncludeNonVisibleObjects = False
    opt.DetailLevel = ViewDetailLevel.Fine
    cable_tray = c
    cableTrayGeo = cable_tray.get_Geometry(opt)

    for cableTrayElement in cableTrayGeo:
        if _Flag == True:
            break
        if isinstance(cableTrayElement, Solid):
            ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
            for duct in ducts:
                if _Flag == True:
                    break
                ductGeo = duct.get_Geometry(opt)
                for ductElement in ductGeo:
                    if isinstance(ductElement, Solid):
                        new_solid = BooleanOperationsUtils.ExecuteBooleanOperation(cableTrayElement, ductElement, BooleanOperationsType.Intersect)
                        if new_solid.SurfaceArea > 0:
                            pt = new_solid.ComputeCentroid()

                            duct_wight = duct.get_Parameter(BuiltInParameter.RBS_CURVE_WIDTH_PARAM).AsDouble()
                            duct_height = duct.get_Parameter(BuiltInParameter.RBS_CURVE_HEIGHT_PARAM).AsDouble()


                            weight            = cable_tray.get_Parameter(BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM).AsDouble()
                            height            = cable_tray.get_Parameter(BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM).AsDouble()

                            reserve = (h * tan(radians(90) - angle) + mm_to_decimal(50) + (height if angle == radians(90) else 0))

                            cable_tray_type = cable_tray.GetTypeId()

                            curve = cable_tray.Location.Curve
                            pt1 = curve.GetEndPoint(0)
                            pt6 = curve.GetEndPoint(1)
                            vector = (pt6 - pt1).Normalize()
                            pt2 = pt1 + vector * (pt1.DistanceTo(pt) - ((duct_wight/2)+reserve))
                            pt5 = pt2 + vector*(2*(reserve+duct_wight/2))

                            pv1 = pt2.Add(XYZ(0, 0, -h))
                            catet1_1 = h
                            gipotenuza_1 = catet1_1 / (cos(radians(90) - angle))
                            catet2_1 = cos(angle) * gipotenuza_1
                            pty = pt2 + vector * catet2_1
                            pt3 = (pt2 + vector * (catet2_1)).Add(adder)
                            pt4 = pt3 + vector*(pt2.DistanceTo(pt5)-2*catet2_1)

                            ct1 = CableTray.Create(doc, cable_tray.GetTypeId(), pt1, pt2, cable_tray.LevelId)
                            ct2 = CableTray.Create(doc, cable_tray.GetTypeId(), pt2, pt3, cable_tray.LevelId)
                            ct3 = CableTray.Create(doc, cable_tray.GetTypeId(), pt3, pt4, cable_tray.LevelId)
                            ct4 = CableTray.Create(doc, cable_tray.GetTypeId(), pt4, pt5, cable_tray.LevelId)
                            ct5 = CableTray.Create(doc, cable_tray.GetTypeId(), pt5, pt6, cable_tray.LevelId)


                            if ((get_angle(ct2, z_axis) >= radians(179.9) or get_angle(ct2,z_axis) <= radians(0.01)) and
                                    (get_angle(ct4, z_axis) >= radians(179.9) or get_angle(ct4,z_axis) <= radians(0.01))):
                                angle0 = get_angle(cable_tray, x_axis) + radians(90)
                                angle1 = 0
                                angle2 = 0
                                if pt1.X <= pt6.X and pt1.Y <= pt6.Y:
                                    angle1 = -(angle0) -radians(180)
                                    angle2 = angle0
                                elif pt1.X >= pt6.X and pt1.Y <= pt6.Y:
                                    angle1 = -(angle0) -radians(180)
                                    angle2 = angle0
                                elif pt1.X >= pt6.X and pt1.Y >= pt6.Y:
                                    angle1 = angle0 -radians(360)
                                    angle2 = -angle0 -radians(180)
                                elif pt1.X <= pt6.X and pt1.Y >= pt6.Y:
                                    angle1 = angle0 - radians(360)
                                    angle2 = -angle0 - radians(180)
                                ElementTransformUtils.RotateElement(doc, ct2.Id, ct2.Location.Curve, angle1)
                                ct2.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('ct2')
                                ElementTransformUtils.RotateElement(doc, ct4.Id, ct4.Location.Curve,angle2)
                                ct4.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('ct4')


                            lst_ct = [ct1, ct2, ct3, ct4, ct5]

                            for _ in lst_ct:
                                _.get_Parameter(BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM).Set(weight)
                                _.get_Parameter(BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM).Set(height)

                            fittings = []
                            for con_1 in cable_tray.ConnectorManager.Connectors:
                                for con_2 in con_1.AllRefs:
                                    if str(con_2.Owner.Category.Name) == 'Соединительные детали кабельных лотков':
                                        fittings.append(con_2.Owner)


                            cable_trays.append(ct5)
                            doc.Delete(cable_tray.Id)



                            for ct in range(len(lst_ct) - 1):
                                cb1 = lst_ct[ct]
                                pt_start1 = cb1.Location.Curve.GetEndPoint(0)
                                pt_end1 = cb1.Location.Curve.GetEndPoint(1)
                                cb2 = lst_ct[ct + 1]
                                pt_start2 = cb2.Location.Curve.GetEndPoint(0)
                                pt_end2 = cb2.Location.Curve.GetEndPoint(1)
                                con1start, con1end = None, None

                                for con in cb1.ConnectorManager.Connectors:
                                    if con.Origin.IsAlmostEqualTo(pt_start1):
                                        con1start = con
                                    elif con.Origin.IsAlmostEqualTo(pt_end1):
                                        con1end = con

                                con2start, con2end = None, None

                                for con in cb2.ConnectorManager.Connectors:
                                    if con.Origin.IsAlmostEqualTo(pt_start2):
                                        con2start = con
                                    elif con.Origin.IsAlmostEqualTo(pt_end2):
                                        con2end = con

                                if con1end != None and con2start != None:
                                    con1end.ConnectTo(con2start)
                                    try:
                                        doc.Create.NewElbowFitting(con1end, con2start)
                                    except:
                                        continue

                            couple_1 = [ct1]
                            couple_2 = [ct5]

                            couples = [couple_1, couple_2]

                            for fitting in fittings:
                                for fcon_1 in fitting.MEPModel.ConnectorManager.Connectors:
                                    for fcon_2 in fcon_1.AllRefs:
                                        if str(fcon_2.Owner.Category.Name) == 'Кабельные лотки':
                                            if fitting.Location.Point.DistanceTo(ct1.Location.Curve.GetEndPoint(
                                                    0)) < fitting.Location.Point.DistanceTo(
                                                    ct5.Location.Curve.GetEndPoint(1)):
                                                couple_1.insert(0, fcon_2.Owner)
                                            else:
                                                couple_2.append(fcon_2.Owner)
                                doc.Delete(fitting.Id)

                            # """___________________________________________________"""
                            # """Необходимо вынести в отдельную функци, то, что ниже"""
                            for couple in couples:
                                for ct in range(len(couple) - 1):
                                    cb1 = couple[ct]
                                    pt_start1 = cb1.Location.Curve.GetEndPoint(0)
                                    pt_end1 = cb1.Location.Curve.GetEndPoint(1)
                                    cb2 = couple[ct + 1]
                                    pt_start2 = cb2.Location.Curve.GetEndPoint(0)
                                    pt_end2 = cb2.Location.Curve.GetEndPoint(1)
                                    con1start, con1end = None, None

                                    for con in cb1.ConnectorManager.Connectors:
                                        if con.Origin.IsAlmostEqualTo(pt_start1):
                                            con1start = con
                                        elif con.Origin.IsAlmostEqualTo(pt_end1):
                                            con1end = con

                                    con2start, con2end = None, None

                                    for con in cb2.ConnectorManager.Connectors:
                                        if con.Origin.IsAlmostEqualTo(pt_start2):
                                            con2start = con
                                        elif con.Origin.IsAlmostEqualTo(pt_end2):
                                            con2end = con

                                    if con1end != None and con2start != None:
                                        con1end.ConnectTo(con2start)
                                        try:
                                            doc.Create.NewElbowFitting(con1end, con2start)
                                        except:
                                            continue
                        # """Необходимо вынести в отдельную функци, то, что выше"""
                        # """---------------------------------------------------"""

                            _Flag = True
                            break

t.Commit()