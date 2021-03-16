"""Scrutini GUI."""
import datetime
import sys
import PyQt5.QtWidgets as qt
# from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
# from PyQt5.QtGui import qt_set_sequence_auto_mnemonic
from sWidgets import SPushButton, on_button_clicked, verify, ask_save, is_float, get_formatted_date
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
        # label_text = ''
        self.label = qt.QLabel('')
        # self.toolbar = self.addToolBar(qc.Qt.LeftToolBarArea, self.tool_bar())
        self.addToolBar(qc.Qt.LeftToolBarArea, SToolBar(self))
        # self.setUnifiedTitleAndToolBarOnMac(True)
        self.app = interface
        self.db = db
        # self.app = PyQtApp()
        self.setWindowTitle("Scrutini ")
        self.setWindowIcon(qg.QIcon("../icons/base/64.png"))
        self.setGeometry(0, 0, 1200, 800)
        self.competition = None
        # self.competition = sc.Competition(0,'','',None,None,'',None)
        # self.competition = self.retrieve_competition()
        # self.set_competition(self.competition.iid)
        # if self.competition is None:
        #     self.disable_buttons()
        self.statusBar()
        self.statusBar().show()
        menubar = qt.QMenuBar(self)
        # menubar.setNativeMenuBar(True)  # True means menubar in upper
        exit_action = qt.QAction(' &Quit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit Application')
        exit_action.triggered.connect(self.exit_app)
        file_menu = menubar.addMenu(' &File')
        file_menu.addAction(exit_action)
        change_competition_action = qt.QAction(' Select Competition', self)
        change_competition_action.setStatusTip(
            'Choose a different competition or make a new one')
        change_competition_action.triggered.connect(self.select_competition)
        edit_competition_action = qt.QAction(' &Edit Competition', self)
        edit_competition_action.setStatusTip('Edit Competition Details')
        edit_competition_action.triggered.connect(self.edit_competition)
        competition_menu = menubar.addMenu(' &Competition')
        competition_menu.addAction(change_competition_action)
        competition_menu.addAction(edit_competition_action)
        self.setMenuBar(menubar)

        self.competition = self.retrieve_competition()
        self.set_competition(self.competition.iid)
        if self.competition is None:
            self.toolBar.buttons.disable_all()
            # self.disable_buttons()
        # self.label.show()

        menubar.show()

    def enter_scores(self, sender=None):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        score_entry_window = ScoreEntryWindow(self, self.competition.iid, self.db)
        score_entry_window.show()
        score_entry_window.exec_()

    def view_scores(self, sender=None):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        results_view_window = ResultsViewWindow(self, self.competition.iid,
                                              self.db)
        results_view_window.show()
        results_view_window.exec_()

    def import_csv(self, sender=None):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        import_window = ImportWindow(self, self.competition.iid, self.db)
        import_window.show()
        import_window.exec_()

    def edit_dancers(self):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        dancer_editor = DancerEditor(self, self.competition.iid, self.db)
        dancer_editor.show()
        dancer_editor.exec_()

    def edit_judges(self):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        judge_selector = JudgeSelector(self, self.competition.iid, self.db)
        judge_selector.show()
        judge_selector.exec_()

    def edit_competition(self):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        competition_editor = CompetitionEditor(
            self, self.competition.iid, self.db)
        competition_editor.show()
        competition_editor.exec_()

    def edit_dancer_group(self, dancer_group):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        dancer_group_editor = DancerGroupEditor(self, dancer_group, self.db)
        dancer_group_editor.show()
        dancer_group_editor.exec_()

    def retrieve_competition(self):
        competitions = self.db.t.competition.get_all()
        competitions_list = []
        for competition in competitions:
            competitions_list.append(competition.iid)
        if self.db.s.last_comp in competitions_list:
            self.competition = self.set_competition(
                self.db.s.last_comp)
            return self.competition
        else:
            self.select_competition()
            if self.competition is not None:
                self.db.s.last_comp = self.competition.iid
                return self.competition
            else:
                return self.new_competition()

    def set_competition(self, competition_id):
        self.competition = self.db.t.competition.get(competition_id)
        if self.competition is not None:
            self.label_text = ('<center>Competition:<br><strong>%s</strong>\
                               <br>%8s<br>%s</center>' %
                               (self.competition.name,
                                get_formatted_date(
                                    self.competition.event_date),
                                self.competition.location))
            self.label.setText(self.label_text)
            self.db.s.last_comp = self.competition.iid
            return self.competition
        else:
            self.label_text = ('<center>No Competition Selected</center>')
            return None

    def select_dancer_group(self):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        window = DancerGroupMenu(self, self.competition.iid, self.db)
        window.show()
        window.exec_()

    def select_competition(self):
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        window = CompetitionSelector(self)
        window.show()
        window.exec_()

    def delete_competition(self):
        verity = verify('Are you sure you want to delete this competition?',
                        ('This will delete all data for the given '\
                         'competition. This cannot be undone.'))
        if verity:
            if self.db.s.verbose:
                print('Will delete competition %d' % self.competition.iid)
            self.db.t.competition.remove(self.competition.iid)
            self.competition = None
            self.select_competition()
        else:
            print('Nothing deleted')

    def exit_app(self, sender):
        self.db.close_connection()
        if self.centralWidget() is not None:
            self.centralWidget().hide()
        print(f"Exit mw 0")
        self.close()
        self.app.exit()

    def new_competition(self):
        self.competition = self.db.t.competition.new()
        self.edit_competition()
        return self.competition


