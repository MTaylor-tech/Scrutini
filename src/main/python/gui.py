"""Scrutini GUI"""
from db import SCDatabase
import classes as sc
import datetime
from pathlib import Path
import os
import csv
from PyQt5 import QtPrintSupport
import sys
import PyQt5.QtWidgets as qt
# QGroupBox, QPushButton, QVBoxLayout
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg
# from PyQt5.QtGui import QPalette
from fpdf import FPDF


class SPushButton(qt.QPushButton):
    def __init__(self, text, sender, identifier, fn):
        super(SPushButton, self).__init__(text)
        self.identifier = identifier
        self.sender = sender
        self.fn = fn

    def on_button_clicked(self):
        self.fn(self.identifier)
#
#
# class SCPushButton(QPushButton):
#     def __init__(self, text, compSelector, identifier):
#         super(SPushButton, self).__init__(text)
#         self.identifier = identifier
#         self.compSelector = compSelector
#
#     def on_button_clicked(self):
#         self.compSelector.set_competition(self.identifier)
#
#
# class SDGPushButton(QPushButton):
#     def __init__(self, text, dgSelector, identifier):
#         super(SDGPushButton, self).__init__(text)
#         self.identifier = identifier
#         self.dgSelector = dgSelector
#
#     def on_button_clicked(self):
#         self.dgSelector.set_dancer_group(self.identifier)


