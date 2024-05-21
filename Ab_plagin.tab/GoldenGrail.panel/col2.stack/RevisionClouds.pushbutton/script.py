#-*- coding: utf-8 -*-

__title__ = "Revision"
__doc__   = "..."

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

import Autodesk
from Autodesk.Revit.DB.Electrical import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import RevisionCloud
from Autodesk.Revit.UI import *
from pyrevit import revit, forms
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB import BoundingBoxXYZ
from Autodesk.Revit.DB import Line, XYZ
from Autodesk.Revit.DB.Structure import StructuralType

def get_type_by_name(type_name):
    param_type  = ElementId(BuiltInParameter.ELEM_TYPE_PARAM)
    f_param     = ParameterValueProvider(param_type)
    evaluator   = FilterStringEquals()
    f_rule      = FilterStringRule(f_param, evaluator, type_name)
    filter_type_name = ElementParameterFilter(f_rule)
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericAnnotation).WherePasses(filter_type_name).WhereElementIsNotElementType().ToElements()



doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
sheets_withoutRevision = []
sheets_withRevision    = []
sheets_hasAlpha        = []

t = Transaction(doc,__title__)
t.Start()

#Данная часть кода отвечает за запись трех последних изменений в семейство изменений на титульный лист.
revision_clouds     = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()
dct_revision_clouds = {}

if len(revision_clouds) != 0:
    for revCloud in revision_clouds:
        num_revCloud      = (revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_NUM).AsString()).rstrip('‪')
        if num_revCloud in dct_revision_clouds:
            continue
        else:
            date_revCloud     = revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_DATE).AsString()
            num_doct_revCloud = revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_ISSUED_TO).AsString()
            dct_revision_clouds[num_revCloud] = [date_revCloud, num_doct_revCloud]

sorted_num_revCloud = sorted(dct_revision_clouds.keys(), reverse= True)
sorted_num_revCloud = sorted_num_revCloud[:3] if len(sorted_num_revCloud ) > 3 else sorted_num_revCloud

for family_instance in get_type_by_name('ZH_Титул_Изменения'):
    if len(sorted_num_revCloud) < 3:
        for i in range(1,4):
            p_num_rev = family_instance.LookupParameter('Изм{0}'.format(i)).Set('')
            p_num_doc = family_instance.LookupParameter('Ном.док.{0}'.format(i)).Set('')
            p_date = family_instance.LookupParameter('Дата{0}'.format(i)).Set('')
        doc.Regenerate()
    for num, num_dct in enumerate(sorted_num_revCloud, 1):
        num_date_dct = dct_revision_clouds[num_dct][0]
        num_doc_dct  = dct_revision_clouds[num_dct][1]

        p_num_rev    = family_instance.LookupParameter('Изм{0}'.format(num)).Set('{0}'.format(num_dct))
        p_num_doc    = family_instance.LookupParameter('Ном.док.{0}'.format(num)).Set(num_doc_dct)
        p_date       = family_instance.LookupParameter('Дата{0}'.format(num)).Set(num_date_dct)





for sheet in sheets:
    filterRevision              = ElementClassFilter(RevisionCloud)
    dependent_Revision_elements = sheet.GetAllRevisionCloudIds()

    p_Note = sheet.LookupParameter('ADSK_Примечание')

    if not len(dependent_Revision_elements) == 0:
        sheets_withRevision.append(sheet)
        my_dict = {}

        for i in dependent_Revision_elements:
            nameRevisionCloud = doc.GetElement(i).get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_NUM).AsString()
            if 'Зам.' in doc.GetElement(i).Name or 'Нов.' in doc.GetElement(i).Name:
                my_dict[nameRevisionCloud] = '-'
                continue
            if nameRevisionCloud in my_dict.keys():
                my_dict[nameRevisionCloud] +=1
            else:
                my_dict[nameRevisionCloud] = 1

###Сортируем 'my_dict' через zip, поскольку сортировка по ключам словарям по какой-то причине не сортируется###
        keys_lst   = [key for key in my_dict.keys()]

        values_lst = [value for value in my_dict.values()]

        ziped_lst = zip(keys_lst,values_lst)
        sorted_ziped_lst = sorted(ziped_lst,key =lambda x: (x[0]))

        new_lst_keys   = [key[0] for key in sorted_ziped_lst]
        new_lst_values = [value[1] for value in sorted_ziped_lst]

        filter = ElementClassFilter(FamilyInstance)
        dependent_elements = sheet.GetDependentElements(filter)

        necessaryTitleBlock = None
        for dElement in dependent_elements:
            if doc.GetElement(dElement).Category.BuiltInCategory == BuiltInCategory.OST_TitleBlocks:
                necessaryTitleBlock = doc.GetElement(dElement)
                break

        if isinstance(necessaryTitleBlock, FamilyInstance):

            # t = Transaction(doc,__title__)
            # t.Start()

            parameters = [necessaryTitleBlock.LookupParameter('Ф3_Стр'+str(iter)+'_КолУч') for iter in range(1,5)]
            param_set  = [p.Set('') for p in parameters]
            doc.Regenerate()
            counter = len(new_lst_keys)
            if counter < 5:
                for value,param in zip(new_lst_values,parameters):
                    if isinstance(param, Parameter):
                        try:
                            param.Set(str(value))
                        except:
                            raise ValueError('ValueError')
            else:
                new_lst_values = new_lst_values[-4:]
                for value,param in zip(new_lst_values,parameters):
                    if isinstance(param, Parameter):
                        try:
                            param.Set(str(value))
                        except:
                            import traceback
                            print(traceback.print_exc())

        if p_Note:
            itog_lst = []
            for i in keys_lst:
                if i not in itog_lst:
                    itog_lst.append('{}'.format(i))
            txt = ';'.join(itog_lst)
            p_Note.Set(txt)


    else:
        sheets_withoutRevision.append(sheet)
        filter = ElementClassFilter(FamilyInstance)
        dependent_elements  = sheet.GetDependentElements(filter)
        necessaryTitleBlock = None
        for dElement in dependent_elements:
            if doc.GetElement(dElement).Category.BuiltInCategory == BuiltInCategory.OST_TitleBlocks:
                necessaryTitleBlock = doc.GetElement(dElement)
                break

        parameters = [necessaryTitleBlock.LookupParameter('Ф3_Стр' + str(iter) + '_КолУч') for iter in range(1, 5)]
        param_set  = [p.Set('') for p in parameters if p is not None]

        if p_Note:
            p_Note.Set('')

t.Commit()

TaskDialog.Show('Уведомление','Процесс прошел успешно!')