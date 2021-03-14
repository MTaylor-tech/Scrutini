from fpdf import FPDF
from PyQt5 import QtPrintSupport
import sys
import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg


class ResultsGroupBox(qt.QGroupBox):
    def __init__(self, text, event, db, main_window):
        super(ResultsGroupBox, self).__init__(text)
        self.db = db
        self.main_window = main_window
        self.event = self.db.tables.events.get(event)
        self.layout = qt.QVBoxLayout()
        self.scores = self.db.tables.scores.get_by_event(event)
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
            label_score = qt.QLabel('%d. (%s) %s %s - %s, %s'
                                    % (place, dancer.number, dancer.firstName,
                                       dancer.lastName, dancer.city,
                                       dancer.state))
            self.print_label += ('%s::' % label_score.text())
            self.layout.addWidget(label_score)
            # print(self.placing_scores)
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
            self.layout.addWidget(label_score)
        self.update()


class ResultsViewWindow(qt.QDialog):
    def __init__(self, main_window, comp_id, db):
        super(ResultsViewWindow, self).__init__()
        self.db = db
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
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
        self.selector_dancerGroup.currentIndexChanged.connect(
            self.new_group_selected)
        self.layout.addWidget(self.selector_dancerGroup)
        self.dancerGroup = self.db.tables.groups.get(
            self.dancerGroup_ids[self.selector_dancerGroup.currentIndex()])
        self.events = self.db.tables.events.get_by_group(self.dancerGroup.id)
        self.dancers = self.db.tables.events.get_by_group(self.dancerGroup.id)
        self.overall_scores = {}
        self.print_label = ''
        for dancer in self.dancers:
            self.overall_scores[dancer.id] = 0
        i = 1
        n = 1
        for event in self.events:
            results_box = ResultsGroupBox(event.name, event.id, self.db,
                                          self.main_window)
            # self.groupBox_scores_layout.addWidget(results_box)
            if i % 2 == 0:
                # self.groupBox_scores_layout.addWidget(results_box, n,1,1,1, qc.Qt.AlignRight)
                self.groupBox_scores_layout.addWidget(results_box)
                n += 1
            else:
                # self.groupBox_scores_layout.addWidget(results_box, n,1,1,1,qc.Qt.AlignLeft)
                self.groupBox_scores_layout.addWidget(results_box)
            self.print_label += ('%s::%s:: ::' % (event.name,
                                 results_box.get_print_label()))
            if event.countsForOverall == 1:
                if self.db.settings.verbose:
                    print(event.name)
                event_placing_scores = results_box.get_placing_scores()
                for dancer, points in event_placing_scores.items():
                    if self.db.settings.verbose:
                        print('(%d) - [%6.2f]' % (dancer, points))
                    if self.overall_scores.get(dancer) is not None:
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
        self.dancerGroup = self.db.tables.groups.get(
            self.dancerGroup_ids[self.selector_dancerGroup.currentIndex()])
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
            results_box = ResultsGroupBox(event.name, event.id,
                                          self.db, self.main_window)
            #self.groupBox_scores_layout.addWidget(results_box)
            results_box.sizeHint()
            if (i%2==0):
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1, qc.Qt.AlignRight)
                n += 1
            else:
                self.groupBox_scores_layout.addWidget(results_box, n,1,1,1,qc.Qt.AlignLeft)
            self.print_label += ('%s::%s:: ::' % (event.name, results_box.get_print_label()))
            if (event.countsForOverall == 1):
                if self.db.settings.verbose:
                    print(event.name)
                event_placing_scores = results_box.get_placing_scores()
                for dancer, points in event_placing_scores.items():
                    if self.db.settings.verbose:
                        print('(%d) - [%6.2f]' % (dancer, points))
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
            label_overall = qt.QLabel('%d. (%s) %s %s - %s, %s: %d points' %
                                       (place, dancer.number, dancer.firstName,
                                        dancer.lastName, dancer.city,
                                        dancer.state, points))
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
