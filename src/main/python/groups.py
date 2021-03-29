import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import SPushButton, verify, ask_save, sanitize


class GroupEditor(qt.QDialog):
    def __init__(self, main_window, dancer_group, db):
        super().__init__()
        self.db = db
        if self.db.s.verbose:
            print("GroupEditor in groups.py")
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.dancer_group = dancer_group
        # self.dancer_group = self.db.t.group.get(dancer_group_id)
        self.changes_made = False
        # id, name, abbrev, age_min, age_max, dancer_category, competition
        self.layout = qt.QVBoxLayout()
        self.label_name = qt.QLabel('Group Name:')
        self.field_name = qt.QLineEdit(self.dancer_group.name)
        self.label_abbrev = qt.QLabel('Abbreviation:')
        self.field_abbrev = qt.QLineEdit(self.dancer_group.abbrev)
        self.label_age_min = qt.QLabel('Minimum Age:')
        self.field_age_min = qt.QLineEdit('%d' % self.dancer_group.age_min)
        self.label_age_max = qt.QLabel('Maxiumum Age:')
        self.field_age_max = qt.QLineEdit('%d' % self.dancer_group.age_max)
        self.selector_dancer_category = qt.QComboBox()
        dancer_categories = self.db.t.category.get_all()
        for dancer_category in dancer_categories:
            self.selector_dancer_category.addItem(dancer_category.name)
            if self.db.s.verbose:
                print('Category: %d [%s]' % (dancer_category.iid,
                                             dancer_category.name))
        if self.dancer_group.dancer_category is not None:
            self.selector_dancer_category.setCurrentIndex(
                self.dancer_group.dancer_category)
        else:
            self.selector_dancer_category.setCurrentIndex(0)
        self.dancers_in_group = self.db.t.dancer.get_by_group(
                                                        dancer_group.iid)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer is not None:
                self.dancer_ids.append(dancer.iid)
        self.table_dancers = qt.QTableWidget()
        self.headers = ['', 'Num', 'First Name', 'Last Name', 'id',
                        'Category', 'Age']
        self.table_dancers.setColumnCount(len(self.headers))
        self.table_dancers.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [20, 60, 120, 150, 0, 100, 40]
        all_dancers = self.db.t.dancer.get_by_competition(
                                        self.dancer_group.competition)
        column = 0
        while column < len(self.column_widths):
            self.table_dancers.setColumnWidth(column,
                                              self.column_widths[column])
            column += 1
        row = 0
        cats = self.db.t.category.get_all()
        for dancer in all_dancers:
            if dancer is not None:
                item_first_name = qt.QTableWidgetItem(dancer.first_name)
                item_last_name = qt.QTableWidgetItem(dancer.last_name)
                item_number = qt.QTableWidgetItem(dancer.competitor_num)
                if dancer.age is not None:
                    item_age = qt.QTableWidgetItem(f"{dancer.age}")
                else:
                    item_age = qt.QTableWidgetItem('')
                item_cat = qt.QTableWidgetItem(
                                            cats[dancer.dancer_category].name)
                checkbox_in_group = qt.QCheckBox()
                if dancer.iid in self.dancer_ids:
                    checkbox_in_group.setCheckState(2)
                else:
                    checkbox_in_group.setCheckState(0)
                checkbox_in_group.stateChanged.connect(self.item_changed)
                item_dancer_id = qt.QTableWidgetItem('%d' % dancer.iid)
                self.table_dancers.setRowCount(row+1)
                self.table_dancers.setCellWidget(row, 0, checkbox_in_group)
                self.table_dancers.setItem(row, 1, item_number)
                self.table_dancers.setItem(row, 2, item_first_name)
                self.table_dancers.setItem(row, 3, item_last_name)
                self.table_dancers.setItem(row, 4, item_dancer_id)
                self.table_dancers.setItem(row, 5, item_cat)
                self.table_dancers.setItem(row, 6, item_age)
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
        self.events = self.db.t.event.get_by_group(self.dancer_group.iid)
        row = 0
        # id, name, dancer_group, dance, competition,
        # counts_for_overall, num_places, earns_stamp
        for event in self.events:
            if event is not None:
                # dance = scrudb.retrieve_dance(event.dance)
                # item_name = QTableWidgetItem(dance.name)
                dances = self.db.t.dance.get_all()
                selector_dance = qt.QComboBox()
                index = 9999999999
                for dance in dances:
                    if dance.iid < index:
                        index = dance.iid
                    selector_dance.addItem(dance.name)
                if event.dance is not None:
                    selector_dance.setCurrentIndex(event.dance - index)
                else:
                    selector_dance.setCurrentIndex(0)
                selector_dance.currentIndexChanged.connect(self.item_changed)
                item_places = qt.QTableWidgetItem('%d' % event.num_places)
                checkbox_counts = qt.QCheckBox()
                if event.counts_for_overall == 1:
                    checkbox_counts.setCheckState(2)
                else:
                    checkbox_counts.setCheckState(0)
                checkbox_counts.stateChanged.connect(self.item_changed)
                checkbox_stamp = qt.QCheckBox()
                if event.earns_stamp == 1:
                    checkbox_stamp.setCheckState(2)
                else:
                    checkbox_stamp.setCheckState(0)
                checkbox_stamp.stateChanged.connect(self.item_changed)
                item_event_id = qt.QTableWidgetItem('%d' % event.iid)
                self.table_events.setRowCount(row+1)
                # self.table_events.setItem(row, 0, item_name)
                self.table_events.setCellWidget(row, 0, selector_dance)
                self.table_events.setItem(row, 2, item_places)
                self.table_events.setCellWidget(row, 1, checkbox_counts)
                self.table_events.setCellWidget(row, 3, checkbox_stamp)
                self.table_events.setItem(row, 4, item_event_id)
                row += 1
        self.group_box = qt.QGroupBox('Events')
        self.group_box_layout = qt.QVBoxLayout()
        self.group_box_layout.addWidget(self.table_events)
        self.button_add_event = qt.QPushButton('Add Event')
        self.button_add_event.clicked.connect(self.new_event)
        self.group_box_layout.addWidget(self.button_add_event)
        self.button_delete_event = qt.QPushButton('Remove Event')
        self.button_delete_event.clicked.connect(self.delete_event)
        self.group_box_layout.addWidget(self.button_delete_event)
        self.group_box.setLayout(self.group_box_layout)
        self.table_dancers.itemChanged.connect(self.item_changed)
        self.table_events.itemChanged.connect(self.item_changed)
        self.field_abbrev.textChanged.connect(self.item_changed)
        self.field_name.textChanged.connect(self.item_changed)
        self.field_age_min.textChanged.connect(self.item_changed)
        self.field_age_max.textChanged.connect(self.item_changed)
        self.selector_dancer_category.currentIndexChanged.connect(
                                                            self.item_changed)
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
        self.layout.addWidget(self.label_age_min)
        self.layout.addWidget(self.field_age_min)
        self.layout.addWidget(self.label_age_max)
        self.layout.addWidget(self.field_age_max)
        self.layout.addWidget(self.selector_dancer_category)
        self.layout.addWidget(self.table_dancers)
        self.layout.addWidget(self.group_box)
        self.layout.addWidget(self.button_delete_group)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.button_exit)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def save_button(self, sender=None):
        self.setFocus()
        self.dancer_group.name = sanitize(self.field_name.text())
        self.dancer_group.abbrev = sanitize(self.field_abbrev.text())
        if (self.field_age_min.text().isdigit()):
            self.dancer_group.age_min = int(self.field_age_min.text())
        if (self.field_age_max.text().isdigit()):
            self.dancer_group.age_max = int(self.field_age_max.text())
        self.dancer_group.dancer_category = (self.selector_dancer_category
                                             .currentIndex())
        self.db.t.group.update(self.dancer_group)
        row = 0
        self.dancers_in_group = self.db.t.dancer.get_by_group(
            self.dancer_group.iid)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer is not None:
                self.dancer_ids.append(dancer.iid)
        while row < self.table_dancers.rowCount():
            checkbox_in_group = self.table_dancers.cellWidget(row, 0)
            dancer_id_text = self.table_dancers.item(row, 4).text()
            if dancer_id_text != '':
                dancer_id = int(dancer_id_text)
            else:
                dancer_id = 9999999999999999999
            if checkbox_in_group.checkState() == 0 and (dancer_id in
                                                        self.dancer_ids):
                if self.db.s.verbose:
                    print('dancer [%s] in row %d is in group but should be '\
                          'removed' % (dancer_id_text, row))
                self.db.t.group.unjoin(dancer_id, self.dancer_group.iid)
            elif checkbox_in_group.checkState() == 2 and (dancer_id not in
                                                          self.dancer_ids):
                if self.db.s.verbose:
                    print('dancer [%s] in row %d is not in group but should '\
                          'be added' % (dancer_id_text, row))
                self.db.t.group.join(dancer_id, self.dancer_group.iid)
            row += 1
        row = 0
        while row < self.table_events.rowCount():
            event_id = int(self.table_events.item(row, 4).text())
            event = self.db.t.event.get(event_id)
            selector_dance = self.table_events.cellWidget(row, 0)
            event.name = ('%s - %s' % (self.dancer_group.name,
                                       selector_dance.currentText()))
            if self.db.s.verbose:
                print(event.name)
            dances = self.db.t.dance.get_all()
            index = 999999
            for dance in dances:
                if dance.iid < index:
                    index = dance.iid
            event.dance = selector_dance.currentIndex() + index
            if self.table_events.item(row, 2).text().isdigit():
                event.num_places = int(self.table_events.item(row, 2).text())
            checkbox_counts = self.table_events.cellWidget(row, 1)
            if checkbox_counts.checkState() == 2:
                event.counts_for_overall = 1
            else:
                event.counts_for_overall = 0
            checkbox_stamp = self.table_events.cellWidget(row, 3)
            if checkbox_stamp.checkState() == 2:
                event.earns_stamp = 1
            else:
                event.earns_stamp = 0
            self.db.t.event.update(event)
            row += 1
        self.changes_made = False

    def new_event(self, sender=None):
        event = self.db.t.event.new(self.dancer_group.iid,
                                          self.dancer_group.competition)
        # event = sc.Event(0, '', self.dancer_group.iid, 0,
        #                  self.dancer_group.competition, 1, 6, 1)
        # event = self.db.t.event.insert(event)
        row = self.table_events.rowCount()
        # id, name, dancer_group, dance, competition,
        # counts_for_overall, num_places, earns_stamp
        self.table_events.insertRow(row)
        dances = self.db.t.dance.get_all()
        selector_dance = qt.QComboBox()
        for dance in dances:
            selector_dance.addItem(dance.name)
        selector_dance.setCurrentIndex(0)
        selector_dance.currentIndexChanged.connect(self.item_changed)
        item_places = qt.QTableWidgetItem('%d' % event.num_places)
        checkbox_counts = qt.QCheckBox()
        if event.counts_for_overall == 1:
            checkbox_counts.setCheckState(2)
        else:
            checkbox_counts.setCheckState(0)
        checkbox_counts.stateChanged.connect(self.item_changed)
        checkbox_stamp = qt.QCheckBox()
        if event.earns_stamp == 1:
            checkbox_stamp.setCheckState(2)
        else:
            checkbox_stamp.setCheckState(0)
        checkbox_stamp.stateChanged.connect(self.item_changed)
        item_event_id = qt.QTableWidgetItem('%d' % event.iid)

        self.table_events.setCellWidget(row, 0, selector_dance)
        self.table_events.setItem(row, 2, item_places)
        self.table_events.setCellWidget(row, 1, checkbox_counts)
        self.table_events.setCellWidget(row, 3, checkbox_stamp)
        self.table_events.setItem(row, 4, item_event_id)
        self.changes_made = True

    def delete_event(self, sender=None):
        row = self.table_events.currentRow()
        if row is not None:
            # event = self.db.t.event.get(int(self.table_events.item(
            # row, 4).text()))
            event = self.db.t.event.get(int(self.table_events.item(
                row, 4)))
            dance = self.db.t.dance.get(event.dance)
            if event is not None:
                verity = verify((('Are you sure you want to delete event %s %s?'
                                 % (self.dancer_group.name, dance.name))),
                                ('This will delete all data for the given '\
                                'event and all scores associated with this '\
                                'event. This cannot be undone.'))
                if verity:
                    if self.db.s.verbose:
                        print('Will delete event %d' % event.iid)
                    self.db.t.event.remove(event.iid)
                    self.table_events.removeRow(row)
                else:
                    print('Nothing deleted')

    def delete_group(self, sender=None):
        verity = verify((('Are you sure you want to delete competitor group '\
                         '%s?' % self.dancer_group.name)), ('This will delete '\
                         'all data for the given group and all scores '\
                         'associated with this group. This cannot be undone.'))
        if verity:
            if self.db.s.verbose:
                print('Will delete group %d' % self.dancer_group.iid)
            self.db.t.group.remove(self.dancer_group.iid)
            self.hide()
        else:
            print('Nothing deleted')

    def exit_button(self, sender=None):
        if self.changes_made:
            save_result = ask_save()
        else:
            save_result = 'discard'
        if self.db.s.verbose:
            print(save_result)
        if save_result == 'discard':
            self.hide()
        elif save_result == 'save':
            self.save_button()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        self.changes_made = True


