#-*- coding: utf-8 -*-

__title__ = "Расчет длины\n электр.цепи"
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


# t = Transaction(doc,__title__)
# t.Start()
#
# electrical_circuits = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ElectricalCircuit).WhereElementIsNotElementType().ToElements()
#
# for i in electrical_circuits:
#     if str(i.CircuitPathMode) == 'FarthestDevice' or str(i.CircuitPathMode) == 'Custom':
#         i.CircuitPathMode = ElectricalCircuitPathMode.AllDevices
#     # elif str(i.CircuitPathMode) == 'FarthestDevice':
#     #     i.CircuitPathMode = ElectricalCircuitPathMode.AllDevices
#     doc.Regenerate()
#
# for i in electrical_circuits:
#     print(i.CircuitPathMode)
#
# # def get_length(i):
# #             if str(i.CircuitPathMode) == 'AllDevices':
# #                 k.CircuitPathMode = ElectricalCircuitPathMode.FarthestDevice
# #             elif str(i.CircuitPathMode) == 'FarthestDevice':
# #                 k.CircuitPathMode = ElectricalCircuitPathMode.AllDevices
# #             doc.Regenerate()
# #             l = decimal_to_mm(i.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM).AsDouble())
# #             return l
# #
# #         lst_l[1] = []
# #         lst_l[2] = []
# #         for i in Electrical_Circuits:
# #             lst_l[1].append(decimal_to_mm(i.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM).AsDouble()))
# #         for k in Electrical_Circuits:
# #             lst_l[2].append(get_length(k))
# #
# #         for i, j in zip(lst_l[1], lst_l[2]):
# #             print('{} + {}'.format(i, j))
# t.Commit()

# element_line = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds()]
#
# lenght = 0
# for i in element_line:
#     lenght+=float(i.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsValueString())/[1]000
#
# print("{0} м".format(lenght))

from math import pi, degrees, radians
import random

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



lst_pt_to_delete = []
count_error = 0

form_components_sw = [Label('Введите значение высоты потолка'),
                      TextBox('textbox1', Text = '3000'),
                      CheckBox('checkbox1','Имя нагрузки'),
                      CheckBox('checkbox2','Добавить точку', default=0),
                      Separator(),
                              Button('Готово')]
starting_window = FlexForm("Исходные данные", form_components_sw)
if starting_window.show() == False:
    sys.exit()

cable_trays = []

counter_el_circuit = 0
electrical_circuits = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds() if doc.GetElement(i).Category.Name == 'Электрические цепи']


