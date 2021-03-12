import datetime
import csv
import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import SPushButton, on_button_clicked, verify, ask_save, is_float



class ImportWindow(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(ImportWindow, self).__init__()
        self.db = db
        self.filename = ""
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.competition = self.db.tables.competitions.get(comp_id)
        self.layout = qt.QVBoxLayout()
        self.resize(600,800)
        self.button_choose = qt.QPushButton('Choose &File')
        self.button_choose.clicked.connect(self.choose_file)
        self.label_filename = qt.QLabel('No file selected')
        self.table_columns = qt.QTableWidget()
        self.button_import = qt.QPushButton('&Import')
        self.button_import.clicked.connect(self.import_file)
        self.button_exit = qt.QPushButton('Cancel')
        self.button_exit.clicked.connect(self.hide)
        self.table_columns.setColumnCount(2)
        self.table_columns.setHorizontalHeaderLabels(['Field Name','Column in CSV'])
        self.column_widths = [200,200]
        column = 0
        while column < len(self.column_widths):
            self.table_columns.setColumnWidth(column,self.column_widths[column])
            column += 1
        rowCount = 0
        self.rows = ['First Name', 'Last Name', 'Competitor Number', 'Street Address', 'City', 'State/Province', 'Zip/Postal Code', 'Phone Number',
                        'Email', 'ScotDance Number', 'Birthdate', 'Age', 'Teacher', 'Teacher Email', 'Date Entry was Received',
                        'Primary Competitor Group', 'Secondary Competitor Group', 'Tertiary Competitor Group']
        for row in self.rows:
            self.table_columns.setRowCount(rowCount + 1)
            item_name = qt.QTableWidgetItem(row)
            item_name.setFlags(qc.Qt.NoItemFlags)
            selector_column = qt.QComboBox()
            selector_column.addItem('')
            self.table_columns.setItem(rowCount, 0, item_name)
            self.table_columns.setCellWidget(rowCount, 1, selector_column)
            rowCount += 1

        self.layout.addWidget(self.label_filename)
        self.layout.addWidget(self.button_choose)
        self.layout.addWidget(self.table_columns)
        self.layout.addWidget(self.button_import)
        self.layout.addWidget(self.button_exit)
        self.setLayout(self.layout)

    def choose_file(self):
        options = qt.QFileDialog.Options()
        options |= qt.QFileDialog.DontUseNativeDialog
        self.filename, _ = qt.QFileDialog.getOpenFileName(self,"Select CSV File", "","CSV Files (*.csv)", options=options)
        if self.filename:
            print(self.filename)
        else:
            return
        self.label_filename.setText(self.filename)
        self.reader = self.db.retrieve_csv_keys(self.filename)
        row = 0
        while row < self.table_columns.rowCount():
            selector_column = self.table_columns.cellWidget(row, 1)
            for item in self.reader:
                selector_column.addItem(item)
            row += 1
        #print(self.reader)

    def import_file(self):
        row = 0
        self.column_names = []
        while row < self.table_columns.rowCount():
            selector_column = self.table_columns.cellWidget(row, 1)
            self.column_names.append(selector_column.currentText())
            row += 1
        with open(self.filename, newline='') as csvfile:
                dict_reader = csv.DictReader(csvfile)
                #['First Name', 'Last Name', 'Competitor Number', 'Street Address', 'City', 'State/Province', 'Zip/Postal Code', 'Phone Number',
                #        'Email', 'ScotDance Number', 'Birthdate', 'Age', 'Teacher', 'Teacher Email', 'Date Entry was Received',
                #        'Primary Competitor Group', 'Secondary Competitor Group', 'Tertiary Competitor Group']
                for row in dict_reader:
                    # dancer = sc.Dancer(0,'','','','','','','','',0,'','','','','','',0,0,self.competition.id)
                    dancer = self.db.tables.dancers.new(self.competition.id)
                    if self.column_names[0] != '':
                        dancer.firstName = row[self.column_names[0]]
                    if self.column_names[1] != '':
                        dancer.lastName = row[self.column_names[1]]
                    if self.column_names[2] != '':
                        dancer.number = row[self.column_names[2]]
                    if self.column_names[3] != '':
                        dancer.street = row[self.column_names[3]]
                    if self.column_names[4] != '':
                        dancer.city = row[self.column_names[4]]
                    if self.column_names[5] != '':
                        dancer.state = row[self.column_names[5]]
                    if self.column_names[6] != '':
                        dancer.zipCode = row[self.column_names[6]]
                    if self.column_names[7] != '':
                        dancer.phonenum = row[self.column_names[7]]
                    if self.column_names[8] != '':
                        dancer.email = row[self.column_names[8]]
                    if self.column_names[9] != '':
                        dancer.scotDanceNum = row[self.column_names[9]]
                    if self.column_names[10] != '':
                        dancer.birthdate = row[self.column_names[10]]
                    if self.column_names[11] != '':
                        if row[self.column_names[11]].isdigit():
                            dancer.age = int(row[self.column_names[11]])
                    if self.column_names[12] != '':
                        dancer.teacher = row[self.column_names[12]]
                    if self.column_names[13] != '':
                        dancer.teacherEmail = row[self.column_names[13]]
                    if self.column_names[14] != '':
                        dancer.registeredDate = row[self.column_names[14]]
                    if self.column_names[15] != '':
                        dancer_grp1 = row[self.column_names[15]]
                    else:
                        dancer_grp1 = ''
                    if self.column_names[16] != '':
                        dancer_grp2 = row[self.column_names[16]]
                    else:
                        dancer_grp2 = ''
                    if self.column_names[17] != '':
                        dancer_grp3 = row[self.column_names[16]]
                    else:
                        dancer_grp3 = ''
                    dancerGroup_1 = self.db.tables.groups.get_by_abbrev(dancer_grp1)
                    dancerGroup_2 = self.db.tables.groups.get_by_abbrev(dancer_grp2)
                    dancerGroup_3 = self.db.tables.groups.get_by_abbrev(dancer_grp3)
                    dancer = self.db.tables.dancers.insert(dancer)
                    if dancerGroup_1 is not None:
                        self.db.tables.groups.join(dancer.id, dancerGroup_1.id)
                    if dancerGroup_2 is not None:
                        self.db.tables.groups.join(dancer.id, dancerGroup_2.id)
                    if dancerGroup_3 is not None:
                        self.db.tables.groups.join(dancer.id, dancerGroup_3.id)
                    #xxx doesn't seem to put dancers into dancerGroups. Why?
        self.hide()
