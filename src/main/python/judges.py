import classes as sc
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
from sWidgets import verify, ask_save


class JudgeSelector(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(JudgeSelector, self).__init__()
        self.db = db
        if self.db.settings.verbose:
            print("JudgeSelector in judges.py")
        self.main_window = main_window
        self.comp_id = comp_id
        self.changes_made = False
        self.layout = qt.QVBoxLayout()
        self.judges = self.db.tables.judges.get_by_competition(comp_id)
        self.table_judges = qt.QTableWidget()
        self.headers = ['First Name', 'Last Name', 'id']
        self.table_judges.setColumnCount(len(self.headers))
        self.table_judges.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [120,150,0]
        column = 0
        while column < len(self.column_widths):
            self.table_judges.setColumnWidth(column, self.column_widths[column])
            column += 1
        row = 0
        for judge in self.judges:
            item_first_name = qt.QTableWidgetItem(judge.firstName)
            item_last_name = qt.QTableWidgetItem(judge.lastName)
            item_judge_id = qt.QTableWidgetItem('%d' % judge.id)
            self.table_judges.setRowCount(row+1)
            self.table_judges.setItem(row, 0, item_first_name)
            self.table_judges.setItem(row, 1, item_last_name)
            self.table_judges.setItem(row, 2, item_judge_id)

            row += 1
        self.table_judges.setColumnHidden(2, True)
        self.table_judges.itemChanged.connect(self.item_changed)
        self.layout.addWidget(self.table_judges)
        self.newButton = qt.QPushButton('&New Judge')
        self.newButton.clicked.connect(self.new_judge)
        self.layout.addWidget(self.newButton)
        self.deleteButton = qt.QPushButton('&Delete Judge')
        self.deleteButton.clicked.connect(self.delete_judge)
        self.layout.addWidget(self.deleteButton)
        self.saveButton = qt.QPushButton('&Save')
        self.saveButton.clicked.connect(self.save_button)
        self.layout.addWidget(self.saveButton)
        self.exitButton = qt.QPushButton('E&xit')
        self.exitButton.clicked.connect(self.exit_button)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def new_judge(self, sender=None):
        row = self.table_judges.rowCount()
        # id, firstName, lastName, competition
        # judge = sc.Judge(0,'','',self.comp_id)
        # judge = self.db.tables.judges.insert(judge)
        judge = self.db.tables.judges.new(self.comp_id)
        self.table_judges.insertRow(row)
        item_first_name = qt.QTableWidgetItem(judge.firstName)
        item_last_name = qt.QTableWidgetItem(judge.lastName)
        item_judge_id = qt.QTableWidgetItem(('%d' % judge.id))

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
            judge = self.db.tables.judges.get(int(
                self.table_judges.item(row, 2).text()))
            if judge is not None:
                verity = verify(('Are you sure you want to delete judge %s %s?'
                                 % (judge.firstName, judge.lastName)),
                                'This will delete all data for the given judge\
                                 and all scores associated with this judge.\
                                 This cannot be undone.')
                if verity:
                    print('Will delete judge %d' % judge.id)
                    self.db.tables.judges.remove(judge.id)
                    self.table_judges.removeRow(row)
                else:
                    print('Nothing deleted')

    def save_button(self, sender=None):
        row = 0
        while row < self.table_judges.rowCount():
            judge_id = int(self.table_judges.item(row, 2).text())
            judge = self.db.tables.judges.get(judge_id)
            judge.firstName = self.table_judges.item(row, 0).text()
            judge.lastName = self.table_judges.item(row, 1).text()
            print('Saving judge %s %s [%d] to competition %d(%d)' %
                  (judge.firstName, judge.lastName, judge.id, self.comp_id,
                   judge.competition))
            self.db.tables.judges.update(judge)

            row += 1
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
            self.save_button()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        # print('Item changed')
        self.changes_made = True
