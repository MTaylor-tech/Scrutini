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
        self.event = self.db.t.event.get(event)
        self.layout = qt.QVBoxLayout()
        self.scores = self.db.t.score.get_by_event(event)
        self.scores.sort(key=lambda score: score.score, reverse=True)
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
                self.placing_scores[score.dancer] = self.db.t.place_value.get(1).points
                self.placing[1] = score.dancer
            elif ((place == 2) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(2).points
                self.placing[2] = score.dancer
            elif ((place == 3) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(3).points
                self.placing[3] = score.dancer
            elif ((place == 4) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(4).points
                self.placing[4] = score.dancer
            elif ((place == 5) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(5).points
                self.placing[5] = score.dancer
            elif ((place == 6) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(6).points
                self.placing[6] = score.dancer

            if ((place > self.event.num_places) or (score.score == 0)):
                break

            dancer = self.db.t.dancer.get(score.dancer)
            previous_score = score.score
            label_score = qt.QLabel('%d. (%s) %s %s - %s, %s'
                                    % (place, dancer.competitor_num,
                                       dancer.first_name,
                                       dancer.last_name, dancer.city,
                                       dancer.state))
            self.print_label += ('%s::' % label_score.text())
            self.layout.addWidget(label_score)
            # print(self.placing_scores)
        self.setLayout(self.layout)
    #
    # def get_score_value(self, score):
    #     return score.score

    def get_print_label(self):
        return self.print_label

    def get_placing_scores(self):
        return self.placing_scores

    def get_placing(self):
        return self.placing

    def select_event(self, event_id):
        self.event = self.db.t.event.get(event_id)
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.update()
        self.scores = self.db.t.score.get_by_event(self.event.iid)
        self.scores.sort(key=lambda score: score.score, reverse=True)
        place = 1
        previous_score = 0
        self.placing_scores = {}
        self.placing = [0]*7
        for score in self.scores:
            if score.score < previous_score:
                place += 1
            if ((place == 1) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(1).points
                self.placing[1] = score.dancer
            elif ((place == 2) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(2).points
                self.placing[2] = score.dancer
            elif ((place == 3) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(3).points
                self.placing[3] = score.dancer
            elif ((place == 4) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(4).points
                self.placing[4] = score.dancer
            elif ((place == 5) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(5).points
                self.placing[5] = score.dancer
            elif ((place == 6) and (score.score > 0)):
                self.placing_scores[score.dancer] = self.db.t.place_value.get(6).points
                self.placing[6] = score.dancer
            if ((place > self.event.num_places) or (score.score == 0)):
                break
            dancer = self.db.t.dancer.get(score.dancer)
            previous_score = score.score
            label_score = qt.QLabel('%d. (%s) %s %s - %s, %s' % (place, dancer.competitor_num,
                                                    dancer.first_name, dancer.last_name, dancer.city, dancer.state))
            self.layout.addWidget(label_score)
        self.update()


class ResultsViewWindow(qt.QDialog):
    def __init__(self, main_window, competition_id, db):
        super(ResultsViewWindow, self).__init__()
        self.db = db
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.competition_id = competition_id
        self.competition = self.db.t.competition.get(self.competition_id)
        self.layout = qt.QVBoxLayout()
        self.dancer_groups = self.db.t.group.get_by_competition(self.competition_id)
        self.big_layout = qt.QVBoxLayout()
        self.big_group_box = qt.QGroupBox()
        self.label_group = qt.QLabel('Viewing results for group:')
        self.layout.addWidget(self.label_group)
        self.selector_dancer_group = qt.QComboBox()
        self.group_box_scores = qt.QGroupBox()
        self.group_box_scores_layout = qt.QGridLayout()
        self.dancer_group_ids = []
        for dancer_group in self.dancer_groups:
            self.selector_dancer_group.addItem(dancer_group.name)
            self.dancer_group_ids.append(dancer_group.iid)
        self.selector_dancer_group.currentIndexChanged.connect(
            self.new_group_selected)
        self.layout.addWidget(self.selector_dancer_group)
        self.dancer_group = self.db.t.group.get(
            self.dancer_group_ids[self.selector_dancer_group.currentIndex()])
        self.events = self.db.t.event.get_by_group(self.dancer_group.iid)
        self.dancers = self.db.t.event.get_by_group(self.dancer_group.iid)
        self.overall_scores = {}
        self.print_label = ''
        for dancer in self.dancers:
            self.overall_scores[dancer.iid] = 0
        i = 1
        n = 1
        for event in self.events:
            results_box = ResultsGroupBox(event.name, event.iid, self.db,
                                          self.main_window)
            # self.group_box_scores_layout.addWidget(results_box)
            if i % 2 == 0:
                # self.group_box_scores_layout.addWidget(results_box, n,1,1,1, qc.Qt.AlignRight)
                self.group_box_scores_layout.addWidget(results_box)
                n += 1
            else:
                # self.group_box_scores_layout.addWidget(results_box, n,1,1,1,qc.Qt.AlignLeft)
                self.group_box_scores_layout.addWidget(results_box)
            self.print_label += ('%s::%s:: ::' % (event.name,
                                 results_box.get_print_label()))
            if event.counts_for_overall == 1:
                if self.db.s.verbose:
                    print(event.name)
                event_placing_scores = results_box.get_placing_scores()
                for dancer, points in event_placing_scores.items():
                    if self.db.s.verbose:
                        print('(%d) - [%6.2f]' % (dancer, points))
                    if self.overall_scores.get(dancer) is not None:
                        self.overall_scores[dancer] += points
            i += 1
        self.overall_scores_sorted = [(k, self.overall_scores[k]) for k in sorted(self.overall_scores, key=self.overall_scores.get, reverse=True)]
        self.group_box_overall = qt.QGroupBox('Overall Results for %s' % self.dancer_group.name)
        self.group_box_overall_layout = qt.QVBoxLayout()
        self.print_label += ('Overall Results for %s::' % self.dancer_group.name)
        place = 1
        for dancer_id, points in self.overall_scores_sorted:
            if points <= 0:
                break
            dancer = self.db.t.dancer.get(dancer_id)
            label_overall = qt.QLabel('%d. (%s) %s %s - %s, %s: %d points' % (place, dancer.competitor_num,
                                                    dancer.first_name, dancer.last_name, dancer.city, dancer.state, points))
            self.group_box_overall_layout.addWidget(label_overall)
            self.print_label += ('%s::' % label_overall.text())
            place += 1
        self.group_box_scores.setLayout(self.group_box_scores_layout)
        self.layout.addWidget(self.group_box_scores)
        self.group_box_overall.setLayout(self.group_box_overall_layout)
        self.layout.addWidget(self.group_box_overall)
        self.button_exit = qt.QPushButton('E&xit')
        self.button_exit.clicked.connect(self.cancel_button)
        self.big_group_box.setLayout(self.layout)
        self.button_print = qt.QPushButton('Print Results')
        self.button_pdf = qt.QPushButton('Save PDF')
        self.button_print.clicked.connect(self.print_to_printer)
        self.button_pdf.clicked.connect(self.print_to_pdf)
        self.big_layout.addWidget(self.button_print)
        self.big_layout.addWidget(self.button_pdf)
        self.big_layout.addWidget(self.button_exit)
        self.big_layout.addWidget(self.big_group_box)
        self.setLayout(self.big_layout)
        # self.sizeHint()
        # self.resize(800,400)

    def print_to_printer(self):
        doc_text = ('<center><strong>%s</strong><br>%s<br>%s</center>' %
                    (self.competition.name,self.competition.event_date[0:10],
                     self.dancer_group.name))
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
        self.pdf.cell(180,5,txt=self.competition.event_date[0:10],ln=1,align='C')
        self.pdf.cell(180,5,txt=self.dancer_group.name,ln=1,align='C')
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
        self.dancer_group = self.db.t.group.get(
            self.dancer_group_ids[self.selector_dancer_group.currentIndex()])
        for i in reversed(range(self.group_box_scores_layout.count())):
            if isinstance(self.group_box_scores_layout.itemAt(i).widget(),ResultsGroupBox):
                self.group_box_scores_layout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.group_box_overall_layout.count())):
            self.group_box_overall_layout.itemAt(i).widget().setParent(None)
        self.update()
        self.events = self.db.t.event.get_by_group(self.dancer_group.iid)
        self.dancers = self.db.t.dancer.get_by_group(self.dancer_group.iid)
        self.overall_scores = {}
        self.print_label = ''
        for dancer in self.dancers:
            self.overall_scores[dancer.iid] = 0
        i = 1
        n = 1
        for event in self.events:
            results_box = ResultsGroupBox(event.name, event.iid,
                                          self.db, self.main_window)
            #self.group_box_scores_layout.addWidget(results_box)
            results_box.sizeHint()
            if (i%2==0):
                self.group_box_scores_layout.addWidget(results_box, n,1,1,1, qc.Qt.AlignRight)
                n += 1
            else:
                self.group_box_scores_layout.addWidget(results_box, n,1,1,1,qc.Qt.AlignLeft)
            self.print_label += ('%s::%s:: ::' % (event.name, results_box.get_print_label()))
            if (event.counts_for_overall == 1):
                if self.db.s.verbose:
                    print(event.name)
                event_placing_scores = results_box.get_placing_scores()
                for dancer, points in event_placing_scores.items():
                    if self.db.s.verbose:
                        print('(%d) - [%6.2f]' % (dancer, points))
                    self.overall_scores[dancer] += points
            i += 1

        self.overall_scores_sorted = [(k, self.overall_scores[k]) for k in sorted(
            self.overall_scores, key=self.overall_scores.get, reverse=True)]
        self.group_box_overall.setTitle('Overall Results for %s' % self.dancer_group.name)
        self.print_label += ('Overall Results for %s::' %
                             self.dancer_group.name)
        place = 1
        for dancer_id, points in self.overall_scores_sorted:
            if points <= 0:
                break
            dancer = self.db.t.dancer.get(dancer_id)
            label_overall = qt.QLabel('%d. (%s) %s %s - %s, %s: %d points' %
                                       (place, dancer.competitor_num,
                                        dancer.first_name,
                                        dancer.last_name, dancer.city,
                                        dancer.state, points))
            self.group_box_overall_layout.addWidget(label_overall)
            self.print_label += ('%s::' % label_overall.text())
            place += 1
        self.group_box_scores.sizeHint()
        self.group_box_overall.sizeHint()
        self.big_group_box.sizeHint()
        self.sizeHint()
        self.update()
        # self.resize(800,400)

    def cancel_button(self, sender=None):
        self.hide()
