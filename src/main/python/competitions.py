import datetime
import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import SPushButton, get_formatted_date, ask_save, sanitize
import pdb


class CompetitionEditor(qt.QDialog):
    def __init__(self, main_window, db):
        super().__init__()
        self.db = db
        v = self.db.settings.verbose
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        # self.db.competition = self.db.t.competition.get(competition_id)
        self.changes_made = False
        self.layout = qt.QVBoxLayout()
        self.label_name = qt.QLabel('Name:')
        self.field_name = qt.QLineEdit(self.db.competition.name)
        self.label_location = qt.QLabel('Location:')
        self.field_location = qt.QLineEdit(self.db.competition.location)
        self.date_competition_event = qc.QDate.fromString(
            self.db.competition.event_date, 'yyyy-MM-dd 00:00:00')
        self.date_competition_deadline = qc.QDate.fromString(
            self.db.competition.deadline, 'yyyy-MM-dd 00:00:00')
        self.label_competition_event_date = qt.QLabel('Event date:')
        self.calendar_competition_event = qt.QCalendarWidget()
        self.calendar_competition_event.setSelectedDate(
            self.date_competition_event)
        self.label_competition_deadline = qt.QLabel('Registration deadline:')
        self.calendar_competition_deadline = qt.QCalendarWidget()
        self.calendar_competition_deadline.setSelectedDate(
            self.date_competition_deadline)
        self.selector_competition_type = qt.QComboBox()
        competition_types = self.db.t.competition_type.get_all()
        for competition_type in competition_types:
            self.selector_competition_type.addItem(competition_type.name)
        self.selector_competition_type.setCurrentIndex(
            self.db.competition.competition_type)
        self.field_name.textChanged.connect(self.item_changed)
        self.field_location.textChanged.connect(self.item_changed)
        self.selector_competition_type.currentIndexChanged.connect(
            self.item_changed)
        self.calendar_competition_event.selectionChanged.connect(
            self.item_changed)
        self.calendar_competition_deadline.selectionChanged.connect(
            self.item_changed)
        self.button_save = qt.QPushButton('&Save')
        self.button_save.clicked.connect(self.save)
        self.button_exit = qt.QPushButton('E&xit')
        self.button_exit.clicked.connect(self.exit_button)
        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.field_name)
        self.layout.addWidget(self.label_location)
        self.layout.addWidget(self.field_location)
        self.layout.addWidget(self.label_competition_event_date)
        self.layout.addWidget(self.calendar_competition_event)
        self.layout.addWidget(self.label_competition_deadline)
        self.layout.addWidget(self.calendar_competition_deadline)
        self.layout.addWidget(self.selector_competition_type)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.button_exit)
        # self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)
        self.main_window.show()
        self.show()
        self.field_name.setFocus()

    def save(self):
        self.db.competition.name = sanitize(self.field_name.text())
        self.db.competition.location = sanitize(self.field_location.text())
        self.db.competition.event_date = (self.calendar_competition_event
                            .selectedDate().toString('yyyy-MM-dd 00:00:00'))
        self.db.competition.deadline = (self.calendar_competition_deadline
                            .selectedDate().toString('yyyy-MM-dd 00:00:00'))
        self.db.competition.competition_type = (self
                                             .selector_competition_type
                                             .currentIndex())
        self.db.t.competition.update(self.db.competition)
        self.main_window.set_competition()
        self.changes_made = False
        self.hide()

    def exit_button(self, sender=None):
        if self.changes_made:
            save_result = ask_save()
        else:
            save_result = 'discard'
        if self.db.settings.verbose:
            print(f"save_result: {save_result}")
        if save_result == 'discard':
            self.hide()
        elif save_result == 'save':
            self.save()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        self.changes_made = True


class CompetitionSelector(qt.QDialog):
    def __init__(self, main_window, db):
        super(CompetitionSelector, self).__init__()
        self.main_window = main_window
        self.db = db
        if self.db.settings.verbose:
            print("CompetitionSelector in competitions.py")
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(qt.QLabel('Choose a competition:'))
        self.competitions = self.db.t.competition.get_all()
        ccid = -1
        if self.db.get_competition() is not None:
            ccid = self.db.competition.iid
        self.competition_buttons = []
        for competition in self.competitions:
            competition_button = SPushButton('%s (%s)' % (competition.name,
                                     get_formatted_date(
                                         competition.event_date)),
                                     self, competition.iid,
                                     self.set_competition)
            if ccid == competition.iid:
                competition_button.setFocus(True)
            else:
                competition_button.setFocus(False)
            competition_button.clicked.connect(
                competition_button.on_button_clicked)
            self.competition_buttons.append(competition_button)
        for competition_button in self.competition_buttons:
            self.layout.addWidget(competition_button)
        self.new_button = qt.QPushButton('&New Competition')
        self.new_button.clicked.connect(self.new_competition)
        self.layout.addWidget(self.new_button)
        self.exit_button = qt.QPushButton('Cancel')
        self.exit_button.clicked.connect(self.hide)
        self.layout.addWidget(self.exit_button)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def on_button_clicked(self, identifier):
        alert = qt.QMessageBox()
        alert.setText(identifier)
        alert.exec_()

    def set_competition(self, competition_id):
        self.db.competition = self.db.t.competition.get(competition_id)
        self.main_window.set_competition()
        self.hide()

    def new_competition(self):
        self.hide()
        self.main_window.new_competition()
