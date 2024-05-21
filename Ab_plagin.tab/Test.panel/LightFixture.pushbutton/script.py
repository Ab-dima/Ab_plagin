#-*- coding: utf-8 -*-

__title__ = 'Расстановка светильников'
__doc__ = 'Показывает информацию об элементе'

import sys

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ IMPORT
# =============================================
# Regular + Autodesk

import sys

from pyrevit.forms import WPFWindow
from Autodesk.Revit.DB import Line
from Autodesk.Revit.DB import UnitUtils
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import revit, forms




from Autodesk.Revit.DB import Electrical
from Autodesk.Revit.DB.Electrical import CableTray,ElectricalSystem, ElectricalCircuitPathMode

from System.Collections.Generic import List

from rpw.ui.forms import Label, TextBox, CheckBox, Separator,ComboBox, Button, TextInput, FlexForm, Alert

from math import sqrt

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# =============================================
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
all_phases = list(doc.Phases)
phase = all_phases[-1]

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel
active_level_elevation = active_level.Elevation



# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# =============================================

def convector_from_mm(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertToInternalUnits(value,UnitTypeId.Millimeters)

def convector_to_mm(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertFromInternalUnits(value,
                                                  UnitTypeId.Millimeters)

def get_type_by_name(type_name):
    param_type  = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
    f_param     = ParameterValueProvider(param_type)
    evaluator   = FilterStringEquals()
    f_rule      = FilterStringRule(f_param, evaluator, type_name)
    filter_type_name = ElementParameterFilter(f_rule)
    return FilteredElementCollector(doc).WherePasses(filter_type_name).WhereElementIsElementType().FirstElement()


def create_line(pt1, pt2):
    curve = Line.CreateBound(pt1, pt2)
    try:
        line  = doc.Create.NewDetailCurve(active_view, curve)
    except:
        sys.exit()
    return line


def create_point(adder):
    if isinstance(adder, XYZ):
        try:
            pt = uidoc.Selection.PickPoint().Add(adder)
        except:
            sys.exit()
    return pt



class CustomISelectionFilter(ISelectionFilter):
    """Filter user selection to certain element."""
    def __init__(self, cats):
        self.cats = cats
    def AllowElement(self, e):
        if str(e.Category.Id) == str(self.cats):
        #if e.Category.Name == "Walls"
            return True
        return False





# ╔╦╗╔═╗ ╦ ╔╗╔
# ║║║╠═╣ ║ ║║║
# ╩ ╩╩ ╩ ╩ ╝╚╝ MAIN
# =============================================
def get_value(*args):
    global values
    global element

    value = starting_window.get_values(*args)
    text_box_1 = starting_window.values['textbox1']
    text_box_2 = starting_window.values['textbox2']
    text_box_3 = starting_window.values['textbox3']


    try:
        element = doc.GetElement(uidoc.Selection.PickObject(ObjectType.Element,CustomISelectionFilter('-2001120'), 'Выберите светильник'))
    except:
        sys.exit()



    form_components_sw = [
                      Label('Высота установки h, мм:'),
                      TextBox('textbox1', Text = text_box_1),
                      Label('Количество по горизонтали ↔'),
                      TextBox('textbox2', Text = text_box_2),
                      Label('Количество по вертикали ↕'),
                      TextBox('textbox3', Text = text_box_3),
                      Separator(),
                      Button('Готово')]
    new_window = FlexForm("Исходные данные", form_components_sw)
    new_window.show()
    values = new_window.values




values = ''
element = ''

lighting_fixtures_types = [i.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsValueString() for i in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LightingFixtures).WhereElementIsElementType().ToElements()]

form_components_sw = [Button('Выбрать с плана', on_click=get_value),
                      Label('Выбрать из списка:'),
                      ComboBox('combobox1',lighting_fixtures_types),
                      Separator(),
                      Label('Высота установки h, мм:'),
                      TextBox('textbox1', Text = '2700'),
                      Label('Количество по горизонтали ↔'),
                      TextBox('textbox2', Text = '1'),
                      Label('Количество по вертикали ↕'),
                      TextBox('textbox3', Text = '1'),
                      Separator(),
                      Button('Готово')]

starting_window = FlexForm("Исходные данные", form_components_sw)

if starting_window.show() == False:
    sys.exit()






if len(values) > 0:
    values = values
else:
    values = starting_window.values





height_ceiling = XYZ(0,0,convector_from_mm(float(values['textbox1']))-active_level_elevation)
row = int(values['textbox3'])
column = int(values['textbox2'])


if element == '':
    name_light_fixtures = values['combobox1']
else:
    name_light_fixtures = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()


light_fixture_type = get_type_by_name(name_light_fixtures)


pt1 = create_point(height_ceiling)


t = Transaction(doc,__title__)
t.Start()

try:
    line1 = create_line(XYZ(pt1.X, pt1.Y, 0), XYZ(pt1.X,pt1.Y+20, 0))
    line2 = create_line(XYZ(pt1.X+0.25, pt1.Y+1.25, 0), XYZ(pt1.X,pt1.Y+2, 0))
    line3 = create_line(XYZ(pt1.X-0.25, pt1.Y+1.25, 0), XYZ(pt1.X,pt1.Y+2, 0))

    pt2 = create_point(height_ceiling)

    line4 = create_line(XYZ(pt2.X, pt2.Y, 0), XYZ(pt2.X+20,pt2.Y, 0))
    line5 = create_line(XYZ(pt2.X+1.25, pt2.Y-0.25, 0), XYZ(pt2.X+2,pt2.Y, 0))
    line6 = create_line(XYZ(pt2.X+1.25, pt2.Y+0.25, 0), XYZ(pt2.X+2,pt2.Y, 0))

    pt3 = create_point(height_ceiling)
except:
    t.Commit()
    sys.exit()


element_to_delete = List[ElementId]([line1.Id,line2.Id,line3.Id,line4.Id,line5.Id,line6.Id])
doc.Delete(element_to_delete)


# pt2 = XYZ(pt1.X, pt2.Y,0).Add(height_ceiling)

gorizontal = pt2.DistanceTo(pt3)
value_2gor = gorizontal/column
value_1gor = value_2gor/2

vartical = pt2.DistanceTo(pt1)
value_2vert = vartical/row
value_1vert = value_2vert/2




iter_vert = 0
iter_gor  = 0

for i in range(row):
    iter_gor = 0
    if iter_vert == 0:
        pt = pt2.Add(XYZ(0, -value_1vert, 0))
        iter_vert += 1
    else:

        pt = pt.Add(XYZ(0, -value_2vert, 0))
        pt = XYZ(pt2.X, pt.Y,pt.Z)

    try:
        for i in range(column):
            if iter_gor == 0:
                pt = pt.Add(XYZ(value_1gor,0,0))
                element = doc.Create.NewFamilyInstance(pt, light_fixture_type, active_level, StructuralType.NonStructural)
                iter_gor+=1
            else:
                pt = pt.Add(XYZ(value_2gor, 0, 0))
                element = doc.Create.NewFamilyInstance(pt, light_fixture_type, active_level, StructuralType.NonStructural)
    except:
        t.Commit()
        Alert('Светильник:\n{0}\nне является активным'.format(name_light_fixtures), title='Ошибка', exit=True)
        sys.exit()
t.Commit()