class SToolBar(qt.QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # self.buttons = STButtons(self)
        buttons = STButtons(self)
        label_text = ''
        self.label = qt.QLabel(label_text)
        self.addWidget(self.label)
        # for button in self.buttons.buttons:
        for button in buttons.buttons:
            self.addWidget(button)
        self.setOrientation(qc.Qt.Vertical)
        self.label.show()
        self.buttons.disable_all()


class STButtons:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        scrutineer = qt.QPushButton('Enter &Scores')
        view_scores = qt.QPushButton('&View/Print Results')
        change_competition = qt.QPushButton('&Change Competition')
        edit_competition = qt.QPushButton('&Edit Competition Details')
        dancers = qt.QPushButton('&Add/Edit Competitors')
        judges = qt.QPushButton('Add/Edit &Judges')
        dancer_groups = qt.QPushButton(
            'Define Competitor &Groups && Dances')
        btn_import = qt.QPushButton('&Import CSV')
        delete = qt.QPushButton('&Delete Competition')
        exit = qt.QPushButton('E&xit')
        scrutineer.clicked.connect(toolbar.parent.enter_scores)
        view_scores.clicked.connect(toolbar.parent.view_scores)
        edit_competition.clicked.connect(toolbar.parent.edit_competition)
        change_competition.clicked.connect(toolbar.parent.select_competition)
        dancers.clicked.connect(toolbar.parent.edit_dancers)
        judges.clicked.connect(toolbar.parent.edit_judges)
        dancer_groups.clicked.connect(toolbar.parent.select_dancer_group)
        btn_import.clicked.connect(toolbar.parent.import_csv)
        delete.clicked.connect(toolbar.parent.delete_competition)
        exit.clicked.connect(toolbar.parent.exit_app)
        self.buttons = [scrutineer, view_scores, change_competition,
                        edit_competition, dancers, judges, dancer_groups,
                        btn_import, delete, exit]

    def enable_all(self):
        if self.toolbar.parent.db.s.verbose:
            print("Enable All Buttons")
        for button in self.buttons:
            button.setEnabled(True)

    def disable_all(self):
        if self.toolbar.parent.db.s.verbose:
            print("Disable All Buttons")
        for button in self.buttons:
            button.setEnabled(False)






class App(qt.QApplication):
    def __init__(self, db):
        super().__init__(sys.argv)
        self.db = db
        qg.qt_set_sequence_auto_mnemonic(True)
        font = qg.QFont("Lucida Grande")
        self.setFont(font)
        self.setObjectName("Scrutini")
        self.setApplicationDisplayName("Scrutini")
        self.main_window = SMainWindow(self, db)

    def start(self):
        self.main_window.show()

    def exit(self):
        self.db.s.write()
        print("Exit Interface")
        self.closeAllWindows()
        sys.exit(0)
