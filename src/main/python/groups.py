import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import SPushButton, verify, ask_save


class GroupEditor(qt.QDialog):
    def __init__(self, main_window, dancerGroup, db):
        super().__init__()
        self.db = db
        if self.db.settings.verbose:
            print("GroupEditor in groups.py")
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.dancerGroup = dancerGroup
        # self.dancerGroup = self.db.tables.groups.get(dancerGroup_id)
        self.changes_made = False
        # id, name, abbrev, ageMin, ageMax, dancerCat, competition
        self.layout = qt.QVBoxLayout()
        self.label_name = qt.QLabel('Group Name:')
        self.field_name = qt.QLineEdit(self.dancerGroup.name)
        self.label_abbrev = qt.QLabel('Abbreviation:')
        print(self.dancerGroup.abbrev)
        self.field_abbrev = qt.QLineEdit(self.dancerGroup.abbrev)
        self.label_ageMin = qt.QLabel('Minimum Age:')
        self.field_ageMin = qt.QLineEdit('%d' % self.dancerGroup.ageMin)
        self.label_ageMax = qt.QLabel('Maxiumum Age:')
        self.field_ageMax = qt.QLineEdit('%d' % self.dancerGroup.ageMax)
        self.selector_dancerCat = qt.QComboBox()
        dancerCats = self.db.tables.categories.get_all()
        for dancerCat in dancerCats:
            self.selector_dancerCat.addItem(dancerCat.name)
            if self.db.settings.verbose:
                print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
        if self.dancerGroup.dancerCat is not None:
            self.selector_dancerCat.setCurrentIndex(self.dancerGroup.dancerCat)
        else:
            self.selector_dancerCat.setCurrentIndex(0)
        self.dancers_in_group = \
            self.db.tables.dancers.get_by_group(dancerGroup.id)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer is not None:
                self.dancer_ids.append(dancer.id)
        self.table_dancers = qt.QTableWidget()
        self.headers = ['', 'Num', 'First Name', 'Last Name', 'id']
        self.table_dancers.setColumnCount(len(self.headers))
        self.table_dancers.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [20, 40, 120, 150, 0]
        all_dancers = self.db.tables.dancers\
            .get_by_competition(self.dancerGroup.competition)
        column = 0
        while column < len(self.column_widths):
            self.table_dancers.setColumnWidth(column,
                                              self.column_widths[column])
            column += 1
        row = 0
        for dancer in all_dancers:
            if dancer is not None:
                item_first_name = qt.QTableWidgetItem(dancer.firstName)
                item_last_name = qt.QTableWidgetItem(dancer.lastName)
                item_number = qt.QTableWidgetItem(dancer.number)
                checkbox_in_group = qt.QCheckBox()
                if dancer.id in self.dancer_ids:
                    checkbox_in_group.setCheckState(2)
                else:
                    checkbox_in_group.setCheckState(0)
                checkbox_in_group.stateChanged.connect(self.item_changed)
                item_dancer_id = qt.QTableWidgetItem('%d' % dancer.id)

                self.table_dancers.setRowCount(row+1)
                self.table_dancers.setCellWidget(row, 0, checkbox_in_group)
                self.table_dancers.setItem(row, 1, item_number)
                self.table_dancers.setItem(row, 2, item_first_name)
                self.table_dancers.setItem(row, 3, item_last_name)
                self.table_dancers.setItem(row, 4, item_dancer_id)

                row += 1

        self.table_dancers.setColumnHidden(4, True)

        self.table_events = qt.QTableWidget()
        self.events_headers = ['Event', 'In Overall', 'Places', 'Stamp', 'id']
        self.table_events.setColumnCount(len(self.events_headers))
        self.table_events.setHorizontalHeaderLabels(self.events_headers)
        self.column_widths = [260, 40, 60, 40, 0]
        column = 0
        while column < len(self.column_widths):
            self.table_events.setColumnWidth(column,
                                             self.column_widths[column])
            column += 1
        self.table_events.setColumnHidden(4, True)
        self.events = self.db.tables.events.get_by_group(self.dancerGroup.id)
        row = 0
        # id, name, dancerGroup, dance, competition,
        # countsForOverall, numPlaces, earnsStamp
        for event in self.events:
            if event is not None:
                # dance = scrudb.retrieve_dance(event.dance)
                # item_name = QTableWidgetItem(dance.name)
                dances = self.db.tables.dances.get_all()
                selector_dance = qt.QComboBox()
                index = 999999
                for dance in dances:
                    if dance.id < index:
                        index = dance.id
                    selector_dance.addItem(dance.name)
                if event.dance is not None:
                    selector_dance.setCurrentIndex(event.dance - index)
                else:
                    selector_dance.setCurrentIndex(0)
                selector_dance.currentIndexChanged.connect(self.item_changed)
                item_places = qt.QTableWidgetItem('%d' % event.numPlaces)
                checkbox_counts = qt.QCheckBox()
                if event.countsForOverall == 1:
                    checkbox_counts.setCheckState(2)
                else:
                    checkbox_counts.setCheckState(0)
                checkbox_counts.stateChanged.connect(self.item_changed)
                checkbox_stamp = qt.QCheckBox()
                if event.earnsStamp == 1:
                    checkbox_stamp.setCheckState(2)
                else:
                    checkbox_stamp.setCheckState(0)
                checkbox_stamp.stateChanged.connect(self.item_changed)
                item_event_id = qt.QTableWidgetItem('%d' % event.id)

                self.table_events.setRowCount(row+1)
                # self.table_events.setItem(row, 0, item_name)
                self.table_events.setCellWidget(row, 0, selector_dance)
                self.table_events.setItem(row, 2, item_places)
                self.table_events.setCellWidget(row, 1, checkbox_counts)
                self.table_events.setCellWidget(row, 3, checkbox_stamp)
                self.table_events.setItem(row, 4, item_event_id)

                row += 1
        self.groupBox = qt.QGroupBox('Events')
        self.groupBox_layout = qt.QVBoxLayout()
        self.groupBox_layout.addWidget(self.table_events)
        self.button_add_event = qt.QPushButton('Add Event')
        self.button_add_event.clicked.connect(self.new_event)
        self.groupBox_layout.addWidget(self.button_add_event)
        self.button_delete_event = qt.QPushButton('Remove Event')
        self.button_delete_event.clicked.connect(self.delete_event)
        self.groupBox_layout.addWidget(self.button_delete_event)
        self.groupBox.setLayout(self.groupBox_layout)

        self.table_dancers.itemChanged.connect(self.item_changed)
        self.table_events.itemChanged.connect(self.item_changed)
        self.field_abbrev.textChanged.connect(self.item_changed)
        self.field_name.textChanged.connect(self.item_changed)
        self.field_ageMin.textChanged.connect(self.item_changed)
        self.field_ageMax.textChanged.connect(self.item_changed)
        self.selector_dancerCat.currentIndexChanged.connect(self.item_changed)

        self.button_save = qt.QPushButton('&Save')
        self.button_save.clicked.connect(self.save_button)
        self.button_delete_group = qt.QPushButton('&Delete')
        self.button_delete_group.clicked.connect(self.delete_group)
        self.button_exit = qt.QPushButton('E&xit')
        self.button_exit.clicked.connect(self.exit_button)

        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.field_name)
        self.layout.addWidget(self.label_abbrev)
        self.layout.addWidget(self.field_abbrev)
        self.layout.addWidget(self.label_ageMin)
        self.layout.addWidget(self.field_ageMin)
        self.layout.addWidget(self.label_ageMax)
        self.layout.addWidget(self.field_ageMax)
        self.layout.addWidget(self.selector_dancerCat)
        self.layout.addWidget(self.table_dancers)
        self.layout.addWidget(self.groupBox)
        self.layout.addWidget(self.button_delete_group)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.button_exit)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def save_button(self, sender=None):
        self.setFocus()
        self.dancerGroup.name = self.field_name.text()
        self.dancerGroup.abbrev = self.field_abbrev.text()
        if (self.field_ageMin.text().isdigit()):
            self.dancerGroup.ageMin = int(self.field_ageMin.text())
        if (self.field_ageMax.text().isdigit()):
            self.dancerGroup.ageMax = int(self.field_ageMax.text())
        self.dancerGroup.dancerCat = self.selector_dancerCat.currentIndex()
        self.db.tables.groups.update(self.dancerGroup)
        row = 0
        self.dancers_in_group = self.db.tables.dancers.get_by_group(
            self.dancerGroup.id)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer is not None:
                self.dancer_ids.append(dancer.id)
        while row < self.table_dancers.rowCount():
            checkbox_in_group = self.table_dancers.cellWidget(row, 0)
            dancer_id_text = self.table_dancers.item(row, 4).text()
            if dancer_id_text != '':
                dancer_id = int(dancer_id_text)
            else:
                dancer_id = 9999999999999999999
            if checkbox_in_group.checkState() == 0 and (dancer_id in
                                                        self.dancer_ids):
                if self.db.settings.verbose:
                    print('dancer [%s] in row %d is in group but should be\
                          removed' % (dancer_id_text, row))
                self.db.tables.groups.unjoin(dancer_id, self.dancerGroup.id)
            elif checkbox_in_group.checkState() == 2 and (dancer_id not in
                                                          self.dancer_ids):
                if self.db.settings.verbose:
                    print('dancer [%s] in row %d is not in group but should be\
                           added' % (dancer_id_text, row))
                self.db.tables.groups.join(dancer_id, self.dancerGroup.id)
            row += 1
        row = 0
        while row < self.table_events.rowCount():
            event_id = int(self.table_events.item(row, 4).text())
            event = self.db.tables.events.get(event_id)
            selector_dance = self.table_events.cellWidget(row, 0)
            event.name = ('%s - %s' % (self.dancerGroup.name,
                                       selector_dance.currentText()))
            if self.db.settings.verbose:
                print(event.name)
            dances = self.db.tables.dances.get_all()
            index = 999999
            for dance in dances:
                if dance.id < index:
                    index = dance.id
            event.dance = selector_dance.currentIndex() + index
            if self.table_events.item(row, 2).text().isdigit():
                event.numPlaces = int(self.table_events.item(row, 2).text())
            checkbox_counts = self.table_events.cellWidget(row, 1)
            if checkbox_counts.checkState() == 2:
                event.countsForOverall = 1
            else:
                event.countsForOverall = 0
            checkbox_stamp = self.table_events.cellWidget(row, 3)
            if checkbox_stamp.checkState() == 2:
                event.earnsStamp = 1
            else:
                event.earnsStamp = 0
            self.db.tables.events.update(event)
            row += 1
        self.changes_made = False

    def new_event(self, sender=None):
        event = self.db.tables.events.new(self.dancerGroup.id,
                                          self.dancerGroup.competition)
        # event = sc.Event(0, '', self.dancerGroup.id, 0,
        #                  self.dancerGroup.competition, 1, 6, 1)
        # event = self.db.tables.events.insert(event)
        row = self.table_events.rowCount()
        # id, name, dancerGroup, dance, competition,
        # countsForOverall, numPlaces, earnsStamp
        self.table_events.insertRow(row)
        dances = self.db.tables.dances.get_all()
        selector_dance = qt.QComboBox()
        for dance in dances:
            selector_dance.addItem(dance.name)
        selector_dance.setCurrentIndex(0)
        selector_dance.currentIndexChanged.connect(self.item_changed)
        item_places = qt.QTableWidgetItem('%d' % event.numPlaces)
        checkbox_counts = qt.QCheckBox()
        if event.countsForOverall == 1:
            checkbox_counts.setCheckState(2)
        else:
            checkbox_counts.setCheckState(0)
        checkbox_counts.stateChanged.connect(self.item_changed)
        checkbox_stamp = qt.QCheckBox()
        if event.earnsStamp == 1:
            checkbox_stamp.setCheckState(2)
        else:
            checkbox_stamp.setCheckState(0)
        checkbox_stamp.stateChanged.connect(self.item_changed)
        item_event_id = qt.QTableWidgetItem('%d' % event.id)

        self.table_events.setCellWidget(row, 0, selector_dance)
        self.table_events.setItem(row, 2, item_places)
        self.table_events.setCellWidget(row, 1, checkbox_counts)
        self.table_events.setCellWidget(row, 3, checkbox_stamp)
        self.table_events.setItem(row, 4, item_event_id)
        self.changes_made = True

    def delete_event(self, sender=None):
        row = self.table_events.currentRow()
        if row is not None:
            # event = self.db.tables.events.get(int(self.table_events.item(
            # row, 4).text()))
            event = self.db.tables.events.get(int(self.table_events.item(
                row, 4)))
            dance = self.db.tables.dances.get(event.dance)
            if event is not None:
                verity = verify(('Are you sure you want to delete event %s %s?'
                                 % (self.dancerGroup.name, dance.name)),
                                'This will delete all data for the given event\
                                and all scores associated with this event.\
                                This cannot be undone.')
                if verity:
                    if self.db.settings.verbose:
                        print('Will delete event %d' % event.id)
                    self.db.tables.events.remove(event.id)
                    self.table_events.removeRow(row)
                else:
                    print('Nothing deleted')

    def delete_group(self, sender=None):
        verity = verify(('Are you sure you want to delete competitor group\
                         %s?' % self.dancerGroup.name), 'This will delete all\
                         data for the given group and all scores associated\
                         with this group. This cannot be undone.')
        if verity:
            if self.db.settings.verbose:
                print('Will delete group %d' % self.dancerGroup.id)
            self.db.tables.groups.remove(self.dancerGroup.id)
            self.hide()
        else:
            print('Nothing deleted')

    def exit_button(self, sender=None):
        if self.changes_made:
            saveResult = ask_save()
        else:
            saveResult = 'discard'
        if self.db.settings.verbose:
            print(saveResult)
        if saveResult == 'discard':
            self.hide()
        elif saveResult == 'save':
            self.save_button()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        self.changes_made = True