for electrical_circuit in electrical_circuits:
    counter_el_circuit+=1

    try:
        height_ceiling = float(starting_window.values['textbox1'])
    except:
        count_error+=1
        forms.alert(msg='Неккоректное значение высоты', title='Ошибка', ok=True)
        sys.exit()

    #Определяем панель к который подключена электрическая цепь, а так же высоту установки
    panel = doc.GetElement(electrical_circuit.BaseEquipment.Id)
    panel_level_height = doc.GetElement(panel.LevelId).get_Parameter(BuiltInParameter.LEVEL_ELEV).AsDouble()
    height_ceiling     = decimal_to_mm(mm_to_decimal(height_ceiling)+panel_level_height)



    #Задаем электрической цепи режим траектории - "Все устройства"
    t = Transaction(doc, __title__)
    t.Start()
    electrical_circuit.CircuitPathMode = ElectricalCircuitPathMode.AllDevices
    doc.Regenerate()
    t.Commit()

    #Определяем элементы, которые входят в электрическую цепь

    electrical_fixtures        = [i for i in electrical_circuit.Elements]

    height_electrical_fixtures_and_panel = [float(i.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).AsValueString()) for
                                  i in electrical_fixtures if i.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM) is not None]
    height_electrical_fixtures_and_panel.append(float(panel.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).AsValueString()))
    # Если высота прокладки равна хотя бы одному положению элементов, подключенных к этой сети, то высоту прокладки делaем на [1] мм выше
    if height_ceiling in height_electrical_fixtures_and_panel:
        height_ceiling = height_ceiling+2

    #Определяем точки расположения в пространстве элементов подключенных к электрической цепи
    point_elFixtures = [i.Location.Point for i in electrical_fixtures]
    #Определяем точку коннектора электроической сети у эл прибора.
    point_Connector_elFixtures = [j.Origin.ToString() for i in electrical_fixtures for j in i.MEPModel.ConnectorManager.Connectors] # !@!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!





    lst_point_elCircuit = electrical_circuit.GetCircuitPath()
    first_point_panel_connector = lst_point_elCircuit[0]



    itog_points_lst_to_set = [first_point_panel_connector]  #[1]



    z_axis     = XYZ(0,0,1)

    step = 0.02
    # supplement = -(random.uniform(0.01, 0.05) / step) * step
    supplement = -step


    str_point_elFix = [i.ToString() for i in point_elFixtures]
    str_point_elCir = [i.ToString() for i in lst_point_elCircuit]




    pozition_vector = 0
    for i in range(len(lst_point_elCircuit)):
        if i == len(lst_point_elCircuit)-1:
            itog_points_lst_to_set.append(lst_point_elCircuit[i])
        else:
            point_end              = lst_point_elCircuit[i+1]
            point_start            = lst_point_elCircuit[i]
            str_point_end          = point_end.ToString()
            vector                 = point_end-point_start
            angle_betwen_z_axis    = degrees(vector.AngleTo(z_axis))
            if angle_betwen_z_axis > 89 and angle_betwen_z_axis < 91:
                """
                Если участок ГОРИЗОНТАЛЬНЫЙ
                """
                if pozition_vector == 0:
                    itog_points_lst_to_set.append(XYZ(point_start.X,point_start.Y, mm_to_decimal(height_ceiling))) #[2]
                    itog_points_lst_to_set.append(XYZ(point_end.X, point_end.Y, mm_to_decimal(height_ceiling)))  # [3]
                    if str_point_end in point_Connector_elFixtures:
                        itog_points_lst_to_set.append(point_end)  # [4]
                        point_end_addX = point_end.Add(XYZ(supplement, 0, 0))
                        itog_points_lst_to_set.append(point_end_addX)  # [5]
                        pozition_vector = 2
                    else:
                        pozition_vector = 1
                elif pozition_vector == 1:
                    itog_points_lst_to_set.append(XYZ(point_end.X, point_end.Y, mm_to_decimal(height_ceiling)))  # [3]
                    if str_point_end in point_Connector_elFixtures:
                        itog_points_lst_to_set.append(point_end)  # [4]
                        point_end_addX = point_end.Add(XYZ(supplement, 0, 0))
                        itog_points_lst_to_set.append(point_end_addX)  # [5]
                        pozition_vector = 2
                elif pozition_vector == 2:
                    itog_points_lst_to_set.append(XYZ(point_start.X, point_start.Y, mm_to_decimal(height_ceiling)).Add(XYZ(supplement,0,0)))  # [2]
                    itog_points_lst_to_set.append(XYZ(point_end.X, point_end.Y, mm_to_decimal(height_ceiling)))  # [3]
                    if str_point_end in point_Connector_elFixtures:
                        itog_points_lst_to_set.append(point_end)  # [4]
                        point_end_addX = point_end.Add(XYZ(supplement, 0, 0))
                        itog_points_lst_to_set.append(point_end_addX)  # [5]
                        pozition_vector = 2
                    else:
                        pozition_vector = 1
            else:
                """
                # Если участок ВЕРТИКАЛЬНЫЙ
                """
                if pozition_vector == 2:
                    # lst_pt_to_delete.append(point_end.ToString())
                    itog_points_lst_to_set.append(point_end.Add(XYZ(supplement,0,0)))  # [4]
                    pozition_vector = 2
                else:
                    itog_points_lst_to_set.append(point_end)            #[4]
                    point_end_addX = point_end.Add(XYZ(supplement,0,0))
                    itog_points_lst_to_set.append(point_end_addX)             #[5]
                    pozition_vector = 2

    if starting_window.values['checkbox2']:
        point_pick = uidoc.Selection.PickPoint()
        point3 = XYZ(point_pick.X, point_pick.Y, mm_to_decimal(height_ceiling))
        point2 = XYZ(itog_points_lst_to_set[2].X, point3.Y,mm_to_decimal(height_ceiling))
        point4 = XYZ(point3.X, itog_points_lst_to_set[3].Y,mm_to_decimal(height_ceiling))

        itog_points_lst_to_set.insert(3, point4)
        itog_points_lst_to_set.insert(3, point3)
        itog_points_lst_to_set.insert(3, point2)


    """Данный код блока не обязательный, но используется как проверка, и работает следующим образом:
    Создаем цикл по итоговым полученным точкам, и раз за разом берем первую и последующую точки, если DistanceTo() у них меньше 0.00[4] дюйма, то берем последнюю точку на этом этапе цикла, где
    произошла ошибка, добавляем к координате X 0.0[1] дюйм, и затем заменяем точку, на только что измененную в данном этапе цикла. Поскольку при построении электрических цепей должны
    быть только либо горизонтальные, либо вертикальные участки, то при переходе к следующему этапу цикла нам необходимо в последующей конечной точке также сделать приращение на 0.0[1] дюйма,
    по X координате.
    Если DistanceTo() больше 0,0[4] дюйма, то переходим к след этапу цикла без изменений.
    """

    # counter_replace = 0
    # for i in range(len(itog_points_lst_to_set)):
    #     pt_start = itog_points_lst_to_set[i]
    #     for j in range(len(itog_points_lst_to_set)):
    #         pt_end = itog_points_lst_to_set[j]
    #         if pt_start != pt_end:
    #             if counter_replace == 0:
    #                 distanceBetweenPt = pt_start.DistanceTo(pt_end)
    #                 if distanceBetweenPt < 0.00[4]:
    #                     pt_end = pt_end.Add(XYZ(0.0[1],0,0))
    #                     itog_points_lst_to_set[j] = pt_end
    #                     counter_replace = [1]
    #                 else:
    #                     continue
    #             elif counter_replace == [1]:
    #                 pt_end = pt_end.Add(XYZ(0.0[1], 0, 0))
    #                 itog_points_lst_to_set[i] = pt_end
    #                 counter_replace = 0
    #         else:
    #             continue


    """
    В данном блоке снизу, будет код, который является костылем, нужно проработать более универсальный алгоритм по которому можно учесть повторные  подьемы эл.цепи
    На данный момент мысль будущего алгоритма следующая. Пройтись по итоговым точкам, и если в радиусе какого-то значения находится какая-то точка из списка, то мы удаляем эту точку.
    Если опуск вертикальный, то должно "удалиться" две точки(на самом деле они останутся, просто будем создавать новый список без этих точек для расчета). После чего точки находяся в
    пространственном порядке, и от начальной, до конечно точки будем выислать DistanceTo, тем самым определяя длину. Касаемо вертикальных участков, поскольку мы удаляем две точки, и
    чтобы не было диагональных линий, нужно предусмотреть, что если участок вертикальный, то начальная точка, которая была в начале вертикального участка, осталась так же начальной и для
    следующего участка, поскольку если этого не сделать, то получится диагональный участок.

    В данном случае, костыль, описанный ниже делает следующее. Начинаем цикл по электрическим приборам, затем проверяем, если координата Z эл.прибора равна последней координате итогового
    списка, то мы пропускаем этот участок. Затем определяем разницу высот, между
    требуемой и той, что обладает эл.прибор. До этого мы создали счетчик длины, равный 0, и скаждой итерацией по эл.прибором дополняем эту длину, итоговый результат записываем в параметр
    проекта AB_Длина. Поскольку внутренние единици ревита это ..., а у нас в программе стоят миллиметры, тем самым когда мы передаем параметру AB_Длина при помощи Set(значение), то он
    автоматически переводит в нужные единицы.
    """
    try:
        t = Transaction(doc, __title__)
        t.Start()
        electrical_circuit.SetCircuitPath(itog_points_lst_to_set)
        electrical_circuit.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('Успешно')
        doc.Regenerate()
        t.Commit()
    except:
        count_error+=1
        forms.alert(msg='Ошибка в построении.\nНомер цепи: {}'.format(electrical_circuit.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER).AsValueString()),title='Ошибка',ok=True)
        electrical_circuit.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('Ошибка')
        t.Commit()


    lenght_subtraction = 0
    lenght_elCirc = electrical_circuit.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM).AsDouble()


    t = Transaction(doc,__title__)
    t.Start()

    delete_counter = []

    for i in electrical_fixtures:
        for con in i.MEPModel.ConnectorManager.Connectors:
            if str(con.Domain) == 'DomainElectrical':
                pt_connector = con.Origin
                if pt_connector.ToString() == itog_points_lst_to_set[-1].ToString():
                    delete_counter.append(1)
                    break
                else:
                    delete_counter.append(2)
                    substraction = mm_to_decimal(height_ceiling) - pt_connector.Z
                    lenght_subtraction+=substraction
                    break

    electrical_circuit.LookupParameter('AB_Длина').Set(lenght_elCirc-lenght_subtraction)
    t.Commit()

    # uniqe_points = {}
    # for i in point_elFixtures:
    #     x = float(str(i.X))
    #     y = float(str(i.Y))
    #     z = float(str(i.Z))
    #     if (x, y) not in uniqe_points or z < uniqe_points[(x, y)]:
    #         uniqe_points[(x, y)] = z
    # result = [XYZ(x, y, z) for (x, y), z in uniqe_points.items()]
    #
    # true_false_lst = [i.ToString() == point_Connector_elFixtures[-1] for i in result]
    # for i in result:
    #     subtraction = mm_to_decimal(height_ceiling) - i.Z
    #     lenght_subtraction += subtraction
    #     continue
    # if True not in true_false_lst:
    #     subtraction = mm_to_decimal(height_ceiling) - point_elFixtures[-1].Z
    #     lenght_subtraction -= subtraction
    #
    #
    # t = Transaction(doc,__title__)
    # t.Start()
    # electrical_circuit.LookupParameter('AB_Длина').Set(lenght_elCirc-lenght_subtraction)
    # t.Commit()


