#!/bin/env python3
#create QT GUI with one button to send message to TCP server
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QHBoxLayout, QFrame, QLabel
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import socket
import json
BUFFER_SIZE = 100000

class tcp_util():
    """Utility class for tcp
    comunication management. """
    def __init__(self, ip, port):
        self.ip          = ip
        self.port        = port
        self.socket      = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.headerBytes = 4

        self.connectSocket()
        pass

    def __del__ (self):
        """Desctuctor, closes socket"""
        try:
            self.closeSocket()
        except:
            pass

    def connectSocket(self):
        """Connects socket"""
        self.socket.connect((self.ip,self.port))
        pass

    def closeSocket(self):
        """Closes socket connection"""
        self.socket.close()
        pass

    def sendMessage(self,message):
        """Encodes message and sends it on socket"""
        encodedMessage = self.encodeMessage(message)
        self.socket.send(encodedMessage)
        pass

    def encodeMessage(self,message):
        """Encodes message adding 4 bytes header"""
        messageLength = len(message) + self.headerBytes +4
        N=0
        encodedMessage = (messageLength).to_bytes(4, byteorder='big') + N.to_bytes(4, byteorder='big') + message.encode('utf-8')
        return encodedMessage

from argparse import Namespace

class caenGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CAEN GUI')
#        self.setGeometry(100, 100, 300, 400)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
#        self.channels = ['HV011','CR01','CR02','CR03','CR04']+["BLV%02d"%x for x in range(1,11)] + ['INT%02d'%x for x in range(1,5)]
#       self.channels = ['CR01','CR02','CR03','CR04','BLV07','BLV08','BLV09','BLV10']
#        self.channels=["BLV11","BLV12","HV012","HV011"]
        self.channels=[]
        for s in [6,7,8,9,10,11]:
            self.channels +=['LV%d_%d'%(s,x) for x in range(1,9)]
        for s in [0,1,2,3]:
            self.channels +=['HV%d_%d'%(s,x) for x in range(1,13)]

        self.led={}
        self.label={}
        #add buttons for On and Off, a status led and a voltage value for each channel in a new horizontal layour
        #object then add the horizontal layout to the main vertical layout
        for i,channel in enumerate(self.channels):
            if i%24 ==0 :
                line =  QFrame()
                line.setFrameShape(QFrame.VLine);
                self.layout.addWidget(line)
                vlayout=QVBoxLayout()
                self.layout.addLayout(vlayout)
            hlayout=QHBoxLayout()
            vlayout.addLayout(hlayout)
            l=QLabel(channel+":")
            hlayout.addWidget(l)
            self.button = QPushButton('ON', self)
            self.button.setMinimumWidth(30)
            self.button.clicked.connect(lambda checked,channel=channel: self.on(channel))
            hlayout.addWidget(self.button)
            self.button = QPushButton('OFF', self)
            self.button.setMinimumWidth(30)
            self.button.clicked.connect(lambda checked,channel=channel: self.off(channel))
            hlayout.addWidget(self.button)
            #use QFrame as a led
            self.label[channel] = QLabel('n/a')
            self.label[channel].setFont(QFont( "Arial", 9))
            hlayout.addWidget(self.label[channel])
            self.led[channel] = QFrame(self)
            self.led[channel].setFrameShape(QFrame.Box)
            self.led[channel].setFixedSize(30,30)

            self.led[channel].setStyleSheet("background-color: red")

            hlayout.addWidget(self.led[channel])



        #create timer for periodic update of the GUI with info from caen
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(2000)
        
        self.show()

    @pyqtSlot()
    def update(self):
      try:
        ret=self.send('GetStatus,PowerSupplyId:caen',True)
        for channel in self.channels:
            #self.led[channel].setOn(ret['caen_'+channel+'_IsOn']>0.5)
          try:
            if ret['caen_'+channel+'_IsOn']>0.5:
                self.led[channel].setStyleSheet("background-color: green")
            else:
                self.led[channel].setStyleSheet("background-color: red")
#            self.label[channel].setText(str(ret['caen_'+channel+'_Voltage']))
            #set label to Voltage, Current, Power
#            self.label[channel].setText('V: '+str(ret['caen_'+channel+'_Voltage'])+' C: '+str(ret['caen_'+channel+'_Current']))
            if "LV" in  channel :
                self.label[channel].setText(f'V: {ret["caen_"+channel+"_Voltage"]:1.1f}V\n I: {ret["caen_"+channel+"_Current"]:1.1f}A ({ret["caen_"+channel+"_Voltage"]*ret["caen_"+channel+"_Current"]:1.1f}W)')  
            else:
                self.label[channel].setText(f'V: {ret["caen_"+channel+"_Voltage"]:3.1f}V\nI: {ret["caen_"+channel+"_Current"]:1.2f}uA')
          except:
              print("No info for", channel)
      except:
          print("Cannot parse")
    @pyqtSlot()
    def on(self,channel):
        self.send('TurnOn,PowerSupplyId:caen,ChannelId:'+channel)
    @pyqtSlot()
    def off(self,channel):
        self.send('TurnOff,PowerSupplyId:caen,ChannelId:'+channel)

    def send(self,message,receive=False):
        print(message)
        tcpClass = tcp_util(ip='192.168.0.45',port=7000)
        tcpClass.sendMessage(message)
        try:
          if receive :
            data = tcpClass.socket.recv(BUFFER_SIZE)[8:].decode("utf-8")
            print(data)
            parsedData={}
            for token in data.split(',') :
                if token.startswith('caen'):
                    key,value=token.split(":")
                    value=float(value)
                    parsedData[key]=value
            print(json.dumps(parsedData,indent=4),flush=True)
            return parsedData
        except:
            print("Cannot parse")
def main():
    app = QApplication(sys.argv)
    ex = caenGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


