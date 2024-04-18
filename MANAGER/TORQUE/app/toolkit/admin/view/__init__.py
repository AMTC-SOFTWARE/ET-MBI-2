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
import requests
from datetime import datetime
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

        if self.data.config_data["cajas_repetidas"]:
            self.ui.checkBox_2.setChecked(True)
        else:
            self.ui.checkBox_2.setChecked(False)


        if self.data.config_data["comparacion_cajasDP"]:
            self.ui.checkBox_3.setChecked(True)
        else:
            self.ui.checkBox_3.setChecked(False)


        #empieza sin motrar GDI
        self.ui.checkBox_4.setChecked(False)

        if self.data.config_data["hora_servidor"]:
            self.ui.checkBox_6.setChecked(True)
        else:
            self.ui.checkBox_6.setChecked(False)
        self.ui.btn_off.setEnabled(False)

        
        if self.data.config_data["conectoresPDCP"]:
            self.ui.checkBox_7.setChecked(True)
        else:
            self.ui.checkBox_7.setChecked(False)
        self.ui.btn_off.setEnabled(False)

        if self.data.config_data["checkAlarma"]:
            self.ui.checkBox_8.setChecked(True)
        else:
            self.ui.checkBox_8.setChecked(False)
        self.ui.btn_off.setEnabled(False)

        if self.data.config_data["sinTorquePDCR"]:
            self.ui.checkBox_9.setChecked(True)
        else:
            self.ui.checkBox_9.setChecked(False)
        self.ui.btn_off.setEnabled(False)

        if self.data.config_data["trazabilidad"]:
            self.ui.checkBox_10.setChecked(True)
        else:
            self.ui.checkBox_10.setChecked(False)
        self.ui.btn_off.setEnabled(False)


        self.ui.btn_off.setVisible(False) #se esconde botón de apagado
        self.ui.checkBox_5.setVisible(False) #se esconde checkbox
        #self.ui.btn_torque.clicked.connect(self.qw_torques.show)
        #self.ui.btn_torque.clicked.connect(self.manualTorque)
        self.ui.btn_reset.clicked.connect(self.resetMachine)
        #self.ui.btn_off.clicked.connect(self.poweroff)

        self.ui.checkBox_1.stateChanged.connect(self.onClicked_1)
        self.ui.checkBox_2.stateChanged.connect(self.onClicked_2)
        self.ui.checkBox_3.stateChanged.connect(self.onClicked_3)
        self.ui.checkBox_4.stateChanged.connect(self.onClicked_4)
        #self.ui.checkBox_5.stateChanged.connect(self.onClicked_5)
        self.ui.checkBox_6.stateChanged.connect(self.onClicked_6)
        self.ui.checkBox_7.stateChanged.connect(self.onClicked_7)
        self.ui.checkBox_8.stateChanged.connect(self.onClicked_8)
        self.ui.checkBox_9.stateChanged.connect(self.onClicked_9)
        self.ui.checkBox_10.stateChanged.connect(self.onClicked_10)
        self.rcv.connect(self.qw_torques.input)
        self.permissions()

