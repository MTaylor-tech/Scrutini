import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import verify, ask_save

class DancerEditor(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(DancerEditor, self).__init__()
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.comp_id = comp_id
        self.db = db
        self.changes_made = False
        self.resize(1680, 1000)
        self.layout = qt.QVBoxLayout()
        self.dancers = self.db.tables.dancers.get_by_competition(comp_id)
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
        # teacher, teacherEmail, dancerCat, dancerGroup, competition
        for dancer in self.dancers:
            item_first_name = qt.QTableWidgetItem(dancer.firstName)
            item_last_name = qt.QTableWidgetItem(dancer.lastName)
            item_number = qt.QTableWidgetItem(dancer.number)
            selector_dancerCat = qt.QComboBox()
            dancerCats = self.db.tables.categories.get_all()
            for dancerCat in dancerCats:
                selector_dancerCat.addItem(dancerCat.name)
                if self.db.settings.verbose:
                    print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
            if dancer.dancerCat is not None:
                selector_dancerCat.setCurrentIndex(dancer.dancerCat)
            else:
                selector_dancerCat.setCurrentIndex(0)
            dancerCat = self.db.tables.categories.get(dancer.dancerCat)
            # if dancerCat is not None:
            #     dancerCat_name = dancerCat.name
            # else:
            #     dancerCat_name = ''
            item_cat_id = qt.QTableWidgetItem(dancer.dancerCat)
            dancer_groups = self.db.tables.groups.get_by_dancer(dancer.id)
            dancer_group_list = ''
            for group in dancer_groups:
                if dancer_group_list != '':
                    dancer_group_list += ', '
                dancer_group_list += group.abbrev
            item_groups = qt.QTableWidgetItem(dancer_group_list)

            item_scotdance = qt.QTableWidgetItem(dancer.scotDanceNum)
            item_address = qt.QTableWidgetItem(dancer.street)
            item_city = qt.QTableWidgetItem(dancer.city)
            item_state = qt.QTableWidgetItem(dancer.state)
            item_zipCode = qt.QTableWidgetItem(dancer.zipCode)

            # if ((dancer.birthdate != '') and (dancer.birthdate != None)):
            #    item_birthdate = QTableWidgetItem(self.get_formatted_date(dancer.birthdate))
            # else:
            #    item_birthdate = QTableWidgetItem('')
            item_birthdate = qt.QTableWidgetItem(dancer.birthdate)

            if type(dancer.age) == int:
                item_age = qt.QTableWidgetItem(('%d' % dancer.age))
            elif dancer.age is not None:
                item_age = qt.QTableWidgetItem(dancer.age)
            else:
                item_age = qt.QTableWidgetItem('')

            #if ((dancer.registeredDate != '') and (dancer.registeredDate != None)):
            #    item_entryrcvd = QTableWidgetItem(self.get_formatted_date(dancer.registeredDate))
            #else:
            #    item_entryrcvd = QTableWidgetItem('')
            item_entryrcvd = qt.QTableWidgetItem(dancer.registeredDate)

            item_phonenum = qt.QTableWidgetItem(dancer.phonenum)
            item_email = qt.QTableWidgetItem(dancer.email)
            item_teacher = qt.QTableWidgetItem(dancer.teacher)
            item_teacherEmail = qt.QTableWidgetItem(dancer.teacherEmail)
            item_dancer_id = qt.QTableWidgetItem(('%d' % dancer.id))

            self.table_dancers.setRowCount(row+1)
            self.table_dancers.setItem(row,  0, item_first_name)
            self.table_dancers.setItem(row,  1, item_last_name)
            self.table_dancers.setItem(row,  2, item_number)
            self.table_dancers.setCellWidget(row, 3, selector_dancerCat)
            self.table_dancers.setItem(row,  4, item_groups)
            self.table_dancers.setItem(row,  5, item_scotdance)
            self.table_dancers.setItem(row,  6, item_address)
            self.table_dancers.setItem(row,  7, item_city)
            self.table_dancers.setItem(row,  8, item_state)
            self.table_dancers.setItem(row,  9, item_zipCode)
            self.table_dancers.setItem(row, 10, item_birthdate)
            self.table_dancers.setItem(row, 11, item_age)
            self.table_dancers.setItem(row, 12, item_entryrcvd)
            self.table_dancers.setItem(row, 13, item_phonenum)
            self.table_dancers.setItem(row, 14, item_email)
            self.table_dancers.setItem(row, 15, item_teacher)
            self.table_dancers.setItem(row, 16, item_teacherEmail)
            self.table_dancers.setItem(row, 17, item_dancer_id)
            self.table_dancers.setItem(row, 18, item_cat_id)

            row += 1
        self.table_dancers.setColumnHidden(17, True)
        self.table_dancers.setColumnHidden(18, True)
        self.table_dancers.setSortingEnabled(True)
        self.table_dancers.itemChanged.connect(self.item_changed)
        self.layout.addWidget(self.table_dancers)
        self.newButton = qt.QPushButton('&New Competitor')
        self.newButton.clicked.connect(self.new_dancer)
        self.layout.addWidget(self.newButton)
        self.deleteButton = qt.QPushButton('&Delete Selected Competitor')
        self.deleteButton.clicked.connect(self.delete_dancer)
        self.layout.addWidget(self.deleteButton)
        self.saveButton = qt.QPushButton('&Save')
        self.saveButton.clicked.connect(self.save_button)
        self.layout.addWidget(self.saveButton)
        self.exitButton = qt.QPushButton('E&xit')
        self.exitButton.clicked.connect(self.cancel_button)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def item_changed(self, sender=None):
        print('Item changed')
        self.changes_made = True

    def cancel_button(self, sender=None):
        if (self.changes_made):
            saveResult = ask_save()
        else:
            saveResult = 'discard'

        if (saveResult == 'discard'):
            self.hide()
        elif (saveResult == 'save'):
            self.save_button()
            self.hide()
        else:
            pass

    def new_dancer(self, sender=None):
        row = self.table_dancers.rowCount()
        # id, firstName, lastName, scotDanceNum, street, city, state, zipCode,
        # birthdate, age, registeredDate, number, phonenum, email, teacher,
        # teacherEmail, dancerCat, dancerGroup, competition
        dancer = self.db.tables.dancers.new()
        self.table_dancers.insertRow(row)
        item_first_name = qt.QTableWidgetItem(dancer.firstName)
        item_last_name = qt.QTableWidgetItem(dancer.lastName)
        item_number = qt.QTableWidgetItem(dancer.number)

        selector_dancerCat = qt.QComboBox()
        dancerCats = self.db.tables.categories.get_all()
        for dancerCat in dancerCats:
            selector_dancerCat.addItem(dancerCat.name)
            if self.db.settings.verbose:
                print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
        if dancer.dancerCat is not None:
            selector_dancerCat.setCurrentIndex(dancer.dancerCat)
        else:
            selector_dancerCat.setCurrentIndex(0)
        dancerCat = self.db.tables.categories.get(dancer.dancerCat)
        if dancerCat is not None:
            dancerCat_name = dancerCat.name
        else:
            dancerCat_name = ''
        # item_cat = qt.QTableWidgetItem(dancerCat_name)
        item_cat_id = qt.QTableWidgetItem(dancer.dancerCat)

        dancer_groups = self.db.tables.groups.get_by_dancer(dancer.id)
        dancer_group_list = ''
        for group in dancer_groups:
            if dancer_group_list != '':
                dancer_group_list += ', '
            dancer_group_list += group.abbrev
        item_groups = qt.QTableWidgetItem(dancer_group_list)

        item_scotdance = qt.QTableWidgetItem(dancer.scotDanceNum)
        item_address = qt.QTableWidgetItem(dancer.street)
        item_city = qt.QTableWidgetItem(dancer.city)
        item_state = qt.QTableWidgetItem(dancer.state)
        item_zipCode = qt.QTableWidgetItem(dancer.zipCode)
        item_birthdate = qt.QTableWidgetItem(dancer.birthdate)

        if type(dancer.age) == int:
            item_age = qt.QTableWidgetItem(('%d' % dancer.age))
        elif dancer.age is not None:
            item_age = qt.QTableWidgetItem(dancer.age)
        else:
            item_age = qt.QTableWidgetItem('')
        item_entryrcvd = qt.QTableWidgetItem(dancer.registeredDate)

        item_phonenum = qt.QTableWidgetItem(dancer.phonenum)
        item_email = qt.QTableWidgetItem(dancer.email)
        item_teacher = qt.QTableWidgetItem(dancer.teacher)
        item_teacherEmail = qt.QTableWidgetItem(dancer.teacherEmail)
        item_dancer_id = qt.QTableWidgetItem(('%d' % dancer.id))

        self.table_dancers.setItem(row,  0, item_first_name)
        self.table_dancers.setItem(row,  1, item_last_name)
        self.table_dancers.setItem(row,  2, item_number)
        self.table_dancers.setCellWidget(row, 3, selector_dancerCat)
        self.table_dancers.setItem(row,  4, item_groups)
        self.table_dancers.setItem(row,  5, item_scotdance)
        self.table_dancers.setItem(row,  6, item_address)
        self.table_dancers.setItem(row,  7, item_city)
        self.table_dancers.setItem(row,  8, item_state)
        self.table_dancers.setItem(row,  9, item_zipCode)
        self.table_dancers.setItem(row, 10, item_birthdate)
        self.table_dancers.setItem(row, 11, item_age)
        self.table_dancers.setItem(row, 12, item_entryrcvd)
        self.table_dancers.setItem(row, 13, item_phonenum)
        self.table_dancers.setItem(row, 14, item_email)
        self.table_dancers.setItem(row, 15, item_teacher)
        self.table_dancers.setItem(row, 16, item_teacherEmail)
        self.table_dancers.setItem(row, 17, item_dancer_id)
        self.table_dancers.setItem(row, 18, item_cat_id)
        self.table_dancers.scrollToItem(self.table_dancers.item(row, 0))
        self.changes_made = True

    def delete_dancer(self, sender=None):
        row = self.table_dancers.currentRow()
        if row is not None:
            dancer = self.db.tables.dancers.get(int(self.table_dancers.item(row, 17).text()))
            if dancer is not None:
                verity = verify(('Are you sure you want to delete dancer %s\
                                 %s?' % (dancer.firstName, dancer.lastName)),
                                'This will delete all data for the given\
                                competitor. This cannot be undone.')
                if verity:
                    print('Will delete dancer %d' % dancer.id)
                    self.db.tables.dancers.remove(dancer.id)
                    self.table_dancers.removeRow(row)
                else:
                    print('Nothing deleted')

    def save_button(self, sender=None):
        self.table_dancers.setFocus()
        row = 0
        while row < self.table_dancers.rowCount():
            dancer_id = int(self.table_dancers.item(row, 17).text())
            dancer = self.db.tables.dancers.get(dancer_id)
            dancer.firstName = self.table_dancers.item(row, 0).text()
            dancer.lastName = self.table_dancers.item(row, 1).text()
            dancer.number = self.table_dancers.item(row, 2).text()

            dancer.scotDanceNum = self.table_dancers.item(row, 5).text()
            dancer.street = self.table_dancers.item(row, 6).text()
            dancer.city = self.table_dancers.item(row, 7).text()
            dancer.state = self.table_dancers.item(row, 8).text()
            dancer.zipCode = self.table_dancers.item(row, 9).text()
            dancer.birthdate = self.table_dancers.item(row, 10).text()
            dancer_age = self.table_dancers.item(row, 11).text()
            if dancer_age.isdigit():
                dancer.age = int(dancer_age)
            dancer.registeredDate = self.table_dancers.item(row, 12).text()
            dancer.phonenum = self.table_dancers.item(row, 13).text()
            dancer.email = self.table_dancers.item(row, 14).text()
            dancer.teacher = self.table_dancers.item(row, 15).text()
            dancer.teacherEmail = self.table_dancers.item(row, 16).text()

            selector_dancerCat = self.table_dancers.cellWidget(row, 3)
            if selector_dancerCat.currentIndex() > 0:
                dancer.dancerCat = selector_dancerCat.currentIndex()
            #item_cat = self.table_dancers.item(row, 18).text()
            #if (item_cat.isdigit()):
            #    dancer.dancerCat = int(item_cat)

            dancer_groups_text = self.table_dancers.item(row, 4).text()
            dancer_groups_text = ''.join(dancer_groups_text.split())
            if dancer_groups_text != '':
                dancer_groups_abbrev = dancer_groups_text.split(',')
                already_in_groups = self.db.tables.groups.get_by_dancer(dancer_id)
                already_in_abbrevs = []
                for group in already_in_groups:
                    if group is not None:
                        already_in_abbrevs.append(group.abbrev)
                for abbrev in dancer_groups_abbrev:
                    if abbrev in already_in_abbrevs:
                        print('Dancer %s %s is already in group [%s] and should remain' % (dancer.firstName, dancer.lastName, abbrev))
                    else:
                        print('Dancer %s %s is not in group [%s] and should be added' % (dancer.firstName, dancer.lastName, abbrev))
                        dancerGroup = self.db.tables.groups.get_by_abbrev(
                                                        abbrev, self.comp_id)
                        if dancerGroup is not None:
                            self.db.tables.groups.join(dancer.id, dancerGroup.id)
                for abbrev in already_in_abbrevs:
                    if abbrev in dancer_groups_abbrev:
                        print('Dancer %s %s is already in group [%s] and should remain' % (dancer.firstName, dancer.lastName, abbrev))
                    else:
                        print('Dancer %s %s is in group [%s] and should be removed' % (dancer.firstName, dancer.lastName, abbrev))
                        dancerGroup = self.db.tables.groups.get_by_abbrev(
                                                        abbrev, self.comp_id)
                        if dancerGroup is not None:
                            self.db.tables.groups.unjoin(dancer.id, dancerGroup.id)

            self.db.tables.dancers.update(dancer)

            row += 1
        self.changes_made = False

    def get_formatted_date(self, date):
        format_str = '%d %b %Y'
        otherformat_str = '%Y-%m-%d'
        return (datetime.datetime.strftime(datetime.datetime.strptime(('%s' % date)[0:10], otherformat_str).date(), format_str))
