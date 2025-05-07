import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from code_editor import CodeEditor
from db_access import distributed_transaction

load_dotenv()
TABLE_NAMES = []
env_tables = os.getenv("TABLE_NAMES", "").strip()
if env_tables:
    TABLE_NAMES = [t.strip() for t in env_tables.split(",")]

class DistributedTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("MySQL — DML-q"))
        self.mysql_query = CodeEditor()
        self.mysql_query.setPlaceholderText("SQL input")
        layout.addWidget(self.mysql_query)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("View MySQL:"))
        self.mysql_table = QComboBox()
        self.mysql_table.addItems(TABLE_NAMES)
        h1.addWidget(self.mysql_table)
        layout.addLayout(h1)

        layout.addWidget(QLabel("PostgreSQL — DML-q:"))
        self.pg_query = CodeEditor()
        self.pg_query.setPlaceholderText("SQL input")
        layout.addWidget(self.pg_query)

        # Выбор таблицы PostgreSQL после
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("View PostgreSQL:"))
        self.pg_table = QComboBox()
        self.pg_table.addItems(TABLE_NAMES)
        h2.addWidget(self.pg_table)
        layout.addLayout(h2)

        self.exec_btn = QPushButton("Execute")
        self.exec_btn.clicked.connect(self.execute_tx)
        layout.addWidget(self.exec_btn)

        self.time_label = QLabel("Time: ")
        layout.addWidget(self.time_label)

        # Результаты
        layout.addWidget(QLabel("Result MySQL:"))
        self.mysql_result = QTableWidget()
        layout.addWidget(self.mysql_result)

        layout.addWidget(QLabel("Result PostgreSQL:"))
        self.pg_result = QTableWidget()
        layout.addWidget(self.pg_result)

    def execute_tx(self):
        mq = self.mysql_query.toPlainText().strip()
        mt = self.mysql_table.currentText().strip()
        pq = self.pg_query.toPlainText().strip()
        pt = self.pg_table.currentText().strip()

        try:
            (res, exec_time) = distributed_transaction(mq, mt, pq, pt)
            m_rows, m_cols   = res["mysql"]
            pg_rows, pg_cols = res["postgresql"]

            self._fill_table(self.mysql_result, m_rows, m_cols)
            self._fill_table(self.pg_result, pg_rows, pg_cols)

            self.time_label.setText(f"Time: {exec_time:.4f} с")
            QMessageBox.information(self, "Done.", "Successfully completed.")
        except Exception as e:
            QMessageBox.critical(self, "Err", f"Transaction canceled:\n{e}")

    def _fill_table(self, table: QTableWidget, rows, cols):
        table.clear()
        table.setColumnCount(len(cols))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(cols)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))
