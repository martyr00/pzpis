from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from db_access import distributed_transaction

class DistributedTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # MySQL-запит
        layout.addWidget(QLabel("MySQL — DML:"))
        self.mysql_query = QTextEdit()
        layout.addWidget(self.mysql_query)
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("MySQL table after:"))
        self.mysql_table = QLineEdit()
        h1.addWidget(self.mysql_table)
        layout.addLayout(h1)

        # PostgreSQL-запит
        layout.addWidget(QLabel("PostgreSQL — DML:"))
        self.pg_query = QTextEdit()
        layout.addWidget(self.pg_query)
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("PostgreSQL table after:"))
        self.pg_table = QLineEdit()
        h2.addWidget(self.pg_table)
        layout.addLayout(h2)

        # Кнопка + час
        self.exec_btn = QPushButton("Execute")
        self.exec_btn.clicked.connect(self.execute_tx)
        layout.addWidget(self.exec_btn)
        self.time_label = QLabel("Time:")
        layout.addWidget(self.time_label)

        # Відображення результатів
        layout.addWidget(QLabel("MySQL after:"))
        self.mysql_result = QTableWidget()
        layout.addWidget(self.mysql_result)
        layout.addWidget(QLabel("PostgreSQL after:"))
        self.pg_result = QTableWidget()
        layout.addWidget(self.pg_result)

    def execute_tx(self):
        mq, mt = self.mysql_query.toPlainText().strip(), self.mysql_table.text().strip()
        pq, pt = self.pg_query.toPlainText().strip(),    self.pg_table.text().strip()

        try:
            (res, exec_time) = distributed_transaction(mq, mt, pq, pt)
            m_rows, m_cols   = res["mysql"]
            pg_rows, pg_cols = res["postgresql"]

            self._fill_table(self.mysql_result, m_rows, m_cols)
            self._fill_table(self.pg_result, pg_rows, pg_cols)
            self.time_label.setText(f"Time: {exec_time:.4f} с")
            QMessageBox.information(self, "Done", "Successfully completed.")
        except Exception as e:
            QMessageBox.critical(self, "Err", f"Transaction canceled:\n{e}")

    def _fill_table(self, table, rows, cols):
        table.clear()
        table.setColumnCount(len(cols))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(cols)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(val)))
