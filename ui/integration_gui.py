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
        MainWindow.resize(720, 705)
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
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.ringLE = QtWidgets.QLineEdit(self.tab)
        self.ringLE.setObjectName("ringLE")
        self.horizontalLayout.addWidget(self.ringLE)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.positionLE = QtWidgets.QLineEdit(self.tab)
        self.positionLE.setObjectName("positionLE")
        self.horizontalLayout.addWidget(self.positionLE)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.graphicsView = QtWidgets.QGraphicsView(self.tab)
        self.graphicsView.setMinimumSize(QtCore.QSize(300, 300))
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
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
        spacerItem1 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.mountPB = QtWidgets.QPushButton(self.tab)
        self.mountPB.setObjectName("mountPB")
        self.horizontalLayout_2.addWidget(self.mountPB)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.fiberCB = QtWidgets.QComboBox(self.tab)
        self.fiberCB.setObjectName("fiberCB")
        self.gridLayout.addWidget(self.fiberCB, 0, 1, 1, 1)
        self.powerConnectionLabel = QtWidgets.QLabel(self.tab)
        self.powerConnectionLabel.setObjectName("powerConnectionLabel")
        self.gridLayout.addWidget(self.powerConnectionLabel, 3, 0, 1, 2)
        self.connectFiberPB = QtWidgets.QPushButton(self.tab)
        self.connectFiberPB.setObjectName("connectFiberPB")
        self.gridLayout.addWidget(self.connectFiberPB, 0, 0, 1, 1)
        self.connectPowerLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectPowerLED.sizePolicy().hasHeightForWidth())
        self.connectPowerLED.setSizePolicy(sizePolicy)
        self.connectPowerLED.setMinimumSize(QtCore.QSize(30, 34))
        self.connectPowerLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.connectPowerLED.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.connectPowerLED.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.connectPowerLED.setObjectName("connectPowerLED")
        self.gridLayout.addWidget(self.connectPowerLED, 2, 3, 1, 1)
        self.powerCB = QtWidgets.QComboBox(self.tab)
        self.powerCB.setObjectName("powerCB")
        self.gridLayout.addWidget(self.powerCB, 2, 1, 1, 1)
        self.fiberConnectionLabel = QtWidgets.QLabel(self.tab)
        self.fiberConnectionLabel.setObjectName("fiberConnectionLabel")
        self.gridLayout.addWidget(self.fiberConnectionLabel, 1, 0, 1, 2)
        self.connectFiberLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectFiberLED.sizePolicy().hasHeightForWidth())
        self.connectFiberLED.setSizePolicy(sizePolicy)
        self.connectFiberLED.setMinimumSize(QtCore.QSize(30, 34))
        self.connectFiberLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.connectFiberLED.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.connectFiberLED.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.connectFiberLED.setObjectName("connectFiberLED")
        self.gridLayout.addWidget(self.connectFiberLED, 0, 3, 1, 1)
        self.connectPowerPB = QtWidgets.QPushButton(self.tab)
        self.connectPowerPB.setObjectName("connectPowerPB")
        self.gridLayout.addWidget(self.connectPowerPB, 2, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 0, 2, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.horizontalLayout_6.addLayout(self.verticalLayout_3)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.checkIDPB = QtWidgets.QPushButton(self.tab)
        self.checkIDPB.setObjectName("checkIDPB")
        self.horizontalLayout_3.addWidget(self.checkIDPB)
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.checkIDLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkIDLED.sizePolicy().hasHeightForWidth())
        self.checkIDLED.setSizePolicy(sizePolicy)
        self.checkIDLED.setMinimumSize(QtCore.QSize(30, 30))
        self.checkIDLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.checkIDLED.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.checkIDLED.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.checkIDLED.setObjectName("checkIDLED")
        self.horizontalLayout_3.addWidget(self.checkIDLED)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem4, 0, 1, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem5, 1, 1, 1, 1)
        self.hvOFFTestCB = QtWidgets.QCheckBox(self.tab)
        self.hvOFFTestCB.setEnabled(False)
        self.hvOFFTestCB.setText("")
        self.hvOFFTestCB.setObjectName("hvOFFTestCB")
        self.gridLayout_2.addWidget(self.hvOFFTestCB, 0, 2, 1, 1)
        self.hvOFFTestPB = QtWidgets.QPushButton(self.tab)
        self.hvOFFTestPB.setObjectName("hvOFFTestPB")
        self.gridLayout_2.addWidget(self.hvOFFTestPB, 0, 0, 1, 1)
        self.hvONTestCB = QtWidgets.QCheckBox(self.tab)
        self.hvONTestCB.setEnabled(False)
        self.hvONTestCB.setText("")
        self.hvONTestCB.setObjectName("hvONTestCB")
        self.gridLayout_2.addWidget(self.hvONTestCB, 1, 2, 1, 1)
        self.hvONTestLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hvONTestLED.sizePolicy().hasHeightForWidth())
        self.hvONTestLED.setSizePolicy(sizePolicy)
        self.hvONTestLED.setMinimumSize(QtCore.QSize(30, 30))
        self.hvONTestLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.hvONTestLED.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.hvONTestLED.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.hvONTestLED.setObjectName("hvONTestLED")
        self.gridLayout_2.addWidget(self.hvONTestLED, 1, 3, 1, 1)
        self.hvONTestPB = QtWidgets.QPushButton(self.tab)
        self.hvONTestPB.setObjectName("hvONTestPB")
        self.gridLayout_2.addWidget(self.hvONTestPB, 1, 0, 1, 1)
        self.hvOFFTestLED = QtWidgets.QFrame(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hvOFFTestLED.sizePolicy().hasHeightForWidth())
        self.hvOFFTestLED.setSizePolicy(sizePolicy)
        self.hvOFFTestLED.setMinimumSize(QtCore.QSize(30, 30))
        self.hvOFFTestLED.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.hvOFFTestLED.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.hvOFFTestLED.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.hvOFFTestLED.setObjectName("hvOFFTestLED")
        self.gridLayout_2.addWidget(self.hvOFFTestLED, 0, 3, 1, 1)
        self.verticalLayout_5.addLayout(self.gridLayout_2)
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
        spacerItem6 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem6)
        self.label_6 = QtWidgets.QLabel(self.caenWidget)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lvOnButton = QtWidgets.QPushButton(self.caenWidget)
        self.lvOnButton.setMinimumSize(QtCore.QSize(0, 34))
        self.lvOnButton.setObjectName("lvOnButton")
        self.horizontalLayout_4.addWidget(self.lvOnButton)
        self.lvOffButton = QtWidgets.QPushButton(self.caenWidget)
        self.lvOffButton.setMinimumSize(QtCore.QSize(0, 34))
        self.lvOffButton.setObjectName("lvOffButton")
        self.horizontalLayout_4.addWidget(self.lvOffButton)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.lvLed = QtWidgets.QFrame(self.caenWidget)
        self.lvLed.setMinimumSize(QtCore.QSize(34, 34))
        self.lvLed.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.lvLed.setObjectName("lvLed")
        self.horizontalLayout_4.addWidget(self.lvLed)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.lvLabel = QtWidgets.QLabel(self.caenWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lvLabel.sizePolicy().hasHeightForWidth())
        self.lvLabel.setSizePolicy(sizePolicy)
        self.lvLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.lvLabel.setObjectName("lvLabel")
        self.verticalLayout_2.addWidget(self.lvLabel)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.hvOnButton = QtWidgets.QPushButton(self.caenWidget)
        self.hvOnButton.setMinimumSize(QtCore.QSize(0, 34))
        self.hvOnButton.setObjectName("hvOnButton")
        self.horizontalLayout_5.addWidget(self.hvOnButton)
        self.hvOffButton = QtWidgets.QPushButton(self.caenWidget)
        self.hvOffButton.setMinimumSize(QtCore.QSize(0, 34))
        self.hvOffButton.setObjectName("hvOffButton")
        self.horizontalLayout_5.addWidget(self.hvOffButton)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_5.addItem(spacerItem8)
        self.hvLed = QtWidgets.QFrame(self.caenWidget)
        self.hvLed.setMinimumSize(QtCore.QSize(34, 34))
        self.hvLed.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.hvLed.setObjectName("hvLed")
        self.horizontalLayout_5.addWidget(self.hvLed)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.hvLabel = QtWidgets.QLabel(self.caenWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hvLabel.sizePolicy().hasHeightForWidth())
        self.hvLabel.setSizePolicy(sizePolicy)
        self.hvLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.hvLabel.setObjectName("hvLabel")
        self.verticalLayout_2.addWidget(self.hvLabel)
        self.verticalLayout_5.addWidget(self.caenWidget)
        self.plotWidget = QtWidgets.QWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy)
        self.plotWidget.setMinimumSize(QtCore.QSize(64, 280))
        self.plotWidget.setObjectName("plotWidget")
        self.verticalLayout_5.addWidget(self.plotWidget)
        self.horizontalLayout_6.addLayout(self.verticalLayout_5)
        self.gridLayout_4.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)
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
        self.gridLayout_5.addWidget(self.label_8, 0, 0, 1, 1)
        self.speedCB = QtWidgets.QComboBox(self.groupBox)
        self.speedCB.setObjectName("speedCB")
        self.speedCB.addItem("")
        self.speedCB.addItem("")
        self.speedCB.addItem("")
        self.gridLayout_5.addWidget(self.speedCB, 0, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 1, 0, 1, 1)
        self.spacerCB = QtWidgets.QComboBox(self.groupBox)
        self.spacerCB.setObjectName("spacerCB")
        self.spacerCB.addItem("")
        self.spacerCB.addItem("")
        self.spacerCB.addItem("")
        self.spacerCB.addItem("")
        self.gridLayout_5.addWidget(self.spacerCB, 1, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 2, 0, 1, 1)
        self.spacerCB_2 = QtWidgets.QComboBox(self.groupBox)
        self.spacerCB_2.setObjectName("spacerCB_2")
        self.spacerCB_2.addItem("")
        self.gridLayout_5.addWidget(self.spacerCB_2, 2, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        self.label_11.setObjectName("label_11")
        self.gridLayout_5.addWidget(self.label_11, 3, 0, 1, 1)
        self.spacerCB_3 = QtWidgets.QComboBox(self.groupBox)
        self.spacerCB_3.setObjectName("spacerCB_3")
        self.spacerCB_3.addItem("")
        self.spacerCB_3.addItem("")
        self.spacerCB_3.addItem("")
        self.gridLayout_5.addWidget(self.spacerCB_3, 3, 1, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox)
        self.treeWidget = QtWidgets.QTreeWidget(self.tab_2)
        self.treeWidget.setMinimumSize(QtCore.QSize(661, 0))
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.verticalLayout_7.addWidget(self.treeWidget)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_10.addItem(spacerItem9)
        self.selectModulePB = QtWidgets.QPushButton(self.tab_2)
        self.selectModulePB.setObjectName("selectModulePB")
        self.horizontalLayout_10.addWidget(self.selectModulePB)
        self.verticalLayout_7.addLayout(self.horizontalLayout_10)
        self.tabWidget.addTab(self.tab_2, "")
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
        self.apiUrlLabel = QtWidgets.QLabel(self.apiGroupBox)
        self.apiUrlLabel.setObjectName("apiUrlLabel")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.apiUrlLabel)
        self.apiBaseUrlLE = QtWidgets.QLineEdit(self.apiGroupBox)
        self.apiBaseUrlLE.setObjectName("apiBaseUrlLE")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.apiBaseUrlLE)
        self.connectFiberLabel = QtWidgets.QLabel(self.apiGroupBox)
        self.connectFiberLabel.setObjectName("connectFiberLabel")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.connectFiberLabel)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.connectFiberMethodCB = QtWidgets.QComboBox(self.apiGroupBox)
        self.connectFiberMethodCB.setObjectName("connectFiberMethodCB")
        self.connectFiberMethodCB.addItem("")
        self.connectFiberMethodCB.addItem("")
        self.connectFiberMethodCB.addItem("")
        self.connectFiberMethodCB.addItem("")
        self.horizontalLayout_7.addWidget(self.connectFiberMethodCB)
        self.connectFiberEndpointLE = QtWidgets.QLineEdit(self.apiGroupBox)
        self.connectFiberEndpointLE.setObjectName("connectFiberEndpointLE")
        self.horizontalLayout_7.addWidget(self.connectFiberEndpointLE)
        self.formLayout_2.setLayout(4, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_7)
        self.connectPowerLabel = QtWidgets.QLabel(self.apiGroupBox)
        self.connectPowerLabel.setObjectName("connectPowerLabel")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.connectPowerLabel)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.connectPowerMethodCB = QtWidgets.QComboBox(self.apiGroupBox)
        self.connectPowerMethodCB.setObjectName("connectPowerMethodCB")
        self.connectPowerMethodCB.addItem("")
        self.connectPowerMethodCB.addItem("")
        self.connectPowerMethodCB.addItem("")
        self.connectPowerMethodCB.addItem("")
        self.horizontalLayout_8.addWidget(self.connectPowerMethodCB)
        self.connectPowerEndpointLE = QtWidgets.QLineEdit(self.apiGroupBox)
        self.connectPowerEndpointLE.setObjectName("connectPowerEndpointLE")
        self.horizontalLayout_8.addWidget(self.connectPowerEndpointLE)
        self.formLayout_2.setLayout(5, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_8)
        self.verticalLayout_6.addWidget(self.apiGroupBox)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_9.addItem(spacerItem10)
        self.applySettingsPB = QtWidgets.QPushButton(self.tab_3)
        self.applySettingsPB.setObjectName("applySettingsPB")
        self.horizontalLayout_9.addWidget(self.applySettingsPB)
        self.verticalLayout_6.addLayout(self.horizontalLayout_9)
        spacerItem11 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem11)
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
        self.label.setText(_translate("MainWindow", "Ring ID"))
        self.label_2.setText(_translate("MainWindow", "Position"))
        self.label_5.setText(_translate("MainWindow", "Ring Position"))
        self.label_7.setText(_translate("MainWindow", "DB actions"))
        self.label_3.setText(_translate("MainWindow", "Module ID"))
        self.mountPB.setText(_translate("MainWindow", "Mount"))
        self.powerConnectionLabel.setText(_translate("MainWindow", "Not connected"))
        self.connectFiberPB.setText(_translate("MainWindow", "Connect Fiber"))
        self.fiberConnectionLabel.setText(_translate("MainWindow", "Not connected"))
        self.connectPowerPB.setText(_translate("MainWindow", "Connect Power"))
        self.checkIDPB.setText(_translate("MainWindow", "Check ID"))
        self.label_4.setText(_translate("MainWindow", "TextLabel"))
        self.hvOFFTestPB.setText(_translate("MainWindow", "Light On Tests (HV off)"))
        self.hvONTestPB.setText(_translate("MainWindow", "Dark Tests (HV on)"))
        self.label_6.setText(_translate("MainWindow", "CAEN control:"))
        self.lvOnButton.setText(_translate("MainWindow", "LV ON"))
        self.lvOffButton.setText(_translate("MainWindow", "LV OFF"))
        self.lvLed.setStyleSheet(_translate("MainWindow", "background-color: red;"))
        self.lvLabel.setText(_translate("MainWindow", "0.0"))
        self.hvOnButton.setText(_translate("MainWindow", "HV ON"))
        self.hvOffButton.setText(_translate("MainWindow", "HV OFF"))
        self.hvLed.setStyleSheet(_translate("MainWindow", "background-color: red;"))
        self.hvLabel.setText(_translate("MainWindow", "0.0"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Mount and Test"))
        self.groupBox.setTitle(_translate("MainWindow", "Filters:"))
        self.label_8.setText(_translate("MainWindow", "Speed:"))
        self.speedCB.setItemText(0, _translate("MainWindow", "any"))
        self.speedCB.setItemText(1, _translate("MainWindow", "5G"))
        self.speedCB.setItemText(2, _translate("MainWindow", "10G"))
        self.label_9.setText(_translate("MainWindow", "Spacer:"))
        self.spacerCB.setItemText(0, _translate("MainWindow", "any"))
        self.spacerCB.setItemText(1, _translate("MainWindow", "4.0mm"))
        self.spacerCB.setItemText(2, _translate("MainWindow", "2.6mm"))
        self.spacerCB.setItemText(3, _translate("MainWindow", "1.8mm"))
        self.label_10.setText(_translate("MainWindow", "Grade:"))
        self.spacerCB_2.setItemText(0, _translate("MainWindow", "any"))
        self.label_11.setText(_translate("MainWindow", "Status:"))
        self.spacerCB_3.setItemText(0, _translate("MainWindow", "Ready For Mounting"))
        self.spacerCB_3.setItemText(1, _translate("MainWindow", "Mounted"))
        self.spacerCB_3.setItemText(2, _translate("MainWindow", "To Be Tested"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Name"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Inventory Slot"))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Speed"))
        self.treeWidget.headerItem().setText(3, _translate("MainWindow", "Spacer"))
        self.treeWidget.headerItem().setText(4, _translate("MainWindow", "Grade"))
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
        self.placeholdersHelpLabel.setText(_translate("MainWindow", "Available placeholders:\n"
"{ring_id} - Ring ID\n"
"{position} - Position number\n"
"{module_id} - Module ID\n"
"{fiber} - Selected fiber\n"
"{power} - Selected power source\n"
"\n"
"Placeholders can be used in commands and API endpoints."))
        self.commandsGroupBox.setTitle(_translate("MainWindow", "Test Commands"))
        self.checkIDLabel.setText(_translate("MainWindow", "Check ID Command:"))
        self.checkIDCommandLE.setText(_translate("MainWindow", "check_id.sh --module {module_id} --position {position}"))
        self.lightOnLabel.setText(_translate("MainWindow", "Light On Test Command:"))
        self.lightOnCommandLE.setText(_translate("MainWindow", "light_on_test.sh --ring {ring_id} --pos {position} --fiber {fiber}"))
        self.darkTestLabel.setText(_translate("MainWindow", "Dark Test Command:"))
        self.darkTestCommandLE.setText(_translate("MainWindow", "dark_test.sh --module {module_id} --power {power}"))
        self.apiGroupBox.setTitle(_translate("MainWindow", "API Settings"))
        self.dbEndpointLabel.setText(_translate("MainWindow", "DB Endpoint:"))
        self.dbEndpointLE.setText(_translate("MainWindow", "http://localhost:5000/modules"))
        self.mqttServerLabel.setText(_translate("MainWindow", "MQTT Server:"))
        self.mqttServerLE.setText(_translate("MainWindow", "test.mosquitto.org"))
        self.mqttTopicLabel.setText(_translate("MainWindow", "MQTT Topic:"))
        self.mqttTopicLE.setText(_translate("MainWindow", "/ar/thermal/image"))
        self.apiUrlLabel.setText(_translate("MainWindow", "API Base URL:"))
        self.apiBaseUrlLE.setText(_translate("MainWindow", "http://localhost:8000/api"))
        self.connectFiberLabel.setText(_translate("MainWindow", "Connect Fiber Endpoint:"))
        self.connectFiberMethodCB.setItemText(0, _translate("MainWindow", "POST"))
        self.connectFiberMethodCB.setItemText(1, _translate("MainWindow", "GET"))
        self.connectFiberMethodCB.setItemText(2, _translate("MainWindow", "PUT"))
        self.connectFiberMethodCB.setItemText(3, _translate("MainWindow", "DELETE"))
        self.connectFiberEndpointLE.setText(_translate("MainWindow", "connect/fiber/{fiber}"))
        self.connectPowerLabel.setText(_translate("MainWindow", "Connect Power Endpoint:"))
        self.connectPowerMethodCB.setItemText(0, _translate("MainWindow", "POST"))
        self.connectPowerMethodCB.setItemText(1, _translate("MainWindow", "GET"))
        self.connectPowerMethodCB.setItemText(2, _translate("MainWindow", "PUT"))
        self.connectPowerMethodCB.setItemText(3, _translate("MainWindow", "DELETE"))
        self.connectPowerEndpointLE.setText(_translate("MainWindow", "connect/power/{power}"))
        self.applySettingsPB.setText(_translate("MainWindow", "Apply Settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Commands Output"))
