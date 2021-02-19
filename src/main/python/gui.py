# Interface 1 (GUI) Instructions
import scrudb
from scruclasses import *
import datetime
from pathlib import Path
import os
import csv
from PyQt5 import QtWidgets, QtGui, QtCore, QtPrintSupport
import sys
from PyQt5.QtWidgets import *
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette
from fpdf import FPDF

class SPushButton(QPushButton):
    def __init__(self, text, compSelector, identifier):
        super(SPushButton, self).__init__(text)
        self.identifier = identifier
        self.compSelector = compSelector

    def on_button_clicked(self):
        self.compSelector.set_competition(self.identifier)
        #alert = QMessageBox()
        #alert.setText(self.identifier)
        #alert.exec_()

class SDGPushButton(QPushButton):
    def __init__(self, text, dgSelector, identifier):
        super(SDGPushButton, self).__init__(text)
        self.identifier = identifier
        self.dgSelector = dgSelector

    def on_button_clicked(self):
        self.dgSelector.set_dancer_group(self.identifier)
        #alert = QMessageBox()
        #alert.setText(self.identifier)
        #alert.exec_()

class ResultsGroupBox(QGroupBox):
    def __init__(self, text, event_id):
        super(ResultsGroupBox, self).__init__(text)
        self.event = scrudb.retrieve_event(event_id)
        self.layout = QVBoxLayout()
        self.scores = scrudb.retrieve_scores_by_event(self.event.id)
        self.scores.sort(key=self.get_score_value, reverse=True)
        #How to calc/show results from multiple judges? xxx
        place = 1
        previous_score = 0
        self.placing_scores = {}
        self.placing = [0,0,0,0,0,0,0]
        self.print_label = ''
        for score in self.scores:
            if score.score < previous_score:
                place += 1
            if ((place == 1) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(1).points
                self.placing[1] = score.dancer
            elif ((place == 2) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(2).points
                self.placing[2] = score.dancer
            elif ((place == 3) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(3).points
                self.placing[3] = score.dancer
            elif ((place == 4) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(4).points
                self.placing[4] = score.dancer
            elif ((place == 5) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(5).points
                self.placing[5] = score.dancer
            elif ((place == 6) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(6).points
                self.placing[6] = score.dancer

            if ((place > self.event.numPlaces) or (score.score == 0)):
                break

            dancer = scrudb.retrieve_dancer(score.dancer)
            previous_score = score.score
            label_score = QLabel('%d. (%s) %s %s - %s, %s' % (place, dancer.number,
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
        self.event = scrudb.retrieve_event(event_id)
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.update()
        self.scores = scrudb.retrieve_scores_by_event(self.event.id)
        self.scores.sort(key=self.get_score_value, reverse=True)
        place = 1
        previous_score = 0
        self.placing_scores = {}
        self.placing = [0,0,0,0,0,0,0]
        for score in self.scores:
            if score.score < previous_score:
                place += 1
            if ((place == 1) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(1).points
                self.placing[1] = score.dancer
            elif ((place == 2) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(2).points
                self.placing[2] = score.dancer
            elif ((place == 3) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(3).points
                self.placing[3] = score.dancer
            elif ((place == 4) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(4).points
                self.placing[4] = score.dancer
            elif ((place == 5) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(5).points
                self.placing[5] = score.dancer
            elif ((place == 6) and (score.score > 0)):
                self.placing_scores[score.dancer] = scrudb.retrieve_placeValue(6).points
                self.placing[6] = score.dancer
            if ((place > self.event.numPlaces) or (score.score == 0)):
                break
            dancer = scrudb.retrieve_dancer(score.dancer)
            previous_score = score.score
            label_score = QLabel('%d. (%s) %s %s - %s, %s' % (place, dancer.number,
                                                    dancer.firstName, dancer.lastName, dancer.city, dancer.state))
            self.layout.addWidget(label_score)
        self.update()

class ResultsViewWindow(QDialog):
    def __init__(self, mainWindow, comp_id):
        super(ResultsViewWindow, self).__init__()
        self.mainWindow = mainWindow
        self.comp_id = comp_id
        self.competition = scrudb.retrieve_competition(self.comp_id)
        self.layout = QVBoxLayout()
        self.dancerGroups = scrudb.retrieve_dancerGroups_by_competition(self.comp_id)
        self.big_layout = QVBoxLayout()
        self.big_groupBox = QGroupBox()
        self.label_group = QLabel('Viewing results for group:')
        self.layout.addWidget(self.label_group)
        self.selector_dancerGroup = QComboBox()
        self.groupBox_scores = QGroupBox()
        self.groupBox_scores_layout = QGridLayout()
        self.dancerGroup_ids = []
        for dancerGroup in self.dancerGroups:
            self.selector_dancerGroup.addItem(dancerGroup.name)
            self.dancerGroup_ids.append(dancerGroup.id)
        self.selector_dancerGroup.currentIndexChanged.connect(self.new_group_selected)
        self.layout.addWidget(self.selector_dancerGroup)
        self.dancerGroup = scrudb.retrieve_dancerGroup(self.dancerGroup_ids[self.selector_dancerGroup.currentIndex()])
        self.events = scrudb.retrieve_events_by_dancerGroup(self.dancerGroup.id)
        self.dancers = scrudb.retrieve_dancers_by_dancerGroup(self.dancerGroup.id)
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
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1, Qt.AlignRight)
                n += 1
            else:
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1,Qt.AlignLeft)
            self.print_label += ('%s::%s:: ::' % (event.name, results_box.get_print_label()))
            if (event.countsForOverall == 1):
                #print(event.name)
                event_placing_scores = results_box.get_placing_scores()
                for dancer, points in event_placing_scores.items():
                    #print('(%d) - [%6.2f]' % (dancer, points))
                    self.overall_scores[dancer] += points
            i += 1

        self.overall_scores_sorted = [(k, self.overall_scores[k]) for k in sorted(self.overall_scores, key=self.overall_scores.get, reverse=True)]
        self.groupBox_overall = QGroupBox('Overall Results for %s' % self.dancerGroup.name)
        self.groupBox_overall_layout = QVBoxLayout()
        self.print_label += ('Overall Results for %s::' % self.dancerGroup.name)
        place = 1
        for dancer_id, points in self.overall_scores_sorted:
            if points <= 0:
                break
            dancer = scrudb.retrieve_dancer(dancer_id)
            label_overall = QLabel('%d. (%s) %s %s - %s, %s: %d points' % (place, dancer.number,
                                                    dancer.firstName, dancer.lastName, dancer.city, dancer.state, points))
            self.groupBox_overall_layout.addWidget(label_overall)
            self.print_label += ('%s::' % label_overall.text())
            place += 1

        self.groupBox_scores.setLayout(self.groupBox_scores_layout)
        self.layout.addWidget(self.groupBox_scores)
        self.groupBox_overall.setLayout(self.groupBox_overall_layout)
        self.layout.addWidget(self.groupBox_overall)
        self.button_exit = QPushButton('E&xit')
        self.button_exit.clicked.connect(self.cancel_button)


        self.big_groupBox.setLayout(self.layout)

        self.button_print = QPushButton('Print Results')
        self.button_pdf = QPushButton('Save PDF')
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
        textedit = QTextEdit(doc_text)
        dialog = QtPrintSupport.QPrintDialog()
        if dialog.exec_() == QDialog.Accepted:
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
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.filename, _ = QFileDialog.getSaveFileName(self,"Save File", "","PDF Files (*.pdf)", options=options)
        if self.filename:
            if (self.filename[-4:].lower() != '.pdf'):
                self.filename += '.pdf'
            print(self.filename)
            self.pdf.output(self.filename)
        else:
            return


    def new_group_selected(self):
        self.dancerGroup = scrudb.retrieve_dancerGroup(self.dancerGroup_ids[self.selector_dancerGroup.currentIndex()])
        for i in reversed(range(self.groupBox_scores_layout.count())):
            if isinstance(self.groupBox_scores_layout.itemAt(i).widget(),ResultsGroupBox):
                self.groupBox_scores_layout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.groupBox_overall_layout.count())):
            self.groupBox_overall_layout.itemAt(i).widget().setParent(None)
        self.update()
        self.events = scrudb.retrieve_events_by_dancerGroup(self.dancerGroup.id)
        self.dancers = scrudb.retrieve_dancers_by_dancerGroup(self.dancerGroup.id)
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
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1, Qt.AlignRight)
                n += 1
            else:
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1,Qt.AlignLeft)
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
            dancer = scrudb.retrieve_dancer(dancer_id)
            label_overall = QLabel('%d. (%s) %s %s - %s, %s: %d points' % (place, dancer.number,
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

class ScoreEntryWindow(QDialog):
    def __init__(self, mainWindow, comp_id):
        super(ScoreEntryWindow, self).__init__()
        self.mainWindow = mainWindow
        self.comp_id = comp_id
        self.competition = scrudb.retrieve_competition(comp_id)
        self.changes_made = False
        #self.resize(1680, 1000)
        self.layout = QVBoxLayout()
        self.events = scrudb.retrieve_events_by_competition(self.comp_id)
        self.label_event = QLabel('Event')
        self.selector_event = QComboBox()
        self.event_ids = []
        for event in self.events:
            self.selector_event.addItem(event.name)
            self.event_ids.append(event.id)
        self.selector_event.currentIndexChanged.connect(self.new_event_selected)
        self.event = scrudb.retrieve_event(self.event_ids[self.selector_event.currentIndex()])
        self.previous_event = self.selector_event.currentIndex()
        self.selector_judge = QComboBox()
        self.judge_ids = [0]
        self.judges = scrudb.retrieve_judges_by_competition(self.comp_id)
        self.selector_judge.addItem('')
        for judge in self.judges:
            self.selector_judge.addItem('%s %s' % (judge.firstName, judge.lastName))
            self.judge_ids.append(judge.id)
        self.table_scores = QTableWidget()
        self.headers = ['Num','Score','id']
        self.table_scores.setColumnCount(len(self.headers))
        self.table_scores.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [60,80,0]
        column = 0
        while column < len(self.column_widths):
            self.table_scores.setColumnWidth(column,self.column_widths[column])
            column += 1
        row = 0
        self.dancers = scrudb.retrieve_dancers_by_dancerGroup_ordered_by_number(self.event.dancerGroup)
        self.scores = {}
        for dancer in self.dancers:
            item_dancer_num = QTableWidgetItem(dancer.number)
            item_dancer_num.setFlags(Qt.NoItemFlags)
            if (scrudb.exists_scores_for_event(self.event.id)):
                score = scrudb.retrieve_score_by_event_and_dancer(self.event.id, dancer.id)
                if (score != None):
                    item_dancer_score = QTableWidgetItem('%6.0f' % score.score)
                else:
                    item_dancer_score = QTableWidgetItem('')
            else:
                item_dancer_score = QTableWidgetItem('')
            item_dancer_id = QTableWidgetItem('%d' % dancer.id)


            self.table_scores.setRowCount(row+1)
            self.table_scores.setItem(row, 0, item_dancer_num)
            self.table_scores.setItem(row, 1, item_dancer_score)
            self.table_scores.setItem(row, 2, item_dancer_id)

            row += 1
        self.table_scores.setColumnHidden(2,True)
        #xxx is there a way to make a column unselectable? If so, make the dancer_num column such
        self.table_scores.itemChanged.connect(self.item_changed)

        self.results_box = ResultsGroupBox('Results:', self.event.id)

        self.button_save = QPushButton('&Save')
        self.button_save.clicked.connect(self.save_button)
        self.button_exit = QPushButton('E&xit')
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
        self.event = scrudb.retrieve_event(self.event_ids[self.selector_event.currentIndex()])
        self.previous_event = self.selector_event.currentIndex()
        row = 0
        self.dancers = scrudb.retrieve_dancers_by_dancerGroup_ordered_by_number(self.event.dancerGroup)
        self.scores = {}
        for dancer in self.dancers:
            item_dancer_num = QTableWidgetItem(dancer.number)
            item_dancer_num.setFlags(Qt.NoItemFlags)
            if (scrudb.exists_scores_for_event(self.event.id)):
                score = scrudb.retrieve_score_by_event_and_dancer(self.event.id, dancer.id)
                if (score != None):
                    item_dancer_score = QTableWidgetItem('%6.0f' % score.score)
                else:
                    item_dancer_score = QTableWidgetItem('')
            else:
                item_dancer_score = QTableWidgetItem('')
            item_dancer_id = QTableWidgetItem('%d' % dancer.id)


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
            scrudb.rm_scores_by_event_and_judge(self.event.id, judge_id)
        else:
            scrudb.rm_scores_by_event(self.event.id)
        while row < self.table_scores.rowCount():
            item_dancer_id = self.table_scores.item(row, 2)
            item_dancer_score = self.table_scores.item(row, 1)
            if (self.is_float(item_dancer_score.text())):
                #print ('[%6.2f]' % float(item_dancer_score.text()))
                dancer_id = int(item_dancer_id.text())
                dancer_score = float(item_dancer_score.text())
                score = Score(0, dancer_id, self.event.id, judge_id,
                              self.event.competition, dancer_score)
                score = scrudb.insert_score(score)
                #id, dancer, event, judge, competition, score

            row += 1
        #xxxs needs to take judge into account for championships
        self.changes_made = False
        self.results_box.select_event(self.event.id)

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


class DancerEditor(QDialog):
    def __init__(self, mainWindow, comp_id):
        super(DancerEditor, self).__init__()
        self.mainWindow = mainWindow
        self.comp_id = comp_id
        self.changes_made = False
        self.resize(1680,1000)
        self.layout = QVBoxLayout()
        self.dancers = scrudb.retrieve_dancers_by_competition(comp_id)
        self.table_dancers = QTableWidget()
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
            item_first_name = QTableWidgetItem(dancer.firstName)
            item_last_name = QTableWidgetItem(dancer.lastName)
            item_number = QTableWidgetItem(dancer.number)

            selector_dancerCat = QComboBox()
            dancerCats = scrudb.retrieve_dancerCats()
            for dancerCat in dancerCats:
                selector_dancerCat.addItem(dancerCat.name)
                #print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
            if (dancer.dancerCat != None):
                selector_dancerCat.setCurrentIndex(dancer.dancerCat)
            else:
                selector_dancerCat.setCurrentIndex(0)


            dancerCat = scrudb.retrieve_dancerCat(dancer.dancerCat)
            if (dancerCat != None):
                dancerCat_name = dancerCat.name
            else:
                dancerCat_name = ''
            item_cat = QTableWidgetItem(dancerCat_name)
            item_cat_id = QTableWidgetItem(dancer.dancerCat)


            dancer_groups = scrudb.retrieve_dancerGroups_by_dancer(dancer.id)
            dancer_group_list = ''
            for group in dancer_groups:
                if (dancer_group_list != ''):
                    dancer_group_list += ', '
                dancer_group_list += group.abbrev
            item_groups = QTableWidgetItem(dancer_group_list)

            item_scotdance = QTableWidgetItem(dancer.scotDanceNum)
            item_address = QTableWidgetItem(dancer.street)
            item_city = QTableWidgetItem(dancer.city)
            item_state = QTableWidgetItem(dancer.state)
            item_zipCode = QTableWidgetItem(dancer.zipCode)

            #if ((dancer.birthdate != '') and (dancer.birthdate != None)):
            #    item_birthdate = QTableWidgetItem(self.get_formatted_date(dancer.birthdate))
            #else:
            #    item_birthdate = QTableWidgetItem('')
            item_birthdate = QTableWidgetItem(dancer.birthdate)

            if (type(dancer.age) == int):
                item_age = QTableWidgetItem(('%d' % dancer.age))
            elif (dancer.age != None):
                item_age = QTableWidgetItem(dancer.age)
            else:
                item_age = QTableWidgetItem('')

            #if ((dancer.registeredDate != '') and (dancer.registeredDate != None)):
            #    item_entryrcvd = QTableWidgetItem(self.get_formatted_date(dancer.registeredDate))
            #else:
            #    item_entryrcvd = QTableWidgetItem('')
            item_entryrcvd = QTableWidgetItem(dancer.registeredDate)

            item_phonenum = QTableWidgetItem(dancer.phonenum)
            item_email = QTableWidgetItem(dancer.email)
            item_teacher = QTableWidgetItem(dancer.teacher)
            item_teacherEmail = QTableWidgetItem(dancer.teacherEmail)
            item_dancer_id = QTableWidgetItem(('%d' % dancer.id))

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
        self.newButton = QPushButton('&New Competitor')
        self.newButton.clicked.connect(self.new_dancer)
        self.layout.addWidget(self.newButton)
        self.deleteButton = QPushButton('&Delete Selected Competitor')
        self.deleteButton.clicked.connect(self.delete_dancer)
        self.layout.addWidget(self.deleteButton)
        self.saveButton = QPushButton('&Save')
        self.saveButton.clicked.connect(self.save_button)
        self.layout.addWidget(self.saveButton)
        self.exitButton = QPushButton('E&xit')
        self.exitButton.clicked.connect(self.cancel_button)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(Qt.ApplicationModal)
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
        dancer = Dancer(0,'','','','','','','','',0,'','','','','','',0,0,self.comp_id)
        dancer = scrudb.insert_dancer(dancer)
        self.table_dancers.insertRow(row)
        item_first_name = QTableWidgetItem(dancer.firstName)
        item_last_name = QTableWidgetItem(dancer.lastName)
        item_number = QTableWidgetItem(dancer.number)

        selector_dancerCat = QComboBox()
        dancerCats = scrudb.retrieve_dancerCats()
        for dancerCat in dancerCats:
            selector_dancerCat.addItem(dancerCat.name)
            #print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
        if (dancer.dancerCat != None):
            selector_dancerCat.setCurrentIndex(dancer.dancerCat)
        else:
            selector_dancerCat.setCurrentIndex(0)


        dancerCat = scrudb.retrieve_dancerCat(dancer.dancerCat)
        if (dancerCat != None):
            dancerCat_name = dancerCat.name
        else:
            dancerCat_name = ''
        item_cat = QTableWidgetItem(dancerCat_name)
        item_cat_id = QTableWidgetItem(dancer.dancerCat)


        dancer_groups = scrudb.retrieve_dancerGroups_by_dancer(dancer.id)
        dancer_group_list = ''
        for group in dancer_groups:
            if (dancer_group_list != ''):
                dancer_group_list += ', '
            dancer_group_list += group.abbrev
        item_groups = QTableWidgetItem(dancer_group_list)

        item_scotdance = QTableWidgetItem(dancer.scotDanceNum)
        item_address = QTableWidgetItem(dancer.street)
        item_city = QTableWidgetItem(dancer.city)
        item_state = QTableWidgetItem(dancer.state)
        item_zipCode = QTableWidgetItem(dancer.zipCode)

        #if ((dancer.birthdate != '') and (dancer.birthdate != None)):
        #    item_birthdate = QTableWidgetItem(self.get_formatted_date(dancer.birthdate))
        #else:
        #    item_birthdate = QTableWidgetItem('')
        item_birthdate = QTableWidgetItem(dancer.birthdate)

        if (type(dancer.age) == int):
            item_age = QTableWidgetItem(('%d' % dancer.age))
        elif (dancer.age != None):
            item_age = QTableWidgetItem(dancer.age)
        else:
            item_age = QTableWidgetItem('')

        #if ((dancer.registeredDate != '') and (dancer.registeredDate != None)):
        #    item_entryrcvd = QTableWidgetItem(self.get_formatted_date(dancer.registeredDate))
        #else:
        #    item_entryrcvd = QTableWidgetItem('')
        item_entryrcvd = QTableWidgetItem(dancer.registeredDate)

        item_phonenum = QTableWidgetItem(dancer.phonenum)
        item_email = QTableWidgetItem(dancer.email)
        item_teacher = QTableWidgetItem(dancer.teacher)
        item_teacherEmail = QTableWidgetItem(dancer.teacherEmail)
        item_dancer_id = QTableWidgetItem(('%d' % dancer.id))

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
        self.table_dancers.scrollToItem(self.table_dancers.item(row, 0))
        self.changes_made = True

    def delete_dancer(self, sender=None):
        row = self.table_dancers.currentRow()
        if (row != None):
            dancer = scrudb.retrieve_dancer(int(self.table_dancers.item(row, 17).text()))
            if (dancer != None):
                verity = verify(('Are you sure you want to delete dancer %s %s?' % (dancer.firstName, dancer.lastName)),
                                'This will delete all data for the given competitor. This cannot be undone.')
                if verity:
                    print('Will delete dancer %d' % dancer.id)
                    scrudb.rm_dancer(dancer.id)
                    self.table_dancers.removeRow(row)
                else:
                    print('Nothing deleted')

    def save_button(self, sender=None):
        row = 0
        while row < self.table_dancers.rowCount():
            dancer_id = int(self.table_dancers.item(row, 17).text())
            dancer = scrudb.retrieve_dancer(dancer_id)
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
            if (dancer_age.isdigit()):
                dancer.age = int(dancer_age)
            dancer.registeredDate = self.table_dancers.item(row, 12).text()
            dancer.phonenum = self.table_dancers.item(row, 13).text()
            dancer.email = self.table_dancers.item(row, 14).text()
            dancer.teacher = self.table_dancers.item(row, 15).text()
            dancer.teacherEmail = self.table_dancers.item(row, 16).text()

            selector_dancerCat = self.table_dancers.cellWidget(row, 3)
            if (selector_dancerCat.currentIndex() > 0):
                dancer.dancerCat = selector_dancerCat.currentIndex()
            #item_cat = self.table_dancers.item(row, 18).text()
            #if (item_cat.isdigit()):
            #    dancer.dancerCat = int(item_cat)

            dancer_groups_text = self.table_dancers.item(row, 4).text()
            dancer_groups_text = ''.join(dancer_groups_text.split())
            if dancer_groups_text != '':
                dancer_groups_abbrev = dancer_groups_text.split(',')
                already_in_groups = scrudb.retrieve_dancerGroups_by_dancer(dancer_id)
                already_in_abbrevs = []
                for group in already_in_groups:
                    if group != None:
                        already_in_abbrevs.append(group.abbrev)
                for abbrev in dancer_groups_abbrev:
                    if abbrev in already_in_abbrevs:
                        print('Dancer %s %s is already in group [%s] and should remain' % (dancer.firstName, dancer.lastName, abbrev))
                    else:
                        print('Dancer %s %s is not in group [%s] and should be added' % (dancer.firstName, dancer.lastName, abbrev))
                        dancerGroup = scrudb.retrieve_dancerGroup_by_abbrev(abbrev)
                        if dancerGroup != None:
                            scrudb.insert_dancerGroupJoin(dancer.id, dancerGroup.id)
                for abbrev in already_in_abbrevs:
                    if abbrev in dancer_groups_abbrev:
                        print('Dancer %s %s is already in group [%s] and should remain' % (dancer.firstName, dancer.lastName, abbrev))
                    else:
                        print('Dancer %s %s is in group [%s] and should be removed' % (dancer.firstName, dancer.lastName, abbrev))
                        dancerGroup = scrudb.retrieve_dancerGroup_by_abbrev(abbrev)
                        if dancerGroup != None:
                            scrudb.rm_dancerGroupJoin_by_dancer_and_dancerGroup(dancer.id, dancerGroup.id)

            scrudb.update_dancer(dancer)

            row += 1
        self.changes_made = False

    def get_formatted_date(self, date):
        format_str = '%d %b %Y'
        otherformat_str = '%Y-%m-%d'
        return (datetime.datetime.strftime(datetime.datetime.strptime(('%s' % date)[0:10], otherformat_str).date(), format_str))

class DancerGroupEditor(QDialog):
    def __init__(self, mainWindow, dancerGroup_id):
        super(DancerGroupEditor, self).__init__()
        self.mainWindow = mainWindow
        self.dancerGroup = scrudb.retrieve_dancerGroup(dancerGroup_id)
        self.changes_made = False
        #id, name, abbrev, ageMin, ageMax, dancerCat, competition
        self.layout = QVBoxLayout()
        self.label_name = QLabel('Group Name:')
        self.field_name = QLineEdit(self.dancerGroup.name)
        self.label_abbrev = QLabel('Abbreviation:')
        self.field_abbrev = QLineEdit(self.dancerGroup.abbrev)
        self.label_ageMin = QLabel('Minimum Age:')
        self.field_ageMin = QLineEdit('%d' % self.dancerGroup.ageMin)
        self.label_ageMax = QLabel('Maxiumum Age:')
        self.field_ageMax = QLineEdit('%d' % self.dancerGroup.ageMax)
        self.selector_dancerCat = QComboBox()
        dancerCats = scrudb.retrieve_dancerCats()
        for dancerCat in dancerCats:
            self.selector_dancerCat.addItem(dancerCat.name)
            #print('Category: %d [%s]' % (dancerCat.id, dancerCat.name))
        if (self.dancerGroup.dancerCat != None):
            self.selector_dancerCat.setCurrentIndex(self.dancerGroup.dancerCat)
        else:
            selector_dancerCat.setCurrentIndex(0)
        self.dancers_in_group = scrudb.retrieve_dancers_by_dancerGroup(dancerGroup_id)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer != None:
                self.dancer_ids.append(dancer.id)
        self.table_dancers = QTableWidget()
        self.headers = ['', 'Num','First Name','Last Name','id']
        self.table_dancers.setColumnCount(len(self.headers))
        self.table_dancers.setHorizontalHeaderLabels(self.headers)
        self.column_widths = [20, 40, 120, 150, 0]
        all_dancers = scrudb.retrieve_dancers_by_competition(self.dancerGroup.competition)
        column = 0
        while column < len(self.column_widths):
            self.table_dancers.setColumnWidth(column,self.column_widths[column])
            column += 1
        row = 0
        for dancer in all_dancers:
            if dancer != None:
                item_first_name = QTableWidgetItem(dancer.firstName)
                item_last_name = QTableWidgetItem(dancer.lastName)
                item_number = QTableWidgetItem(dancer.number)
                checkbox_in_group = QCheckBox()
                if (dancer.id in self.dancer_ids):
                    checkbox_in_group.setCheckState(2)
                else:
                    checkbox_in_group.setCheckState(0)
                checkbox_in_group.stateChanged.connect(self.item_changed)
                item_dancer_id = QTableWidgetItem('%d' % dancer.id)

                self.table_dancers.setRowCount(row+1)
                self.table_dancers.setCellWidget(row, 0, checkbox_in_group)
                self.table_dancers.setItem(row, 1, item_number)
                self.table_dancers.setItem(row, 2, item_first_name)
                self.table_dancers.setItem(row, 3, item_last_name)
                self.table_dancers.setItem(row, 4, item_dancer_id)

                row += 1

        self.table_dancers.setColumnHidden(4, True)

        self.table_events = QTableWidget()
        self.events_headers = ['Event','In Overall','Places','Stamp','id']
        self.table_events.setColumnCount(len(self.events_headers))
        self.table_events.setHorizontalHeaderLabels(self.events_headers)
        self.column_widths = [260, 40, 60, 40, 0]
        column = 0
        while column < len(self.column_widths):
            self.table_events.setColumnWidth(column,self.column_widths[column])
            column += 1
        self.table_events.setColumnHidden(4, True)
        self.events = scrudb.retrieve_events_by_dancerGroup(self.dancerGroup.id)
        row = 0
        #id, name, dancerGroup, dance, competition, countsForOverall, numPlaces, earnsStamp
        for event in self.events:
            if event != None:
                #dance = scrudb.retrieve_dance(event.dance)
                #item_name = QTableWidgetItem(dance.name)
                dances = scrudb.retrieve_dances()
                selector_dance = QComboBox()
                index = 999999
                for dance in dances:
                    if (dance[0] < index):
                        index = dance[0]
                    selector_dance.addItem(dance[1])
                if (event.dance != None):
                    selector_dance.setCurrentIndex(event.dance - index)
                else:
                    selector_dance.setCurrentIndex(0)
                selector_dance.currentIndexChanged.connect(self.item_changed)
                item_places = QTableWidgetItem('%d' % event.numPlaces)
                checkbox_counts = QCheckBox()
                if (event.countsForOverall == 1):
                    checkbox_counts.setCheckState(2)
                else:
                    checkbox_counts.setCheckState(0)
                checkbox_counts.stateChanged.connect(self.item_changed)
                checkbox_stamp = QCheckBox()
                if (event.earnsStamp == 1):
                    checkbox_stamp.setCheckState(2)
                else:
                    checkbox_stamp.setCheckState(0)
                checkbox_stamp.stateChanged.connect(self.item_changed)
                item_event_id = QTableWidgetItem('%d' % event.id)

                self.table_events.setRowCount(row+1)
                #self.table_events.setItem(row, 0, item_name)
                self.table_events.setCellWidget(row, 0, selector_dance)
                self.table_events.setItem(row, 2, item_places)
                self.table_events.setCellWidget(row, 1, checkbox_counts)
                self.table_events.setCellWidget(row, 3, checkbox_stamp)
                self.table_events.setItem(row, 4, item_event_id)

                row += 1
        self.groupBox = QGroupBox('Events')
        self.groupBox_layout = QVBoxLayout()
        self.groupBox_layout.addWidget(self.table_events)
        self.button_add_event = QPushButton('Add Event')
        self.button_add_event.clicked.connect(self.new_event)
        self.groupBox_layout.addWidget(self.button_add_event)
        self.button_delete_event = QPushButton('Remove Event')
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

        self.button_save = QPushButton('&Save')
        self.button_save.clicked.connect(self.save_button)
        self.button_delete_group = QPushButton('&Delete')
        self.button_delete_group.clicked.connect(self.delete_group)
        self.button_exit = QPushButton('E&xit')
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
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(self.layout)


    def save_button(self, sender=None):
        self.dancerGroup.name = self.field_name.text()
        self.dancerGroup.abbrev = self.field_abbrev.text()
        if (self.field_ageMin.text().isdigit()):
            self.dancerGroup.ageMin = int(self.field_ageMin.text())
        if (self.field_ageMax.text().isdigit()):
            self.dancerGroup.ageMax = int(self.field_ageMax.text())
        self.dancerGroup.dancerCat = self.selector_dancerCat.currentIndex()
        scrudb.update_dancerGroup(self.dancerGroup)
        row = 0
        self.dancers_in_group = scrudb.retrieve_dancers_by_dancerGroup(self.dancerGroup.id)
        self.dancer_ids = []
        for dancer in self.dancers_in_group:
            if dancer != None:
                self.dancer_ids.append(dancer.id)
        while row < self.table_dancers.rowCount():
            checkbox_in_group = self.table_dancers.cellWidget(row, 0)
            dancer_id_text = self.table_dancers.item(row,4).text()
            if (dancer_id_text != ''):
                dancer_id = int(dancer_id_text)
            else:
                dancer_id = 9999999999999999999
            if ((checkbox_in_group.checkState() == 0) and (dancer_id in self.dancer_ids)):
                print('dancer [%s] in row %d is in group but should be removed' % (dancer_id_text, row))
                scrudb.rm_dancerGroupJoin_by_dancer_and_dancerGroup(dancer_id,self.dancerGroup.id)
            elif ((checkbox_in_group.checkState() == 2) and (dancer_id not in self.dancer_ids)):
                print('dancer [%s] in row %d is not in group but should be added' % (dancer_id_text, row))
                scrudb.insert_dancerGroupJoin(dancer_id,self.dancerGroup.id)

            row += 1

        row = 0
        while row < self.table_events.rowCount():
            event_id = int(self.table_events.item(row, 4).text())
            event = scrudb.retrieve_event(event_id)
            selector_dance = self.table_events.cellWidget(row, 0)
            event.name = ('%s - %s' % (self.dancerGroup.name, selector_dance.currentText()))
            print(event.name)
            dances = scrudb.retrieve_dances()
            index = 999999
            for dance in dances:
                if (dance[0] < index):
                    index = dance[0]
            event.dance = (selector_dance.currentIndex() + index)
            if (self.table_events.item(row, 2).text().isdigit()):
                event.numPlaces = int(self.table_events.item(row, 2).text())
            checkbox_counts = self.table_events.cellWidget(row, 1)
            if (checkbox_counts.checkState() == 2):
                event.countsForOverall = 1
            else:
                event.countsForOverall = 0
            checkbox_stamp = self.table_events.cellWidget(row, 3)
            if (checkbox_stamp.checkState() == 2):
                event.earnsStamp = 1
            else:
                event.earnsStamp = 0

            scrudb.update_event(event)

            row += 1
        self.changes_made = False

    def new_event(self, sender=None):
        event = Event(0,'',self.dancerGroup.id,0,self.dancerGroup.competition,1,6,1)
        event = scrudb.insert_event(event)
        row = self.table_events.rowCount()
        #id, name, dancerGroup, dance, competition, countsForOverall, numPlaces, earnsStamp
        self.table_events.insertRow(row)
        dances = scrudb.retrieve_dances()
        selector_dance = QComboBox()
        for dance in dances:
            selector_dance.addItem(dance[1])
        selector_dance.setCurrentIndex(0)
        selector_dance.currentIndexChanged.connect(self.item_changed)
        item_places = QTableWidgetItem('%d' % event.numPlaces)
        checkbox_counts = QCheckBox()
        if (event.countsForOverall == 1):
            checkbox_counts.setCheckState(2)
        else:
            checkbox_counts.setCheckState(0)
        checkbox_counts.stateChanged.connect(self.item_changed)
        checkbox_stamp = QCheckBox()
        if (event.earnsStamp == 1):
            checkbox_stamp.setCheckState(2)
        else:
            checkbox_stamp.setCheckState(0)
        checkbox_stamp.stateChanged.connect(self.item_changed)
        item_event_id = QTableWidgetItem('%d' % event.id)

        self.table_events.setCellWidget(row, 0, selector_dance)
        self.table_events.setItem(row, 2, item_places)
        self.table_events.setCellWidget(row, 1, checkbox_counts)
        self.table_events.setCellWidget(row, 3, checkbox_stamp)
        self.table_events.setItem(row, 4, item_event_id)
        self.changes_made = True

    def delete_event(self, sender=None):
        row = self.table_events.currentRow()
        if (row != None):
            event = scrudb.retrieve_event(int(self.table_events.item(row, 4).text()))
            dance = scrudb.retrieve_dance(event.dance)
            if (event != None):
                verity = verify(('Are you sure you want to delete event %s %s?' % (self.dancerGroup.name, dance.name)),
                                'This will delete all data for the given event and all scores associated with this event. This cannot be undone.')
                if verity:
                    print('Will delete event %d' % event.id)
                    scrudb.rm_event(event.id)
                    self.table_events.removeRow(row)
                else:
                    print('Nothing deleted')

    def delete_group(self, sender=None):
        verity = verify(('Are you sure you want to delete competitor group %s?' % self.dancerGroup.name),
                                'This will delete all data for the given group and all scores associated with this group. This cannot be undone.')
        if verity:
            print('Will delete group %d' % dancerGroup.id)
            scrudb.rm_dancerGroup(dancerGroup.id)
            self.hide()
        else:
            print('Nothing deleted')

    def exit_button(self, sender=None):
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

    def item_changed(self, sender=None):
        print('Item changed')
        self.changes_made = True

class CompetitionEditor(QDialog):
    def __init__(self, mainWindow, comp_id):
        super(CompetitionEditor, self).__init__()
        self.mainWindow = mainWindow
        self.competition = scrudb.retrieve_competition(comp_id)
        self.changes_made = False
        self.layout = QVBoxLayout()
        self.label_name = QLabel('Name:')
        self.field_name = QLineEdit(self.competition.name)
        self.label_location = QLabel('Location:')
        self.field_location = QLineEdit(self.competition.location)
        self.date_comp_event = QDate.fromString(self.competition.eventDate, 'yyyy-MM-dd 00:00:00')
        self.date_comp_deadline = QDate.fromString(self.competition.deadline, 'yyyy-MM-dd 00:00:00')
        self.label_comp_eventDate = QLabel('Event date:')
        self.calendar_comp_event = QCalendarWidget()
        self.calendar_comp_event.setSelectedDate(self.date_comp_event)
        self.label_comp_deadline = QLabel('Registration deadline:')
        self.calendar_comp_deadline = QCalendarWidget()
        self.calendar_comp_deadline.setSelectedDate(self.date_comp_deadline)
        self.selector_compType = QComboBox()
        compTypes = scrudb.retrieve_competitionTypes()
        for compType in compTypes:
            self.selector_compType.addItem(compType.name)
        self.selector_compType.setCurrentIndex(self.competition.competitionType)

        self.field_name.textChanged.connect(self.item_changed)
        self.field_location.textChanged.connect(self.item_changed)
        self.selector_compType.currentIndexChanged.connect(self.item_changed)
        self.calendar_comp_event.selectionChanged.connect(self.item_changed)
        self.calendar_comp_deadline.selectionChanged.connect(self.item_changed)

        self.button_save = QPushButton('&Save')
        self.button_save.clicked.connect(self.save)
        self.button_exit = QPushButton('E&xit')
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
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(self.layout)

    def save(self):
        self.competition.name = self.field_name.text()
        self.competition.location = self.field_location.text()
        self.competition.eventDate = self.calendar_comp_event.selectedDate().toString('yyyy-MM-dd 00:00:00')
        self.competition.deadline = self.calendar_comp_deadline.selectedDate().toString('yyyy-MM-dd 00:00:00')
        self.competition.competitionType = self.selector_compType.currentIndex()
        scrudb.update_competition(self.competition)
        self.mainWindow.set_competition(self.competition.id)
        self.changes_made = False

    def exit_button(self, sender=None):
        if (self.changes_made):
            saveResult = ask_save()
        else:
            saveResult = 'discard'

        if (saveResult == 'discard'):
            self.hide()
        elif (saveResult == 'save'):
            self.save()
            self.hide()
        else:
            pass

    def item_changed(self, sender=None):
        print('Item changed')
        self.changes_made = True


class DancerGroupMenu(QDialog):
    def __init__(self, mainWindow, comp_id):
        super(DancerGroupMenu, self).__init__()
        self.mainWindow = mainWindow
        self.comp_id = comp_id
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Choose a Competitor Group:'))
        self.dancerGroups = scrudb.retrieve_dancerGroups_by_competition(comp_id)
        self.dgButtons = []
        for dancerGroup in self.dancerGroups:
            dgButton = SDGPushButton(('[%s] %s' % (dancerGroup.abbrev, dancerGroup.name)),self,dancerGroup.id)
            dgButton.clicked.connect(dgButton.on_button_clicked)
            self.dgButtons.append(dgButton)
        for dgButton in self.dgButtons:
            self.layout.addWidget(dgButton)
        self.newButton = QPushButton('&New Group')
        self.newButton.clicked.connect(self.new_group)
        self.layout.addWidget(self.newButton)
        self.exitButton = QPushButton('E&xit')
        self.exitButton.clicked.connect(self.hide)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(self.layout)

    def new_group(self, sender=None):
        dancerGroup = DancerGroup(0,'','',4,99,0,self.comp_id)
        dancerGroup = scrudb.insert_dancerGroup(dancerGroup)
        #id, name, abbrev, ageMin, ageMax, dancerCat, competition
        self.set_dancer_group(dancerGroup.id)

    def set_dancer_group(self, dancerGroup_id):
        dancerGroup = scrudb.retrieve_dancerGroup(dancerGroup_id)
        if (dancerGroup != None):
            print('Group: [%s] %s' % (dancerGroup.abbrev, dancerGroup.name))
            self.hide()
            self.mainWindow.edit_dancerGroup(dancerGroup_id)

class CompetitionSelector(QDialog):
    def __init__(self, mainWindow):
        super(CompetitionSelector, self).__init__()
        self.mainWindow = mainWindow
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Choose a competition:'))
        self.competitions = scrudb.retrieve_competitions()
        self.compButtons = []
        for comp in self.competitions:
            compButton = SPushButton('%s (%s)' % (comp.name, self.get_formatted_date(comp.eventDate)),self,comp.id)
            compButton.clicked.connect(compButton.on_button_clicked)
            self.compButtons.append(compButton)
        for compButton in self.compButtons:
            self.layout.addWidget(compButton)
        self.newButton = QPushButton('&New Competition')
        self.newButton.clicked.connect(self.new_competition)
        self.layout.addWidget(self.newButton)
        self.exitButton = QPushButton('Cancel')
        self.exitButton.clicked.connect(self.hide)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(self.layout)

    def get_formatted_date(self, date):
        format_str = '%d %b %Y'
        otherformat_str = '%Y-%m-%d'
        return (datetime.datetime.strftime(datetime.datetime.strptime(('%s' % date)[0:10], otherformat_str).date(), format_str))

    def on_button_clicked(self, identifier):
        alert = QMessageBox()
        alert.setText(identifier)
        alert.exec_()

    def set_competition(self, comp_id):
        self.mainWindow.set_competition(comp_id)
        self.hide()

    def new_competition(self):
        self.hide()
        self.mainWindow.new_competition()

class JudgeSelector(QDialog):
    def __init__(self, mainWindow, comp_id):
        super(JudgeSelector, self).__init__()
        self.mainWindow = mainWindow
        self.comp_id = comp_id
        self.changes_made = False
        self.layout = QVBoxLayout()
        self.judges = scrudb.retrieve_judges_by_competition(comp_id)
        self.table_judges = QTableWidget()
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
            item_first_name = QTableWidgetItem(judge.firstName)
            item_last_name = QTableWidgetItem(judge.lastName)
            item_judge_id = QTableWidgetItem('%d' % judge.id)
            self.table_judges.setRowCount(row+1)
            self.table_judges.setItem(row, 0, item_first_name)
            self.table_judges.setItem(row, 1, item_last_name)
            self.table_judges.setItem(row, 2, item_judge_id)

            row += 1
        self.table_judges.setColumnHidden(2, True)
        self.table_judges.itemChanged.connect(self.item_changed)
        self.layout.addWidget(self.table_judges)
        self.newButton = QPushButton('&New Judge')
        self.newButton.clicked.connect(self.new_judge)
        self.layout.addWidget(self.newButton)
        self.deleteButton = QPushButton('&Delete Judge')
        self.deleteButton.clicked.connect(self.delete_judge)
        self.layout.addWidget(self.deleteButton)
        self.saveButton = QPushButton('&Save')
        self.saveButton.clicked.connect(self.save_button)
        self.layout.addWidget(self.saveButton)
        self.exitButton = QPushButton('E&xit')
        self.exitButton.clicked.connect(self.exit_button)
        self.layout.addWidget(self.exitButton)
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(self.layout)

    def new_judge(self, sender=None):
        row = self.table_judges.rowCount()
        #id, firstName, lastName, competition
        judge = Judge(0,'','',self.comp_id)
        judge = scrudb.insert_judge(judge)
        self.table_judges.insertRow(row)
        item_first_name = QTableWidgetItem(judge.firstName)
        item_last_name = QTableWidgetItem(judge.lastName)
        item_judge_id = QTableWidgetItem(('%d' % judge.id))

        self.table_judges.setItem(row,  0, item_first_name)
        self.table_judges.setItem(row,  1, item_last_name)
        self.table_judges.setItem(row,  2, item_judge_id)

        self.table_judges.scrollToItem(self.table_judges.item(row, 0))
        self.changes_made = True

    def delete_judge(self, sender=None):
        row = self.table_judges.currentRow()
        #print('Current row:',row)
        #print('Text = %s' % self.table_judges.item(row, 2).text())
        if (row != None):
            judge = scrudb.retrieve_judge(int(self.table_judges.item(row, 2).text()))
            if (judge != None):
                verity = verify(('Are you sure you want to delete judge %s %s?' % (judge.firstName, judge.lastName)),
                                'This will delete all data for the given judge and all scores associated with this judge. This cannot be undone.')
                if verity:
                    print('Will delete judge %d' % judge.id)
                    scrudb.rm_judge(judge.id)
                    self.table_judges.removeRow(row)
                else:
                    print('Nothing deleted')

    def save_button(self, sender=None):
        row = 0
        while row < self.table_judges.rowCount():
            judge_id = int(self.table_judges.item(row, 2).text())
            judge = scrudb.retrieve_judge(judge_id)
            judge.firstName = self.table_judges.item(row, 0).text()
            judge.lastName = self.table_judges.item(row, 1).text()
            print('Saving judge %s %s [%d] to competition %d(%d)' % (judge.firstName, judge.lastName, judge.id, self.comp_id, judge.competition))
            scrudb.update_judge(judge)

            row += 1
        self.changes_made = False

    def exit_button(self, sender=None):
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

    def item_changed(self, sender=None):
        print('Item changed')
        self.changes_made = True

def print_settings():
    # displays the current settings
    settings = scrudb.retrieve_settings('current')
    if (settings.interface == 0):
        settings.interface = 1
        scrudb.set_settings(settings)
    print('Settings details - Version: %f - Schema: %f - Interface: %d - Last Competition: %d' %
          (settings.version, settings.schema, settings.interface, settings.lastComp))


class PyQtApp(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("Scrutini")
        self.setWindowIcon(QtGui.QIcon("Your/image/file.png"))


def on_button_clicked(sender):
    alert = QMessageBox()
    alert.setText(sender.text())
    alert.exec_()


def verify(prompt='Are you sure?', subprompt=''):
    alert = QMessageBox()
    alert.setText(prompt)
    alert.setInformativeText(subprompt)
    alert.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    alert.setDefaultButton(QMessageBox.Cancel)
    alert.setEscapeButton(QMessageBox.Cancel)
    buttonReply = alert.exec_()
    if buttonReply == QMessageBox.Yes:
        print('Yes clicked.')
        return True
    else:
        print('No clicked.')
        return False

def ask_save(prompt='Do you want to save your changes?', subprompt=''):
    alert = QMessageBox()
    alert.setText(prompt)
    alert.setInformativeText(subprompt)
    alert.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    alert.setDefaultButton(QMessageBox.Save)
    alert.setEscapeButton(QMessageBox.Cancel)
    buttonReply = alert.exec_()
    if buttonReply == QMessageBox.Save:
        print('Save clicked.')
        return 'save'
    elif buttonReply == QMessageBox.Discard:
        print('Discard clicked')
        return 'discard'
    else:
        print('Cancel clicked.')
        return 'cancel'

class SMainWindow(QMainWindow):
    def __init__(self):
        # Constructor
        super(SMainWindow, self).__init__()
        self.myapp = PyQtApp()
        self.layout = QVBoxLayout()
        self.label_text = ''
        self.label = QLabel(self.label_text)
        self.settings = scrudb.retrieve_settings('current')
        self.competition = self.retrieve_competition()
        self.set_competition(self.competition.id)
        self.button_scrutineer = QPushButton('Enter &Scores')
        self.button_view_scores = QPushButton('&View/Print Results')
        self.button_comps = QPushButton('&Change Competition')
        self.button_comp = QPushButton('&Edit Competition Details')
        self.button_dancers = QPushButton('&Add/Edit Competitors')
        self.button_judges = QPushButton('Add/Edit &Judges')
        self.button_dancerGroups = QPushButton(
            'Define Competitor &Groups && Dances')
        self.button_import = QPushButton('&Import CSV')
        self.button_delete = QPushButton('&Delete Competition')
        self.button_exit = QPushButton('E&xit')
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
        if (self.competition == None):
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
        self.myapp.setLayout(self.layout)

        self.statusBar()
        self.statusBar().show()
        menubar = QMenuBar(None)
        #self._menu_bar = QMenuBar()
        #menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        self.setMenuBar(menubar)

        exitAct = QAction(' &Quit',self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit Application')
        exitAct.triggered.connect(self.exit_app)

        fileMenu = QMenu(' &File')
        menubar.addMenu(fileMenu)
        fileMenu.addAction(exitAct)

        changeCompAct = QAction(' &Select Competition',self)
        changeCompAct.setStatusTip('Choose a different competition or make a new one')
        changeCompAct.triggered.connect(self.select_competition)

        editCompAct = QAction(' &Edit Competition',self)
        editCompAct.setStatusTip('Edit Competition Details')
        editCompAct.triggered.connect(self.edit_competition)

        compMenu = menubar.addMenu(' &Competition')
        compMenu.addAction(changeCompAct)
        compMenu.addAction(editCompAct)


    def enter_scores(self, sender=None):
        scoreEntryWindow = ScoreEntryWindow(self,self.competition.id)
        scoreEntryWindow.show()
        scoreEntryWindow.exec_()

    def view_scores(self, sender=None):
        resultsViewWindow = ResultsViewWindow(self,self.competition.id)
        resultsViewWindow.show()
        resultsViewWindow.exec_()

    def import_csv(self, sender=None):
        importWindow = ImportWindow(self, self.competition.id)
        importWindow.show()
        importWindow.exec_()

    def edit_dancers(self):
        dancerEditor = DancerEditor(self, self.competition.id)
        dancerEditor.show()
        dancerEditor.exec_()

    def edit_judges(self):
        judgeSelector = JudgeSelector(self, self.competition.id)
        judgeSelector.show()
        judgeSelector.exec_()

    def edit_competition(self):
        compEditor = CompetitionEditor(self, self.competition.id)
        compEditor.show()
        compEditor.exec_()

    def edit_dancerGroup(self, dancerGroup_id):
        dgEditor = DancerGroupEditor(self, dancerGroup_id)
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
        competitions = scrudb.retrieve_competitions()
        competitions_list = []
        for comp in competitions:
            competitions_list.append(comp.id)
        if (self.settings.lastComp in competitions_list):
            self.competition = self.set_competition(
                self.settings.lastComp)
            return self.competition
        else:
            self.select_competition()
            self.settings.lastComp = self.competition.id
            scrudb.set_settings(self.settings)
            return self.competition

    def set_competition(self, comp_id):
        self.competition = scrudb.retrieve_competition(comp_id)
        if (self.competition != None):
            self.label_text = ('<center>Competition:<br><strong>%s</strong><br>%8s<br>%s</center>' % (self.competition.name, self.get_formatted_date(self.competition.eventDate), self.competition.location))
            self.label.setText(self.label_text)
            self.settings.lastComp = self.competition.id
            scrudb.set_settings(self.settings)
            return self.competition
        else:
            self.label_text = ('<center>No Competition Selected</center>')
            return None

    def select_dancerGroup(self):
        window = DancerGroupMenu(self, self.competition.id)
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
            scrudb.rm_competition(self.competition.id)
            self.competition = None
            self.select_competition()
        else:
            print('Nothing deleted')

    def exit_app(self, sender):
        scrudb.close_connection()
        sys.exit()

    def new_competition(self):
        #id, name, description, eventDate, deadline, location, competitionType, isChampionship
        today = datetime.date.today()
        competition = Competition(0,'','',today,today,'',0,0)
        self.competition = scrudb.insert_competition(competition)
        self.edit_competition()

def is_float(string):
    try:
        val = float(string)
        return True
    except ValueError:
        return False



class ImportWindow(QDialog):
    def __init__(self, mainWindow, comp_id):
        super(ImportWindow, self).__init__()
        self.mainWindow = mainWindow
        self.competition = scrudb.retrieve_competition(comp_id)
        self.layout = QVBoxLayout()
        self.resize(600,800)
        self.button_choose = QPushButton('Choose &File')
        self.button_choose.clicked.connect(self.choose_file)
        self.label_filename = QLabel('No file selected')
        self.table_columns = QTableWidget()
        self.button_import = QPushButton('&Import')
        self.button_import.clicked.connect(self.import_file)
        self.button_exit = QPushButton('Cancel')
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
            item_name = QTableWidgetItem(row)
            item_name.setFlags(Qt.NoItemFlags)
            selector_column = QComboBox()
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
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.filename, _ = QFileDialog.getOpenFileName(self,"Select CSV File", "","CSV Files (*.csv)", options=options)
        if self.filename:
            print(self.filename)
        else:
            return
        self.label_filename.setText(self.filename)
        self.reader = scrudb.retrieve_csv_keys(self.filename)
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
                    dancer = Dancer(0,'','','','','','','','',0,'','','','','','',0,0,self.competition.id)
                    if (self.column_names[0] != ''):
                        dancer.firstName = row[self.column_names[0]]
                    if (self.column_names[1] != ''):
                        dancer.lastName = row[self.column_names[1]]
                    if (self.column_names[2] != ''):
                        dancer.number = row[self.column_names[2]]
                    if (self.column_names[3] != ''):
                        dancer.street = row[self.column_names[3]]
                    if (self.column_names[4] != ''):
                        dancer.city = row[self.column_names[4]]
                    if (self.column_names[5] != ''):
                        dancer.state = row[self.column_names[5]]
                    if (self.column_names[6] != ''):
                        dancer.zipCode = row[self.column_names[6]]
                    if (self.column_names[7] != ''):
                        dancer.phonenum = row[self.column_names[7]]
                    if (self.column_names[8] != ''):
                        dancer.email = row[self.column_names[8]]
                    if (self.column_names[9] != ''):
                        dancer.scotDanceNum = row[self.column_names[9]]
                    if (self.column_names[10] != ''):
                        dancer.birthdate = row[self.column_names[10]]
                    if (self.column_names[11] != ''):
                        if (row[self.column_names[11]].isdigit()):
                            dancer.age = int(row[self.column_names[11]])
                    if (self.column_names[12] != ''):
                        dancer.teacher = row[self.column_names[12]]
                    if (self.column_names[13] != ''):
                        dancer.teacherEmail = row[self.column_names[13]]
                    if (self.column_names[14] != ''):
                        dancer.registeredDate = row[self.column_names[14]]
                    if (self.column_names[15] != ''):
                        dancer_grp1 = row[self.column_names[15]]
                    else:
                        dancer_grp1 = ''
                    if (self.column_names[16] != ''):
                        dancer_grp2 = row[self.column_names[16]]
                    else:
                        dancer_grp2 = ''
                    if (self.column_names[17] != ''):
                        dancer_grp3 = row[self.column_names[16]]
                    else:
                        dancer_grp3 = ''
                    dancerGroup_1 = scrudb.retrieve_dancerGroup_by_abbrev(dancer_grp1)
                    dancerGroup_2 = scrudb.retrieve_dancerGroup_by_abbrev(dancer_grp2)
                    dancerGroup_3 = scrudb.retrieve_dancerGroup_by_abbrev(dancer_grp3)
                    dancer = scrudb.insert_dancer(dancer)
                    if (dancerGroup_1 != None):
                        scrudb.insert_dancerGroupJoin(dancer.id, dancerGroup_1.id)
                    if (dancerGroup_2 != None):
                        scrudb.insert_dancerGroupJoin(dancer.id, dancerGroup_2.id)
                    if (dancerGroup_3 != None):
                        scrudb.insert_dancerGroupJoin(dancer.id, dancerGroup_3.id)
                    #xxx doesn't seem to put dancers into dancerGroups. Why?
        self.hide()


def menu_main():
    app = QApplication(sys.argv)
    mainWindow = SMainWindow()
    mainWindow.myapp.show()
    sys.exit(app.exec_())