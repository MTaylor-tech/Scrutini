import datetime
import csv
import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from fuzzywuzzy import process
from sWidgets import SPushButton, on_button_clicked, verify, ask_save, is_float
from sWidgets import retrieve_csv_keys, retrieve_csv_dict, sanitize


class ImportWindow(qt.QDialog):
    def __init__(self, main_window, db):
        super(ImportWindow, self).__init__()
        self.db = db
        self.filename = ""
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.competition = self.db.competition
        self.layout = qt.QVBoxLayout()
        self.resize(600, 800)
        self.button_choose = qt.QPushButton('Choose &File')
        self.button_choose.clicked.connect(self.choose_file)
        self.label_filename = qt.QLabel('No file selected')
        self.table_columns = qt.QTableWidget()
        self.button_import = qt.QPushButton('&Import')
        self.button_import.clicked.connect(self.import_file)
        self.button_import.setEnabled(False)
        self.button_exit = qt.QPushButton('Cancel')
        self.button_exit.clicked.connect(self.hide)
        self.table_columns.setColumnCount(2)
        self.table_columns.setHorizontalHeaderLabels(['Field Name',
                                                      'Column in CSV'])
        self.column_widths = [200,200]
        column = 0
        while column < len(self.column_widths):
            self.table_columns.setColumnWidth(column,self.column_widths[column])
            column += 1
        row_count = 0
        self.rows = ['First Name', 'Last Name', 'Competitor Number',
                     'Street Address', 'City', 'State/Province',
                     'Zip/Postal Code', 'Phone Number', 'Email',
                     'ScotDance Number', 'Category', 'Birthdate', 'Age',
                     'Teacher', 'Teacher Email', 'Date Entry was Received',
                     'Primary Competitor Group', 'Secondary Competitor Group',
                     'Tertiary Competitor Group']
        for row in self.rows:
            self.table_columns.setRowCount(row_count + 1)
            item_name = qt.QTableWidgetItem(row)
            item_name.setFlags(qc.Qt.NoItemFlags)
            selector_column = qt.QComboBox()
            selector_column.addItem('')
            self.table_columns.setItem(row_count, 0, item_name)
            self.table_columns.setCellWidget(row_count, 1, selector_column)
            row_count += 1
        self.layout.addWidget(self.label_filename)
        self.layout.addWidget(self.button_choose)
        self.layout.addWidget(self.table_columns)
        self.layout.addWidget(self.button_import)
        self.layout.addWidget(self.button_exit)
        self.setLayout(self.layout)

    def choose_file(self):
        options = qt.QFileDialog.Options()
        options |= qt.QFileDialog.DontUseNativeDialog
        self.filename, _ = qt.QFileDialog.getOpenFileName(self,
                                                          "Select CSV File",
                                                          "",
                                                          "CSV Files (*.csv)",
                                                          options=options)
        if self.filename:
            print(self.filename)
        else:
            return
        self.label_filename.setText(self.filename)
        self.reader = retrieve_csv_keys(self.filename)
        self.button_import.setEnabled(True)
        row = 0
        while row < self.table_columns.rowCount():
            selector_column = self.table_columns.cellWidget(row, 1)
            for item in self.reader:
                selector_column.addItem(item)
            row += 1

    def import_file(self):
        row = 0
        self.column_names = []
        while row < self.table_columns.rowCount():
            selector_column = self.table_columns.cellWidget(row, 1)
            self.column_names.append(selector_column.currentText())
            row += 1
        categories = self.db.t.category.get_all()
        categories_names = [cat.name for cat in categories]
        categories_ids = [cat.iid for cat in categories]
        with open(self.filename, newline='') as csvfile:
                dict_reader = csv.DictReader(csvfile)
                # ['First Name', 'Last Name', 'Competitor Number', 'Street Address', 'City', 'State/Province', 'Zip/Postal Code', 'Phone Number',
                #        'Email', 'ScotDance Number', 'Birthdate', 'Age', 'Teacher', 'Teacher Email', 'Date Entry was Received',
                #        'Primary Competitor Group', 'Secondary Competitor Group', 'Tertiary Competitor Group']
                for row in dict_reader:
                    # dancer = sc.Dancer(0,'','','','','','','','',0,'','','','','','',0,0,self.competition.iid)
                    dancer = self.db.t.dancer.new(self.competition.iid)
                    if self.column_names[0] != '':
                        dancer.first_name = sanitize(row[self.column_names[0]])
                    if self.column_names[1] != '':
                        dancer.last_name = sanitize(row[self.column_names[1]])
                    if self.column_names[2] != '':
                        dancer.competitor_num = sanitize(
                            row[self.column_names[2]])
                    if self.column_names[3] != '':
                        dancer.street = sanitize(row[self.column_names[3]])
                    if self.column_names[4] != '':
                        dancer.city = sanitize(row[self.column_names[4]])
                    if self.column_names[5] != '':
                        dancer.state = sanitize(row[self.column_names[5]])
                    if self.column_names[6] != '':
                        dancer.zip = sanitize(row[self.column_names[6]])
                    if self.column_names[7] != '':
                        dancer.phone_num = sanitize(row[self.column_names[7]])
                    if self.column_names[8] != '':
                        dancer.email = sanitize(row[self.column_names[8]])
                    if self.column_names[9] != '':
                        dancer.scot_dance_num = sanitize(
                            row[self.column_names[9]])
                    if self.column_names[10] != '':
                        cat_name, _ = process.extractOne(row[
                            self.column_names[10]], categories_names)
                        dancer.dancer_category = categories_ids[
                            categories_names.index(cat_name)]-1
                    if self.column_names[11] != '':
                        dancer.birthdate = row[self.column_names[11]]
                    if self.column_names[12] != '':
                        if row[self.column_names[12]].isdigit():
                            dancer.age = int(row[self.column_names[12]])
                    if self.column_names[13] != '':
                        dancer.teacher = sanitize(row[self.column_names[13]])
                    if self.column_names[14] != '':
                        dancer.teacher_email = sanitize(
                            row[self.column_names[14]])
                    if self.column_names[15] != '':
                        dancer.registered_date = row[self.column_names[15]]
                    if self.column_names[16] != '':
                        dancer_grp1 = row[self.column_names[16]]
                        dancer_group_1 = self.db.t.group.get_or_new(
                            self.competition.iid, dancer_grp1)
                        self.db.t.group.join(dancer.iid,
                                                   dancer_group_1.iid)
                    # else:
                    #     dancer_grp1 = ''
                    if self.column_names[17] != '':
                        dancer_grp2 = row[self.column_names[17]]
                        dancer_group_2 = self.db.t.group.get_or_new(
                            self.competition.iid, dancer_grp2)
                        self.db.t.group.join(dancer.iid,
                                                   dancer_group_2.iid)
                    # else:
                    #     dancer_grp2 = ''
                    if self.column_names[18] != '':
                        dancer_grp3 = row[self.column_names[18]]
                        dancer_group_3 = self.db.t.group.get_or_new(
                            self.competition.iid, dancer_grp3)
                        self.db.t.group.join(dancer.iid,
                                                   dancer_group_3.iid)
                    # else:
                    #     dancer_grp3 = ''
                    # dancer_group_1 = self.db.tables.groups.get_by_abbrev(
                    #                                             dancer_grp1)
                    # dancer_group_2 = self.db.tables.groups.get_by_abbrev(
                    #                                             dancer_grp2)
                    # dancer_group_3 = self.db.tables.groups.get_by_abbrev(
                    #                                             dancer_grp3)
                    # dancer = self.db.tables.dancers.insert(dancer)
                    # if dancer_group_1 is not None:
                    #     self.db.tables.groups.join(dancer.iid, dancer_group_1.iid)
                    # if dancer_group_2 is not None:
                    #     self.db.tables.groups.join(dancer.iid, dancer_group_2.iid)
                    # if dancer_group_3 is not None:
                    #     self.db.tables.groups.join(dancer.iid, dancer_group_3.iid)
                    self.db.t.dancer.update(dancer)
                    # xxx doesn't seem to put dancers into dancer_groups. Why?
        self.hide()
