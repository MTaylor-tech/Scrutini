import datetime
import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import SPushButton


class CompetitionEditor(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super().__init__()
        self.db = db
        if self.db.settings.verbose:
            print("CompetitionEditor in competitions.py")
        self.main_window = main_window
        # self.main_window.setCentralWidget(self)
        self.competition = self.db.tables.competitions.get(comp_id)
        self.changes_made = False
        self.layout = qt.QVBoxLayout()
        self.label_name = qt.QLabel('Name:')
        self.field_name = qt.QLineEdit(self.competition.name)
        self.label_location = qt.QLabel('Location:')
        self.field_location = qt.QLineEdit(self.competition.location)
        self.date_comp_event = qc.QDate.fromString(self.competition.eventDate,
                                                   'yyyy-MM-dd 00:00:00')
        self.date_comp_deadline = qc.QDate.fromString(
            self.competition.deadline, 'yyyy-MM-dd 00:00:00')
        self.label_comp_eventDate = qt.QLabel('Event date:')
        self.calendar_comp_event = qt.QCalendarWidget()
        self.calendar_comp_event.setSelectedDate(self.date_comp_event)
        self.label_comp_deadline = qt.QLabel('Registration deadline:')
        self.calendar_comp_deadline = qt.QCalendarWidget()
        self.calendar_comp_deadline.setSelectedDate(self.date_comp_deadline)
        self.selector_compType = qt.QComboBox()
        compTypes = self.db.tables.competition_types.get_all()
        for compType in compTypes:
            self.selector_compType.addItem(compType.name)
        self.selector_compType.setCurrentIndex(self.competition.competitionType)

        self.field_name.textChanged.connect(self.item_changed)
        self.field_location.textChanged.connect(self.item_changed)
        self.selector_compType.currentIndexChanged.connect(self.item_changed)
        self.calendar_comp_event.selectionChanged.connect(self.item_changed)
        self.calendar_comp_deadline.selectionChanged.connect(self.item_changed)

        self.button_save = qt.QPushButton('&Save')
        self.button_save.clicked.connect(self.save)
        self.button_exit = qt.QPushButton('E&xit')
        self.button_exit.clicked.connect(self.exit_button)
        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.field_name)
        self.layout.addWidget(self.label_location)
        self.layout.addWidget(self.field_location)
        self.layout.addWidget(self.label_comp_eventDate)
        self.layout.addWidget(self.calendar_comp_event)
        self.layout.addWidget(self.label_comp_deadline)
        self.layout.addWidget(self.calendar_comp_deadline)
        self.layout.addWidget(self.selector_compType)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.button_exit)
        # self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def save(self):
        self.competition.name = self.field_name.text()
        self.competition.location = self.field_location.text()
        self.competition.eventDate = self.calendar_comp_event.selectedDate().toString('yyyy-MM-dd 00:00:00')
        self.competition.deadline = self.calendar_comp_deadline.selectedDate().toString('yyyy-MM-dd 00:00:00')
        self.competition.competitionType = self.selector_compType.currentIndex()
        self.db.tables.competitions.update(self.competition)
        self.main_window.set_competition(self.competition.id)
        self.changes_made = False
        self.hide()

    def exit_button(self, sender=None):
        if self.changes_made:
            saveResult = ask_save()
        else:
            saveResult = 'discard'
        if self.db.settings.verbose:
            print(f"saveResult: {saveResult}")
        if saveResult == 'discard':
            self.hide()
        elif saveResult == 'save':
            self.save()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        self.changes_made = True


class CompetitionSelector(qt.QDialog):
    def __init__(self, main_window):
        super(CompetitionSelector, self).__init__()
        self.main_window = main_window
        if self.main_window.db.settings.verbose:
            print("CompetitionSelector in competitions.py")
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(qt.QLabel('Choose a competition:'))
        self.competitions = self.main_window.db.tables.competitions.get_all()
        self.compButtons = []
        for comp in self.competitions:
            compButton = SPushButton('%s (%s)' % (comp.name,
                                      self.get_formatted_date(comp.eventDate)),
                                      self,comp.id,
                                      self.set_competition)
            compButton.clicked.connect(compButton.on_button_clicked)
            self.compButtons.append(compButton)
        for compButton in self.compButtons:
            self.layout.addWidget(compButton)
        self.newButton = qt.QPushButton('&New Competition')
        self.newButton.clicked.connect(self.new_competition)
        self.layout.addWidget(self.newButton)
        self.exitButton = qt.QPushButton('Cancel')
        self.exitButton.clicked.connect(self.hide)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def get_formatted_date(self, date):
        format_str = '%d %b %Y'
        otherformat_str = '%Y-%m-%d'
        return (datetime.datetime.strftime(datetime.datetime.strptime(('%s' % date)[0:10], otherformat_str).date(), format_str))

    def on_button_clicked(self, identifier):
        alert = qt.QMessageBox()
        alert.setText(identifier)
        alert.exec_()

    def set_competition(self, comp_id):
        self.main_window.set_competition(comp_id)
        self.hide()

    def new_competition(self):
        self.hide()
        self.main_window.new_competition()
