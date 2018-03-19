# -*- coding: utf-8 -*-
import os
import xlwt
import xlrd
from xml.dom.minidom import parse
import xml.dom.minidom

from enum_util import get_enum_dict

#定义字段模型
class Field :
    def __init__(self,field_name,field_desc,field_type,field_value_dict):
        self.field_name = field_name
        self.field_desc = field_desc
        self.field_type = field_type
        self.field_value_dict = field_value_dict

#定义表模型
class Table :
    def __init__(self,table_name,table_desc,field_list):
        self.table_name = table_name
        self.table_desc = table_desc
        self.field_list = field_list


# 获取某目录下的文件名（含子目录）
def get_file_list():
    #获取目标文件所在的目录
    current_path = os.path.dirname(__file__)  # 获得d所在的目录,即d的父级目录
    parent_path = os.path.dirname(current_path)
    target_path = parent_path + "/data/xml/at/"
    #获取指定目录下的所有文件名（含子目录）
    list = []
    for root, dirs, files in os.walk(target_path):
        for filespath in files:
            list.append(os.path.join(root,filespath))
    return list

#读取业务表的xml文件，获取表实体列表
def get_tables():
    print "------表实体文件读取------开始"

    #定义本方法返回结果：key为表文件名，value为该文件里的表实体
    table_category_dict = {}
    #获取目标文件
    list = get_file_list()
    #获取枚举数据
    enum_dict = get_enum_dict()
    for file in list:
        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(file)
        root = DOMTree.documentElement

        #根节点的信息即代表该表分类的信息
        table_category = root.getAttribute("id")+"-"+root.getAttribute("longname")

        # 遍历节点
        table_list = []
        table_nodes = root.getElementsByTagName("table")
        for table in table_nodes:
            # 源文件里，每个节点的子节点下有隐含的换行的text节点，此处需过滤掉
            if table.nodeName != "table":
                continue
            table_name = table.getAttribute("id")
            table_desc = table.getAttribute("longname")
            field_list = []
            field_nodes = table.childNodes[1]

            for field in field_nodes.childNodes :
                # 源文件里，每个节点的子节点下有隐含的换行的text节点，此处需过滤掉
                if field.nodeName != "field":
                    continue
                field_name = field.getAttribute("id")
                field_desc = field.getAttribute("longname")
                field_type = field.getAttribute("type")
                (field_type,type_code) = field_type.split(".")
                # 字典里匹配不到对应key，则默认返回None
                field_value_dict = enum_dict.get(type_code,None)

                field_info = Field(field_name,field_desc,field_type,field_value_dict)
                field_list.append(field_info)

            table_info = Table(table_name,table_desc,field_list)

            table_list.append(table_info)

        table_category_dict[table_category] = table_list

    print "------表实体文件读取------完毕"

    print "------合计共有"+str(len(table_category_dict))+"个表文件"

    return table_category_dict

#生成关于表分类的excel
def write_category_excel(table_category_dict):
    print "------表分类文件写入------开始"

    #创建一个excel
    file = xlwt.Workbook()
    # 创建一个sheet
    sheet = file.add_sheet(u'表分类', cell_overwrite_ok=True)
    # 写第一行
    row0 = [u'表分类名', u'表分类中文名', u'表名', u'表中文名']
    for i in range(0, len(row0)):
        sheet.write(0, i, row0[i]);

    # 写表分类的主体数据
    i, j = 1, 1
    for (table_category, table_list) in table_category_dict.items():
        #根据'-'截取，以获取表分类名、表分类中文名
        (category_name,category_desc) = table_category.split("-")
        #设置合并单元格的起始行、结束行
        col_start = i
        col_end = i + len(table_list) - 1  # 由于索引从0开始，故要减1
        #合并单元格，并写入数据
        sheet.write_merge(col_start, col_end, 0, 0, category_name)
        sheet.write_merge(col_start, col_end, 1, 1, category_desc)
        for table in table_list:
            sheet.write(j, 2, table.table_name)
            sheet.write(j, 3, table.table_desc)
            j += 1

        i += len(table_list)

    # 设置列宽
    sheet.col(0).width = 256 * 20
    sheet.col(1).width = 256 * 20
    sheet.col(2).width = 256 * 20
    sheet.col(3).width = 256 * 20

    file.save('../data/excel/表分类.xlsx')

    print "------表分类文件写入------完毕"


#将表数据写入到excel
def write_table_excel(table_category_dict):
    print "------表数据写入到excel------开始"

    # 第一行
    row0 = [u'字段名', u'字段中文名', u'字段取值', u'备注']

    #遍历表数据
    for (table_category,table_list) in table_category_dict.items() :
        # 创建excel文件，一个table_category对应一个excel文件
        file = xlwt.Workbook()
        # 根据'-'截取，以获取表分类名、表分类中文名
        (category_name, category_desc) = table_category.split("-")
        #一个table对应一个sheet
        for table in table_list :
            # 创建一个sheet
            sheet_name = table.table_name+"-"+table.table_desc
            sheet = file.add_sheet(sheet_name, cell_overwrite_ok=True)
            # 写入第一行
            for i in range(0, len(row0)):
                sheet.write(0, i, row0[i]);
            # 写入该表的字段数据
            i, j = 1, 1
            for field in table.field_list :
                if field.field_value_dict is not None:#字段有枚举值时
                    # 设置合并单元格的起始行、结束行
                    col_start = i
                    col_end = i + len(field.field_value_dict) - 1
                    # 合并单元格，并写入数据
                    sheet.write_merge(col_start, col_end, 0, 0, field.field_name)
                    sheet.write_merge(col_start, col_end, 1, 1, field.field_desc)
                    #写入字段枚举值
                    for (key, value) in field.field_value_dict.items():
                        sheet.write(j, 2, key + "-" + value)
                        j = j + 1
                    i += len(field.field_value_dict)
                else:
                    sheet.write(i, 0, field.field_name)
                    sheet.write(i, 1, field.field_desgc)
                    sheet.write(i, 2, "")
                    i = i + 1
                    j = i

            # 设置列宽
            sheet.col(0).width = 256 * 20
            sheet.col(1).width = 256 * 22
            sheet.col(2).width = 256 * 25
            sheet.col(3).width = 256 * 20

        #保存该excel
        file.save('../data/excel/'+table_category+'.xlsx')

    print "------表数据写入到excel------结束"

if __name__ == '__main__':
    # 获取所有的表分类信息
    all_tables = get_tables()

    #表分类文件写入到excel
    write_category_excel(all_tables)

    #表实体文件写入到excel
    write_table_excel(all_tables)
