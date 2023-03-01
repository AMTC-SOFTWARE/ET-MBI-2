from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QObject, Qt
from paho.mqtt.client import Client
from paho.mqtt import publish
from pickle import load, dump
from os.path import exists
from cv2 import imwrite
from time import sleep
from os import system
from copy import copy
import json
#import requests    #Descomentar el día que se habilite el envío de info al servidor de P2
#import datetime    #Descomentar el día que se habilite el envío de info al servidor de P2

from toolkit.admin.view import admin, torques
from toolkit.admin.model import Model
from gui.view import PopOut    #Descomentar el día que se habilite el envío de info al servidor de P2

#from toolkit.plugins.rework import Rework


class Admin (QDialog):
    rcv     = pyqtSignal()

    def __init__(self, data):
        self.data = data
        super().__init__(data.mainWindow)
        self.ui = admin.Ui_admin()
        self.ui.setupUi(self)
        self.model = Model()
        self.user_type = self.data.local_data["user"]["type"]
        self.client = Client()
        self.qw_torques = Torques(model = self.model, client = self.client, parent = self)
        self.config = {}
        self.kiosk_mode = True
        self.pop_out = PopOut(self)    #Descomentar el día que se habilite el envío de info al servidor de P2

        self.torques = False

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        QTimer.singleShot(100, self.startClient)

        #if exists("data\config"):
        #    with open("data\config", "rb") as f:
        #        self.config = load(f)
        #        if "untwist" in self.config:
        #            if self.config["untwist"] == True:
        #                self.ui.checkBox_2.setChecked(True)
        #            else:
        #                self.ui.checkBox_2.setChecked(False)
        #else:
        #    self.config["untwist"] = False

        if self.data.config_data["untwist"]:
            self.ui.checkBox_4.setChecked(True)
        else:
            self.ui.checkBox_4.setChecked(False)

        if self.data.config_data["flexible_mode"]:
            self.ui.checkBox_5.setChecked(True)
        else:
            self.ui.checkBox_5.setChecked(False)

        if self.data.config_data["trazabilidad"]:
            self.ui.checkBox_6.setChecked(True)
        else:
            self.ui.checkBox_6.setChecked(False)

        if self.data.config_data["untangle_mode"]:
            self.ui.checkBox_3.setChecked(True)
        else:
            self.ui.checkBox_3.setChecked(False)


        self.ui.btn_off.setEnabled(False) 

        self.ui.btn_torque.clicked.connect(self.qw_torques.show)
        self.ui.btn_torque.clicked.connect(self.manualTorque)       #botón de TorqueManual "profile": 10 para calibración de Calidad
        self.ui.btn_reset.clicked.connect(self.resetMachine)        #botón de Reinicio de PC
        self.ui.btn_off.clicked.connect(self.poweroff)              #botón de Apagado de PC

        self.ui.checkBox_1.stateChanged.connect(self.onClicked_1)   #checkBox_1 = Abrir Carpetas                                (Abrir Explorador Windows)
        self.ui.checkBox_2.stateChanged.connect(self.onClicked_2)   #checkBox_2 = Ocultar/Mostrar GDI                           (GraphicalDeviceInterface)
        self.ui.checkBox_3.stateChanged.connect(self.onClicked_3)   #checkBox_3 = self.data.config_data["untangle_mode"] = True (RETRABAJO TERMINALES INVERTIDAS)
        self.ui.checkBox_4.stateChanged.connect(self.onClicked_4)   #checkBox_4 = self.data.config_data["untwist"] = True       (MODO DESAPRIETE)
        self.ui.checkBox_5.stateChanged.connect(self.onClicked_5)   #checkBox_5 = self.data.config_data["flexible_mode"] = True (RETRABAJO CON CAMBIO DE CAJA)
        self.ui.checkBox_6.stateChanged.connect(self.onClicked_6)   #checkBox_6 = self.data.config_data["trazabilidad"] = True  (TRAZABILIDAD)
        
        self.rcv.connect(self.qw_torques.input)
        self.permissions()

