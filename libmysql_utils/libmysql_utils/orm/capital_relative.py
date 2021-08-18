from libmysql_utils.orm.form import formCapitalRelativeMatrix
from libmysql_utils.mysql8 import mysqlMeta, mysqlHeader

class FormORMCapRelative(mysqlMeta):
    database = 'analysis'
    table_name = 'capital_relative_matrix'
    def __init__(self, acc: str, pw: str, host='115.159.1.221'):
        header = mysqlHeader(acc, pw, self.database, host)
        super().__init__(header)

    def get_null_pair(self, n=100):
        result = self.session.query(formCapitalRelativeMatrix.stock_1, formCapitalRelativeMatrix.stock_2).filter(formCapitalRelativeMatrix.relative.is_(None)).limit(n).all()
        return list(result)

    def get_relative(self, stock_1, stock_2):
        

event = FormORMCapRelative('stock', 'stock2020')
event.get_null_pair()