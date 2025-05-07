from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
)
from code_editor import CodeEditor
from jdbc_odbc.jdbc_odbc_access import run_query

class JDBCODBCTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Method:"))
        self.method_selector = QComboBox()
        self.method_selector.addItems(["JDBC", "ODBC"])
        h1.addWidget(self.method_selector)
        layout.addLayout(h1)

        self.query_input = CodeEditor()
        self.query_input.setPlaceholderText("SQL")
        layout.addWidget(self.query_input)

        self.run_btn = QPushButton("Execute")
        self.run_btn.clicked.connect(self.execute)
        layout.addWidget(self.run_btn)

        self.result_table = QTableWidget()
        layout.addWidget(self.result_table)

        self.time_label = QLabel("Time:")
        layout.addWidget(self.time_label)

    def execute(self):
        method = self.method_selector.currentText()
        query = self.query_input.toPlainText().strip()

        df, duration, error = run_query(method, query)
        if error:
            QMessageBox.critical(self, "Err", error)
            return

        self.result_table.clear()
        self.result_table.setColumnCount(len(df.columns))
        self.result_table.setHorizontalHeaderLabels(df.columns.tolist())
        self.result_table.setRowCount(len(df))
        for i, row in df.iterrows():
            for j, val in enumerate(row):
                self.result_table.setItem(i, j, QTableWidgetItem(str(val)))

        self.time_label.setText(f"Time ({method}): {duration:.4f} s")
