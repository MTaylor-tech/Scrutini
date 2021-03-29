import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import verify, ask_save, sanitize


class JudgeSelector(qt.QDialog):
    def __init__(self, main_window, db):
        super(JudgeSelector, self).__init__()
        self.db = db
        if self.db.s.verbose:
            print("JudgeSelector in judges.py")
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.competition_id = self.db.competition.iid
        self.changes_made = False
        self.layout = qt.QVBoxLayout()
        self.judges = self.db.t.judge.get_by_competition(self.competition_id)
        self.table_judges = qt.QTableWidget()
        self.headers = ['First Name', 'Last Name', 'id']
        self.table_judges.setColumnCount(len(self.headers))
        self.table_judges.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [120, 150, 0]
        column = 0
        while column < len(self.column_widths):
            self.table_judges.setColumnWidth(column,
                                             self.column_widths[column])
            column += 1
        row = 0
        for judge in self.judges:
            item_first_name = qt.QTableWidgetItem(judge.first_name)
            item_last_name = qt.QTableWidgetItem(judge.last_name)
            item_judge_id = qt.QTableWidgetItem('%d' % judge.iid)
            self.table_judges.setRowCount(row+1)
            self.table_judges.setItem(row, 0, item_first_name)
            self.table_judges.setItem(row, 1, item_last_name)
            self.table_judges.setItem(row, 2, item_judge_id)
            row += 1
        self.table_judges.setColumnHidden(2, True)
        self.table_judges.itemChanged.connect(self.item_changed)
        self.layout.addWidget(self.table_judges)
        self.new_button = qt.QPushButton('&New Judge')
        self.new_button.clicked.connect(self.new_judge)
        self.layout.addWidget(self.new_button)
        self.delete_button = qt.QPushButton('&Delete Judge')
        self.delete_button.clicked.connect(self.delete_judge)
        self.layout.addWidget(self.delete_button)
        self.save_btn = qt.QPushButton('&Save')
        self.save_btn.clicked.connect(self.save_button)
        self.layout.addWidget(self.save_btn)
        self.exit_btn = qt.QPushButton('E&xit')
        self.exit_btn.clicked.connect(self.exit_button)
        self.layout.addWidget(self.exit_btn)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def new_judge(self, sender=None):
        row = self.table_judges.rowCount()
        # id, first_name, last_name, competition
        # judge = sc.Judge(0,'','',self.competition_id)
        # judge = self.db.t.judge.insert(judge)
        judge = self.db.t.judge.new(self.competition_id)
        self.table_judges.insertRow(row)
        item_first_name = qt.QTableWidgetItem(judge.first_name)
        item_last_name = qt.QTableWidgetItem(judge.last_name)
        item_judge_id = qt.QTableWidgetItem(('%d' % judge.iid))
        self.table_judges.setItem(row,  0, item_first_name)
        self.table_judges.setItem(row,  1, item_last_name)
        self.table_judges.setItem(row,  2, item_judge_id)
        self.table_judges.scrollToItem(self.table_judges.item(row, 0))
        self.changes_made = True

    def delete_judge(self, sender=None):
        row = self.table_judges.currentRow()
        # print('Current row:',row)
        # print('Text = %s' % self.table_judges.item(row, 2).text())
        if row is not None:
            judge = self.db.t.judge.get(int(
                self.table_judges.item(row, 2).text()))
            if judge is not None:
                verity = verify(('Are you sure you want to delete judge %s %s?'
                                 % (judge.first_name, judge.last_name)),
                                ('This will delete all data for the given '\
                                'judge and all scores associated with this '\
                                'judge. This cannot be undone.'))
                if verity:
                    print('Will delete judge %d' % judge.iid)
                    self.db.t.judge.remove(judge.iid)
                    self.table_judges.removeRow(row)
                else:
                    print('Nothing deleted')

    def save_button(self, sender=None):
        self.table_judges.setFocus()
        row = 0
        while row < self.table_judges.rowCount():
            judge_id = int(self.table_judges.item(row, 2).text())
            judge = self.db.t.judge.get(judge_id)
            judge.first_name = sanitize(self.table_judges.item(row, 0).text())
            judge.last_name = sanitize(self.table_judges.item(row, 1).text())
            if self.db.s.verbose:
                print('Saving judge %s %s [%d] to competition %d(%d)' %
                      (judge.first_name, judge.last_name, judge.iid,
                       self.competition_id, judge.competition))
            self.db.t.judge.update(judge)
            row += 1
        self.changes_made = False
        self.hide()

    def exit_button(self, sender=None):
        if self.changes_made:
            save_result = ask_save()
        else:
            save_result = 'discard'
        if self.db.s.verbose:
            print(f"save_result: {save_result}")
        if save_result == 'discard':
            self.hide()
        elif save_result == 'save':
            self.save_button()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        self.changes_made = True
