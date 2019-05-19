# -*- coding: utf-8 -*-
# Copyright: (C) 2019 Lovac42
# Support: https://github.com/lovac42/Pennywise
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version: 0.0.1


from aqt import mw
from anki.hooks import wrap
from aqt import addcards
from aqt.utils import shortcut
from anki.lang import _
from aqt.qt import *

from anki import version
ANKI21=version.startswith("2.1.")

if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


def cbSaveState(ac_dialog): #save to profile
    ac_dialog.mw.pm.profile['AddOnceOnlyCKBOX'] = ac_dialog.addOnceChkBox.isChecked()


def wrap_setupButtons(ac_dialog, _old):
    cbState = ac_dialog.mw.pm.profile.get("AddOnceOnlyCKBOX", False)
    ac_dialog.addOnceChkBox = QCheckBox(_("Once"))
    ac_dialog.addOnceChkBox.setCheckState(cbState)
    ac_dialog.addOnceChkBox.setTristate(False)
    ac_dialog.form.buttonBox.addButton(ac_dialog.addOnceChkBox,QDialogButtonBox.ActionRole)
    ac_dialog.addOnceChkBox.clicked.connect(lambda:cbSaveState(ac_dialog))
    ac_dialog.addOnceChkBox.setShortcut(QKeySequence("Ctrl+o"))
    ac_dialog.addOnceChkBox.setToolTip(shortcut(_("Add (shortcut: Ctrl+o)")))

    ret=_old(ac_dialog)
    ac_dialog.form.buttonBox.removeButton(ac_dialog.helpButton)
    return ret


hasNote=None
def wrap_addNote(ac_dialog, note, _old):
    global hasNote
    hasNote=_old(ac_dialog, note)
    return hasNote
    #If first field, the sorting field is empty, there is no note.
    #This is used to prevent addOnlyOnce from closing the dialog.


def wrap_addCards(ac_dialog, _old):
    ret=_old(ac_dialog) #calls addNote, always returns None
    if hasNote and ac_dialog.addOnceChkBox.isChecked():
        ac_dialog.reject() #call reject after adding
    return ret


def wrap_canClose20(ac_dialog, _old):
    if ac_dialog.addOnceChkBox.isChecked():
        return True
    return _old(ac_dialog)


def wrap_canClose21(ac_dialog, onOk, _old):
    if not ac_dialog.addOnceChkBox.isChecked():
        return _old(ac_dialog, onOk)
    ac_dialog.editor.saveNow(onOk)



addcards.AddCards.setupButtons = wrap(addcards.AddCards.setupButtons, wrap_setupButtons, 'around')
addcards.AddCards.addNote = wrap(addcards.AddCards.addNote, wrap_addNote, 'around')


if ANKI21:
    addcards.AddCards.addCards = wrap(addcards.AddCards._addCards, wrap_addCards, 'around')
    addcards.AddCards.ifCanClose = wrap(addcards.AddCards.ifCanClose, wrap_canClose21, 'around')
else:
    addcards.AddCards.addCards = wrap(addcards.AddCards.addCards, wrap_addCards, 'around')
    addcards.AddCards.canClose = wrap(addcards.AddCards.canClose, wrap_canClose20, 'around')