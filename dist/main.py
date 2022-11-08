import sys
import sqlite3
import datetime

from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from design import Ui_MainWindow


# Наследуемся от виджета из PyQt5.QtWidgets и от класса с интерфейсом
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        self.setupUi(self)

        #загрузим изображение
        self.setWindowIcon(QIcon("finapp.png"))

        # приветсвуем пользователя диалоговым окном
        #воспользуемся блоком try...except
        try:
            first_window = QMessageBox()
            first_window.setWindowTitle("Домашние финансы")
            first_window.setWindowIcon(QIcon("image/logo.png"))
            # открываем файл для окна-приветствия
            with open('C:/Users/Sviri/PycharmProjects/Home Finance/venv/text.txt', encoding="utf-8") as file:
                data = file.read()
                first_window.setText(data)
            first_window.exec_()
        except Exception as e:
            print('Ошибка!' % e)

        # подключаем БД
        self.connection = sqlite3.connect('C:/Users/Sviri/PycharmProjects/home_money1/data.db')
        self.select_data_bill()
        self.select_data_profit()
        self.select_data_waste()
        self.much_money()
        self.combo()

        # настраиваем кнопки
        self.btn_new_bill.clicked.connect(self.new_bill)
        self.btn_new_profit.clicked.connect(self.new_profit)
        self.btn_new_waste.clicked.connect(self.new_waste)
        self.btn_stat_waste.clicked.connect(self.statistic)
        self.pushButton.clicked.connect(self.note)

        # настраиваем даты
        date_now = datetime.datetime.today()
        self.write_date_waste.setDateTime(date_now)
        self.write_date_profit.setDateTime(date_now)
        self.date_s1.setDateTime(date_now)
        self.date_s2.setDateTime(date_now)

    def statistic(self):
        # обновление статистики по расходам
        kind_of_wastes = self.comboBox.currentText()
        date_1 = tuple([int(i) for i in self.date_s1.text().split('.')][::-1])
        date_2 = tuple([int(i) for i in self.date_s2.text().split('.')][::-1])
        cursor = self.connection.cursor()
        request = f"SELECT money, date FROM waste_table WHERE kind = '{kind_of_wastes}'"
        money = cursor.execute(request).fetchall()
        date_1 = datetime.datetime(*date_1)
        date_2 = datetime.datetime(*date_2)
        result = []
        for i in money:
            date_wastes = tuple([int(j) for j in i[1].split('.')][::-1])
            date_wastes = datetime.datetime(*date_wastes)
            if date_1 <= date_wastes and date_wastes <= date_2:
                result.append(i[0])
        self.report_stat_waste.setText(f'{sum(result)} руб')
        self.report_stat_waste.setAlignment(Qt.AlignCenter)

    def note(self):
        # функция заполнения заметок
        note = self.lineEdit.text()
        db = sqlite3.connect('data.db')
        cursor = db.cursor()
        cursor.execute("SELECT note FROM note")
        if self.pushButton.isEnabled():
            cursor.execute(f"INSERT INTO note VALUES (?)", note)
            db.commit()

    def much_money(self):
        # обновление страницы статистики
        cursor = self.connection.cursor()
        request_money = f"SELECT money FROM bill"
        money_acc = cursor.execute(request_money).fetchall()
        res = sum([i[0] for i in money_acc])
        self.label_all_money_now.setText(f'{res} руб')
        self.label_all_money_now.setAlignment(Qt.AlignCenter)
        request_money = f"SELECT money FROM profit_table"
        money_profit = cursor.execute(request_money).fetchall()
        res = sum([i[0] for i in money_profit])
        self.label_all_profit.setText(f'{res} руб')
        self.label_all_profit.setAlignment(Qt.AlignCenter)
        request_money = f"SELECT money FROM waste_table"
        money_income = cursor.execute(request_money).fetchall()
        res = sum([i[0] for i in money_income])
        self.label_all_waste.setText(f'{res} руб')
        self.label_all_waste.setAlignment(Qt.AlignCenter)

    def new_waste(self):
        # функция создания нового расхода
        money = float(self.write_money_waste.text().replace(',', '.'))
        other = self.write_other_waste.text()
        kind_of_wastes = self.write_bill_waste.currentText()
        kind_of_bill = self.write_kind_of_wastes.currentText()
        date_bill = self.write_date_waste.text()
        cursor = self.connection.cursor()
        request = f"""INSERT INTO waste_table(date, money, kind, bill, note)
                    VALUES(?, ?, ?, ?, ?)"""
        data_cortege = (kind_of_bill, money, kind_of_wastes, kind_of_bill, other)
        cursor.execute(request, data_cortege)
        request_money = f"SELECT money FROM bill where name='{date_bill}'"
        money_old = cursor.execute(request_money).fetchall()[0][0]
        money_old -= money
        request = f"UPDATE bill set money = {money_old} WHERE name = '{date_bill}'"
        cursor.execute(request)
        self.connection.commit()
        self.select_data_bill()
        self.select_data_waste()
        self.much_money()

    def new_profit(self):
        # функция создания нового дохода
        money = float(self.write_money_profit.text().replace(',', '.'))
        other = self.write_other_profit.text()
        kind_profit = self.write_kind_of_profit.currentText()
        kind_bill = self.write_bill_profit.currentText()
        date_profit = self.write_date_profit.text()
        cursor = self.connection.cursor()
        request = f"""INSERT INTO profit_table(date, money, kind_of_profit, bill, note)
                    VALUES(?, ?, ?, ?, ?)"""
        data_cortege = (date_profit, money, kind_profit, kind_bill, other)
        cursor.execute(request, data_cortege)
        request_money = f"SELECT money FROM bill where name='{kind_bill}'"
        money_old = cursor.execute(request_money).fetchall()[0][0]
        money += money_old
        request = f"UPDATE bill set money = {money} WHERE name = '{kind_bill}'"
        cursor.execute(request)
        self.connection.commit()
        self.select_data_bill()
        self.select_data_waste()
        self.much_money()

    def new_bill(self):
        # создание нового счёта
        name1 = self.write_new_bill.text()
        cursor = self.connection.cursor()
        request = f"""INSERT INTO bill(name) VALUES('{name1}')"""
        cursor.execute(request)
        self.connection.commit()
        self.select_data_bill()
        self.combo()
        self.much_money()

    def combo(self):
        # функция настройки всех combo box
        res = self.connection.cursor().execute("SELECT name FROM waste_kind").fetchall()
        waste_kind = [i[0] for i in res]
        self.write_bill_waste.addItems(waste_kind)
        self.comboBox.clear()
        self.comboBox.addItems(waste_kind)
        request = "SELECT name FROM bill"
        res = self.connection.cursor().execute(request).fetchall()
        bill_list = [i[0] for i in res]
        self.write_kind_of_wastes.clear()
        self.write_bill_profit.clear()
        self.write_kind_of_wastes.addItems(bill_list)
        self.write_bill_profit.addItems(bill_list)
        res = self.connection.cursor().execute("SELECT name FROM profit_kind").fetchall()
        kind_of_profit = [i[0] for i in res]
        self.write_kind_of_profit.clear()
        self.write_kind_of_profit.addItems(kind_of_profit)

    def select_data_waste(self):
        # создание или обновление таблицы расходов
        request = "SELECT * FROM waste_table"
        res = self.connection.cursor().execute(request).fetchall()
        self.table_waste.setColumnCount(6)
        self.table_waste.setRowCount(0)
        hed = ['№', 'Датa', 'Сумма' + ' ' * 20, 'Причина расхода',
               'Счёт списания', 'Примечание']
        self.table_waste.setHorizontalHeaderLabels(hed)
        for i, r in enumerate(res):
            self.table_waste.setRowCount(
                self.table_waste.rowCount() + 1)
            for j, e in enumerate(r):
                self.table_waste.setItem(
                    i, j, QTableWidgetItem(str(e)))
        self.table_waste.resizeColumnsToContents()

    def select_data_profit(self):
        # создание или обновление таблицы доходов
        request = "SELECT * FROM profit_table"
        res = self.connection.cursor().execute(request).fetchall()
        self.table_profit.setColumnCount(6)
        self.table_profit.setRowCount(0)
        hed = ['№', 'Датa', 'Сумма' + ' ' * 20, 'Источник дохода',
               'Счёт поступления', 'Примечание']
        self.table_profit.setHorizontalHeaderLabels(hed)
        for i, r in enumerate(res):
            self.table_profit.setRowCount(
                self.table_profit.rowCount() + 1)
            for j, e in enumerate(r):
                self.table_profit.setItem(
                    i, j, QTableWidgetItem(str(e)))
        self.table_profit.resizeColumnsToContents()

    def select_data_bill(self):
        # создание или обновление таблицы счетов
        request = "SELECT name, money FROM bill"
        res = self.connection.cursor().execute(request).fetchall()
        self.table_bill.setColumnCount(2)
        self.table_bill.setRowCount(0)
        self.table_bill.setHorizontalHeaderLabels(["Назавание счёта" + ' ' * 70, "Остаток" + ' ' * 100])
        for i, r in enumerate(res):
            self.table_bill.setRowCount(
                self.table_bill.rowCount() + 1)
            for j, e in enumerate(r):
                self.table_bill.setItem(
                    i, j, QTableWidgetItem(str(e)))
        self.table_bill.resizeColumnsToContents()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