######################################### Plugins #######################################
        #self.qw_rework = None
        #self.ui.btn_off.clicked.connect(self.show_rework)

    def permissions (self):
        if self.user_type == "SUPERUSUARIO" or self.user_type == "AMTC":
            self.ui.btn_off.setEnabled(True)        #power off PC
            self.ui.btn_reset.setEnabled(True)      #reset PC
            self.ui.btn_torque.setEnabled(True)     #torque manual (profile 10)
            self.ui.checkBox_1.setEnabled(True)     #Abrir Explorador Windows
            self.ui.checkBox_2.setEnabled(True)     #GDI
            self.ui.checkBox_3.setEnabled(True)     #retrabajo de terminales
            self.ui.checkBox_4.setEnabled(True)     #desapriete
            self.ui.checkBox_5.setEnabled(True)     #retrabajo con cambio de caja
            self.ui.checkBox_6.setEnabled(True)     #trazabilidad
        elif self.user_type == "CALIDAD" or self.user_type == "SUPCALIDAD":
            self.ui.btn_off.setEnabled(False)       #power off PC
            self.ui.btn_reset.setEnabled(False)     #reset PC
            self.ui.btn_torque.setEnabled(True)     #torque manual (profile 10)
            self.ui.checkBox_1.setEnabled(False)    #Abrir Explorador Windows
            self.ui.checkBox_2.setEnabled(False)    #GDI
            self.ui.checkBox_3.setEnabled(True)     #retrabajo de terminales
            self.ui.checkBox_4.setEnabled(True)     #desapriete
            self.ui.checkBox_5.setEnabled(True)     #retrabajo con cambio de caja
            self.ui.checkBox_6.setEnabled(False)    #trazabilidad
        elif self.user_type == "MANTENIMIENTO":
            self.ui.btn_off.setEnabled(True)        #power off PC
            self.ui.btn_reset.setEnabled(True)      #reset PC
            self.ui.btn_torque.setEnabled(True)     #torque manual (profile 10)
            self.ui.checkBox_1.setEnabled(True)     #Abrir Explorador Windows
            self.ui.checkBox_2.setEnabled(True)     #GDI
            self.ui.checkBox_3.setEnabled(False)    #retrabajo de terminales
            self.ui.checkBox_4.setEnabled(False)    #desapriete
            self.ui.checkBox_5.setEnabled(False)    #retrabajo con cambio de caja
            self.ui.checkBox_6.setEnabled(False)    #trazabilidad
        elif self.user_type == "PRODUCCION":
            self.ui.btn_off.setEnabled(False)       #power off PC
            self.ui.btn_reset.setEnabled(True)      #reset PC
            self.ui.btn_torque.setEnabled(False)    #torque manual (profile 10)
            self.ui.checkBox_1.setEnabled(False)    #Abrir Explorador Windows
            self.ui.checkBox_2.setEnabled(True)     #GDI
            self.ui.checkBox_3.setEnabled(True)     #retrabajo de terminales
            self.ui.checkBox_4.setEnabled(False)    #desapriete
            self.ui.checkBox_5.setEnabled(True)     #retrabajo con cambio de caja
            self.ui.checkBox_6.setEnabled(False)    #trazabilidad
        elif self.user_type == "OPERADOR":
            self.ui.btn_off.setEnabled(False)       #power off PC
            self.ui.btn_reset.setEnabled(False)     #reset PC
            self.ui.btn_torque.setEnabled(False)    #torque manual (profile 10)
            self.ui.checkBox_1.setEnabled(False)    #Abrir Explorador Windows
            self.ui.checkBox_2.setEnabled(False)    #GDI
            self.ui.checkBox_3.setEnabled(False)    #retrabajo de terminales
            self.ui.checkBox_4.setEnabled(False)    #desapriete
            self.ui.checkBox_5.setEnabled(False)    #retrabajo con cambio de caja
            self.ui.checkBox_6.setEnabled(False)    #trazabilidad
        self.show()

    #def show_rework (self):
    #    if self.model.plugins["rework"] == False:
    #        self.qw_rework = Rework(model = self.model, client = self.client, parent = self)
    #        self.model.plugins["rework"] = True
    #        self.rcv.connect(self.qw_rework.input)

