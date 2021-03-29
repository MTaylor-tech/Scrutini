import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from resultsc import ResultsGroupBox
from sWidgets import is_float


class ScoreEntryWindow(qt.QDialog):
    def __init__(self, main_window, db):
        super(ScoreEntryWindow, self).__init__()
        self.db = db
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.competition = self.db.competition
        self.changes_made = False
        #self.resize(1680, 1000)
        self.layout = qt.QVBoxLayout()
        self.events = self.db.t.event.get_by_competition(self.competition.iid)
        self.label_event = qt.QLabel('Event')
        self.selector_event = qt.QComboBox()
        self.event_ids = []
        for event in self.events:
            self.selector_event.addItem(event.name)
            self.event_ids.append(event.iid)
        self.selector_event.currentIndexChanged.connect(self.new_event_selected)
        self.event = self.db.t.event.get(self.event_ids[self.selector_event.currentIndex()])
        self.previous_event = self.selector_event.currentIndex()
        self.selector_judge = qt.QComboBox()
        self.judge_ids = [0]
        self.judges = self.db.t.judge.get_by_competition(self.competition.iid)
        self.selector_judge.addItem('')
        for judge in self.judges:
            self.selector_judge.addItem('%s %s' % (judge.first_name,
                                                   judge.last_name))
            self.judge_ids.append(judge.iid)
        self.table_scores = qt.QTableWidget()
        self.headers = ['Num', 'Score', 'id']
        self.table_scores.setColumnCount(len(self.headers))
        self.table_scores.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [60,80,0]
        column = 0
        while column < len(self.column_widths):
            self.table_scores.setColumnWidth(column,self.column_widths[column])
            column += 1
        row = 0
        self.dancers = self.db.t.dancer.get_ordered_by_number(self.event.dancer_group)
        self.scores = {}
        if len(self.dancers) > 0:
            if self.db.t.score.exists_for_event(self.event.iid):
                for x in range(len(self.dancers)):
                    score = self.db.t.score.get_by_event_dancer(
                        self.event.iid, self.dancers[x].iid)
                    if score is not None:
                        self.judge_id = score.judge
                        self.selector_judge.setCurrentIndex(
                            self.judge_ids.index(self.judge_id))
                        break
            else:
                self.judge_id = 0
                self.selector_judge.setCurrentIndex(0)
            for dancer in self.dancers:
                item_dancer_num = qt.QTableWidgetItem(dancer.competitor_num)
                item_dancer_num.setFlags(qc.Qt.NoItemFlags)
                if self.db.t.score.exists_for_event(self.event.iid):
                    score = self.db.t.score.get_by_event_dancer(self.event.iid, dancer.iid)
                    if score is not None:
                        item_dancer_score = qt.QTableWidgetItem('%6.0f' % score.score)
                    else:
                        item_dancer_score = qt.QTableWidgetItem('')
                else:
                    item_dancer_score = qt.QTableWidgetItem('')
                item_dancer_id = qt.QTableWidgetItem('%d' % dancer.iid)

                self.table_scores.setRowCount(row+1)
                self.table_scores.setItem(row, 0, item_dancer_num)
                self.table_scores.setItem(row, 1, item_dancer_score)
                self.table_scores.setItem(row, 2, item_dancer_id)

                row += 1
        self.table_scores.setColumnHidden(2,True)
        #xxx is there a way to make a column unselectable? If so, make the dancer_num column such
        self.table_scores.itemChanged.connect(self.item_changed)

        self.results_box = ResultsGroupBox('Results:', self.event.iid, self.db, self.main_window)

        self.button_save = qt.QPushButton('&Save')
        self.button_save.clicked.connect(self.save_button)
        self.button_exit = qt.QPushButton('E&xit')
        self.button_exit.clicked.connect(self.cancel_button)

        self.layout.addWidget(self.label_event)
        self.layout.addWidget(self.selector_event)
        self.layout.addWidget(self.selector_judge)
        self.layout.addWidget(self.table_scores)
        self.layout.addWidget(self.results_box)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.button_exit)
        self.setLayout(self.layout)

    def new_event_selected(self, sender=None):
        if (self.changes_made):
            saveResult = ask_save()
        else:
            saveResult = 'discard'
        if (saveResult == 'save'):
            self.save_button()
        elif (saveResult == 'cancel'):
            self.selector_event.setCurrentIndex(self.previous_event)
            return
        self.event = self.db.t.event.get(self.event_ids[self.selector_event.currentIndex()])
        self.previous_event = self.selector_event.currentIndex()
        row = 0
        self.dancers = self.db.t.dancer.get_ordered_by_number(self.event.dancer_group)
        self.scores = {}
        if len(self.dancers) > 0:
            if self.db.t.score.exists_for_event(self.event.iid):
                for x in range(len(self.dancers)):
                    score = self.db.t.score.get_by_event_dancer(
                        self.event.iid, self.dancers[x].iid)
                    if score is not None:
                        self.judge_id = score.judge
                        self.selector_judge.setCurrentIndex(
                            self.judge_ids.index(self.judge_id))
                        break
            else:
                self.judge_id = 0
                self.selector_judge.setCurrentIndex(0)
            for dancer in self.dancers:
                item_dancer_num = qt.QTableWidgetItem(dancer.competitor_num)
                item_dancer_num.setFlags(qc.Qt.NoItemFlags)
                if self.db.t.score.exists_for_event(self.event.iid):
                    score = self.db.t.score.get_by_event_dancer(self.event.iid, dancer.iid)
                    if score is not None:
                        item_dancer_score = qt.QTableWidgetItem('%6.0f' % score.score)
                    else:
                        item_dancer_score = qt.QTableWidgetItem('')
                else:
                    item_dancer_score = qt.QTableWidgetItem('')
                item_dancer_id = qt.QTableWidgetItem('%d' % dancer.iid)
                self.table_scores.setRowCount(row+1)
                self.table_scores.setItem(row, 0, item_dancer_num)
                self.table_scores.setItem(row, 1, item_dancer_score)
                self.table_scores.setItem(row, 2, item_dancer_id)

                row += 1
        self.results_box.select_event(self.event.iid) #xxx
        self.changes_made = False

    def save_button(self, sender=None):
        self.table_scores.setFocus()
        row = 0
        judge_id = (self.judge_ids[self.selector_judge.currentIndex()])
        # print(judge_id)
        if (self.competition.competition_type > 0): # TODO this should be a real check for championship
            self.db.t.score.remove_by_event_judge(self.event.iid, judge_id)
        else:
            self.db.t.score.remove_by_event(self.event.iid)
        while row < self.table_scores.rowCount():
            item_dancer_id = self.table_scores.item(row, 2)
            item_dancer_score = self.table_scores.item(row, 1)
            if is_float(item_dancer_score.text()):
                #print ('[%6.2f]' % float(item_dancer_score.text()))
                dancer_id = int(item_dancer_id.text())
                dancer_score = float(item_dancer_score.text())
                score = sc.Score(0, dancer_id, self.event.iid, judge_id,
                              self.event.competition, dancer_score)
                score = self.db.t.score.insert(score)
                #id, dancer, event, judge, competition, score
            row += 1
        self.db.conn.commit()
        # xxxs needs to take judge into account for championships
        self.changes_made = False
        self.results_box.select_event(self.event.iid)

    def item_changed(self, sender=None):
        # print('Item changed')
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
