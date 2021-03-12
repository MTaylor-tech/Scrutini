"""Scrutini GUI."""
import datetime
import sys
import PyQt5.QtWidgets as qt
# from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import SPushButton, on_button_clicked, verify, ask_save, is_float
from resultsc import ResultsViewWindow  # ResultsGroupBox
from scores import ScoreEntryWindow
from dancers import DancerEditor
from groups import GroupEditor as DancerGroupEditor
from groups import GroupMenu as DancerGroupMenu
from competitions import CompetitionEditor, CompetitionSelector
from importWindow import ImportWindow
from judges import JudgeSelector


class SMainWindow(qt.QMainWindow):
    def __init__(self, interface, db):
        super(SMainWindow, self).__init__()
        label_text = ''
        self.label = qt.QLabel(label_text)
        self.toolbar = self.addToolBar(qc.Qt.LeftToolBarArea, self.tool_bar())
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.app = interface
        self.db = db
        # self.app = PyQtApp()
        self.setWindowTitle("Scrutini ")
        self.setWindowIcon(qg.QIcon("../icons/base/64.png"))
        self.setGeometry(0, 0, 1200, 800)
        self.settings = db.settings
        # self.competition = sc.Competition(0,'','',None,None,'',None)
        self.competition = self.retrieve_competition()
        self.set_competition(self.competition.id)
        if self.competition is None:
            self.disable_buttons()
        self.statusBar()
        self.statusBar().show()
        menubar = qt.QMenuBar(self)
        # menubar.setNativeMenuBar(False)  # True means menubar in upper
        exitAct = qt.QAction(' &Quit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        exitAct.triggered.connect(self.exit_app)
        fileMenu = menubar.addMenu(' &File')
        fileMenu.addAction(exitAct)
        changeCompAct = qt.QAction(' &Select Competition',self)
        changeCompAct.setStatusTip('Choose a different competition or make a new one')
        changeCompAct.triggered.connect(self.select_competition)
        editCompAct = qt.QAction(' &Edit Competition',self)
        editCompAct.setStatusTip('Edit Competition Details')
        editCompAct.triggered.connect(self.edit_competition)
        compMenu = menubar.addMenu(' &Competition')
        compMenu.addAction(changeCompAct)
        compMenu.addAction(editCompAct)
        self.setMenuBar(menubar)
        menubar.show()

    def tool_bar(self):
        button_scrutineer = qt.QPushButton('Enter &Scores')
        button_view_scores = qt.QPushButton('&View/Print Results')
        button_comps = qt.QPushButton('&Change Competition')
        button_comp = qt.QPushButton('&Edit Competition Details')
        button_dancers = qt.QPushButton('&Add/Edit Competitors')
        button_judges = qt.QPushButton('Add/Edit &Judges')
        button_dancerGroups = qt.QPushButton(
            'Define Competitor &Groups && Dances')
        button_import = qt.QPushButton('&Import CSV')
        button_delete = qt.QPushButton('&Delete Competition')
        button_exit = qt.QPushButton('E&xit')
        button_scrutineer.clicked.connect(self.enter_scores)
        button_view_scores.clicked.connect(self.view_scores)
        button_comp.clicked.connect(self.edit_competition)
        button_comps.clicked.connect(self.select_competition)
        button_dancers.clicked.connect(self.edit_dancers)
        button_judges.clicked.connect(self.edit_judges)
        button_dancerGroups.clicked.connect(self.select_dancerGroup)
        button_import.clicked.connect(self.import_csv)
        button_delete.clicked.connect(self.delete_competition)
        button_exit.clicked.connect(self.exit_app)
        layout = qt.QToolBar(self)
        layout.addWidget(self.label)
        layout.addWidget(button_scrutineer)
        layout.addWidget(button_view_scores)
        layout.addWidget(button_comps)
        layout.addWidget(button_comp)
        layout.addWidget(button_dancers)
        layout.addWidget(button_judges)
        layout.addWidget(button_dancerGroups)
        layout.addWidget(button_import)
        layout.addWidget(button_delete)
        layout.addWidget(button_exit)
        layout.setOrientation(qc.Qt.Vertical)
        return layout

    def enter_scores(self, sender=None):
        scoreEntryWindow = ScoreEntryWindow(self, self.competition.id, self.db)
        scoreEntryWindow.show()
        scoreEntryWindow.exec_()

    def view_scores(self, sender=None):
        resultsViewWindow = ResultsViewWindow(self, self.competition.id, self.db)
        resultsViewWindow.show()
        resultsViewWindow.exec_()

    def import_csv(self, sender=None):
        importWindow = ImportWindow(self, self.competition.id, self.db)
        importWindow.show()
        importWindow.exec_()

    def edit_dancers(self):
        dancerEditor = DancerEditor(self, self.competition.id, self.db)
        dancerEditor.show()
        dancerEditor.exec_()

    def edit_judges(self):
        judgeSelector = JudgeSelector(self, self.competition.id, self.db)
        judgeSelector.show()
        judgeSelector.exec_()

    def edit_competition(self):
        compEditor = CompetitionEditor(self, self.competition.id, self.db)
        compEditor.show()
        compEditor.exec_()

    def edit_dancerGroup(self, dancerGroup):
        dgEditor = DancerGroupEditor(self, dancerGroup, self.db)
        dgEditor.show()
        dgEditor.exec_()

    def disable_buttons(self):
        # self.button_scrutineer.setEnabled = False
        # self.button_comp.setEnabled = False
        # self.button_dancers.setEnabled = False
        # self.button_judges.setEnabled = False
        # self.button_dancerGroups.setEnabled = False
        # self.button_import.setEnabled = False
        # self.button_delete.setEnabled = False
        for button in self.toolbar.children():
            button.setEnabled = False

    def enable_buttons(self):
        # self.button_scrutineer.setEnabled = True
        # self.button_comp.setEnabled = True
        # self.button_dancers.setEnabled = True
        # self.button_judges.setEnabled = True
        # self.button_dancerGroups.setEnabled = True
        # self.button_import.setEnabled = True
        # self.button_delete.setEnabled = True
        for button in self.toolbar.children():
            button.setEnabled = True

    def get_formatted_date(self, date):
        format_str = '%d %b %Y'
        otherformat_str = '%Y-%m-%d'
        return (datetime.datetime.strftime(datetime.datetime.strptime(
            ('%s' % date)[0:10], otherformat_str).date(), format_str))

    def retrieve_competition(self):
        competitions = self.db.tables.competitions.get_all()
        competitions_list = []
        for comp in competitions:
            competitions_list.append(comp.id)
        if self.settings.last_comp in competitions_list:
            self.competition = self.set_competition(
                self.settings.last_comp)
            return self.competition
        else:
            self.select_competition()
            self.settings.last_comp = self.competition.id
            return self.competition

    def set_competition(self, comp_id):
        self.competition = self.db.tables.competitions.get(comp_id)
        if self.competition is not None:
            self.label_text = ('<center>Competition:<br><strong>%s</strong>\
                               <br>%8s<br>%s</center>' %
                               (self.competition.name,
                                self.get_formatted_date(
                                    self.competition.eventDate),
                                self.competition.location))
            self.label.setText(self.label_text)
            self.settings.last_comp = self.competition.id
            return self.competition
        else:
            self.label_text = ('<center>No Competition Selected</center>')
            return None

    def select_dancerGroup(self):
        window = DancerGroupMenu(self, self.competition.id, self.db)
        window.show()
        window.exec_()

    def select_competition(self):
        window = CompetitionSelector(self)
        window.show()
        window.exec_()

    def delete_competition(self):
        verity = verify('Are you sure you want to delete this competition?',
                        'This will delete all data for the given competition.\
                        This cannot be undone.')
        if verity:
            if self.db.settings.verbose:
                print('Will delete comp %d' % self.competition.id)
            self.db.tables.competitions.remove(self.competition.id)
            self.competition = None
            self.select_competition()
        else:
            print('Nothing deleted')

    def exit_app(self, sender):
        self.db.close_connection()
        print(f"Exit mw {self.app}")
        self.close()
        self.app.exit()

    def new_competition(self):
        self.competition = self.db.tables.competitions.new()
        self.edit_competition()


class App(qt.QApplication):
    def __init__(self, db):
        super().__init__(sys.argv)
        self.setObjectName("Scrutini")
        self.setApplicationDisplayName("Scrutini")
        self.main_window = SMainWindow(self, db)

    def start(self):
        # pass
        self.main_window.show()
        # self.main_window.app.show()

    def exit(self):
        # rc = self.exec_()
        print("Exit Interface")
        self.closeAllWindows()
        sys.exit()
