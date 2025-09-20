from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import sys
import time
#to link with data base
import psycopg2

class main(QMainWindow):
    def __init__(self):
        super(main,self).__init__()
        uic.loadUi("C:/Users/COMPUMARTS/Downloads/cashier project/cashier.ui",self)
        self.handle_conn()
        self.initui()
        

    def initui(self):
        self.setWindowTitle('cashier')
        self.tabWidget.tabBar().setVisible(False)
        self.handlebtn()

        self.statusbar=QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.totalprice=0.0
        self.pricelist=[]
        self.total_price.setDigitCount(10)
        # self.show_sales()
        # self.calc_total_profit()

        
    def handle_conn(self):
        self.db = psycopg2.connect(
            host="localhost",
            database="cashier",
            user="postgres",
            password="1212")
        self.curr = self.db.cursor()
        print("connection is Done!")

    def handlebtn(self):
        self.ok_btn.clicked.connect(self.add_pro)
        self.line_input.returnPressed.connect(self.product_id)
        self.cancel_btn.clicked.connect(self.cancel_purchase)
        self.addpro_ok_btn.clicked.connect(self.add_new_pro)


    def product_id(self):
        '''this function responsible for checking with products in data base and add it to table when
        user write its code'''
        pro_id=self.line_input.text()

        #check the input 
        if pro_id!='' and pro_id.isdigit():
            self.curr.execute('''select pro_id,name , price from products where pro_id=%s''',
                         (pro_id,))
            self.db.commit()
            #print 1 tuple every time
            rows=self.curr.fetchall()
            
            if not rows:
                self.statusbar.showMessage('no product with this id')
                QTimer.singleShot(2000, lambda: self.statusbar.clearMessage())
                self.line_input.setText('')
                return
             

            #!this checks if the product already scaned to add for its quantity
            found = False
            for row in range(self.cashier_w.rowCount()):
                item = self.cashier_w.item(row, 0) 
                #is item exists                    #!name coming form database 
                if item and item.text() == str(rows[0][0]): 
                    #qty column
                    add_qty = self.cashier_w.item(row, 3)  
                    new_qty = int(add_qty.text()) + 1
                    add_qty.setText(str(new_qty))
                    found = True
                    break

            if not found:
                row_number = self.cashier_w.rowCount()
                self.cashier_w.insertRow(row_number)
                                                    #علشان يوزع العناصر صح علي كل الاعمده 
                for column_number, data in enumerate(rows[0]):
                    self.cashier_w.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                self.cashier_w.setItem(row_number, 3, QTableWidgetItem("1"))
            
            self.line_input.setText('')
        
            price = rows[0][2]
            self.totalprice += price
            self.pricelist.append(self.totalprice)
            self.total_price.display(str(self.totalprice))

        else:
            self.statusbar.showMessage('No id entered')
            self.line_input.setText('')
            QTimer.singleShot(2000, lambda: self.statusbar.clearMessage())


    def add_pro(self):
            '''this function add the products to the sales table and responsible for cleaning 
            cashier table after finishing the operation'''
            for i in range(self.cashier_w.rowCount()):
                pro_id = self.cashier_w.item(i,0).text()
                qty = int(self.cashier_w.item(i,3).text())

                # if product exists
                self.curr.execute('''
                    UPDATE sales
                    SET qun = qun + %s
                    WHERE pro_id = %s
                ''', (qty, pro_id))

                # نشوف اتأثر كام صف
                if self.curr.rowcount == 0:
                    # if there is no row affected
                    self.curr.execute('''
                        INSERT INTO sales
                        SELECT p.pro_id, p.name, p.profit, %s
                        FROM products p
                        WHERE p.pro_id = %s
                    ''', (qty, int(pro_id)))

            self.db.commit()
            self.statusbar.showMessage('تم تحديث المبيعات')
            # self.show_sales()
            self.cashier_w.setRowCount(0)
            self.pricelist=[]
            self.totalprice=0
            self.total_price.display(0)
            # self.calc_total_profit()
            

    def cancel_purchase(self):
        self.cashier_w.setRowCount(0)
        self.pricelist=[]
        self.totalprice=0
        self.total_price.display(0)
        self.line_input.setText('')
        self.statusbar.showMessage('تم إلغاء العملية')


    def add_new_pro(self):
                    #this all returns string be careful
        pro_id=self.newproID_input.text()
        pro_name=self.newproName_input.text()
        pro_price=self.newproPrice_input.text()
        pro_profit=self.newproProfit_input.text()
        self.curr.execute('select pro_id from products')
        products_ids=self.curr.fetchall()
        all_pros_ids=[str(i[0]) for i in products_ids]
        print(all_pros_ids)

        #if there is a product with the same id
        # if pro_id in all_pros_ids:
        #     self.statusbar.showMessage('هذا المنتج موجود بالفعل')
        #     return
        
        if pro_id !="" and pro_name !="" and pro_price !="" and pro_profit !="":
            if pro_id in all_pros_ids:
                self.statusbar.showMessage('هذا المنتج موجود بالفعل',5000)
                return
            else:
                self.curr.execute('''insert into products(pro_id,name,price,profit) values(%s,%s,%s,%s)'''
                                ,(pro_id,pro_name,pro_price,pro_profit))
                self.db.commit()
                
                self.statusbar.showMessage('تم اضافة المنتج بنجاح')
        else:
            self.statusbar.showMessage('من فضلك ادخل كل القيم',5000)
            
    # def calc_total_profit(self):
    #     tprof=0
    #     self.curr.execute('''select profit ,qun from sales''')
    #     prof=self.curr.fetchall()
    #     for i in prof:
    #         total=i[0]*i[1]
    #         tprof+=total
    #         self.top_sales_label.setText(str(tprof))


    # def show_sales(self):
    #     '''this fucntion for displaying sales into table and insures that every product have 
    #     the right quantity'''

    #     self.curr.execute('''select * from sales;''')
    #     rows=self.curr.fetchall()
        
    #     headers = ["كود المنتج", "اسم المنتج", "الربح", "الكميه المباعه"]
    #     #how many columns i have
    #     self.sales_w.setColumnCount(len(headers))
    #     #write headers
    #     self.sales_w.setHorizontalHeaderLabels(headers)
    #     self.sales_w.setRowCount(0)

    #     for row_number, row_data in enumerate(rows):
    #         #this adds a new empty row
    #         self.sales_w.insertRow(row_number)
    #         #this loop for checking inside every row
    #         for column_number, data in enumerate(row_data):
    #             #!what will be inside the cell 
    #                                     #row         column         data
    #             self.sales_w.setItem(row_number, column_number, QTableWidgetItem(str(data)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = main()
    window.show()
    sys.exit(app.exec_())