class GroupMenu(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.comp_id = comp_id
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(qt.QLabel('Choose a Competitor Group:'))
        self.dancerGroups = self.db.tables.groups.get_by_competition(comp_id)
        self.dgButtons = []
        for dancerGroup in self.dancerGroups:
            dgButton = SPushButton(('[%s] %s' % (dancerGroup.abbrev,
                                                 dancerGroup.name)),
                                   self, dancerGroup.id, self.set_dancer_group)
            dgButton.clicked.connect(dgButton.on_button_clicked)
            self.dgButtons.append(dgButton)
        for dgButton in self.dgButtons:
            self.layout.addWidget(dgButton)
        self.newButton = qt.QPushButton('&New Group')
        self.newButton.clicked.connect(self.new_group)
        self.layout.addWidget(self.newButton)
        self.exitButton = qt.QPushButton('E&xit')
        self.exitButton.clicked.connect(self.hide)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def new_group(self, sender=None):
        group = self.db.tables.groups.new(self.comp_id)
        self.set_dancer_group(group.id)

    def set_dancer_group(self, dancerGroup_id):
        dancerGroup = self.db.tables.groups.get(dancerGroup_id)
        if dancerGroup is not None:
            if self.main_window.settings.verbose:
                print('Group: [%s] %s' %
                      (dancerGroup.abbrev, dancerGroup.name))
            self.hide()
            self.main_window.edit_dancerGroup(dancerGroup)
