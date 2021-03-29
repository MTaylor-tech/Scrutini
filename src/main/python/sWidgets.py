import os
import csv
import datetime
from PyQt5.QtWidgets import QPushButton, QMessageBox
from PyQt5.QtCore import QDate

class SPushButton(QPushButton):
    def __init__(self, text, sender, identifier, fn):
        super(SPushButton, self).__init__(text)
        self.identifier = identifier
        self.sender = sender
        self.fn = fn

    def on_button_clicked(self):
        self.fn(self.identifier)


class SMessageBox(QMessageBox):
    def __init__(self, sender):
        super().__init__()
        self.setText(sender.text())
        self.exec_()


def on_button_clicked(sender):
    alert = QMessageBox()
    alert.setText(sender.text())
    alert.exec_()


def verify(prompt='Are you sure?', subprompt=''):
    """Double-check an important decision with the user."""
    alert = QMessageBox()
    alert.setText(prompt)
    alert.setInformativeText(subprompt)
    alert.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    alert.setEscapeButton(QMessageBox.Cancel)
    button_reply = alert.exec_()
    if button_reply == QMessageBox.Yes:
        print('Yes clicked.')
        return True
    else:
        print('No clicked.')
        return False


def ask_save(prompt='Do you want to save your changes?', subprompt=''):
    """"Ask the user if they want to save and return their answer."""
    alert = QMessageBox()
    alert.setText(prompt)
    alert.setInformativeText(subprompt)
    alert.setStandardButtons(QMessageBox.Save | QMessageBox.Discard
                             | QMessageBox.Cancel)
    alert.setDefaultButton(QMessageBox.Save)
    alert.setEscapeButton(QMessageBox.Cancel)
    button_reply = alert.exec_()
    if button_reply == QMessageBox.Save:
        print('Save clicked.')
        return 'save'
    elif button_reply == QMessageBox.Discard:
        print('Discard clicked')
        return 'discard'
    else:
        print('Cancel clicked.')
        return 'cancel'


def is_float(string):
    """Verify that the value of the string can be cast to a float."""
    try:
        val = float(string)
        return val == val
    except ValueError:
        return False


def retrieve_csv_dict(csv_filename):
    """Return a dictionary with the data from the csv."""
    if os.path.exists(csv_filename):
        with open(csv_filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return reader
    else:
        print('File not found.')
        return None


def retrieve_csv_keys(csv_filename):
    """Grab the column names as dictionary keys from the csv."""
    if os.path.exists(csv_filename):
        with open(csv_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            return next(reader)
    else:
        print('File not found.')
        return None


def today():
    """Grab today's date."""
    return get_formatted_date(datetime.date.today())


def get_formatted_date(date):
    """Return a nicely formatted date like: 22 May 2021."""
    format_str = '%d %b %Y'
    otherformat_str = '%Y-%m-%d'
    return (datetime.datetime.strftime(datetime.datetime.strptime(
        ('%s' % date)[0:10], otherformat_str).date(), format_str))


def exit_handler(sender):
    if sender.changes_made:
        save_result = ask_save()
    else:
        save_result = 'discard'
    # if self.db.settings.verbose:
    #     print(f"save_result: {save_result}")
    if save_result == 'discard':
        sender.hide()
    elif save_result == 'save':
        sender.save()
        sender.hide()
    else:
        pass


def sanitize(phrase):
    new_phrase = phrase.replace("'", "\\'")
    new_phrase = new_phrase.replace('"', '\\"')
    new_phrase = new_phrase.replace("--", "-")
    print(f"Sanitize: '{phrase}' into: '{new_phrase}'")
    # phrase.replace("'","\\'").replace('"','\\"').replace("--","-")
    # phrase.replace("'","").replace('"','').replace("--","-")
    # print(f"to: {phrase}")
    return new_phrase
