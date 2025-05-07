# distributed_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from code_editor import CodeEditor
from db_access import distributed_transaction

class DistributedTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # 1) Поле ввода SQL для MySQL
        layout.addWidget(QLabel("MySQL — DML-запит:"))
        self.mysql_query = CodeEditor()
        self.mysql_query.setPlaceholderText("SQL для MySQL")
        layout.addWidget(self.mysql_query)

        # 2) Поле ввода имени таблицы MySQL
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Таблиця MySQL після:"))
        self.mysql_table = QLineEdit()
        h1.addWidget(self.mysql_table)
        layout.addLayout(h1)

        # 3) Поле ввода SQL для PostgreSQL
        layout.addWidget(QLabel("PostgreSQL — DML-запит:"))
        self.pg_query = CodeEditor()
        self.pg_query.setPlaceholderText("SQL для PostgreSQL")
        layout.addWidget(self.pg_query)

        # 4) Поле ввода имени таблицы PostgreSQL
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Таблиця PostgreSQL після:"))
        self.pg_table = QLineEdit()
        h2.addWidget(self.pg_table)
        layout.addLayout(h2)

        # 5) Кнопка выполнения и метка времени
        self.exec_btn = QPushButton("Виконати розподілену транзакцію")
        self.exec_btn.clicked.connect(self.execute_tx)
        layout.addWidget(self.exec_btn)

        self.time_label = QLabel("Час виконання транзакції: ")
        layout.addWidget(self.time_label)

        # 6) Таблицы для отображения результатов
        layout.addWidget(QLabel("Вміст MySQL після:"))
        self.mysql_result = QTableWidget()
        layout.addWidget(self.mysql_result)

        layout.addWidget(QLabel("Вміст PostgreSQL після:"))
        self.pg_result = QTableWidget()
        layout.addWidget(self.pg_result)

    def execute_tx(self):
        mq = self.mysql_query.toPlainText().strip()
        mt = self.mysql_table.text().strip()
        pq = self.pg_query.toPlainText().strip()
        pt = self.pg_table.text().strip()

        try:
            (res, exec_time) = distributed_transaction(mq, mt, pq, pt)
            m_rows, m_cols   = res["mysql"]
            pg_rows, pg_cols = res["postgresql"]

            self._fill_table(self.mysql_result, m_rows, m_cols)
            self._fill_table(self.pg_result, pg_rows, pg_cols)

            self.time_label.setText(f"Час виконання транзакції: {exec_time:.4f} с")
            QMessageBox.information(self, "Готово", "Розподілена транзакція успішно виконана.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка транзакції", f"Транзакцію відмінено:\n{e}")

    def _fill_table(self, table: QTableWidget, rows, cols):
        table.clear()
        table.setColumnCount(len(cols))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(cols)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))
