import sys

import qdarkstyle
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout
from single_tab import SingleTab
from jdbc_odbc.jdbc_odbc_tab import JDBCODBCTab
from distributed_tab import DistributedTab

class DBApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DB GUI")
        self.resize(900, 700)

        tabs = QTabWidget()
        tabs.addTab(JDBCODBCTab(),    "JDBC/ODBC")
        tabs.addTab(SingleTab(),      "mySQL/postSQL query")
        tabs.addTab(DistributedTab(), "Distributed transaction")

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = DBApp()
    win.show()
    sys.exit(app.exec_())