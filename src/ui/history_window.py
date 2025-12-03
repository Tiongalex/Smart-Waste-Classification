import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detection History")
        self.setGeometry(350, 300, 700, 400)

        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID","Waste Type","Bin","Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        
        self.load_history()

    def load_history(self):
        conn = sqlite3.connect("waste_detection.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, class, bin, timestamp FROM detections ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))

        for row_num, row_data in enumerate(rows):
            for col_num, value in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(value)))

        