class ResultsGroupBox(qt.QGroupBox):
    def __init__(self, text, event, db):
        super(ResultsGroupBox, self).__init__(text)
        self.db = db
        self.event = event
        self.layout = qt.QVBoxLayout()
        self.scores = event.scores
        self.scores.sort(key=self.get_score_value, reverse=True)
        # How to calc/show results from multiple judges? xxx
        place = 1
        previous_score = 0
        self.placing_scores = {}
        self.placing = [0]*7
        self.print_label = ''
        for score in self.scores:
            if score.score < previous_score:
                place += 1
            if ((place == 1) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(1).points
                self.placing[1] = score.dancer
            elif ((place == 2) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(2).points
                self.placing[2] = score.dancer
            elif ((place == 3) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(3).points
                self.placing[3] = score.dancer
            elif ((place == 4) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(4).points
                self.placing[4] = score.dancer
            elif ((place == 5) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(5).points
                self.placing[5] = score.dancer
            elif ((place == 6) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(6).points
                self.placing[6] = score.dancer

            if ((place > self.event.numPlaces) or (score.score == 0)):
                break

            dancer = self.db.tables.dancers.get(score.dancer)
            previous_score = score.score
            label_score = qt.QLabel('%d. (%s) %s %s - %s, %s' % (place, dancer.number,
                                                    dancer.firstName, dancer.lastName, dancer.city, dancer.state))
            self.print_label += ('%s::' % label_score.text())
            self.layout.addWidget(label_score)
            #print(self.placing_scores)
        self.setLayout(self.layout)

    def get_score_value(self, score):
        return score.score

    def get_print_label(self):
        return self.print_label

    def get_placing_scores(self):
        return self.placing_scores

    def get_placing(self):
        return self.placing

    def select_event(self, event_id):
        self.event = self.db.tables.events.get(event_id)
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.update()
        self.scores = self.db.tables.scores.get_by_event(self.event.id)
        self.scores.sort(key=self.get_score_value, reverse=True)
        place = 1
        previous_score = 0
        self.placing_scores = {}
        self.placing = [0]*7
        for score in self.scores:
            if score.score < previous_score:
                place += 1
            if ((place == 1) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(1).points
                self.placing[1] = score.dancer
            elif ((place == 2) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(2).points
                self.placing[2] = score.dancer
            elif ((place == 3) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(3).points
                self.placing[3] = score.dancer
            elif ((place == 4) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(4).points
                self.placing[4] = score.dancer
            elif ((place == 5) and (score.score > 0)):
                self.placing_scores[score.dancer] = db.tables.place_values.get(5).points
                self.placing[5] = score.dancer
            elif ((place == 6) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.tables.place_values.get(6).points
                self.placing[6] = score.dancer
            if ((place > self.event.numPlaces) or (score.score == 0)):
                break
            dancer = self.db.tables.dancers.get(score.dancer)
            previous_score = score.score
            label_score = qt.QLabel('%d. (%s) %s %s - %s, %s' % (place, dancer.number,
                                                    dancer.firstName, dancer.lastName, dancer.city, dancer.state))
            self.layout.addWidget(label_score)
        self.update()

class ResultsViewWindow(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(ResultsViewWindow, self).__init__()
        self.db = db
        self.main_window = main_window
        self.comp_id = comp_id
        self.competition = self.db.tables.competitions.get(self.comp_id)
        self.layout = qt.QVBoxLayout()
        self.dancerGroups = self.db.tables.groups.get_by_competition(self.comp_id)
        self.big_layout = qt.QVBoxLayout()
        self.big_groupBox = qt.QGroupBox()
        self.label_group = qt.QLabel('Viewing results for group:')
        self.layout.addWidget(self.label_group)
        self.selector_dancerGroup = qt.QComboBox()
        self.groupBox_scores = qt.QGroupBox()
        self.groupBox_scores_layout = qt.QGridLayout()
        self.dancerGroup_ids = []
        for dancerGroup in self.dancerGroups:
            self.selector_dancerGroup.addItem(dancerGroup.name)
            self.dancerGroup_ids.append(dancerGroup.id)
        self.selector_dancerGroup.currentIndexChanged.connect(self.new_group_selected)
        self.layout.addWidget(self.selector_dancerGroup)
        self.dancerGroup = self.db.tables.groups.get(self.dancerGroup_ids[self.selector_dancerGroup.currentIndex()])
        self.events = self.db.tables.events.get_by_group(self.dancerGroup.id)
        self.dancers = self.db.tables.events.get_by_group(self.dancerGroup.id)
        self.overall_scores = {}
        self.print_label = ''
        for dancer in self.dancers:
            self.overall_scores[dancer.id] = 0
        i=1
        n=1
        for event in self.events:
            results_box = ResultsGroupBox(event.name, event.id)
            #self.groupBox_scores_layout.addWidget(results_box)
            if (i%2==0):
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1, qt.Qt.AlignRight)
                n += 1
            else:
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1,qt.Qt.AlignLeft)
            self.print_label += ('%s::%s:: ::' % (event.name, results_box.get_print_label()))
            if (event.countsForOverall == 1):
                #print(event.name)
                event_placing_scores = results_box.get_placing_scores()
                for dancer, points in event_placing_scores.items():
                    #print('(%d) - [%6.2f]' % (dancer, points))
                    self.overall_scores[dancer] += points
            i += 1

        self.overall_scores_sorted = [(k, self.overall_scores[k]) for k in sorted(self.overall_scores, key=self.overall_scores.get, reverse=True)]
        self.groupBox_overall = qt.QGroupBox('Overall Results for %s' % self.dancerGroup.name)
        self.groupBox_overall_layout = qt.QVBoxLayout()
        self.print_label += ('Overall Results for %s::' % self.dancerGroup.name)
        place = 1
        for dancer_id, points in self.overall_scores_sorted:
            if points <= 0:
                break
            dancer = self.db.tables.dancers.get(dancer_id)
            label_overall = qt.QLabel('%d. (%s) %s %s - %s, %s: %d points' % (place, dancer.number,
                                                    dancer.firstName, dancer.lastName, dancer.city, dancer.state, points))
            self.groupBox_overall_layout.addWidget(label_overall)
            self.print_label += ('%s::' % label_overall.text())
            place += 1

        self.groupBox_scores.setLayout(self.groupBox_scores_layout)
        self.layout.addWidget(self.groupBox_scores)
        self.groupBox_overall.setLayout(self.groupBox_overall_layout)
        self.layout.addWidget(self.groupBox_overall)
        self.button_exit = qt.QPushButton('E&xit')
        self.button_exit.clicked.connect(self.cancel_button)


        self.big_groupBox.setLayout(self.layout)

        self.button_print = qt.QPushButton('Print Results')
        self.button_pdf = qt.QPushButton('Save PDF')
        self.button_print.clicked.connect(self.print_to_printer)
        self.button_pdf.clicked.connect(self.print_to_pdf)
        self.big_layout.addWidget(self.button_print)
        self.big_layout.addWidget(self.button_pdf)
        self.big_layout.addWidget(self.button_exit)
        self.big_layout.addWidget(self.big_groupBox)
        self.setLayout(self.big_layout)
        self.sizeHint()
        self.resize(800,400)

    def print_to_printer(self):
        doc_text = ('<center><strong>%s</strong><br>%s<br>%s</center>' % (self.competition.name,self.competition.eventDate[0:10],self.dancerGroup.name))
        print_label_list = self.print_label.split('::')
        for label in print_label_list:
            doc_text += ('<br>%s' % label)
        textedit = qt.QTextEdit(doc_text)
        dialog = QtPrintSupport.QPrintDialog()
        if dialog.exec_() == qt.QDialog.Accepted:
            textedit.document().print_(dialog.printer())


    def print_to_pdf(self):
        self.pdf = FPDF(orientation='P',unit='mm',format='letter')
        self.pdf.add_page()
        self.pdf.set_font('helvetica','B', size=12)
        self.pdf.cell(180,5,txt=self.competition.name,ln=1,align='C')
        self.pdf.set_font('helvetica', size=12)
        self.pdf.cell(180,5,txt=self.competition.eventDate[0:10],ln=1,align='C')
        self.pdf.cell(180,5,txt=self.dancerGroup.name,ln=1,align='C')
        self.pdf.cell(180,5,txt=' ',ln=1,align='C')
        print_label_list = self.print_label.split('::')
        for label in print_label_list:
            self.pdf.cell(180,5,txt=label,ln=1,align='L')
        options = qt.QFileDialog.Options()
        options |= qt.QFileDialog.DontUseNativeDialog
        self.filename, _ = qt.QFileDialog.getSaveFileName(self,"Save File", "","PDF Files (*.pdf)", options=options)
        if self.filename:
            if (self.filename[-4:].lower() != '.pdf'):
                self.filename += '.pdf'
            print(self.filename)
            self.pdf.output(self.filename)
        else:
            return

    def new_group_selected(self):
        self.dancerGroup = self.db.tables.groups.get(self.dancerGroup_ids[self.selector_dancerGroup.currentIndex()])
        for i in reversed(range(self.groupBox_scores_layout.count())):
            if isinstance(self.groupBox_scores_layout.itemAt(i).widget(),ResultsGroupBox):
                self.groupBox_scores_layout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.groupBox_overall_layout.count())):
            self.groupBox_overall_layout.itemAt(i).widget().setParent(None)
        self.update()
        self.events = self.db.tables.events.get_by_group(self.dancerGroup.id)
        self.dancers = self.db.tables.dancers.get_by_group(self.dancerGroup.id)
        self.overall_scores = {}
        self.print_label = ''
        for dancer in self.dancers:
            self.overall_scores[dancer.id] = 0
        i = 1
        n = 1
        for event in self.events:
            results_box = ResultsGroupBox(event.name, event.id)
            #self.groupBox_scores_layout.addWidget(results_box)
            results_box.sizeHint()
            if (i%2==0):
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1, qt.Qt.AlignRight)
                n += 1
            else:
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1,qt.Qt.AlignLeft)
            self.print_label += ('%s::%s:: ::' % (event.name, results_box.get_print_label()))
            if (event.countsForOverall == 1):
                #print(event.name)
                event_placing_scores = results_box.get_placing_scores()
                for dancer, points in event_placing_scores.items():
                    #print('(%d) - [%6.2f]' % (dancer, points))
                    self.overall_scores[dancer] += points
            i += 1

        self.overall_scores_sorted = [(k, self.overall_scores[k]) for k in sorted(self.overall_scores, key=self.overall_scores.get, reverse=True)]
        self.groupBox_overall.setTitle('Overall Results for %s' % self.dancerGroup.name)
        self.print_label += ('Overall Results for %s::' % self.dancerGroup.name)
        place = 1
        for dancer_id, points in self.overall_scores_sorted:
            if points <= 0:
                break
            dancer = self.db.tables.dancers.get(dancer_id)
            label_overall = qt.qQLabel('%d. (%s) %s %s - %s, %s: %d points' % (place, dancer.number,
                                                    dancer.firstName, dancer.lastName, dancer.city, dancer.state, points))
            self.groupBox_overall_layout.addWidget(label_overall)
            self.print_label += ('%s::' % label_overall.text())
            place += 1

        self.groupBox_scores.sizeHint()
        self.groupBox_overall.sizeHint()
        self.big_groupBox.sizeHint()
        self.sizeHint()
        self.update()
        self.resize(800,400)

    def cancel_button(self, sender=None):
        self.hide()

class ScoreEntryWindow(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(ScoreEntryWindow, self).__init__()
        self.db = db
        self.main_window = main_window
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


class DancerEditor(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(DancerEditor, self).__init__()
        self.main_window = main_window
        self.comp_id = comp_id
        self.db = db
        self.changes_made = False
        self.resize(1680,1000)
        self.layout = qt.QVBoxLayout()
        self.dancers = self.db.tables.dancers.get_by_competition(comp_id)
        self.table_dancers = qt.QTableWidget()
        self.headers = ['First Name','Last Name','Num','Category','Groups','ScotDance#','Address','City','ST','Zip Code','Birthdate','Age','Entry Rcvd','Phone #','Email','Teacher','Teacher\'s Email','id','cat_id']
        self.table_dancers.setColumnCount(len(self.headers))
        self.table_dancers.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [120,150,40,130,100,100,150,120,40,60,80,30,80,110,250,200,250,0,0]
        column = 0
        while column < len(self.column_widths):
            self.table_dancers.setColumnWidth(column,self.column_widths[column])
            column += 1
        row = 0
        #id, firstName, lastName, scotDanceNum, street, city, state, zipCode, birthdate, age, registeredDate,
        #number, phonenum, email, teacher, teacherEmail, dancerCat, dancerGroup, competition
        for dancer in self.dancers:
            item_first_name = qt.QTableWidgetItem(dancer.firstName)
            item_last_name = qt.QTableWidgetItem(dancer.lastName)
            item_number = qt.QTableWidgetItem(dancer.number)

            selector_dancerCat = qt.QComboBox()
            dancerCats = self.db.tables.categories.get_all()
            for dancerCat in dancerCats:
                selector_dancerCat.addItem(dancerCat.name)
                #print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
            if dancer.dancerCat is not None:
                selector_dancerCat.setCurrentIndex(dancer.dancerCat)
            else:
                selector_dancerCat.setCurrentIndex(0)


            dancerCat = self.db.tables.categories.get(dancer.dancerCat)
            if dancerCat is not None:
                dancerCat_name = dancerCat.name
            else:
                dancerCat_name = ''
            item_cat = qt.QTableWidgetItem(dancerCat_name)
            item_cat_id = qt.QTableWidgetItem(dancer.dancerCat)


            dancer_groups = self.db.tables.groups.get_by_dancer(dancer.id)
            dancer_group_list = ''
            for group in dancer_groups:
                if dancer_group_list != '':
                    dancer_group_list += ', '
                dancer_group_list += group.abbrev
            item_groups = qt.QTableWidgetItem(dancer_group_list)

            item_scotdance = qt.QTableWidgetItem(dancer.scotDanceNum)
            item_address = qt.QTableWidgetItem(dancer.street)
            item_city = qt.QTableWidgetItem(dancer.city)
            item_state = qt.QTableWidgetItem(dancer.state)
            item_zipCode = qt.QTableWidgetItem(dancer.zipCode)

            # if ((dancer.birthdate != '') and (dancer.birthdate != None)):
            #    item_birthdate = QTableWidgetItem(self.get_formatted_date(dancer.birthdate))
            # else:
            #    item_birthdate = QTableWidgetItem('')
            item_birthdate = qt.QTableWidgetItem(dancer.birthdate)

            if type(dancer.age) == int:
                item_age = qt.QTableWidgetItem(('%d' % dancer.age))
            elif dancer.age is not None:
                item_age = qt.QTableWidgetItem(dancer.age)
            else:
                item_age = qt.QTableWidgetItem('')

            #if ((dancer.registeredDate != '') and (dancer.registeredDate != None)):
            #    item_entryrcvd = QTableWidgetItem(self.get_formatted_date(dancer.registeredDate))
            #else:
            #    item_entryrcvd = QTableWidgetItem('')
            item_entryrcvd = qt.QTableWidgetItem(dancer.registeredDate)

            item_phonenum = qt.QTableWidgetItem(dancer.phonenum)
            item_email = qt.QTableWidgetItem(dancer.email)
            item_teacher = qt.QTableWidgetItem(dancer.teacher)
            item_teacherEmail = qt.QTableWidgetItem(dancer.teacherEmail)
            item_dancer_id = qt.QTableWidgetItem(('%d' % dancer.id))

            self.table_dancers.setRowCount(row+1)
            self.table_dancers.setItem(row,  0, item_first_name)
            self.table_dancers.setItem(row,  1, item_last_name)
            self.table_dancers.setItem(row,  2, item_number)
            #self.table_dancers.setItem(row,  3, item_cat)
            self.table_dancers.setCellWidget(row, 3, selector_dancerCat)
            self.table_dancers.setItem(row,  4, item_groups)
            self.table_dancers.setItem(row,  5, item_scotdance)
            self.table_dancers.setItem(row,  6, item_address)
            self.table_dancers.setItem(row,  7, item_city)
            self.table_dancers.setItem(row,  8, item_state)
            self.table_dancers.setItem(row,  9, item_zipCode)
            self.table_dancers.setItem(row, 10, item_birthdate)
            self.table_dancers.setItem(row, 11, item_age)
            self.table_dancers.setItem(row, 12, item_entryrcvd)
            self.table_dancers.setItem(row, 13, item_phonenum)
            self.table_dancers.setItem(row, 14, item_email)
            self.table_dancers.setItem(row, 15, item_teacher)
            self.table_dancers.setItem(row, 16, item_teacherEmail)
            self.table_dancers.setItem(row, 17, item_dancer_id)
            self.table_dancers.setItem(row, 18, item_cat_id)

            row += 1
        self.table_dancers.setColumnHidden(17,True)
        self.table_dancers.setColumnHidden(18,True)
        self.table_dancers.setSortingEnabled(True)
        self.table_dancers.itemChanged.connect(self.item_changed)
        #connect(self.table_dancers,
        #    SIGNAL(itemChanged(QTableWidgetItem *)), self, SLOT(on_any_itemChanged(QTableWidgetItem *)));
        self.layout.addWidget(self.table_dancers)
        self.newButton = qt.QPushButton('&New Competitor')
        self.newButton.clicked.connect(self.new_dancer)
        self.layout.addWidget(self.newButton)
        self.deleteButton = qt.QPushButton('&Delete Selected Competitor')
        self.deleteButton.clicked.connect(self.delete_dancer)
        self.layout.addWidget(self.deleteButton)
        self.saveButton = qt.QPushButton('&Save')
        self.saveButton.clicked.connect(self.save_button)
        self.layout.addWidget(self.saveButton)
        self.exitButton = qt.QPushButton('E&xit')
        self.exitButton.clicked.connect(self.cancel_button)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(qc.Qt.ApplicationModal)
        self.setLayout(self.layout)

    def item_changed(self, sender=None):
        print('Item changed')
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

    def new_dancer(self, sender=None):
        row = self.table_dancers.rowCount()
        #id, firstName, lastName, scotDanceNum, street, city, state, zipCode,
        #birthdate, age, registeredDate, number, phonenum, email, teacher, teacherEmail, dancerCat, dancerGroup, competition
        dancer = sc.Dancer(0,'','','','','','','','',0,'','','','','','',0,0,self.comp_id)
        dancer = self.db.tables.dancers.insert(dancer)
        self.table_dancers.insertRow(row)
        item_first_name = qt.QTableWidgetItem(dancer.firstName)
        item_last_name = qt.QTableWidgetItem(dancer.lastName)
        item_number = qt.QTableWidgetItem(dancer.number)

        selector_dancerCat = qt.QComboBox()
        dancerCats = self.db.tables.categories.get_all()
        for dancerCat in dancerCats:
            selector_dancerCat.addItem(dancerCat.name)
            #print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
        if dancer.dancerCat is not None:
            selector_dancerCat.setCurrentIndex(dancer.dancerCat)
        else:
            selector_dancerCat.setCurrentIndex(0)


        dancerCat = self.db.tables.categories.get(dancer.dancerCat)
        if dancerCat is not None:
            dancerCat_name = dancerCat.name
        else:
            dancerCat_name = ''
        item_cat = qt.QTableWidgetItem(dancerCat_name)
        item_cat_id = qt.QTableWidgetItem(dancer.dancerCat)


        dancer_groups = self.db.tables.groups.get_by_dancer(dancer.id)
        dancer_group_list = ''
        for group in dancer_groups:
            if dancer_group_list != '':
                dancer_group_list += ', '
            dancer_group_list += group.abbrev
        item_groups = qt.QTableWidgetItem(dancer_group_list)

        item_scotdance = qt.QTableWidgetItem(dancer.scotDanceNum)
        item_address = qt.QTableWidgetItem(dancer.street)
        item_city = qt.QTableWidgetItem(dancer.city)
        item_state = qt.QTableWidgetItem(dancer.state)
        item_zipCode = qt.QTableWidgetItem(dancer.zipCode)

        #if ((dancer.birthdate != '') and (dancer.birthdate != None)):
        #    item_birthdate = QTableWidgetItem(self.get_formatted_date(dancer.birthdate))
        #else:
        #    item_birthdate = QTableWidgetItem('')
        item_birthdate = qt.QTableWidgetItem(dancer.birthdate)

        if type(dancer.age) == int:
            item_age = qt.QTableWidgetItem(('%d' % dancer.age))
        elif dancer.age is not None:
            item_age = qt.QTableWidgetItem(dancer.age)
        else:
            item_age = qt.QTableWidgetItem('')

        # if ((dancer.registeredDate != '') and (dancer.registeredDate != None)):
        #    item_entryrcvd = QTableWidgetItem(self.get_formatted_date(dancer.registeredDate))
        # else:
        #    item_entryrcvd = QTableWidgetItem('')
        item_entryrcvd = qt.QTableWidgetItem(dancer.registeredDate)

        item_phonenum = qt.QTableWidgetItem(dancer.phonenum)
        item_email = qt.QTableWidgetItem(dancer.email)
        item_teacher = qt.QTableWidgetItem(dancer.teacher)
        item_teacherEmail = qt.QTableWidgetItem(dancer.teacherEmail)
        item_dancer_id = qt.QTableWidgetItem(('%d' % dancer.id))

        self.table_dancers.setItem(row,  0, item_first_name)
        self.table_dancers.setItem(row,  1, item_last_name)
        self.table_dancers.setItem(row,  2, item_number)
        # self.table_dancers.setItem(row,  3, item_cat)
        self.table_dancers.setCellWidget(row, 3, selector_dancerCat)
        self.table_dancers.setItem(row,  4, item_groups)
        self.table_dancers.setItem(row,  5, item_scotdance)
        self.table_dancers.setItem(row,  6, item_address)
        self.table_dancers.setItem(row,  7, item_city)
        self.table_dancers.setItem(row,  8, item_state)
        self.table_dancers.setItem(row,  9, item_zipCode)
        self.table_dancers.setItem(row, 10, item_birthdate)
        self.table_dancers.setItem(row, 11, item_age)
        self.table_dancers.setItem(row, 12, item_entryrcvd)
        self.table_dancers.setItem(row, 13, item_phonenum)
        self.table_dancers.setItem(row, 14, item_email)
        self.table_dancers.setItem(row, 15, item_teacher)
        self.table_dancers.setItem(row, 16, item_teacherEmail)
        self.table_dancers.setItem(row, 17, item_dancer_id)
        self.table_dancers.setItem(row, 18, item_cat_id)
        self.table_dancers.scrollToItem(self.table_dancers.item(row, 0))
        self.changes_made = True

    def delete_dancer(self, sender=None):
        row = self.table_dancers.currentRow()
        if row is not None:
            dancer = self.db.tables.dancers.get(int(self.table_dancers.item(row, 17).text()))
            if dancer is not None:
                verity = verify(('Are you sure you want to delete dancer %s %s?' % (dancer.firstName, dancer.lastName)),
                                'This will delete all data for the given competitor. This cannot be undone.')
                if verity:
                    print('Will delete dancer %d' % dancer.id)
                    self.db.tables.dancers.remove(dancer.id)
                    self.table_dancers.removeRow(row)
                else:
                    print('Nothing deleted')

    def save_button(self, sender=None):
        row = 0
        while row < self.table_dancers.rowCount():
            dancer_id = int(self.table_dancers.item(row, 17).text())
            dancer = self.db.tables.dancers.get(dancer_id)
            dancer.firstName = self.table_dancers.item(row, 0).text()
            dancer.lastName = self.table_dancers.item(row, 1).text()
            dancer.number = self.table_dancers.item(row, 2).text()

            dancer.scotDanceNum = self.table_dancers.item(row, 5).text()
            dancer.street = self.table_dancers.item(row, 6).text()
            dancer.city = self.table_dancers.item(row, 7).text()
            dancer.state = self.table_dancers.item(row, 8).text()
            dancer.zipCode = self.table_dancers.item(row, 9).text()
            dancer.birthdate = self.table_dancers.item(row, 10).text()
            dancer_age = self.table_dancers.item(row, 11).text()
            if dancer_age.isdigit():
                dancer.age = int(dancer_age)
            dancer.registeredDate = self.table_dancers.item(row, 12).text()
            dancer.phonenum = self.table_dancers.item(row, 13).text()
            dancer.email = self.table_dancers.item(row, 14).text()
            dancer.teacher = self.table_dancers.item(row, 15).text()
            dancer.teacherEmail = self.table_dancers.item(row, 16).text()

            selector_dancerCat = self.table_dancers.cellWidget(row, 3)
            if selector_dancerCat.currentIndex() > 0:
                dancer.dancerCat = selector_dancerCat.currentIndex()
            #item_cat = self.table_dancers.item(row, 18).text()
            #if (item_cat.isdigit()):
            #    dancer.dancerCat = int(item_cat)

            dancer_groups_text = self.table_dancers.item(row, 4).text()
            dancer_groups_text = ''.join(dancer_groups_text.split())
            if dancer_groups_text != '':
                dancer_groups_abbrev = dancer_groups_text.split(',')
                already_in_groups = self.db.tables.groups.get_by_dancer(dancer_id)
                already_in_abbrevs = []
                for group in already_in_groups:
                    if group is not None:
                        already_in_abbrevs.append(group.abbrev)
                for abbrev in dancer_groups_abbrev:
                    if abbrev in already_in_abbrevs:
                        print('Dancer %s %s is already in group [%s] and should remain' % (dancer.firstName, dancer.lastName, abbrev))
                    else:
                        print('Dancer %s %s is not in group [%s] and should be added' % (dancer.firstName, dancer.lastName, abbrev))
                        dancerGroup = self.db.tables.groups.get_by_abbrev(abbrev)
                        if dancerGroup is not None:
                            self.db.tables.groups.join(dancer.id, dancerGroup.id)
                for abbrev in already_in_abbrevs:
                    if abbrev in dancer_groups_abbrev:
                        print('Dancer %s %s is already in group [%s] and should remain' % (dancer.firstName, dancer.lastName, abbrev))
                    else:
                        print('Dancer %s %s is in group [%s] and should be removed' % (dancer.firstName, dancer.lastName, abbrev))
                        dancerGroup = self.db.tables.groups.get_by_abbrev(abbrev)
                        if dancerGroup is not None:
                            self.db.tables.groups.unjoin(dancer.id, dancerGroup.id)

            self.db.tables.dancers.update(dancer)

            row += 1
        self.changes_made = False

    def get_formatted_date(self, date):
        format_str = '%d %b %Y'
        otherformat_str = '%Y-%m-%d'
        return (datetime.datetime.strftime(datetime.datetime.strptime(('%s' % date)[0:10], otherformat_str).date(), format_str))

class DancerGroupEditor(qt.QDialog):
    def __init__(self, main_window, dancerGroup_id, db):
        super(DancerGroupEditor, self).__init__()
        self.db = db
        self.main_window = main_window
        self.dancerGroup = self.db.tables.groups.get(dancerGroup_id)
        self.changes_made = False
        #id, name, abbrev, ageMin, ageMax, dancerCat, competition
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
            #print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
        if self.dancerGroup.dancerCat is not None:
            self.selector_dancerCat.setCurrentIndex(self.dancerGroup.dancerCat)
        else:
            selector_dancerCat.setCurrentIndex(0)
        self.dancers_in_group = self.db.tables.dancers.get_by_group(dancerGroup_id)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer is not None:
                self.dancer_ids.append(dancer.id)
        self.table_dancers = qt.QTableWidget()
        self.headers = ['', 'Num','First Name','Last Name','id']
        self.table_dancers.setColumnCount(len(self.headers))
        self.table_dancers.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [20, 40, 120, 150, 0]
        all_dancers = self.db.tables.dancers.get_by_competition(self.dancerGroup.competition)
        column = 0
        while column < len(self.column_widths):
            self.table_dancers.setColumnWidth(column,self.column_widths[column])
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
        self.events_headers = ['Event','In Overall','Places','Stamp','id']
        self.table_events.setColumnCount(len(self.events_headers))
        self.table_events.setHorizontalHeaderLabels(self.events_headers)
        self.column_widths = [260, 40, 60, 40, 0]
        column = 0
        while column < len(self.column_widths):
            self.table_events.setColumnWidth(column,self.column_widths[column])
            column += 1
        self.table_events.setColumnHidden(4, True)
        self.events = self.db.tables.dancers.get_by_group(self.dancerGroup.id)
        row = 0
        #id, name, dancerGroup, dance, competition, countsForOverall, numPlaces, earnsStamp
        for event in self.events:
            if event is not None:
                #dance = scrudb.retrieve_dance(event.dance)
                #item_name = QTableWidgetItem(dance.name)
                dances = self.db.tables.dances.get_all()
                selector_dance = qt.QComboBox()
                index = 999999
                for dance in dances:
                    if dance[0] < index:
                        index = dance[0]
                    selector_dance.addItem(dance[1])
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
                #self.table_events.setItem(row, 0, item_name)
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
        self.setWindowModality(qt.Qt.ApplicationModal)
        self.setLayout(self.layout)


    def save_button(self, sender=None):
        self.dancerGroup.name = self.field_name.text()
        self.dancerGroup.abbrev = self.field_abbrev.text()
        if (self.field_ageMin.text().isdigit()):
            self.dancerGroup.ageMin = int(self.field_ageMin.text())
        if (self.field_ageMax.text().isdigit()):
            self.dancerGroup.ageMax = int(self.field_ageMax.text())
        self.dancerGroup.dancerCat = self.selector_dancerCat.currentIndex()
        self.db.tables.groups.update(self.dancerGroup)
        row = 0
        self.dancers_in_group = self.db.tables.dancers.get_by_group(self.dancerGroup.id)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer is not None:
                self.dancer_ids.append(dancer.id)
        while row < self.table_dancers.rowCount():
            checkbox_in_group = self.table_dancers.cellWidget(row, 0)
            dancer_id_text = self.table_dancers.item(row,4).text()
            if (dancer_id_text != ''):
                dancer_id = int(dancer_id_text)
            else:
                dancer_id = 9999999999999999999
            if checkbox_in_group.checkState() == 0 and dancer_id in self.dancer_ids:
                print('dancer [%s] in row %d is in group but should be removed' % (dancer_id_text, row))
                self.db.tables.groups.unjoin(dancer_id,self.dancerGroup.id)
            elif checkbox_in_group.checkState() == 2 and dancer_id not in self.dancer_ids:
                print('dancer [%s] in row %d is not in group but should be added' % (dancer_id_text, row))
                self.db.tables.groups.join(dancer_id,self.dancerGroup.id)

            row += 1

        row = 0
        while row < self.table_events.rowCount():
            event_id = int(self.table_events.item(row, 4).text())
            event = self.db.tables.events.get(event_id)
            selector_dance = self.table_events.cellWidget(row, 0)
            event.name = ('%s - %s' % (self.dancerGroup.name, selector_dance.currentText()))
            print(event.name)
            dances = self.db.tables.dances.get()
            index = 999999
            for dance in dances:
                if dance[0] < index:
                    index = dance[0]
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
        event = Event(0,'',self.dancerGroup.id,0,self.dancerGroup.competition,1,6,1)
        event = self.db.tables.events.insert(event)
        row = self.table_events.rowCount()
        #id, name, dancerGroup, dance, competition, countsForOverall, numPlaces, earnsStamp
        self.table_events.insertRow(row)
        dances = scrudb.retrieve_dances()
        selector_dance = qt.QComboBox()
        for dance in dances:
            selector_dance.addItem(dance[1])
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
            event = self.db.tables.events.get(int(self.table_events.item(row, 4).text()))
            dance = self.db.tables.dances.get(event.dance)
            if event is not None:
                verity = verify(('Are you sure you want to delete event %s %s?' % (self.dancerGroup.name, dance.name)),
                                'This will delete all data for the given event and all scores associated with this event. This cannot be undone.')
                if verity:
                    print('Will delete event %d' % event.id)
                    self.db.tables.events.remove(event.id)
                    self.table_events.removeRow(row)
                else:
                    print('Nothing deleted')

    def delete_group(self, sender=None):
        verity = verify(('Are you sure you want to delete competitor group %s?' % self.dancerGroup.name),
                                'This will delete all data for the given group and all scores associated with this group. This cannot be undone.')
        if verity:
            print('Will delete group %d' % dancerGroup.id)
            self.db.tables.groups.remove(dancerGroup.id)
            self.hide()
        else:
            print('Nothing deleted')

    def exit_button(self, sender=None):
        if self.changes_made:
            saveResult = ask_save()
        else:
            saveResult = 'discard'

        if saveResult == 'discard':
            self.hide()
        elif saveResult == 'save':
            self.save_button()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        print('Item changed')
        self.changes_made = True

class CompetitionEditor(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(CompetitionEditor, self).__init__()
        self.db = db
        self.main_window = main_window
        self.competition = self.db.tables.competitions.get(comp_id)
        self.changes_made = False
        self.layout = qt.QVBoxLayout()
        self.label_name = qt.QLabel('Name:')
        self.field_name = qt.QLineEdit(self.competition.name)
        self.label_location = qt.QLabel('Location:')
        self.field_location = qt.QLineEdit(self.competition.location)
        self.date_comp_event = qc.QDate.fromString(self.competition.eventDate, 'yyyy-MM-dd 00:00:00')
        self.date_comp_deadline = qc.QDate.fromString(self.competition.deadline, 'yyyy-MM-dd 00:00:00')
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
        self.setWindowModality(qc.Qt.ApplicationModal)
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

    def exit_button(self, sender=None):
        if self.changes_made:
            saveResult = ask_save()
        else:
            saveResult = 'discard'

        if saveResult == 'discard':
            self.hide()
        elif saveResult == 'save':
            self.save()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        print('Item changed')
        self.changes_made = True


class DancerGroupMenu(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(DancerGroupMenu, self).__init__()
        self.db = db
        self.main_window = main_window
        self.comp_id = comp_id
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(qt.QLabel('Choose a Competitor Group:'))
        self.dancerGroups = self.db.tables.groups.get_by_competition(comp_id)
        self.dgButtons = []
        for dancerGroup in self.dancerGroups:
            dgButton = SPushButton(('[%s] %s' % (dancerGroup.abbrev, dancerGroup.name)),self,dancerGroup.id,self.set_dancer_group)
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
        dancerGroup = sc.DancerGroup(0,'','',4,99,0,self.comp_id)
        dancerGroup = self.db.tables.groups.insert(dancerGroup)
        # id, name, abbrev, ageMin, ageMax, dancerCat, competition
        self.set_dancer_group(dancerGroup.id)

    def set_dancer_group(self, dancerGroup_id):
        dancerGroup = self.db.tables.groups.get(dancerGroup_id)
        if dancerGroup is not None:
            print('Group: [%s] %s' % (dancerGroup.abbrev, dancerGroup.name))
            self.hide()
            self.main_window.edit_dancerGroup(dancerGroup_id)

class CompetitionSelector(qt.QDialog):
    def __init__(self, main_window):
        super(CompetitionSelector, self).__init__()
        self.main_window = main_window
        self.layout = qt.QVBoxLayout()
        self.layout.addWidget(qt.QLabel('Choose a competition:'))
        self.competitions = self.main_window.db.tables.competitions.get_all()
        self.compButtons = []
        for comp in self.competitions:
            compButton = SPushButton('%s (%s)' % (comp.name, self.get_formatted_date(comp.eventDate)),self,comp.id,self.set_competition)
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


class JudgeSelector(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(JudgeSelector, self).__init__()
        self.db = db
        self.main_window = main_window
        self.comp_id = comp_id
        self.changes_made = False
        self.layout = qt.QVBoxLayout()
        self.judges = self.db.tables.judges.get_by_competition(comp_id)
        self.table_judges = qt.QTableWidget()
        self.headers = ['First Name','Last Name','id']
        self.table_judges.setColumnCount(len(self.headers))
        self.table_judges.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [120,150,0]
        column = 0
        while column < len(self.column_widths):
            self.table_judges.setColumnWidth(column,self.column_widths[column])
            column += 1
        row = 0
        for judge in self.judges:
            #print('%d. [%d] %s %s' % (row, judge.id, judge.firstName, judge.lastName))
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
        #id, firstName, lastName, competition
        judge = sc.Judge(0,'','',self.comp_id)
        judge = self.db.tables.judges.insert(judge)
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
        #print('Current row:',row)
        #print('Text = %s' % self.table_judges.item(row, 2).text())
        if row is not None:
            judge = self.db.tables.judges.get(int(self.table_judges.item(row, 2).text()))
            if judge is not None:
                verity = verify(('Are you sure you want to delete judge %s %s?' % (judge.firstName, judge.lastName)),
                                'This will delete all data for the given judge and all scores associated with this judge. This cannot be undone.')
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
            print('Saving judge %s %s [%d] to competition %d(%d)' % (judge.firstName, judge.lastName, judge.id, self.comp_id, judge.competition))
            self.db.tables.judges.update(judge)

            row += 1
        self.changes_made = False

    def exit_button(self, sender=None):
        if self.changes_made:
            saveResult = ask_save()
        else:
            saveResult = 'discard'

        if saveResult == 'discard':
            self.hide()
        elif saveResult == 'save':
            self.save_button()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        print('Item changed')
        self.changes_made = True

def print_settings():
    # displays the current settings
    settings = self.db.tables.settings.get('current')
    if settings.interface == 0:
        settings.interface = 1
        self.db.tables.settigns.update(settings)
    print('Settings details - Version: %f - Schema: %f - Interface: %d - Last Competition: %d' %
          (settings.version, settings.schema, settings.interface, settings.lastComp))


class PyQtApp(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setWindowTitle("Scrutini")
        self.setWindowIcon(qg.QIcon("Your/image/file.png"))


def on_button_clicked(sender):
    alert = QMessageBox()
    alert.setText(sender.text())
    alert.exec_()


def verify(prompt='Are you sure?', subprompt=''):
    alert = qt.QMessageBox()
    alert.setText(prompt)
    alert.setInformativeText(subprompt)
    alert.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.Cancel)
    alert.setEscapeButton(qt.QMessageBox.Cancel)
    buttonReply = alert.exec_()
    if buttonReply == qt.QMessageBox.Yes:
        print('Yes clicked.')
        return True
    else:
        print('No clicked.')
        return False

def ask_save(prompt='Do you want to save your changes?', subprompt=''):
    alert = qt.QMessageBox()
    alert.setText(prompt)
    alert.setInformativeText(subprompt)
    alert.setStandardButtons(qt.QMessageBox.Save | qt.QMessageBox.Discard | qt.QMessageBox.Cancel)
    alert.setDefaultButton(qt.QMessageBox.Save)
    alert.setEscapeButton(qt.QMessageBox.Cancel)
    buttonReply = alert.exec_()
    if buttonReply == qt.QMessageBox.Save:
        print('Save clicked.')
        return 'save'
    elif buttonReply == qt.QMessageBox.Discard:
        print('Discard clicked')
        return 'discard'
    else:
        print('Cancel clicked.')
        return 'cancel'

class SMainWindow(qt.QMainWindow):
    def __init__(self, db):
        super(SMainWindow, self).__init__()
        self.db = db
        self.app = PyQtApp()
        self.layout = qt.QVBoxLayout()
        self.label_text = ''
        self.label = qt.QLabel(self.label_text)
        self.settings = db.tables.settings.get('current')
        self.competition = self.retrieve_competition()
        self.set_competition(self.competition.id)
        self.button_scrutineer = qt.QPushButton('Enter &Scores')
        self.button_view_scores = qt.QPushButton('&View/Print Results')
        self.button_comps = qt.QPushButton('&Change Competition')
        self.button_comp = qt.QPushButton('&Edit Competition Details')
        self.button_dancers = qt.QPushButton('&Add/Edit Competitors')
        self.button_judges = qt.QPushButton('Add/Edit &Judges')
        self.button_dancerGroups = qt.QPushButton(
            'Define Competitor &Groups && Dances')
        self.button_import = qt.QPushButton('&Import CSV')
        self.button_delete = qt.QPushButton('&Delete Competition')
        self.button_exit = qt.QPushButton('E&xit')
        self.button_scrutineer.clicked.connect(self.enter_scores)
        self.button_view_scores.clicked.connect(self.view_scores)
        self.button_comp.clicked.connect(self.edit_competition)
        self.button_comps.clicked.connect(self.select_competition)
        self.button_dancers.clicked.connect(self.edit_dancers)
        self.button_judges.clicked.connect(self.edit_judges)
        self.button_dancerGroups.clicked.connect(self.select_dancerGroup)
        self.button_import.clicked.connect(self.import_csv)
        self.button_delete.clicked.connect(self.delete_competition)
        self.button_exit.clicked.connect(self.exit_app)
        if self.competition is None:
            self.disable_buttons()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button_scrutineer)
        self.layout.addWidget(self.button_view_scores)
        self.layout.addWidget(self.button_comps)
        self.layout.addWidget(self.button_comp)
        self.layout.addWidget(self.button_dancers)
        self.layout.addWidget(self.button_judges)
        self.layout.addWidget(self.button_dancerGroups)
        self.layout.addWidget(self.button_import)
        self.layout.addWidget(self.button_delete)
        self.layout.addWidget(self.button_exit)
        self.app.setLayout(self.layout)

        self.statusBar()
        self.statusBar().show()
        menubar = qt.QMenuBar(None)
        menubar.setNativeMenuBar(False)
        self.setMenuBar(menubar)

        exitAct = qt.QAction(' &Quit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        exitAct.triggered.connect(self.exit_app)

        fileMenu = qt.QMenu(' &File')
        menubar.addMenu(fileMenu)
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

    def edit_dancerGroup(self, dancerGroup_id):
        dgEditor = DancerGroupEditor(self, dancerGroup_id, self.db)
        dgEditor.show()
        dgEditor.exec_()

    def disable_buttons(self):
        self.button_scrutineer.setEnabled = False
        self.button_comp.setEnabled = False
        self.button_dancers.setEnabled = False
        self.button_judges.setEnabled = False
        self.button_dancerGroups.setEnabled = False
        self.button_import.setEnabled = False
        self.button_delete.setEnabled = False

    def enable_buttons(self):
        self.button_scrutineer.setEnabled = True
        self.button_comp.setEnabled = True
        self.button_dancers.setEnabled = True
        self.button_judges.setEnabled = True
        self.button_dancerGroups.setEnabled = True
        self.button_import.setEnabled = True
        self.button_delete.setEnabled = True

    def get_formatted_date(self, date):
        format_str = '%d %b %Y'
        otherformat_str = '%Y-%m-%d'
        return (datetime.datetime.strftime(datetime.datetime.strptime(('%s' % date)[0:10], otherformat_str).date(), format_str))

    def retrieve_competition(self):
        competitions = self.db.tables.competitions.get_all()
        competitions_list = []
        for comp in competitions:
            competitions_list.append(comp.id)
        if self.settings.lastComp in competitions_list:
            self.competition = self.set_competition(
                self.settings.lastComp)
            return self.competition
        else:
            self.select_competition()
            self.settings.lastComp = self.competition.id
            self.db.tables.settings.update(self.settings)
            return self.competition

    def set_competition(self, comp_id):
        self.competition = self.db.tables.competitions.get(comp_id)
        if self.competition is not None:
            self.label_text = ('<center>Competition:<br><strong>%s</strong><br>%8s<br>%s</center>' % (self.competition.name, self.get_formatted_date(self.competition.eventDate), self.competition.location))
            self.label.setText(self.label_text)
            self.settings.lastComp = self.competition.id
            self.db.tables.settings.update(self.settings)
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
                        'This will delete all data for the given competition. This cannot be undone.')
        if verity:
            #print('Will delete comp %d' % self.competition.id)
            self.db.tables.competitions.remove(self.competition.id)
            self.competition = None
            self.select_competition()
        else:
            print('Nothing deleted')

    def exit_app(self, sender):
        self.db.close_connection()
        print(f"Exit mw {self.app}")
        self.close()
        # sys.exit() # (self.app)

    def new_competition(self):
        #id, name, description, eventDate, deadline, location, competitionType, isChampionship
        today = datetime.date.today()
        competition = sc.Competition(0,'','',today,today,'',0,0)
        self.competition = self.db.tables.competitions.insert(competition)
        self.edit_competition()

def is_float(string):
    try:
        val = float(string)
        return True
    except ValueError:
        return False



class ImportWindow(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(ImportWindow, self).__init__()
        self.db = db
        self.filename = ""
        self.main_window = main_window
        self.competition = self.db.tables.competitions.get(comp_id)
        self.layout = qt.QVBoxLayout()
        self.resize(600,800)
        self.button_choose = qt.QPushButton('Choose &File')
        self.button_choose.clicked.connect(self.choose_file)
        self.label_filename = qt.QLabel('No file selected')
        self.table_columns = qt.QTableWidget()
        self.button_import = qt.QPushButton('&Import')
        self.button_import.clicked.connect(self.import_file)
        self.button_exit = qt.QPushButton('Cancel')
        self.button_exit.clicked.connect(self.hide)
        self.table_columns.setColumnCount(2)
        self.table_columns.setHorizontalHeaderLabels(['Field Name','Column in CSV'])
        self.column_widths = [200,200]
        column = 0
        while column < len(self.column_widths):
            self.table_columns.setColumnWidth(column,self.column_widths[column])
            column += 1
        rowCount = 0
        self.rows = ['First Name', 'Last Name', 'Competitor Number', 'Street Address', 'City', 'State/Province', 'Zip/Postal Code', 'Phone Number',
                        'Email', 'ScotDance Number', 'Birthdate', 'Age', 'Teacher', 'Teacher Email', 'Date Entry was Received',
                        'Primary Competitor Group', 'Secondary Competitor Group', 'Tertiary Competitor Group']
        for row in self.rows:
            self.table_columns.setRowCount(rowCount + 1)
            item_name = qt.QTableWidgetItem(row)
            item_name.setFlags(qc.Qt.NoItemFlags)
            selector_column = qt.QComboBox()
            selector_column.addItem('')
            self.table_columns.setItem(rowCount, 0, item_name)
            self.table_columns.setCellWidget(rowCount, 1, selector_column)
            rowCount += 1

        self.layout.addWidget(self.label_filename)
        self.layout.addWidget(self.button_choose)
        self.layout.addWidget(self.table_columns)
        self.layout.addWidget(self.button_import)
        self.layout.addWidget(self.button_exit)
        self.setLayout(self.layout)

    def choose_file(self):
        options = qt.QFileDialog.Options()
        options |= qt.QFileDialog.DontUseNativeDialog
        self.filename, _ = qt.QFileDialog.getOpenFileName(self,"Select CSV File", "","CSV Files (*.csv)", options=options)
        if self.filename:
            print(self.filename)
        else:
            return
        self.label_filename.setText(self.filename)
        self.reader = self.db.retrieve_csv_keys(self.filename)
        row = 0
        while row < self.table_columns.rowCount():
            selector_column = self.table_columns.cellWidget(row, 1)
            for item in self.reader:
                selector_column.addItem(item)
            row += 1
        #print(self.reader)

    def import_file(self):
        row = 0
        self.column_names = []
        while row < self.table_columns.rowCount():
            selector_column = self.table_columns.cellWidget(row, 1)
            self.column_names.append(selector_column.currentText())
            row += 1
        with open(self.filename, newline='') as csvfile:
                dict_reader = csv.DictReader(csvfile)
                #['First Name', 'Last Name', 'Competitor Number', 'Street Address', 'City', 'State/Province', 'Zip/Postal Code', 'Phone Number',
                #        'Email', 'ScotDance Number', 'Birthdate', 'Age', 'Teacher', 'Teacher Email', 'Date Entry was Received',
                #        'Primary Competitor Group', 'Secondary Competitor Group', 'Tertiary Competitor Group']
                for row in dict_reader:
                    dancer = sc.Dancer(0,'','','','','','','','',0,'','','','','','',0,0,self.competition.id)
                    if self.column_names[0] != '':
                        dancer.firstName = row[self.column_names[0]]
                    if self.column_names[1] != '':
                        dancer.lastName = row[self.column_names[1]]
                    if self.column_names[2] != '':
                        dancer.number = row[self.column_names[2]]
                    if self.column_names[3] != '':
                        dancer.street = row[self.column_names[3]]
                    if self.column_names[4] != '':
                        dancer.city = row[self.column_names[4]]
                    if self.column_names[5] != '':
                        dancer.state = row[self.column_names[5]]
                    if self.column_names[6] != '':
                        dancer.zipCode = row[self.column_names[6]]
                    if self.column_names[7] != '':
                        dancer.phonenum = row[self.column_names[7]]
                    if self.column_names[8] != '':
                        dancer.email = row[self.column_names[8]]
                    if self.column_names[9] != '':
                        dancer.scotDanceNum = row[self.column_names[9]]
                    if self.column_names[10] != '':
                        dancer.birthdate = row[self.column_names[10]]
                    if self.column_names[11] != '':
                        if row[self.column_names[11]].isdigit():
                            dancer.age = int(row[self.column_names[11]])
                    if self.column_names[12] != '':
                        dancer.teacher = row[self.column_names[12]]
                    if self.column_names[13] != '':
                        dancer.teacherEmail = row[self.column_names[13]]
                    if self.column_names[14] != '':
                        dancer.registeredDate = row[self.column_names[14]]
                    if self.column_names[15] != '':
                        dancer_grp1 = row[self.column_names[15]]
                    else:
                        dancer_grp1 = ''
                    if self.column_names[16] != '':
                        dancer_grp2 = row[self.column_names[16]]
                    else:
                        dancer_grp2 = ''
                    if self.column_names[17] != '':
                        dancer_grp3 = row[self.column_names[16]]
                    else:
                        dancer_grp3 = ''
                    dancerGroup_1 = self.db.tables.groups.get_by_abbrev(dancer_grp1)
                    dancerGroup_2 = self.db.tables.groups.get_by_abbrev(dancer_grp2)
                    dancerGroup_3 = self.db.tables.groups.get_by_abbrev(dancer_grp3)
                    dancer = self.db.tables.dancers.insert(dancer)
                    if dancerGroup_1 is not None:
                        self.db.tables.groups.join(dancer.id, dancerGroup_1.id)
                    if dancerGroup_2 is not None:
                        self.db.tables.groups.join(dancer.id, dancerGroup_2.id)
                    if dancerGroup_3 is not None:
                        self.db.tables.groups.join(dancer.id, dancerGroup_3.id)
                    #xxx doesn't seem to put dancers into dancerGroups. Why?
        self.hide()


class Interface:
    def __init__(self, db):
        self.app = qt.QApplication(sys.argv)
        self.main_window = SMainWindow(db)

    def start(self):
        self.main_window.app.show()

    def exit(self):
        rc = self.app.exec_()
        print(f"Exit Interface {rc}")
        sys.exit()
