import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from code_editor import CodeEditor
from db_access import run_single_query

# завантажуємо список таблиць із .env
load_dotenv()
env_tables = os.getenv("TABLE_NAMES", "").strip()
TABLE_NAMES = [t.strip() for t in env_tables.split(",")] if env_tables else []

class SingleTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # вибір БД і таблиці для перегляду
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("BD:"))
        self.db_selector = QComboBox()
        self.db_selector.addItems(["MySQL", "PostgreSQL"])
        h1.addWidget(self.db_selector)
        h1.addWidget(QLabel("Table:"))
        self.table_selector = QComboBox()
        self.table_selector.addItems(TABLE_NAMES)
        h1.addWidget(self.table_selector)
        layout.addLayout(h1)

        self.query_input = CodeEditor()
        self.query_input.setPlaceholderText("SQL input")
        layout.addWidget(self.query_input)

        # кнопка виконати
        self.run_btn = QPushButton("Execute")
        self.run_btn.clicked.connect(self.execute)
        layout.addWidget(self.run_btn)

        # вміст таблиці ДО запиту
        layout.addWidget(QLabel("Result:"))
        self.before_table = QTableWidget()
        layout.addWidget(self.before_table)

        # час виконання
        self.time_label = QLabel("Time: ")
        layout.addWidget(self.time_label)

    def execute(self):
        db = self.db_selector.currentText()
        tbl = self.table_selector.currentText().strip()
        query = self.query_input.toPlainText().strip()

        if not query and tbl:
            query = f"SELECT * FROM {tbl};"

        if tbl:
            try:
                rows, cols, _ = run_single_query(db, f"SELECT * FROM {tbl}")
                self._fill_table(self.before_table, rows, cols)
            except Exception as e:
                QMessageBox.warning(self, "Err", f"Failed data from {tbl}:\n{e}")
                return

        try:
            rows, cols, t = run_single_query(db, query)
            self.time_label.setText(f"Time: {t:.4f} с")
            self._fill_table(self.before_table, rows, cols)
        except Exception as e:
            QMessageBox.critical(self, "Failed", str(e))

    def _fill_table(self, table: QTableWidget, rows, cols):
        table.clear()
        table.setColumnCount(len(cols))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(cols)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))