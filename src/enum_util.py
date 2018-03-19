# -*- coding: utf-8 -*-
import xlwt
import xlrd
from xml.dom.minidom import parse
import xml.dom.minidom

#定义一个枚举类
class Enum :
    #filed_value_dict 指枚举值列表，为一个字典
    def __init__(self,field_name,field_desc,field_value_dict):
        self.field_name = field_name
        self.field_desc = field_desc
        self.field_value_dict = field_value_dict

# 读取枚举数据的xml文件
def read_enum_xml():
        print "------枚举数据文件读取------开始"
        source_file = "../data/xml/enum/BaseEnumType.e_schema.xml"
        enum_list = []
        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(source_file)
        collection = DOMTree.documentElement

        # 遍历节点
        node_list = collection.getElementsByTagName("restrictionType")
        for node in node_list:
            field_name = node.getAttribute("id")
            field_desc = node.getAttribute("longname")

            field_value_dict = {}
            for child in node.childNodes:
                # 源文件里，每个节点的子节点下有隐含的换行的text节点，此处需过滤掉
                if child.nodeName != "enumeration":
                    continue
                key = child.getAttribute("value")
                value = child.getAttribute("longname")
                field_value_dict[key] = value

            enum_info = Enum(field_name, field_desc, field_value_dict)
            enum_list.append(enum_info)

        print "------枚举数据文件读取------完毕"

        return enum_list

#将所有枚举放入到一个字典中,key为枚举字段名，value为该枚举字段的取值列表（为一个字典）
def get_enum_dict():
    enum_dict = {}
    enum_list = read_enum_xml()
    for enum_item in enum_list :
        enum_dict[enum_item.field_name] = enum_item.field_value_dict
    return enum_dict

#写入到枚举excel
def write_enum_excel(enum_list):
    print "------枚举数据写入到excel------开始"
    # 创建excel文件
    file = xlwt.Workbook()

    # 创建一个sheet
    sheet = file.add_sheet(u'枚举', cell_overwrite_ok=True)

    # 第一行
    row0 = [u'枚举字段名', u'字段中文名', u'枚举值', u'枚举值说明']
    for i in range(0,len(row0)):
        sheet.write(0,i,row0[i]);

    # 写入数据
    i, j = 1, 1
    for enum_item in enum_list :
        # 设置合并单元格的起始行、结束行
        col_start = i
        col_end = i+len(enum_item.field_value_dict)-1 #由于索引从0开始，故要减1
        # 合并单元格，并写入数据
        sheet.write_merge(col_start,col_end,0,0,enum_item.field_name)
        sheet.write_merge(col_start,col_end,1,1,enum_item.field_desc)
        for key in enum_item.field_value_dict:
            sheet.write(j,2,key)
            sheet.write(j,3,enum_item.field_value_dict[key])
            j += 1

        i += len(enum_item.field_value_dict)

    #设置列宽
    sheet.col(0).width = 256 * 20
    sheet.col(1).width = 256 * 20
    sheet.col(3).width = 256 * 20

    file.save('../data/excel/枚举.xlsx')

    print "------枚举数据写入到excel------完毕"


if __name__ == '__main__':
    enum_list = read_enum_xml()
    write_enum_excel(enum_list)