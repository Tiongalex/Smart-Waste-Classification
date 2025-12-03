import sqlite3
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detection History")
        self.setGeometry(350, 250, 600, 400)

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID","Waste Type", "Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_history()

    def load_history(self):
        conn = sqlite3.connect("waste_detection.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, class, timestamp FROM detections ORDER BY id DESC")
        rows = cursor.fetchall()

        self.table.setRowCount(len(rows))

        for row_num, row_data in enumerate(rows):
            for col_num, value in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(value)))

        conn.close()