######################################### Plugins #######################################
        #self.qw_rework = None
        #self.ui.btn_off.clicked.connect(self.show_rework)

    def permissions (self):
        if self.user_type == "SUPERUSUARIO":
            #self.ui.btn_off.setEnabled(True)
            self.ui.btn_reset.setEnabled(True)
            #self.ui.btn_torque.setEnabled(True)
            self.ui.checkBox_1.setEnabled(True)
            self.ui.checkBox_2.setEnabled(True)
            self.ui.checkBox_3.setEnabled(True)
            self.ui.checkBox_4.setEnabled(True)
            self.ui.checkBox_5.setEnabled(True)
            self.ui.checkBox_6.setEnabled(True)
            self.ui.checkBox_7.setEnabled(True)
            self.ui.checkBox_8.setEnabled(True)
            self.ui.checkBox_9.setEnabled(True)
            self.ui.checkBox_10.setEnabled(True)
        elif self.user_type == "CALIDAD":
            #self.ui.btn_off.setEnabled(False)
            self.ui.btn_reset.setEnabled(True)
            #self.ui.btn_torque.setEnabled(True)
            self.ui.checkBox_1.setEnabled(True)
            self.ui.checkBox_2.setEnabled(True)
            self.ui.checkBox_3.setEnabled(True)
            self.ui.checkBox_4.setEnabled(False)
            self.ui.checkBox_5.setEnabled(True)
            self.ui.checkBox_6.setEnabled(True)
            self.ui.checkBox_7.setEnabled(True)
            self.ui.checkBox_8.setEnabled(True)
            self.ui.checkBox_9.setEnabled(True)
            self.ui.checkBox_10.setEnabled(False)
        elif self.user_type == "MANTENIMIENTO":
            #self.ui.btn_off.setEnabled(True)
            self.ui.btn_reset.setEnabled(True)
            ##self.ui.btn_torque.setEnabled(False)
            self.ui.checkBox_1.setEnabled(True)
            self.ui.checkBox_2.setEnabled(False)
            self.ui.checkBox_3.setEnabled(False)
            self.ui.checkBox_4.setEnabled(False)
            self.ui.checkBox_5.setEnabled(True)
            self.ui.checkBox_6.setEnabled(False)
            self.ui.checkBox_7.setEnabled(False)
            self.ui.checkBox_8.setEnabled(False)
            self.ui.checkBox_9.setEnabled(False)
            self.ui.checkBox_10.setEnabled(False)
        elif self.user_type == "PRODUCCION":
            #self.ui.btn_off.setEnabled(False)
            #self.ui.btn_reset.setEnabled(True)
            #self.ui.btn_torque.setEnabled(False)
            self.ui.checkBox_1.setEnabled(True)
            self.ui.checkBox_2.setEnabled(False)
            self.ui.checkBox_3.setEnabled(False)
            self.ui.checkBox_4.setEnabled(False)
            self.ui.checkBox_5.setEnabled(False)
            self.ui.checkBox_6.setEnabled(True)
            self.ui.checkBox_7.setEnabled(False)
            self.ui.checkBox_8.setEnabled(False)
            self.ui.checkBox_9.setEnabled(False)
            self.ui.checkBox_10.setEnabled(False)
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
                        "profile": 10               # Perfil de torque para calibraci[on de calidad
                      }
            for i in self.data.pub_topics["torque"]:
                publish.single(self.data.pub_topics["torque"][i],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def resetMachine(self):
        choice = QMessageBox.question(self, 'Reiniciar', "Estas seguro de reiniciar la estación?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            print("reiniciando equipo...")
            system("shutdown /r")
            self.client.publish("config/status", '{"shutdown": true}')
            self.close()
        else:
            print("se cancela reinicio de equipo ")
            pass

    def poweroff(self):
        choice = QMessageBox.question(self, 'Apagar', "Estas seguro de apagar la estación?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            system("shutdown /s")
            self.client.publish("config/status", '{"shutdown": true}')
            self.close()
        else:
            pass

    #abrir carpetas
    def onClicked_1(self):
        if self.ui.checkBox_1.isChecked() and self.kiosk_mode:
            system("start explorer.exe")
            self.kiosk_mode = False

    #cajas repetidas
    def onClicked_2(self):
        if self.ui.checkBox_2.isChecked():
            self.data.config_data["cajas_repetidas"] = True
            fecha_actual = datetime.now()
            data = {
                "NAME": self.data.local_data["user"]["name"],
                "GAFET":  self.data.local_data["user"]["pass"],
                "TYPE": self.data.local_data["user"]["type"],
                "LOG": "cajas_repetidas_True",
                "DATETIME": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                }
                
                
            endpoint = "http://{}/api/post/login".format(self.data.server)
            resp = requests.post(endpoint, data=json.dumps(data))
        else:
            self.data.config_data["cajas_repetidas"] = False
            fecha_actual = datetime.now()
            data = {
                "NAME": self.data.local_data["user"]["name"],
                "GAFET":  self.data.local_data["user"]["pass"],
                "TYPE": self.data.local_data["user"]["type"],
                "LOG": "cajas_repetidas_False",
                "DATETIME": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                }
                
                
            endpoint = "http://{}/api/post/login".format(self.data.server)
            resp = requests.post(endpoint, data=json.dumps(data))
    
    #cajas PDC-D y PDC-P comparación con registros de FET
    def onClicked_3(self):
        if self.ui.checkBox_3.isChecked():
            self.data.config_data["comparacion_cajasDP"] = True
            fecha_actual = datetime.now()
            data = {
                "NAME": self.data.local_data["user"]["name"],
                "GAFET":  self.data.local_data["user"]["pass"],
                "TYPE": self.data.local_data["user"]["type"],
                "LOG": "comparacion_cajasDP_True",
                "DATETIME": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                }
                
                
            endpoint = "http://{}/api/post/login".format(self.data.server)
            resp = requests.post(endpoint, data=json.dumps(data))
        else:
            self.data.config_data["comparacion_cajasDP"] = False
            fecha_actual = datetime.now()
            data = {
                "NAME": self.data.local_data["user"]["name"],
                "GAFET":  self.data.local_data["user"]["pass"],
                "TYPE": self.data.local_data["user"]["type"],
                "LOG": "comparacion_cajasDP_False",
                "DATETIME": fecha_actual.strftime("%Y/%m/%d %H:%M:%S"),
                }
                
                
            endpoint = "http://{}/api/post/login".format(self.data.server)
            resp = requests.post(endpoint, data=json.dumps(data))
    
    #Mostrar/Esconder GDI
    def onClicked_4(self):
        try:
            if self.ui.checkBox_4.isChecked():
                print("Mostrando GDI: contains(Mostrar)")
                self.client.publish("GDI",json.dumps({"Mostrar" : "Mostrando GDI..."}), qos = 2)
                self.pop_out.setText("Mostrando GDI")
                self.pop_out.setWindowTitle("Acción Realizada")
                QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
                self.pop_out.exec()
            else:
                print("Ocultando GDI: containts(Esconder)")
                self.client.publish("GDI",json.dumps({"Esconder" : "Ocultando GDI..."}), qos = 2)
                self.pop_out.setText("Ocultando GDI")
                self.pop_out.setWindowTitle("Acción Realizada")
                QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
                self.pop_out.exec()
        except Exception as ex:
            print("Error al ocultar o mostrar GDI ", ex)

    #checkbox Libre
    def onClicked_5(self):
        
        #if self.ui.checkBox_5.isChecked():
        #    self.data.config_data["flexible_mode"] = True
        #else:
        #    self.data.config_data["flexible_mode"] = False
        pass

    def onClicked_6(self):     #Descomentar el día que se habilite el envío de info al servidor de P2
        if self.ui.checkBox_6.isChecked():
            """
            La hora del servidor define cuando los registros se hacen con la hora extraida del servidor
            """
            self.data.config_data["hora_servidor"] = True
            
        else:
            self.data.config_data["hora_servidor"] = False
           

    def onClicked_7(self):     #Descomentar el día que se habilite el envío de info al servidor de P2
        if self.ui.checkBox_7.isChecked():
            """
            Conectores PDCP True habilitados
            """
            self.data.config_data["conectoresPDCP"] = True
            
        else:
            self.data.config_data["conectoresPDCP"] = False


    def onClicked_8(self):     
        if self.ui.checkBox_8.isChecked():
            """
            Alarma de tuerca faltante habilitada
            """
            self.data.config_data["checkAlarma"] = True
            
        else:
            self.data.config_data["checkAlarma"] = False

    def onClicked_9(self):     
        if self.ui.checkBox_9.isChecked():
            """
            bypass pdcr
            """
            self.data.config_data["sinTorquePDCR"] = True
            
        else:
            self.data.config_data["sinTorquePDCR"] = False
            
            

    #trazabilidad
    def onClicked_10(self):     #Descomentar el día que se habilite el envío de info al servidor de P2
        if self.ui.checkBox_10.isChecked():
            self.data.config_data["trazabilidad"] = True
            print("Sistema de Trazabilidad Habilitado")
            self.pop_out.setText("El Sistema de Trazabilidad ha sido Habilitado")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()
        else:
            self.data.config_data["trazabilidad"] = False
            print("Sistema de Trazabilidad Deshabilitado")
            self.pop_out.setText("El Sistema de Trazabilidad ha sido Deshabilitado")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
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

