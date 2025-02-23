# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'integration.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(823, 909)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.ringLE = QtWidgets.QLineEdit(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ringLE.sizePolicy().hasHeightForWidth())
        self.ringLE.setSizePolicy(sizePolicy)
        self.ringLE.setMinimumSize(QtCore.QSize(180, 0))
        self.ringLE.setObjectName("ringLE")
        self.horizontalLayout.addWidget(self.ringLE)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.positionLE = QtWidgets.QLineEdit(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.positionLE.sizePolicy().hasHeightForWidth())
        self.positionLE.setSizePolicy(sizePolicy)
        self.positionLE.setMinimumSize(QtCore.QSize(45, 0))
        self.positionLE.setObjectName("positionLE")
        self.horizontalLayout.addWidget(self.positionLE)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.graphicsView = QtWidgets.QGraphicsView(self.tab)
        self.graphicsView.setMinimumSize(QtCore.QSize(400, 400))
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.label_7 = QtWidgets.QLabel(self.tab)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.moduleLE = QtWidgets.QLineEdit(self.tab)
        self.moduleLE.setObjectName("moduleLE")
        self.horizontalLayout_2.addWidget(self.moduleLE)
        self.mountPB = QtWidgets.QPushButton(self.tab)
        self.mountPB.setObjectName("mountPB")
        self.horizontalLayout_2.addWidget(self.mountPB)
        self.unmountPB = QtWidgets.QPushButton(self.tab)
        self.unmountPB.setEnabled(False)
        self.unmountPB.setObjectName("unmountPB")
        self.horizontalLayout_2.addWidget(self.unmountPB)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.powerCB = QtWidgets.QComboBox(self.tab)
        self.powerCB.setObjectName("powerCB")
        self.gridLayout.addWidget(self.powerCB, 2, 1, 1, 1)
        self.fiberConnectionLabel = QtWidgets.QLabel(self.tab)
        self.fiberConnectionLabel.setObjectName("fiberConnectionLabel")
        self.gridLayout.addWidget(self.fiberConnectionLabel, 1, 0, 1, 2)
        self.connectFiberPB = QtWidgets.QPushButton(self.tab)
        self.connectFiberPB.setObjectName("connectFiberPB")
        self.gridLayout.addWidget(self.connectFiberPB, 0, 0, 1, 1)
        self.powerConnectionLabel = QtWidgets.QLabel(self.tab)
        self.powerConnectionLabel.setObjectName("powerConnectionLabel")
        self.gridLayout.addWidget(self.powerConnectionLabel, 3, 0, 1, 2)
        self.connectPowerPB = QtWidgets.QPushButton(self.tab)
        self.connectPowerPB.setObjectName("connectPowerPB")
        self.gridLayout.addWidget(self.connectPowerPB, 2, 0, 1, 1)
        self.connectPowerLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectPowerLED.sizePolicy().hasHeightForWidth())
        self.connectPowerLED.setSizePolicy(sizePolicy)
        self.connectPowerLED.setMinimumSize(QtCore.QSize(30, 34))
        self.connectPowerLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.connectPowerLED.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.connectPowerLED.setObjectName("connectPowerLED")
        self.gridLayout.addWidget(self.connectPowerLED, 2, 3, 1, 1)
        self.fiberCB = QtWidgets.QComboBox(self.tab)
        self.fiberCB.setObjectName("fiberCB")
        self.gridLayout.addWidget(self.fiberCB, 0, 1, 1, 1)
        self.connectFiberLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectFiberLED.sizePolicy().hasHeightForWidth())
        self.connectFiberLED.setSizePolicy(sizePolicy)
        self.connectFiberLED.setMinimumSize(QtCore.QSize(30, 34))
        self.connectFiberLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.connectFiberLED.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.connectFiberLED.setObjectName("connectFiberLED")
        self.gridLayout.addWidget(self.connectFiberLED, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_4.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.checkIDPB = QtWidgets.QPushButton(self.tab)
        self.checkIDPB.setMinimumSize(QtCore.QSize(0, 30))
        self.checkIDPB.setObjectName("checkIDPB")
        self.horizontalLayout_3.addWidget(self.checkIDPB)
        self.checkIDlabel = QtWidgets.QLabel(self.tab)
        self.checkIDlabel.setObjectName("checkIDlabel")
        self.horizontalLayout_3.addWidget(self.checkIDlabel)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.checkIDLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkIDLED.sizePolicy().hasHeightForWidth())
        self.checkIDLED.setSizePolicy(sizePolicy)
        self.checkIDLED.setMinimumSize(QtCore.QSize(30, 30))
        self.checkIDLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.checkIDLED.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.checkIDLED.setObjectName("checkIDLED")
        self.horizontalLayout_3.addWidget(self.checkIDLED)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 2, 2, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem4, 0, 2, 1, 1)
        self.hvOFFTestLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hvOFFTestLED.sizePolicy().hasHeightForWidth())
        self.hvOFFTestLED.setSizePolicy(sizePolicy)
        self.hvOFFTestLED.setMinimumSize(QtCore.QSize(30, 30))
        self.hvOFFTestLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.hvOFFTestLED.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.hvOFFTestLED.setObjectName("hvOFFTestLED")
        self.gridLayout_2.addWidget(self.hvOFFTestLED, 0, 3, 1, 1)
        self.hvONTestPB = QtWidgets.QPushButton(self.tab)
        self.hvONTestPB.setMinimumSize(QtCore.QSize(0, 30))
        self.hvONTestPB.setObjectName("hvONTestPB")
        self.gridLayout_2.addWidget(self.hvONTestPB, 2, 0, 1, 1)
        self.hvONTestCB = QtWidgets.QCheckBox(self.tab)
        self.hvONTestCB.setEnabled(False)
        self.hvONTestCB.setText("")
        self.hvONTestCB.setObjectName("hvONTestCB")
        self.gridLayout_2.addWidget(self.hvONTestCB, 2, 1, 1, 1)
        self.hvONTestLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hvONTestLED.sizePolicy().hasHeightForWidth())
        self.hvONTestLED.setSizePolicy(sizePolicy)
        self.hvONTestLED.setMinimumSize(QtCore.QSize(30, 30))
        self.hvONTestLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.hvONTestLED.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.hvONTestLED.setObjectName("hvONTestLED")
        self.gridLayout_2.addWidget(self.hvONTestLED, 2, 3, 1, 1)
        self.hvOFFTestCB = QtWidgets.QCheckBox(self.tab)
        self.hvOFFTestCB.setEnabled(False)
        self.hvOFFTestCB.setText("")
        self.hvOFFTestCB.setObjectName("hvOFFTestCB")
        self.gridLayout_2.addWidget(self.hvOFFTestCB, 0, 1, 1, 1)
        self.hvOFFTestPB = QtWidgets.QPushButton(self.tab)
        self.hvOFFTestPB.setMinimumSize(QtCore.QSize(0, 30))
        self.hvOFFTestPB.setObjectName("hvOFFTestPB")
        self.gridLayout_2.addWidget(self.hvOFFTestPB, 0, 0, 1, 1)
        self.verticalLayout_5.addLayout(self.gridLayout_2)
        self.resultsLabel = QtWidgets.QLabel(self.tab)
        self.resultsLabel.setMinimumSize(QtCore.QSize(0, 100))
        self.resultsLabel.setObjectName("resultsLabel")
        self.verticalLayout_5.addWidget(self.resultsLabel)
        self.pushButton = QtWidgets.QPushButton(self.tab)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 30))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_5.addWidget(self.pushButton)
        self.caenWidget = QtWidgets.QWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.caenWidget.sizePolicy().hasHeightForWidth())
        self.caenWidget.setSizePolicy(sizePolicy)
        self.caenWidget.setMinimumSize(QtCore.QSize(60, 140))
        self.caenWidget.setObjectName("caenWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.caenWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_6 = QtWidgets.QLabel(self.caenWidget)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lvOnButton = QtWidgets.QPushButton(self.caenWidget)
        self.lvOnButton.setMinimumSize(QtCore.QSize(0, 30))
        self.lvOnButton.setObjectName("lvOnButton")
        self.horizontalLayout_4.addWidget(self.lvOnButton)
        self.lvOffButton = QtWidgets.QPushButton(self.caenWidget)
        self.lvOffButton.setMinimumSize(QtCore.QSize(0, 34))
        self.lvOffButton.setObjectName("lvOffButton")
        self.horizontalLayout_4.addWidget(self.lvOffButton)
        self.lvLabel = QtWidgets.QLabel(self.caenWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lvLabel.sizePolicy().hasHeightForWidth())
        self.lvLabel.setSizePolicy(sizePolicy)
        self.lvLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.lvLabel.setObjectName("lvLabel")
        self.horizontalLayout_4.addWidget(self.lvLabel)
        self.lvLed = QtWidgets.QFrame(self.caenWidget)
        self.lvLed.setMinimumSize(QtCore.QSize(34, 34))
        self.lvLed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lvLed.setObjectName("lvLed")
        self.horizontalLayout_4.addWidget(self.lvLed)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.hvOnButton = QtWidgets.QPushButton(self.caenWidget)
        self.hvOnButton.setMinimumSize(QtCore.QSize(0, 30))
        self.hvOnButton.setObjectName("hvOnButton")
        self.horizontalLayout_5.addWidget(self.hvOnButton)
        self.hvOffButton = QtWidgets.QPushButton(self.caenWidget)
        self.hvOffButton.setMinimumSize(QtCore.QSize(0, 34))
        self.hvOffButton.setObjectName("hvOffButton")
        self.horizontalLayout_5.addWidget(self.hvOffButton)
        self.hvLabel = QtWidgets.QLabel(self.caenWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hvLabel.sizePolicy().hasHeightForWidth())
        self.hvLabel.setSizePolicy(sizePolicy)
        self.hvLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.hvLabel.setObjectName("hvLabel")
        self.horizontalLayout_5.addWidget(self.hvLabel)
        self.hvLed = QtWidgets.QFrame(self.caenWidget)
        self.hvLed.setMinimumSize(QtCore.QSize(34, 34))
        self.hvLed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.hvLed.setObjectName("hvLed")
        self.horizontalLayout_5.addWidget(self.hvLed)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.airONPB = QtWidgets.QPushButton(self.caenWidget)
        self.airONPB.setObjectName("airONPB")
        self.horizontalLayout_6.addWidget(self.airONPB)
        self.airOFFPB = QtWidgets.QPushButton(self.caenWidget)
        self.airOFFPB.setMinimumSize(QtCore.QSize(0, 30))
        self.airOFFPB.setObjectName("airOFFPB")
        self.horizontalLayout_6.addWidget(self.airOFFPB)
        self.tMaxLabel = QtWidgets.QLabel(self.caenWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tMaxLabel.sizePolicy().hasHeightForWidth())
        self.tMaxLabel.setSizePolicy(sizePolicy)
        self.tMaxLabel.setObjectName("tMaxLabel")
        self.horizontalLayout_6.addWidget(self.tMaxLabel)
        self.airLed = QtWidgets.QFrame(self.caenWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.airLed.sizePolicy().hasHeightForWidth())
        self.airLed.setSizePolicy(sizePolicy)
        self.airLed.setMinimumSize(QtCore.QSize(34, 34))
        self.airLed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.airLed.setObjectName("airLed")
        self.horizontalLayout_6.addWidget(self.airLed)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.verticalLayout_5.addWidget(self.caenWidget)
        self.plotWidget = QtWidgets.QWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy)
        self.plotWidget.setMinimumSize(QtCore.QSize(300, 400))
        self.plotWidget.setObjectName("plotWidget")
        self.verticalLayout_5.addWidget(self.plotWidget)
        self.gridLayout_4.addLayout(self.verticalLayout_5, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.groupBox = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout_5.addWidget(self.label_8, 1, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 3, 0, 1, 1)
        self.spacerCB = QtWidgets.QComboBox(self.groupBox)
        self.spacerCB.setObjectName("spacerCB")
        self.spacerCB.addItem("")
        self.spacerCB.addItem("")
        self.spacerCB.addItem("")
        self.spacerCB.addItem("")
        self.gridLayout_5.addWidget(self.spacerCB, 2, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 2, 0, 1, 1)
        self.spacerCB_2 = QtWidgets.QComboBox(self.groupBox)
        self.spacerCB_2.setObjectName("spacerCB_2")
        self.spacerCB_2.addItem("")
        self.gridLayout_5.addWidget(self.spacerCB_2, 3, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        self.label_11.setObjectName("label_11")
        self.gridLayout_5.addWidget(self.label_11, 4, 0, 1, 1)
        self.speedCB = QtWidgets.QComboBox(self.groupBox)
        self.speedCB.setObjectName("speedCB")
        self.speedCB.addItem("")
        self.speedCB.addItem("")
        self.speedCB.addItem("")
        self.gridLayout_5.addWidget(self.speedCB, 1, 1, 1, 1)
        self.spacerCB_3 = QtWidgets.QComboBox(self.groupBox)
        self.spacerCB_3.setObjectName("spacerCB_3")
        self.spacerCB_3.addItem("")
        self.spacerCB_3.addItem("")
        self.spacerCB_3.addItem("")
        self.gridLayout_5.addWidget(self.spacerCB_3, 4, 1, 1, 1)
        self.layertypeCB = QtWidgets.QComboBox(self.groupBox)
        self.layertypeCB.setObjectName("layertypeCB")
        self.layertypeCB.addItem("")
        self.gridLayout_5.addWidget(self.layertypeCB, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout_5.addWidget(self.label_4, 0, 0, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox)
        self.treeWidget = QtWidgets.QTreeWidget(self.tab_2)
        self.treeWidget.setMinimumSize(QtCore.QSize(661, 0))
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.verticalLayout_7.addWidget(self.treeWidget)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem5)
        self.selectModulePB = QtWidgets.QPushButton(self.tab_2)
        self.selectModulePB.setObjectName("selectModulePB")
        self.horizontalLayout_10.addWidget(self.selectModulePB)
        self.verticalLayout_7.addLayout(self.horizontalLayout_10)
        self.tabWidget.addTab(self.tab_2, "")
        self.moduleDetailsTab = QtWidgets.QWidget()
        self.moduleDetailsTab.setObjectName("moduleDetailsTab")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.moduleDetailsTab)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.moduleNameLabel = QtWidgets.QLabel(self.moduleDetailsTab)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.moduleNameLabel.setFont(font)
        self.moduleNameLabel.setText("")
        self.moduleNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.moduleNameLabel.setObjectName("moduleNameLabel")
        self.verticalLayout_8.addWidget(self.moduleNameLabel)
        self.detailsTree = QtWidgets.QTreeWidget(self.moduleDetailsTab)
        self.detailsTree.setColumnCount(2)
        self.detailsTree.setObjectName("detailsTree")
        self.verticalLayout_8.addWidget(self.detailsTree)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.editDetailsButton = QtWidgets.QPushButton(self.moduleDetailsTab)
        self.editDetailsButton.setObjectName("editDetailsButton")
        self.horizontalLayout_11.addWidget(self.editDetailsButton)
        self.saveDetailsButton = QtWidgets.QPushButton(self.moduleDetailsTab)
        self.saveDetailsButton.setObjectName("saveDetailsButton")
        self.horizontalLayout_11.addWidget(self.saveDetailsButton)
        self.verticalLayout_8.addLayout(self.horizontalLayout_11)
        self.tabWidget.addTab(self.moduleDetailsTab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.placeholdersHelpLabel = QtWidgets.QLabel(self.tab_3)
        self.placeholdersHelpLabel.setObjectName("placeholdersHelpLabel")
        self.verticalLayout_6.addWidget(self.placeholdersHelpLabel)
        self.commandsGroupBox = QtWidgets.QGroupBox(self.tab_3)
        self.commandsGroupBox.setObjectName("commandsGroupBox")
        self.formLayout = QtWidgets.QFormLayout(self.commandsGroupBox)
        self.formLayout.setObjectName("formLayout")
        self.checkIDLabel = QtWidgets.QLabel(self.commandsGroupBox)
        self.checkIDLabel.setObjectName("checkIDLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkIDLabel)
        self.checkIDCommandLE = QtWidgets.QLineEdit(self.commandsGroupBox)
        self.checkIDCommandLE.setObjectName("checkIDCommandLE")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.checkIDCommandLE)
        self.lightOnLabel = QtWidgets.QLabel(self.commandsGroupBox)
        self.lightOnLabel.setObjectName("lightOnLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lightOnLabel)
        self.lightOnCommandLE = QtWidgets.QLineEdit(self.commandsGroupBox)
        self.lightOnCommandLE.setObjectName("lightOnCommandLE")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lightOnCommandLE)
        self.darkTestLabel = QtWidgets.QLabel(self.commandsGroupBox)
        self.darkTestLabel.setObjectName("darkTestLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.darkTestLabel)
        self.darkTestCommandLE = QtWidgets.QLineEdit(self.commandsGroupBox)
        self.darkTestCommandLE.setObjectName("darkTestCommandLE")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.darkTestCommandLE)
        self.label_13 = QtWidgets.QLabel(self.commandsGroupBox)
        self.label_13.setObjectName("label_13")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.airCommandLE = QtWidgets.QLineEdit(self.commandsGroupBox)
        self.airCommandLE.setObjectName("airCommandLE")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.airCommandLE)
        self.label_14 = QtWidgets.QLabel(self.commandsGroupBox)
        self.label_14.setObjectName("label_14")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_14)
        self.resultsUrlLE = QtWidgets.QLineEdit(self.commandsGroupBox)
        self.resultsUrlLE.setObjectName("resultsUrlLE")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.resultsUrlLE)
        self.verticalLayout_6.addWidget(self.commandsGroupBox)
        self.apiGroupBox = QtWidgets.QGroupBox(self.tab_3)
        self.apiGroupBox.setObjectName("apiGroupBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.apiGroupBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.dbEndpointLabel = QtWidgets.QLabel(self.apiGroupBox)
        self.dbEndpointLabel.setObjectName("dbEndpointLabel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.dbEndpointLabel)
        self.dbEndpointLE = QtWidgets.QLineEdit(self.apiGroupBox)
        self.dbEndpointLE.setObjectName("dbEndpointLE")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.dbEndpointLE)
        self.mqttServerLabel = QtWidgets.QLabel(self.apiGroupBox)
        self.mqttServerLabel.setObjectName("mqttServerLabel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.mqttServerLabel)
        self.mqttServerLE = QtWidgets.QLineEdit(self.apiGroupBox)
        self.mqttServerLE.setObjectName("mqttServerLE")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.mqttServerLE)
        self.mqttTopicLabel = QtWidgets.QLabel(self.apiGroupBox)
        self.mqttTopicLabel.setObjectName("mqttTopicLabel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.mqttTopicLabel)
        self.mqttTopicLE = QtWidgets.QLineEdit(self.apiGroupBox)
        self.mqttTopicLE.setObjectName("mqttTopicLE")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.mqttTopicLE)
        self.verticalLayout_6.addWidget(self.apiGroupBox)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.applySettingsPB = QtWidgets.QPushButton(self.tab_3)
        self.applySettingsPB.setObjectName("applySettingsPB")
        self.horizontalLayout_9.addWidget(self.applySettingsPB)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem6)
        self.verticalLayout_6.addLayout(self.horizontalLayout_9)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem7)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.commandOutputTE = QtWidgets.QPlainTextEdit(self.tab_4)
        self.commandOutputTE.setReadOnly(True)
        self.commandOutputTE.setPlainText("")
        self.commandOutputTE.setObjectName("commandOutputTE")
        self.verticalLayout_4.addWidget(self.commandOutputTE)
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.tab_5)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.webView = QtWebEngineWidgets.QWebEngineView(self.tab_5)
        self.webView.setProperty("url", QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.gridLayout_6.addWidget(self.webView, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_5, "")
        self.gridLayout_3.addWidget(self.tabWidget, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Ring:</span></p></body></html>"))
        self.label.setText(_translate("MainWindow", "Ring ID"))
        self.label_2.setText(_translate("MainWindow", "Position"))
        self.label_7.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Module:</span></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "Module ID"))
        self.mountPB.setText(_translate("MainWindow", "Mount"))
        self.unmountPB.setText(_translate("MainWindow", "Un-mount"))
        self.fiberConnectionLabel.setText(_translate("MainWindow", "Not connected"))
        self.connectFiberPB.setText(_translate("MainWindow", "Connect Fiber"))
        self.powerConnectionLabel.setText(_translate("MainWindow", "Not connected"))
        self.connectPowerPB.setText(_translate("MainWindow", "Connect Power"))
        self.checkIDPB.setText(_translate("MainWindow", "Check ID"))
        self.checkIDlabel.setText(_translate("MainWindow", "TextLabel"))
        self.hvONTestPB.setText(_translate("MainWindow", "Dark Tests (HV on)"))
        self.hvOFFTestPB.setText(_translate("MainWindow", "Light On Tests (HV off)"))
        self.resultsLabel.setText(_translate("MainWindow", "<html><head/><body><p>Noise:</p><p>MPA: 0.0     </p><p>SSA: 0.0</p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Test Results (plots)"))
        self.label_6.setText(_translate("MainWindow", "CAEN control:"))
        self.lvOnButton.setText(_translate("MainWindow", "LV ON"))
        self.lvOffButton.setText(_translate("MainWindow", "LV OFF"))
        self.lvLabel.setText(_translate("MainWindow", "0.0"))
        self.lvLed.setStyleSheet(_translate("MainWindow", "background-color: red;"))
        self.hvOnButton.setText(_translate("MainWindow", "HV ON"))
        self.hvOffButton.setText(_translate("MainWindow", "HV OFF"))
        self.hvLabel.setText(_translate("MainWindow", "0.0"))
        self.hvLed.setStyleSheet(_translate("MainWindow", "background-color: red;"))
        self.airONPB.setText(_translate("MainWindow", "Air ON"))
        self.airOFFPB.setText(_translate("MainWindow", "Air OFF"))
        self.tMaxLabel.setText(_translate("MainWindow", "Tmax: 0.0"))
        self.airLed.setStyleSheet(_translate("MainWindow", "background-color: red;"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Mount and Test"))
        self.groupBox.setTitle(_translate("MainWindow", "Filters:"))
        self.label_8.setText(_translate("MainWindow", "Speed:"))
        self.label_10.setText(_translate("MainWindow", "Grade:"))
        self.spacerCB.setItemText(0, _translate("MainWindow", "any"))
        self.spacerCB.setItemText(1, _translate("MainWindow", "4.0mm"))
        self.spacerCB.setItemText(2, _translate("MainWindow", "2.6mm"))
        self.spacerCB.setItemText(3, _translate("MainWindow", "1.8mm"))
        self.label_9.setText(_translate("MainWindow", "Spacer:"))
        self.spacerCB_2.setItemText(0, _translate("MainWindow", "any"))
        self.label_11.setText(_translate("MainWindow", "Status:"))
        self.speedCB.setItemText(0, _translate("MainWindow", "any"))
        self.speedCB.setItemText(1, _translate("MainWindow", "5G"))
        self.speedCB.setItemText(2, _translate("MainWindow", "10G"))
        self.spacerCB_3.setItemText(0, _translate("MainWindow", "Ready For Mounting"))
        self.spacerCB_3.setItemText(1, _translate("MainWindow", "Mounted"))
        self.spacerCB_3.setItemText(2, _translate("MainWindow", "To Be Tested"))
        self.layertypeCB.setItemText(0, _translate("MainWindow", "any"))
        self.label_4.setText(_translate("MainWindow", "Layer type:"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Name"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Inventory Slot"))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Speed"))
        self.treeWidget.headerItem().setText(3, _translate("MainWindow", "Spacer"))
        self.treeWidget.headerItem().setText(4, _translate("MainWindow", "Status"))
        self.treeWidget.headerItem().setText(5, _translate("MainWindow", "Description"))
        self.treeWidget.headerItem().setText(6, _translate("MainWindow", "Connections"))
        self.treeWidget.headerItem().setText(7, _translate("MainWindow", "Mounted_on"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("MainWindow", "PS_PG_99999"))
        self.treeWidget.topLevelItem(0).setText(1, _translate("MainWindow", "3B_05"))
        self.treeWidget.topLevelItem(0).setText(2, _translate("MainWindow", "5G"))
        self.treeWidget.topLevelItem(0).setText(3, _translate("MainWindow", "40"))
        self.treeWidget.topLevelItem(0).setText(4, _translate("MainWindow", "A++"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.selectModulePB.setText(_translate("MainWindow", "Select Module"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Module Inventory"))
        self.detailsTree.headerItem().setText(0, _translate("MainWindow", "Field"))
        self.detailsTree.headerItem().setText(1, _translate("MainWindow", "Value"))
        self.editDetailsButton.setText(_translate("MainWindow", "Edit Selected"))
        self.saveDetailsButton.setText(_translate("MainWindow", "Save Changes"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.moduleDetailsTab), _translate("MainWindow", "Module Details"))
        self.placeholdersHelpLabel.setText(_translate("MainWindow", "Available placeholders:\n"
"{ring_id} - Ring ID\n"
"{position} - Position number\n"
"{module_id} - Module ID\n"
"{fiber} - Selected fiber\n"
"{power} - Selected power source\n"
"{fiber_endpoint} - Fiber endpoint (i.e. FC7)\n"
"\n"
"Placeholders can be used in commands."))
        self.commandsGroupBox.setTitle(_translate("MainWindow", "Test Commands"))
        self.checkIDLabel.setText(_translate("MainWindow", "Check ID Command:"))
        self.checkIDCommandLE.setText(_translate("MainWindow", "check_id.sh --module {module_id} --position {position}"))
        self.lightOnLabel.setText(_translate("MainWindow", "Light-On Test Command:"))
        self.lightOnCommandLE.setText(_translate("MainWindow", "light_on_test.sh --ring {ring_id} --pos {position} --fiber {fiber}"))
        self.darkTestLabel.setText(_translate("MainWindow", "Dark Test Command:"))
        self.darkTestCommandLE.setText(_translate("MainWindow", "dark_test.sh --module {module_id} --power {power}"))
        self.label_13.setText(_translate("MainWindow", "Air control command:"))
        self.airCommandLE.setText(_translate("MainWindow", "air.sh {airOn}"))
        self.label_14.setText(_translate("MainWindow", "Results URL:"))
        self.resultsUrlLE.setText(_translate("MainWindow", "file:Results/html/latest/index.html"))
        self.apiGroupBox.setTitle(_translate("MainWindow", "API Settings"))
        self.dbEndpointLabel.setText(_translate("MainWindow", "Database URL:"))
        self.dbEndpointLE.setText(_translate("MainWindow", "http://localhost:5000"))
        self.mqttServerLabel.setText(_translate("MainWindow", "MQTT Server:"))
        self.mqttServerLE.setText(_translate("MainWindow", "test.mosquitto.org"))
        self.mqttTopicLabel.setText(_translate("MainWindow", "MQTT Topic:"))
        self.mqttTopicLE.setText(_translate("MainWindow", "/ar/thermal/image"))
        self.applySettingsPB.setText(_translate("MainWindow", "Apply settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Commands Output"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "Plots"))
from PyQt5 import QtWebEngineWidgets
