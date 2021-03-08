import time

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QFileDialog, QListView, QTreeView, \
    QAbstractItemView, QDialog, QMessageBox
from PyQt5 import QtWidgets
from scrapegui import Ui_MainWindow
from worker import WorkerSignals, Worker


class MainWindowUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindowUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.msgBox = QMessageBox()
        self.ui.setupUi(self)
        self.signals = WorkerSignals()
        self.threadpool = QThreadPool()
        # Connect button signals to slots
        self.ui.scFilebtn.clicked.connect(self.browseCopyFrom)
        self.ui.mFilebtn.clicked.connect(self.browseInsertInto)
        self.ui.startbtn.clicked.connect(self.clickedExecute)

    def browseCriteriaFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.copyFromFile, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                                     "Open", "",
                                                                     "All "
                                                                     "Files ("
                                                                     "*);;Python Files "
                                                                     "(*.py)",
                                                                     options=options)
        if self.criteriaFile:
            self.ui.FileNameCopy.setText(self.copyFromFile)

    def browseInsertInto(self):
        multiSelect = QFileDialog()
        multiSelect.setOption(multiSelect.DontUseNativeDialog, True)
        multiSelect.setOption(multiSelect.HideNameFilterDetails, True)
        multiSelect.setOption(multiSelect.ShowDirsOnly, False)
        multiSelect.findChildren(QListView)[0].setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        multiSelect.findChildren(QTreeView)[0].setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        if multiSelect.exec_() == QDialog.Accepted:
            self.insertIntoFiles = multiSelect.selectedFiles()
            # clear out any old selections
            self.ui.FileNamesInsertInto.clear()
            # loop through all files selected and add to screen
            for file in range(len(self.insertIntoFiles)):
                self.ui.FileNamesInsertInto.append(self.insertIntoFiles[file])

    def pdfJob(self, progress_callback):
        self.executePDF.merge(self.copyFromFile, self.insertIntoFiles,
                              self.ui.InsertAfterPageNum.value(),
                              self.ui.InsertEveryNthPageNum.value())
        for n in range(0, 5):
            time.sleep(1)
            progress_callback.emit((n * 100 / 4))

    def progressNum(self, n):
        self.ui.progress_label.setText("Merging in Progress...%d%% done" % n)

    def startProc(self):
        self.ui.progress_label.setText("Merging in Progress...firing up the "
                                       "engine")

    def showCompletion(self):
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText("Merge Completed Successfully")
        self.msgBox.setWindowTitle("Program Status")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.exec()

    def completed(self):
        self.showCompletion()
        self.ui.progress_label.setText(" ")
        return

    def clickedExecute(self):
        # call process
        self.stopped = False
        self.runThreadedProcess()

    def runThreadedProcess(self):
        # Execute a function in the background with a worker
        worker = Worker(self.pdfJob)
        worker.signals.start.connect(self.startProc)
        worker.signals.progress.connect(self.progressNum)
        worker.signals.finished.connect(self.completed)
        # start worker
        self.threadpool.start(worker)