from libmysql_utils.mysql8 import mysqlMeta, mysqlHeader
from libmysql_utils.orm.form import formStockManager
import datetime
from sqlalchemy import update

class FormORMStockManager(mysqlMeta):
    database = 'stock'
    table_name = 'stock_manager'
    def __init__(self, acc: str, pw: str, host='115.159.1.221'):
        header = mysqlHeader(acc, pw, self.database, host)
        super().__init__(header)

    def init_stock(self, stock_code_list: list):
        for stock_code in stock_code_list:
            update_date = datetime.date.today().strftime('%Y-%m-%d')
            stock = formStockManager(stock_code=stock_code, create_date= update_date)
            self.session.add(stock)
            self.session.commit()

    def add_stock(self, stock_code: str, stock_name: str, orgId: str, short_code: str, flag: str):
        update_date = datetime.date.today().strftime('%Y-%m-%d')
        stock = formStockManager(
            stock_code=stock_code,
            stock_name=stock_name,
            orgId=orgId,
            short_code=short_code,
            flag=flag,
            create_date= update_date)
        self.session.add(stock)
        self.session.commit()

    def update_name(self, stock_code: str, stock_name: str):
        sql = update(formStockManager).where(formStockManager.stock_code==stock_code).values(stock_name=stock_name).execution_options(synchronize_session="fetch")
        self.session.execute(sql)
        self.session.commit()

    def update_stock(self, stock_code: str, args: dict):
        """
        args keys: stock_name, orgId, short_code, flag
        """
        sql = update(formStockManager).where(formStockManager.stock_code==stock_code).values(args).execution_options(synchronize_session="fetch")
        self.session.execute(sql)
        self.session.commit()

event = FormORMStockManager(acc='stock', pw='stock2020')

# event.add_stock('TEST002', 'TEST_STOCK', 'g0001', 'TEST', 't')

event.update_name('TEST002', 'TEST_STOCK_003')
event.update_stock('TEST002', {"stock_name": 'TEST_STOCK_003', "orgId": 'test002'})