#
#     """_____________________________"""
#     """Необязательная часть_1 начало"""
#     """_____________________________"""
#
#     if starting_window.values['checkbox1'] == 1:
#         # В этой части код блока создаем текст на основание комментария подключеннных приборов и записываем его в параметр имени нагрузки эл.цепи
#         elFixtures_param_comment = []
#         for i in electrical_fixtures:
#             comment_of_elFixt = i.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
#             if comment_of_elFixt is not None and comment_of_elFixt != '':
#                 elFixtures_param_comment.append(comment_of_elFixt.AsValueString())
#         elFixtures_param_comment = [i if i != None else 'Пустое поле!' for i in list(set(elFixtures_param_comment))]
#         try:
#             elCirc_name = ";".join(elFixtures_param_comment)
#         except:
#             count_error += 1
#             forms.alert(msg='Ошибка при создании имени нагрузки', title='Ошибка', ok=True)
#
#         try:
#             t = Transaction(doc, __title__)
#             t.Start()
#             str_to_write = elCirc_name
#             electrical_circuit.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_NAME).Set(str_to_write)    #.Set(str(elCirt_name))
#
#             t.Commit()
#         except:
#             count_error += 1
#             forms.alert(msg='Ошибка при записи имени нагрузки', title='Ошибка', ok=True)
#             t.Commit()
#     """Необязательная часть_1 окончание"""
#     """‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾"""
#
# forms.alert(msg='Операция завершена.\nКоличество ошибок: {0}\nПроанализировано цепей: {1}'.format(count_error, counter_el_circuit), title='Ошибка', ok=True)






# lines  = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds()]
# dlina = 0
# for i in lines:
#     dlina+=i.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
# print(decimal_to_mm(dlina))





