import xlrd
from xlrd import XL_CELL_NUMBER


class Excel(object):
    """
    excel 工具库
    """
    def __init__(self, file_name, callback=None, date_format="%Y-%m-%d"):
        self.home = "/tmp"
        self.callback = callback
        self.date_format = date_format
        self.depth = 0
        self.wb = xlrd.open_workbook(file_name)

    def load_sheet_content(self, sheet_index=0):
        """
        加载文件内容
        :param file_content: 文件内容
        :param sheet_index: 索引
        :return:
        """
        title, data = [], []
        # self.wb = xlrd.open_workbook(file_content)
        sheet = self.wb.sheet_by_index(sheet_index)

        # 获取首行title
        for i in range(sheet.ncols):
            title.append(sheet.cell(0, i).value)

        # 打包文件content： unit格式为{"title1"："value1", "title2": "value2"}，最终打包成data列表
        for i in range(1, sheet.nrows):
            unit = {}
            for j in range(sheet.ncols):
                if sheet.cell(i, j).ctype == XL_CELL_NUMBER:
                    unit[title[j]] = f'{sheet.cell(i, j).value}'
                else:
                    unit[title[j]] = sheet.cell(i, j).value
            data.append(unit)
        return data
