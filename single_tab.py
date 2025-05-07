from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
)
from code_editor import CodeEditor
from db_access import run_single_query

class SingleTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("BD:"))
        self.db_selector = QComboBox()
        self.db_selector.addItems(["MySQL", "PostgreSQL"])
        h1.addWidget(self.db_selector)
        h1.addWidget(QLabel("Table for view:"))
        self.table_input = QLineEdit()
        h1.addWidget(self.table_input)
        layout.addLayout(h1)

        self.query_input = CodeEditor()
        self.query_input.setPlaceholderText("SQL")
        layout.addWidget(self.query_input)

        self.run_btn = QPushButton("Execute")
        self.run_btn.clicked.connect(self.execute)
        layout.addWidget(self.run_btn)

        # Вміст таблиці ДО запиту
        layout.addWidget(QLabel("Tabel before query:"))
        self.before_table = QTableWidget()
        layout.addWidget(self.before_table)

        # Час виконання
        self.time_label = QLabel("Time: ")
        layout.addWidget(self.time_label)

    def execute(self):
        db = self.db_selector.currentText()
        tbl = self.table_input.text().strip()
        query = self.query_input.toPlainText().strip()

        if tbl:
            try:
                rows, cols, _ = run_single_query(db, f"SELECT * FROM {tbl}")
                self._fill_table(self.before_table, rows, cols)
            except Exception as e:
                QMessageBox.warning(self, "Err", f"Failed from {tbl}:\n{e}")
                return

        try:
            rows, cols, t = run_single_query(db, query)
            self.time_label.setText(f"Time: {t:.4f} с")
        except Exception as e:
            QMessageBox.critical(self, "Failed", str(e))

    def _fill_table(self, table, rows, cols):
        table.clear()
        table.setColumnCount(len(cols))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(cols)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))
