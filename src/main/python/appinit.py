from PyQt5.QtCore import QThreadPool, QThread
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets
from scrapegui import Ui_MainWindow
from worker import Worker


class MainWindowUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindowUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.msgBox = QMessageBox()
        self.ui.setupUi(self)
        self.threadpool = QThreadPool()
        # Connect button signals to slots
        self.ui.scFilebtn.clicked.connect(self.browseSearchFile)
        self.ui.mFilebtn.clicked.connect(self.browseMasterFile)
        self.ui.startbtn.clicked.connect(self.started)
        self.ui.freeformRdBtn.clicked.connect(self.searchCriteria)
        self.ui.upldRdBtn.clicked.connect(self.searchCriteria)

    def searchCriteria(self):
        # Enable either the file upload or the manual entry option based upon
        # user's radio button choice
        if self.ui.upldRdBtn.isChecked():
            self.ui.scFilebox.setEnabled(True)
            self.ui.scFilebtn.setEnabled(True)
            self.ui.freeformSrch.clear()
            self.ui.freeformSrch.setEnabled(False)
        elif self.ui.freeformRdBtn.isChecked():
            self.ui.freeformSrch.setEnabled(True)
            self.ui.scFilebox.setEnabled(False)
            self.ui.scFilebtn.setEnabled(False)
            self.ui.scFilebox.clear()

    def browseSearchFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.searchFile, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open",
                                                                   "", "Excel "
                                                                       "Files ("
                                                                       "*.xl"
                                                                       "*);;All "
                                                                       "Files "
                                                                       "(*)",
                                                                   options=options)
        if self.searchFile:
            self.ui.scFilebox.setText(self.searchFile)

    def browseMasterFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.masterFile, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open",
                                                                   "", "Excel "
                                                                       "Files ("
                                                                       "*.xl"
                                                                       "*);;All "
                                                                       "Files "
                                                                       "(*)",
                                                                   options=options)
        if self.masterFile:
            self.ui.mFilebox.setText(self.masterFile)

    def completed(self):
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText("Scraping Complete")
        self.msgBox.setWindowTitle("Program Status")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.exec()

    def progressDialogue(self, text):
        redColor = QColor(198, 45, 66)
        greenColor = QColor(16, 88, 82)
        if "No Results" in text:
            self.ui.scrapingDialogue.setTextColor(redColor)
            self.ui.scrapingDialogue.append(text)
        else:
            self.ui.scrapingDialogue.setTextColor(greenColor)
            self.ui.scrapingDialogue.append(text)

    def started(self):
        # do error checking
        try:
            if self.ui.freeformSrch.isEnabled():
                self.srchFile = self.ui.freeformSrch.toPlainText()
                self.searchFile = self.srchFile.split(',')
                self.searchFile = [x.strip(' ') for x in self.searchFile]
            # clear Scraping Stats & Scraping Dialogue in case user reruns the
            # application
            self.ui.scrapingDialogue.clear()
            self.ui.txtRuntime.setText("")
            self.ui.txtSrchItm.setText("")
            self.ui.txtScrapes.setText("")
            self.ui.txtCompleted.setText("")
            print(self.searchFile)
            print(self.masterFile)
        except AttributeError:
            self.msgBox.setIcon(QMessageBox.Critical)
            self.msgBox.setText("Missing Search Criteria and/or Master File")
            self.msgBox.setWindowTitle("Missing Data")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.exec()
        else:
            # call process
            self.runThreadedProcess()

    def runThreadedProcess(self):
        # Execute a function in the background with a worker
        self.thread = QThread()
        self.worker = Worker(self.searchFile, self.masterFile)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.currentStatus.connect(self.ui.txtRuntime.setText)
        self.worker.progressSearch.connect(self.ui.txtSrchItm.setText)
        self.worker.progressDialogue.connect(self.progressDialogue)
        self.worker.progressScrapes.connect(self.ui.txtScrapes.setText)
        self.worker.progressCompleted.connect(self.ui.txtCompleted.setText)
        self.worker.finished.connect(self.completed)
        self.worker.finished.connect(self.thread.quit)
        # start worker
        self.thread.start()

