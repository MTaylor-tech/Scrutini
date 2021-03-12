import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg


class ScoreEntryWindow(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(ScoreEntryWindow, self).__init__()
        self.db = db
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.comp_id = comp_id
        self.competition = self.db.tables.competitions.get(comp_id)
        self.changes_made = False
        #self.resize(1680, 1000)
        self.layout = qt.QVBoxLayout()
        self.events = self.db.tables.events.get_by_competition(self.comp_id)
        self.label_event = qt.QLabel('Event')
        self.selector_event = qt.QComboBox()
        self.event_ids = []
        for event in self.events:
            self.selector_event.addItem(event.name)
            self.event_ids.append(event.id)
        self.selector_event.currentIndexChanged.connect(self.new_event_selected)
        self.event = self.db.tables.events.get(self.event_ids[self.selector_event.currentIndex()])
        self.previous_event = self.selector_event.currentIndex()
        self.selector_judge = qt.QComboBox()
        self.judge_ids = [0]
        self.judges = self.db.tables.judges.get_by_competition(self.comp_id)
        self.selector_judge.addItem('')
        for judge in self.judges:
            self.selector_judge.addItem('%s %s' % (judge.firstName, judge.lastName))
            self.judge_ids.append(judge.id)
        self.table_scores = qt.QTableWidget()
        self.headers = ['Num','Score','id']
        self.table_scores.setColumnCount(len(self.headers))
        self.table_scores.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [60,80,0]
        column = 0
        while column < len(self.column_widths):
            self.table_scores.setColumnWidth(column,self.column_widths[column])
            column += 1
        row = 0
        self.dancers = self.db.tables.dancers.get_ordered_by_number(self.event.dancerGroup)
        self.scores = {}
        for dancer in self.dancers:
            item_dancer_num = qt.QTableWidgetItem(dancer.number)
            item_dancer_num.setFlags(qt.Qt.NoItemFlags)
            if self.db.tables.scores.exists_for_event(self.event.id):
                score = self.db.tables.scores.get_by_event_dancer(self.event.id, dancer.id)
                if score is not None:
                    item_dancer_score = qt.QTableWidgetItem('%6.0f' % score.score)
                else:
                    item_dancer_score = qt.QTableWidgetItem('')
            else:
                item_dancer_score = qt.QTableWidgetItem('')
            item_dancer_id = qt.QTableWidgetItem('%d' % dancer.id)


            self.table_scores.setRowCount(row+1)
            self.table_scores.setItem(row, 0, item_dancer_num)
            self.table_scores.setItem(row, 1, item_dancer_score)
            self.table_scores.setItem(row, 2, item_dancer_id)

            row += 1
        self.table_scores.setColumnHidden(2,True)
        #xxx is there a way to make a column unselectable? If so, make the dancer_num column such
        self.table_scores.itemChanged.connect(self.item_changed)

        self.results_box = ResultsGroupBox('Results:', self.event.id)

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

    def is_float(self, string):
        try:
            val = float(string)
            return True
        except ValueError:
            return False

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
        self.event = self.db.table.events.get(self.event_ids[self.selector_event.currentIndex()])
        self.previous_event = self.selector_event.currentIndex()
        row = 0
        self.dancers = self.db.tables.dancers.get_ordered_by_number(self.event.dancerGroup)
        self.scores = {}
        for dancer in self.dancers:
            item_dancer_num = qt.QTableWidgetItem(dancer.number)
            item_dancer_num.setFlags(qt.Qt.NoItemFlags)
            if self.db.tables.scores.exists_for_event(self.event.id):
                score = self.db.tables.scores.get_by_event_dancer(self.event.id, dancer.id)
                if score is not None:
                    item_dancer_score = qt.QTableWidgetItem('%6.0f' % score.score)
                else:
                    item_dancer_score = qt.QTableWidgetItem('')
            else:
                item_dancer_score = qt.QTableWidgetItem('')
            item_dancer_id = qt.QTableWidgetItem('%d' % dancer.id)


            self.table_scores.setRowCount(row+1)
            self.table_scores.setItem(row, 0, item_dancer_num)
            self.table_scores.setItem(row, 1, item_dancer_score)
            self.table_scores.setItem(row, 2, item_dancer_id)

            row += 1
        self.results_box.select_event(self.event.id) #xxx
        self.changes_made = False

    def save_button(self, sender=None):
        row = 0
        judge_id = (self.judge_ids[self.selector_judge.currentIndex()])
        if (self.competition.competitionType > 0):
            self.db.tables.scores.remove_by_event_judge(self.event.id, judge_id)
        else:
            self.db.tables.scores.remove_by_event(self.event.id)
        while row < self.table_scores.rowCount():
            item_dancer_id = self.table_scores.item(row, 2)
            item_dancer_score = self.table_scores.item(row, 1)
            if self.is_float(item_dancer_score.text()):
                #print ('[%6.2f]' % float(item_dancer_score.text()))
                dancer_id = int(item_dancer_id.text())
                dancer_score = float(item_dancer_score.text())
                score = Score(0, dancer_id, self.event.id, judge_id,
                              self.event.competition, dancer_score)
                score = self.db.tables.scores.insert(score)
                #id, dancer, event, judge, competition, score
            row += 1
        #xxxs needs to take judge into account for championships
        self.changes_made = False
        self.results_box.select_event(self.event.id)

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
