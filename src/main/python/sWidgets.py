from PyQt5.QtWidgets import QPushButton, QMessageBox


class SPushButton(QPushButton):
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


def on_button_clicked(sender):
    alert = QMessageBox()
    alert.setText(sender.text())
    alert.exec_()


def verify(prompt='Are you sure?', subprompt=''):
    alert = QMessageBox()
    alert.setText(prompt)
    alert.setInformativeText(subprompt)
    alert.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
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


def is_float(string):
    try:
        val = float(string)
        return True
    except ValueError:
        return False