class GroupMenu(qt.QDialog):
    def __init__(self, main_window, competition_id, db):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.competition_id = competition_id
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(qt.QLabel('Choose a Competitor Group:'))
        self.dancer_groups = self.db.t.group.get_by_competition(competition_id)
        self.dg_buttons = []
        cats = self.db.t.category.get_all()
        for dancer_group in self.dancer_groups:
            if dancer_group.age_max >= 99:
                aMax = '+'
            else:
                aMax = f"-{dancer_group.age_max}"
            dg_button = SPushButton(('[%s] %s (%s %d%s)' %
                                    (dancer_group.abbrev.replace('&', '&&'),
                                     dancer_group.name.replace('&', '&&'),
                                     cats[dancer_group.dancer_category].abbrev,
                                     dancer_group.age_min, aMax)),
                                   self, dancer_group.iid,
                                   self.set_dancer_group)
            dg_button.clicked.connect(dg_button.on_button_clicked)
            self.dg_buttons.append(dg_button)
        for dg_button in self.dg_buttons:
            self.layout.addWidget(dg_button)
        self.new_button = qt.QPushButton('&New Group')
        self.new_button.clicked.connect(self.new_group)
        self.layout.addWidget(self.new_button)
        self.exit_button = qt.QPushButton('E&xit')
        self.exit_button.clicked.connect(self.hide)
        self.layout.addWidget(self.exit_button)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def new_group(self, sender=None):
        group = self.db.t.group.new(self.competition_id)
        self.set_dancer_group(group.iid)

    def set_dancer_group(self, dancer_group_id):
        dancer_group = self.db.t.group.get(dancer_group_id)
        if dancer_group is not None:
            if self.db.s.verbose:
                print('Group: [%s] %s' %
                      (dancer_group.abbrev, dancer_group.name))
            self.hide()
            self.main_window.edit_dancer_group(dancer_group)
