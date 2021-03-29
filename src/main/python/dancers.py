import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import verify, ask_save, sanitize

class DancerEditor(qt.QDialog):
    def __init__(self, main_window, db):
        super(DancerEditor, self).__init__()
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.db = db
        self.competition_id = self.db.competition.iid
        self.changes_made = False
        self.resize(1680, 1000)
        self.layout = qt.QVBoxLayout()
        self.dancers = self.db.t.dancer.get_by_competition(competition_id)
        self.table_dancers = qt.QTableWidget()
        self.headers = ['First Name', 'Last Name', 'Num', 'Category',
                        'Groups', 'ScotDance#', 'Address', 'City', 'ST',
                        'Zip Code', 'Birthdate', 'Age', 'Entry Rcvd',
                        'Phone #', 'Email', 'Teacher', 'Teacher\'s Email',
                        'id', 'cat_id']
        self.table_dancers.setColumnCount(len(self.headers))
        self.table_dancers.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [120, 150, 40, 130, 100, 100, 150, 120, 40, 60,
                              80, 30, 80, 110, 250, 200, 250, 0, 0]
        column = 0
        while column < len(self.column_widths):
            self.table_dancers.setColumnWidth(column,
                                              self.column_widths[column])
            column += 1
        row = 0
        # id, firstName, lastName, scotDanceNum, street, city, state,
        # zipCode, birthdate, age, registeredDate, number, phonenum, email,
        # teacher, teacherEmail, dancerCat, dancer_group, competition
        for dancer in self.dancers:
            item_first_name = qt.QTableWidgetItem(dancer.first_name)
            item_last_name = qt.QTableWidgetItem(dancer.last_name)
            item_number = qt.QTableWidgetItem(dancer.competitor_num)
            selector_category = qt.QComboBox()
            categories = self.db.t.category.get_all()
            for category in categories:
                selector_category.addItem(category.name)
                if self.db.settings.verbose:
                    print('Category: %d [%s]' % (category.iid, category.name))
            if dancer.dancer_category is not None:
                selector_category.setCurrentIndex(dancer.dancer_category)
            else:
                selector_category.setCurrentIndex(0)
            category = self.db.t.category.get(dancer.dancer_category)
            item_cat_id = qt.QTableWidgetItem(dancer.dancer_category)
            dancer_groups = self.db.t.group.get_by_dancer(dancer.iid)
            dancer_group_list = ''
            for group in dancer_groups:
                if dancer_group_list != '':
                    dancer_group_list += ', '
                dancer_group_list += group.abbrev
            item_groups = qt.QTableWidgetItem(dancer_group_list)
            item_scotdance = qt.QTableWidgetItem(dancer.scot_dance_num)
            item_address = qt.QTableWidgetItem(dancer.street)
            item_city = qt.QTableWidgetItem(dancer.city)
            item_state = qt.QTableWidgetItem(dancer.state)
            item_zip = qt.QTableWidgetItem(dancer.zip)
            item_birthdate = qt.QTableWidgetItem(dancer.birthdate)
            if dancer.age is not None:
                item_age = qt.QTableWidgetItem(f"{dancer.age}")
            else:
                item_age = qt.QTableWidgetItem('')
            item_entryrcvd = qt.QTableWidgetItem(dancer.registered_date)
            item_phone_num = qt.QTableWidgetItem(dancer.phone_num)
            item_email = qt.QTableWidgetItem(dancer.email)
            item_teacher = qt.QTableWidgetItem(dancer.teacher)
            item_teacher_email = qt.QTableWidgetItem(dancer.teacher_email)
            item_dancer_id = qt.QTableWidgetItem(('%d' % dancer.iid))
            self.table_dancers.setRowCount(row+1)
            self.table_dancers.setItem(row,  0, item_first_name)
            self.table_dancers.setItem(row,  1, item_last_name)
            self.table_dancers.setItem(row,  2, item_number)
            self.table_dancers.setCellWidget(row, 3, selector_category)
            self.table_dancers.setItem(row,  4, item_groups)
            self.table_dancers.setItem(row,  5, item_scotdance)
            self.table_dancers.setItem(row,  6, item_address)
            self.table_dancers.setItem(row,  7, item_city)
            self.table_dancers.setItem(row,  8, item_state)
            self.table_dancers.setItem(row,  9, item_zip)
            self.table_dancers.setItem(row, 10, item_birthdate)
            self.table_dancers.setItem(row, 11, item_age)
            self.table_dancers.setItem(row, 12, item_entryrcvd)
            self.table_dancers.setItem(row, 13, item_phone_num)
            self.table_dancers.setItem(row, 14, item_email)
            self.table_dancers.setItem(row, 15, item_teacher)
            self.table_dancers.setItem(row, 16, item_teacher_email)
            self.table_dancers.setItem(row, 17, item_dancer_id)
            self.table_dancers.setItem(row, 18, item_cat_id)
            row += 1
        self.table_dancers.setColumnHidden(17, True)
        self.table_dancers.setColumnHidden(18, True)
        self.table_dancers.setSortingEnabled(True)
        self.table_dancers.itemChanged.connect(self.item_changed)
        self.layout.addWidget(self.table_dancers)
        self.new_button = qt.QPushButton('&New Competitor')
        self.new_button.clicked.connect(self.new_dancer)
        self.layout.addWidget(self.new_button)
        self.delete_button = qt.QPushButton('&Delete Selected Competitor')
        self.delete_button.clicked.connect(self.delete_dancer)
        self.layout.addWidget(self.delete_button)
        self.save_btn = qt.QPushButton('&Save')
        self.save_btn.clicked.connect(self.save_button)
        self.layout.addWidget(self.save_btn)
        self.exit_button = qt.QPushButton('E&xit')
        self.exit_button.clicked.connect(self.cancel_button)
        self.layout.addWidget(self.exit_button)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def item_changed(self, sender=None):
        self.changes_made = True

    def cancel_button(self, sender=None):
        if self.changes_made:
            save_result = ask_save()
        else:
            save_result = 'discard'
        if self.db.settings.verbose:
            print(save_result)
        if save_result == 'discard':
            self.hide()
        elif save_result == 'save':
            self.save_button()
            self.hide()
        else:
            pass

    def new_dancer(self, sender=None):
        row = self.table_dancers.rowCount()
        # id, firstName, lastName, scotDanceNum, street, city, state, zipCode,
        # birthdate, age, registeredDate, number, phonenum, email, teacher,
        # teacherEmail, dancerCat, dancer_group, competition
        dancer = self.db.t.dancer.new()
        self.table_dancers.insertRow(row)
        item_first_name = qt.QTableWidgetItem(dancer.first_name)
        item_last_name = qt.QTableWidgetItem(dancer.last_name)
        item_number = qt.QTableWidgetItem(dancer.competitor_num)
        selector_category = qt.QComboBox()
        categories = self.db.t.category.get_all()
        for category in categories:
            selector_category.addItem(category.name)
        if dancer.dancer_category is not None:
            selector_category.setCurrentIndex(dancer.dancer_category)
        else:
            selector_category.setCurrentIndex(0)
        category = self.db.t.category.get(dancer.dancer_category)
        if category is not None:
            category_name = category.name
        else:
            category_name = ''
        # item_cat = qt.QTableWidgetItem(dancerCat_name)
        item_cat_id = qt.QTableWidgetItem(dancer.dancer_category)
        dancer_groups = self.db.t.group.get_by_dancer(dancer.iid)
        dancer_group_list = ''
        for group in dancer_groups:
            if dancer_group_list != '':
                dancer_group_list += ', '
            dancer_group_list += group.abbrev
        item_groups = qt.QTableWidgetItem(dancer_group_list)
        item_scotdance = qt.QTableWidgetItem(dancer.scot_dance_num)
        item_address = qt.QTableWidgetItem(dancer.street)
        item_city = qt.QTableWidgetItem(dancer.city)
        item_state = qt.QTableWidgetItem(dancer.state)
        item_zip = qt.QTableWidgetItem(dancer.zip)
        item_birthdate = qt.QTableWidgetItem(dancer.birthdate)
        if dancer.age is not None:
            item_age = qt.QTableWidgetItem(f"{dancer.age}")
        else:
            item_age = qt.QTableWidgetItem('')
        item_entryrcvd = qt.QTableWidgetItem(dancer.registered_date)
        item_phone_num = qt.QTableWidgetItem(dancer.phone_num)
        item_email = qt.QTableWidgetItem(dancer.email)
        item_teacher = qt.QTableWidgetItem(dancer.teacher)
        item_teacher_email = qt.QTableWidgetItem(dancer.teacher_email)
        item_dancer_id = qt.QTableWidgetItem(('%d' % dancer.iid))
        self.table_dancers.setItem(row,  0, item_first_name)
        self.table_dancers.setItem(row,  1, item_last_name)
        self.table_dancers.setItem(row,  2, item_number)
        self.table_dancers.setCellWidget(row, 3, selector_category)
        self.table_dancers.setItem(row,  4, item_groups)
        self.table_dancers.setItem(row,  5, item_scotdance)
        self.table_dancers.setItem(row,  6, item_address)
        self.table_dancers.setItem(row,  7, item_city)
        self.table_dancers.setItem(row,  8, item_state)
        self.table_dancers.setItem(row,  9, item_zip)
        self.table_dancers.setItem(row, 10, item_birthdate)
        self.table_dancers.setItem(row, 11, item_age)
        self.table_dancers.setItem(row, 12, item_entryrcvd)
        self.table_dancers.setItem(row, 13, item_phone_num)
        self.table_dancers.setItem(row, 14, item_email)
        self.table_dancers.setItem(row, 15, item_teacher)
        self.table_dancers.setItem(row, 16, item_teacher_email)
        self.table_dancers.setItem(row, 17, item_dancer_id)
        self.table_dancers.setItem(row, 18, item_cat_id)
        self.table_dancers.scrollToItem(self.table_dancers.item(row, 0))
        self.changes_made = True

    def delete_dancer(self, sender=None):
        row = self.table_dancers.currentRow()
        if row is not None:
            dancer = self.db.t.dancer.get(
                int(self.table_dancers.item(row, 17).text()))
            if dancer is not None:
                verity = verify(('Are you sure you want to delete dancer %s '\
                                 '%s?' % (dancer.first_name, dancer.last_name)),
                                 'This will delete all data for the given '\
                                 'competitor. This cannot be undone.')
                if verity:
                    print('Will delete dancer %d' % dancer.iid)
                    self.db.t.dancer.remove(dancer.iid)
                    self.table_dancers.removeRow(row)
                else:
                    print('Nothing deleted')

    def save_button(self, sender=None):
        self.table_dancers.setFocus()
        row = 0
        while row < self.table_dancers.rowCount():
            dancer_id = int(self.table_dancers.item(row, 17).text())
            dancer = self.db.t.dancer.get(dancer_id)
            dancer.first_name = sanitize(self.table_dancers.item(row, 0).text())
            dancer.last_name = sanitize(self.table_dancers.item(row, 1).text())
            dancer.competitor_num = sanitize(
                self.table_dancers.item(row, 2).text())
            dancer.scot_dance_num = sanitize(
                self.table_dancers.item(row, 5).text())
            dancer.street = sanitize(self.table_dancers.item(row, 6).text())
            dancer.city = sanitize(self.table_dancers.item(row, 7).text())
            dancer.state = sanitize(self.table_dancers.item(row, 8).text())
            dancer.zip = sanitize(self.table_dancers.item(row, 9).text())
            dancer.birthdate = self.table_dancers.item(row, 10).text()
            dancer_age = self.table_dancers.item(row, 11).text()
            if dancer_age.isdigit():
                dancer.age = int(dancer_age)
            dancer.registered_date = self.table_dancers.item(row, 12).text()
            dancer.phone_num = sanitize(self.table_dancers.item(row, 13).text())
            dancer.email = sanitize(self.table_dancers.item(row, 14).text())
            dancer.teacher = sanitize(self.table_dancers.item(row, 15).text())
            dancer.teacher_email = sanitize(
                self.table_dancers.item(row, 16).text())
            selector_category = self.table_dancers.cellWidget(row, 3)
            if selector_category.currentIndex() > 0:
                dancer.dancer_category = selector_category.currentIndex()
            dancer_groups_text = self.table_dancers.item(row, 4).text()
            dancer_groups_text = ''.join(dancer_groups_text.split())
            if dancer_groups_text != '':
                dancer_groups_abbrev = dancer_groups_text.split(',')
                already_in_groups = self.db.t.group.get_by_dancer(dancer_id)
                already_in_abbrevs = []
                for group in already_in_groups:
                    if group is not None:
                        already_in_abbrevs.append(group.abbrev)
                for abbrev in dancer_groups_abbrev:
                    if abbrev in already_in_abbrevs:
                        if self.db.settings.verbose:
                            print('Dancer %s %s is already in group [%s] and '\
                                  'should remain' % (dancer.first_name,
                                                     dancer.last_name, abbrev))
                    else:
                        if self.db.settings.verbose:
                            print('Dancer %s %s is not in group [%s] and '
                                  'should be added' % (dancer.first_name,
                                                       dancer.last_name,
                                                       abbrev))
                        dancer_group = self.db.t.group.get_by_abbrev(
                                                        abbrev,
                                                        self.competition_id)
                        if dancer_group is not None:
                            self.db.t.group.join(dancer.iid, dancer_group.iid)
                for abbrev in already_in_abbrevs:
                    if abbrev in dancer_groups_abbrev:
                        if self.db.settings.verbose:
                            print('Dancer %s %s is already in group [%s] and '
                                  'should remain' % (dancer.first_name,
                                                     dancer.last_name, abbrev))
                    else:
                        if self.db.settings.verbose:
                            print('Dancer %s %s is in group [%s] and should '
                                  'be removed' % (dancer.first_name,
                                                  dancer.last_name, abbrev))
                        dancer_group = self.db.t.group.get_by_abbrev(
                                                        abbrev,
                                                        self.competition_id)
                        if dancer_group is not None:
                            self.db.t.group.unjoin(dancer.iid, dancer_group.iid)
            self.db.t.dancer.update(dancer)
            row += 1
        self.changes_made = False