##################################################################################################

    def startClient(self):
        try:
            self.client.connect(host = "127.0.0.1", port = 1883, keepalive = 60)
            self.client.loop_start()
        except Exception as ex:
            print("Admin MQTT client connection fail. Exception:\n", ex.args)

    def stopClient (self):
        self.client.loop_stop()
        self.client.disconnect()
        
    def resetClient (self):
        self.stop()
        self.start()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("#")
        print("Admin MQTT client connected with code [{}]".format(rc))

    def on_message(self, client, userdata, message):
        try:
            self.model.input_message = message
            self.rcv.emit()
        except Exception as ex:
            print("Admin MQTT client on_message() Exception:\n", ex.args)
     
    def manualTorque(self):
        if self.torques:
            self.ui.btn_torque.setStyleSheet("background-color : gray") 
            self.torques = False
            for i in self.data.pub_topics["torque"]:
                profile = self.data.torque_data[i]["stop_profile"]
                publish.single(self.data.pub_topics["torque"][i],json.dumps({"profile" : profile}),hostname='127.0.0.1', qos = 2)
        else:
            self.ui.btn_torque.setStyleSheet("background-color : green") 
            self.torques = True
            command = {
                        "profile": 10               # Perfil de torque para calibración de calidad
                      }
            for i in self.data.pub_topics["torque"]:
                publish.single(self.data.pub_topics["torque"][i],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def resetMachine(self):
        choice = QMessageBox.question(self, 'Reiniciar', "Estas seguro de reiniciar la estación?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            system("shutdown /r")
            self.client.publish("config/status", '{"shutdown": true}')
            self.close()
        else:
            pass

    def poweroff(self):
        choice = QMessageBox.question(self, 'Apagar', "Estas seguro de apagar la estación?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            system("shutdown /s")
            self.client.publish("config/status", '{"shutdown": true}')
            self.close()
        else:
            pass

    #Abrir Explorador Windows
    def onClicked_1(self):
        if self.ui.checkBox_1.isChecked() and self.kiosk_mode:
            system("start explorer.exe")
            self.kiosk_mode = False

    #Mostrar, Ocultar GDI
    def onClicked_2(self):
        if self.ui.checkBox_2.isChecked():
            self.client.publish("GDI",json.dumps({"Mostrar" : "wacks"}), qos = 2)
            print("Mostrando GDI")
            self.pop_out.setText("Mostrando Software GDI")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()
        else:
            self.client.publish("GDI",json.dumps({"Esconder" : "wacks"}), qos = 2)
            print("Ocultando GDI")
            self.pop_out.setText("Ocultando Software GDI")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()

    #Retrabajo (sin Cambio de Caja, desenredar terminales)
    def onClicked_3(self):
        if self.ui.checkBox_3.isChecked():
            if self.ui.checkBox_5.isChecked() or self.ui.checkBox_4.isChecked():
                self.ui.checkBox_3.setChecked(False)
                print("solo se permite un modo")
                self.pop_out.setText("Solo se permite seleccionar un Modo")
                self.pop_out.setWindowTitle("Error")
                QTimer.singleShot(3000, self.pop_out.button(QMessageBox.Ok).click)
                self.pop_out.exec()
            else:
                self.data.config_data["untangle_mode"] = True
        else:
            self.data.config_data["untangle_mode"] = False
    
    #modo Desapriete
    def onClicked_4(self):
        if self.ui.checkBox_4.isChecked():
            if self.ui.checkBox_3.isChecked() or self.ui.checkBox_5.isChecked():
                self.ui.checkBox_4.setChecked(False)
                print("solo se permite un modo")
                self.pop_out.setText("Solo se permite seleccionar un Modo")
                self.pop_out.setWindowTitle("Error")
                QTimer.singleShot(3000, self.pop_out.button(QMessageBox.Ok).click)
                self.pop_out.exec()
            else:
                self.data.config_data["untwist"] = True
        else:
            self.data.config_data["untwist"] = False

    #Retrabajo (con Cambio de Caja)
    def onClicked_5(self):
        if self.ui.checkBox_5.isChecked():
            if self.ui.checkBox_3.isChecked() or self.ui.checkBox_4.isChecked():
                self.ui.checkBox_5.setChecked(False)
                print("solo se permite un modo")
                self.pop_out.setText("Solo se permite seleccionar un Modo")
                self.pop_out.setWindowTitle("Error")
                QTimer.singleShot(3000, self.pop_out.button(QMessageBox.Ok).click)
                self.pop_out.exec()
            else:
                self.data.config_data["flexible_mode"] = True
        else:
            self.data.config_data["flexible_mode"] = False
    
    #trazabilidad
    def onClicked_6(self):
        if self.ui.checkBox_6.isChecked():
            self.data.config_data["trazabilidad"] = True
            print("Sistema de Trazabilidad Habilitado")
            self.pop_out.setText("El Sistema de Trazabilidad ha sido Habilitado")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(3000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()
        else:
            self.data.config_data["trazabilidad"] = False
            print("Sistema de Trazabilidad Deshabilitado")
            self.pop_out.setText("El Sistema de Trazabilidad ha sido Deshabilitado")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(3000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()

    def closeEvent(self, event):
        self.client.publish("config/status", '{"finish": true}')
        with open("data\config", "wb") as f:
            dump(self.config, f, protocol=3)
        #self.client.publish("modules/set",json.dumps({"window" : False}), qos = 2)
        #self.client.publish("visycam/set",json.dumps({"window" : False}), qos = 2)
        #self.client.publish("torque/1/set",json.dumps({"profile" : 0}), qos = 2)
        #system("taskkill /f /im explorer.exe")
        self.stopClient()
        event.accept()
        self.deleteLater()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")


class Torques (QDialog):
    def __init__(self, model, client = None, parent = None):
        super().__init__(parent)
        self.ui = torques.Ui_torques()
        self.ui.setupUi(self)
        self.client = client
        self.model = model

        self.ui.btn_p1.clicked.connect(self.profile_1)
        self.ui.btn_p2.clicked.connect(self.profile_2)
        self.ui.btn_p3.clicked.connect(self.profile_3)
        self.ui.btn_p4.clicked.connect(self.backward)

        self.ui.lbl_info_2.setText("")
        self.BB = self.model.torque_BB
        
    def profile_1 (self):
        self.drawBB([2,3,5,6])
        self.client.publish("torque/1/set",json.dumps({"profile" : 1}), qos = 2)
        self.ui.lbl_info_1.setText("Torque activado con perfil 1")
        
    def profile_2 (self):
        self.drawBB([1])
        self.client.publish("torque/1/set",json.dumps({"profile" : 2}), qos = 2)
        self.ui.lbl_info_1.setText("Torque activado con perfil 2")
    
    def profile_3 (self):
        self.drawBB([4])
        self.client.publish("torque/1/set",json.dumps({"profile" : 4}), qos = 2)
        self.ui.lbl_info_1.setText("Torque activado con perfil 3")
           
    def backward (self):
        self.drawBB([1,2,3,4,5,6])
        self.client.publish("torque/1/set",json.dumps({"profile" : 3}), qos = 2)
        self.ui.lbl_info_1.setText("Torque activado en reversa")
        self.ui.lbl_info_2.setText("")

    def drawBB (self, zones = []):
        img = copy(self.model.torque_img)
        for i in zones:
            cnt = (i - 1) * 2
            temp = [self.BB[cnt], self.BB[cnt+1]]
            img = self.model.drawBB(img = img, BB = temp, color = (31, 186, 226))
        imwrite("imgs/torques.jpg", img)
        self.client.publish("gui/set",json.dumps({"img_center" : "torques.jpg"}), qos = 2)

    @pyqtSlot()
    def input(self):
        if self.model.input_message.topic == "torque/1/status":
            payload = json.loads(self.model.input_message.payload)
            if "torque" in payload:
                self.ui.lbl_info_2.setText("Resultado: " + payload["torque"] + " Nm")
                if payload["result"] == 1:
                    self.ui.lbl_info_2.setStyleSheet("color: " + "green")
                else:
                    self.ui.lbl_info_2.setStyleSheet("color: " + "red")

    def closeEvent(self, event):
        self.client.publish("torque/1/set",json.dumps({"profile" : 0}), qos = 2)
        img = copy(self.model.torque_img)
        imwrite("imgs/torques.jpg", img)
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    Window = Admin()
    sys.exit(app.exec_())

