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


        if self.data.config_data["cajas_repetidas"]:
            self.ui.checkBox_2.setChecked(True)
        else:
            self.ui.checkBox_2.setChecked(False)


        if self.data.config_data["comparacion_cajasDP"]:
            self.ui.checkBox_3.setChecked(True)
        else:
            self.ui.checkBox_3.setChecked(False)

        self.ui.checkBox_altura_tool1.setChecked(self.data.config_data["deshabilitar_altura"]["tool1"])
        self.ui.checkBox_altura_tool2.setChecked(self.data.config_data["deshabilitar_altura"]["tool2"])
        self.ui.checkBox_altura_tool3.setChecked(self.data.config_data["deshabilitar_altura"]["tool3"])
        #empieza sin motrar GDI
        self.ui.checkBox_4.setChecked(False)
        #empieza sin utilizar sensores inductivos
        self.ui.checkBox_10.setChecked(False)
        #se deshabilita el botón para apagar la PC
        self.ui.btn_off.setEnabled(False)
        #se esconde botón de apagado
        self.ui.btn_off.setVisible(False) 
        #se esconde checkbox_5 (se utilizaba para modo puntual)
        self.ui.checkBox_5.setVisible(False) 


        if self.data.config_data["hora_servidor"]:
            self.ui.checkBox_6.setChecked(True)
        else:
            self.ui.checkBox_6.setChecked(False)

        if self.data.config_data["conectoresPDCP"]:
            self.ui.checkBox_7.setChecked(True)
        else:
            self.ui.checkBox_7.setChecked(False)
        
        if self.data.config_data["checkAlarma"]:
            self.ui.checkBox_8.setChecked(True)
        else:
            self.ui.checkBox_8.setChecked(False)

        if self.data.config_data["sinTorquePDCR"]:
            self.ui.checkBox_9.setChecked(True)
        else:
            self.ui.checkBox_9.setChecked(False)
        
        if self.data.config_data["shift_ctrl_function"]:
            self.ui.checkBox_11.setChecked(True)
        else:
            self.ui.checkBox_11.setChecked(False)

        if self.data.config_data["trazabilidad"]:
            self.ui.checkBox_12.setChecked(True)
        else:
            self.ui.checkBox_12.setChecked(False)

        self.ui.checkBoxMFBP2_A20.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A20"])
        self.ui.checkBoxMFBP2_A21.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A21"])
        self.ui.checkBoxMFBP2_A22.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A22"])
        self.ui.checkBoxMFBP2_A23.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A23"])
        self.ui.checkBoxMFBP2_A24.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A24"])
        self.ui.checkBoxMFBP2_A25.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A25"])
        self.ui.checkBoxMFBP2_A26.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A26"])
        self.ui.checkBoxMFBP2_A27.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A27"])
        self.ui.checkBoxMFBP2_A28.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A28"])
        self.ui.checkBoxMFBP2_A29.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A29"])
        self.ui.checkBoxMFBP2_A30.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P2"]["A30"])

        self.ui.checkBoxMFBP1_A41.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P1"]["A41"])
        self.ui.checkBoxMFBP1_A42.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P1"]["A42"])
        self.ui.checkBoxMFBP1_A43.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P1"]["A43"])
        self.ui.checkBoxMFBP1_A44.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P1"]["A44"])
        self.ui.checkBoxMFBP1_A45.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P1"]["A45"])
        self.ui.checkBoxMFBP1_A46.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P1"]["A46"])
        self.ui.checkBoxMFBP1_A47.setChecked(self.data.config_data["sensores_inductivos"]["MFB-P1"]["A47"])

        self.ui.checkBoxMFBS_A51.setChecked(self.data.config_data["sensores_inductivos"]["MFB-S"]["A51"])
        self.ui.checkBoxMFBS_A52.setChecked(self.data.config_data["sensores_inductivos"]["MFB-S"]["A52"])
        self.ui.checkBoxMFBS_A53.setChecked(self.data.config_data["sensores_inductivos"]["MFB-S"]["A53"])
        self.ui.checkBoxMFBS_A54.setChecked(self.data.config_data["sensores_inductivos"]["MFB-S"]["A54"])
        self.ui.checkBoxMFBS_A55.setChecked(self.data.config_data["sensores_inductivos"]["MFB-S"]["A55"])
        self.ui.checkBoxMFBS_A56.setChecked(self.data.config_data["sensores_inductivos"]["MFB-S"]["A56"])

        self.ui.checkBoxMFBE_E1.setChecked(self.data.config_data["sensores_inductivos"]["MFB-E"]["E1"])
        self.ui.checkBoxMFBE_A1.setChecked(self.data.config_data["sensores_inductivos"]["MFB-E"]["A1"])
        self.ui.checkBoxMFBE_A2.setChecked(self.data.config_data["sensores_inductivos"]["MFB-E"]["A2"])


        self.ui.btn_reset.clicked.connect(self.resetMachine) #botón para reiniciar PC activa función resetMachine
        #self.ui.btn_torque.clicked.connect(self.qw_torques.show)
        #self.ui.btn_torque.clicked.connect(self.manualTorque)
        #self.ui.btn_off.clicked.connect(self.poweroff)

        self.ui.checkBox_1.stateChanged.connect(self.onClicked_1)           # Abrir Carpeta
        self.ui.checkBox_2.stateChanged.connect(self.onClicked_2)           # Cajas Repetidas
        self.ui.checkBox_3.stateChanged.connect(self.onClicked_3)           # Comparación PDC-P & PDC-D con FET
        self.ui.checkBox_4.stateChanged.connect(self.onClicked_4)           # Habilitar GDI
        #self.ui.checkBox_5.stateChanged.connect(self.onClicked_5)          # Modo Puntual
        self.ui.checkBox_6.stateChanged.connect(self.onClicked_6)           # Usar Hora de Servidor
        self.ui.checkBox_7.stateChanged.connect(self.onClicked_7)           # Revisión de Conectores PDC-P
        self.ui.checkBox_8.stateChanged.connect(self.onClicked_8)           # Alarma de Tuerca Faltante
        self.ui.checkBox_9.stateChanged.connect(self.onClicked_9)           # Sin Tuerca PDC-R (Ciclo no pide tuerca, solo candados)
        self.ui.checkBox_10.stateChanged.connect(self.onClicked_10)         # Zonas con Sensores
        self.ui.checkBox_11.stateChanged.connect(self.onClicked_11)         # Función shift ctrl Focus
        self.ui.checkBox_12.stateChanged.connect(self.onClicked_12)         # Sistema de Trazabilidad

        self.ui.checkBoxMFBP2_A20.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A21.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A22.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A23.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A24.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A25.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A26.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A27.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A28.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A29.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP2_A30.stateChanged.connect(self.onClicked_10)

        self.ui.checkBoxMFBP1_A41.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP1_A42.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP1_A43.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP1_A44.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP1_A45.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP1_A46.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBP1_A47.stateChanged.connect(self.onClicked_10)

        self.ui.checkBoxMFBS_A51.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBS_A52.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBS_A53.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBS_A54.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBS_A55.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBS_A56.stateChanged.connect(self.onClicked_10)

        self.ui.checkBoxMFBE_E1.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBE_A1.stateChanged.connect(self.onClicked_10)
        self.ui.checkBoxMFBE_A2.stateChanged.connect(self.onClicked_10)

        self.ui.checkBox_altura_tool1.stateChanged.connect(self.onClicked_altura_tool1)
        self.ui.checkBox_altura_tool2.stateChanged.connect(self.onClicked_altura_tool2)
        self.ui.checkBox_altura_tool3.stateChanged.connect(self.onClicked_altura_tool3)

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
            self.ui.checkBox_11.setEnabled(True)
            self.ui.checkBox_12.setEnabled(True)
            self.ui.checkBox_altura_tool1.setEnabled(True)
            self.ui.checkBox_altura_tool2.setEnabled(True)
            self.ui.checkBox_altura_tool3.setEnabled(True)
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
            self.ui.checkBox_11.setEnabled(False)
            self.ui.checkBox_12.setEnabled(False)
            self.ui.checkBox_altura_tool1.setEnabled(False)
            self.ui.checkBox_altura_tool2.setEnabled(False)
            self.ui.checkBox_altura_tool3.setEnabled(False)
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
            self.ui.checkBox_11.setEnabled(False)
            self.ui.checkBox_12.setEnabled(False)
            self.ui.checkBox_altura_tool1.setEnabled(False)
            self.ui.checkBox_altura_tool2.setEnabled(False)
            self.ui.checkBox_altura_tool3.setEnabled(False)
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
            self.ui.checkBox_11.setEnabled(False)
            self.ui.checkBox_12.setEnabled(False)
            self.ui.checkBox_altura_tool1.setEnabled(False)
            self.ui.checkBox_altura_tool2.setEnabled(False)
            self.ui.checkBox_altura_tool3.setEnabled(False)
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
            else:
                print("Ocultando GDI: containts(Esconder)")
                self.client.publish("GDI",json.dumps({"Esconder" : "Ocultando GDI..."}), qos = 2)
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
            bypass PDCR
            """
            self.data.config_data["sinTorquePDCR"] = True
        else:
            self.data.config_data["sinTorquePDCR"] = False
            
    def onClicked_10(self):     
        if self.ui.checkBox_10.isChecked():

            self.ui.checkBoxMFBP2_A20.setEnabled(True)
            self.ui.checkBoxMFBP2_A21.setEnabled(True)
            self.ui.checkBoxMFBP2_A22.setEnabled(True)
            self.ui.checkBoxMFBP2_A23.setEnabled(True)
            self.ui.checkBoxMFBP2_A24.setEnabled(True)
            self.ui.checkBoxMFBP2_A25.setEnabled(True)
            self.ui.checkBoxMFBP2_A26.setEnabled(True)
            self.ui.checkBoxMFBP2_A27.setEnabled(True)
            self.ui.checkBoxMFBP2_A28.setEnabled(True)
            self.ui.checkBoxMFBP2_A29.setEnabled(True)
            self.ui.checkBoxMFBP2_A30.setEnabled(True)

            self.ui.checkBoxMFBP1_A41.setEnabled(True)
            self.ui.checkBoxMFBP1_A42.setEnabled(True)
            self.ui.checkBoxMFBP1_A43.setEnabled(True)
            self.ui.checkBoxMFBP1_A44.setEnabled(True)
            self.ui.checkBoxMFBP1_A45.setEnabled(True)
            self.ui.checkBoxMFBP1_A46.setEnabled(True)
            self.ui.checkBoxMFBP1_A47.setEnabled(True)

            self.ui.checkBoxMFBS_A51.setEnabled(True)
            self.ui.checkBoxMFBS_A52.setEnabled(True)
            self.ui.checkBoxMFBS_A53.setEnabled(True)
            self.ui.checkBoxMFBS_A54.setEnabled(True)
            self.ui.checkBoxMFBS_A55.setEnabled(True)
            self.ui.checkBoxMFBS_A56.setEnabled(True)

            self.ui.checkBoxMFBE_E1.setEnabled(True)
            self.ui.checkBoxMFBE_A1.setEnabled(True)
            self.ui.checkBoxMFBE_A2.setEnabled(True)

        else:
            
            self.ui.checkBoxMFBP2_A20.setChecked(False)
            self.ui.checkBoxMFBP2_A21.setChecked(False)
            self.ui.checkBoxMFBP2_A22.setChecked(False)
            self.ui.checkBoxMFBP2_A23.setChecked(False)
            self.ui.checkBoxMFBP2_A24.setChecked(False)
            self.ui.checkBoxMFBP2_A25.setChecked(False)
            self.ui.checkBoxMFBP2_A26.setChecked(False)
            self.ui.checkBoxMFBP2_A27.setChecked(False)
            self.ui.checkBoxMFBP2_A28.setChecked(False)
            self.ui.checkBoxMFBP2_A29.setChecked(False)
            self.ui.checkBoxMFBP2_A30.setChecked(False)

            self.ui.checkBoxMFBP1_A41.setChecked(False)
            self.ui.checkBoxMFBP1_A42.setChecked(False)
            self.ui.checkBoxMFBP1_A43.setChecked(False)
            self.ui.checkBoxMFBP1_A44.setChecked(False)
            self.ui.checkBoxMFBP1_A45.setChecked(False)
            self.ui.checkBoxMFBP1_A46.setChecked(False)
            self.ui.checkBoxMFBP1_A47.setChecked(False)

            self.ui.checkBoxMFBS_A51.setChecked(False)
            self.ui.checkBoxMFBS_A52.setChecked(False)
            self.ui.checkBoxMFBS_A53.setChecked(False)
            self.ui.checkBoxMFBS_A54.setChecked(False)
            self.ui.checkBoxMFBS_A55.setChecked(False)
            self.ui.checkBoxMFBS_A56.setChecked(False)

            self.ui.checkBoxMFBE_E1.setChecked(False)
            self.ui.checkBoxMFBE_A1.setChecked(False)
            self.ui.checkBoxMFBE_A2.setChecked(False)

            ######################

            self.ui.checkBoxMFBP2_A20.setEnabled(False)
            self.ui.checkBoxMFBP2_A21.setEnabled(False)
            self.ui.checkBoxMFBP2_A22.setEnabled(False)
            self.ui.checkBoxMFBP2_A23.setEnabled(False)
            self.ui.checkBoxMFBP2_A24.setEnabled(False)
            self.ui.checkBoxMFBP2_A25.setEnabled(False)
            self.ui.checkBoxMFBP2_A26.setEnabled(False)
            self.ui.checkBoxMFBP2_A27.setEnabled(False)
            self.ui.checkBoxMFBP2_A28.setEnabled(False)
            self.ui.checkBoxMFBP2_A29.setEnabled(False)
            self.ui.checkBoxMFBP2_A30.setEnabled(False)

            self.ui.checkBoxMFBP1_A41.setEnabled(False)
            self.ui.checkBoxMFBP1_A42.setEnabled(False)
            self.ui.checkBoxMFBP1_A43.setEnabled(False)
            self.ui.checkBoxMFBP1_A44.setEnabled(False)
            self.ui.checkBoxMFBP1_A45.setEnabled(False)
            self.ui.checkBoxMFBP1_A46.setEnabled(False)
            self.ui.checkBoxMFBP1_A47.setEnabled(False)

            self.ui.checkBoxMFBS_A51.setEnabled(False)
            self.ui.checkBoxMFBS_A52.setEnabled(False)
            self.ui.checkBoxMFBS_A53.setEnabled(False)
            self.ui.checkBoxMFBS_A54.setEnabled(False)
            self.ui.checkBoxMFBS_A55.setEnabled(False)
            self.ui.checkBoxMFBS_A56.setEnabled(False)

            self.ui.checkBoxMFBE_E1.setEnabled(False)
            self.ui.checkBoxMFBE_A1.setEnabled(False)
            self.ui.checkBoxMFBE_A2.setEnabled(False)


        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A20"] = self.ui.checkBoxMFBP2_A20.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A21"] = self.ui.checkBoxMFBP2_A21.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A22"] = self.ui.checkBoxMFBP2_A22.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A23"] = self.ui.checkBoxMFBP2_A23.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A24"] = self.ui.checkBoxMFBP2_A24.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A25"] = self.ui.checkBoxMFBP2_A25.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A26"] = self.ui.checkBoxMFBP2_A26.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A27"] = self.ui.checkBoxMFBP2_A27.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A28"] = self.ui.checkBoxMFBP2_A28.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A29"] = self.ui.checkBoxMFBP2_A29.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P2"]["A30"] = self.ui.checkBoxMFBP2_A30.isChecked()

        self.data.config_data["sensores_inductivos"]["MFB-P1"]["A41"] = self.ui.checkBoxMFBP1_A41.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P1"]["A42"] = self.ui.checkBoxMFBP1_A42.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P1"]["A43"] = self.ui.checkBoxMFBP1_A43.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P1"]["A44"] = self.ui.checkBoxMFBP1_A44.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P1"]["A45"] = self.ui.checkBoxMFBP1_A45.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P1"]["A46"] = self.ui.checkBoxMFBP1_A46.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-P1"]["A47"] = self.ui.checkBoxMFBP1_A47.isChecked()

        self.data.config_data["sensores_inductivos"]["MFB-S"]["A51"] = self.ui.checkBoxMFBS_A51.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-S"]["A52"] = self.ui.checkBoxMFBS_A52.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-S"]["A53"] = self.ui.checkBoxMFBS_A53.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-S"]["A54"] = self.ui.checkBoxMFBS_A54.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-S"]["A55"] = self.ui.checkBoxMFBS_A55.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-S"]["A56"] = self.ui.checkBoxMFBS_A56.isChecked()

        self.data.config_data["sensores_inductivos"]["MFB-E"]["E1"] = self.ui.checkBoxMFBE_E1.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-E"]["A1"] = self.ui.checkBoxMFBE_A1.isChecked()
        self.data.config_data["sensores_inductivos"]["MFB-E"]["A2"] = self.ui.checkBoxMFBE_A2.isChecked()

        print("cambio en sensores_inductivos: ",self.data.config_data["sensores_inductivos"])

    #Función para Shift/Ctrl en Focus de LineEdit de QR_CAJA y QR_KEY
    def onClicked_11(self):
        if self.ui.checkBox_11.isChecked():
            self.data.config_data["shift_ctrl_function"] = True
        else:
            self.data.config_data["shift_ctrl_function"] = False

    #trazabilidad
    def onClicked_12(self):
        if self.ui.checkBox_12.isChecked():
            self.data.config_data["trazabilidad"] = True
            print("Sistema de Trazabilidad Habilitado")
            self.pop_out.setText("El Sistema de Trazabilidad ha sido Habilitado")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(1000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()
        else:
            self.data.config_data["trazabilidad"] = False
            print("Sistema de Trazabilidad Deshabilitado")
            self.pop_out.setText("El Sistema de Trazabilidad ha sido Deshabilitado")
            self.pop_out.setWindowTitle("Acción Realizada")
            QTimer.singleShot(1000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()
            
    def onClicked_altura_tool1(self):
        if self.ui.checkBox_altura_tool1.isChecked():
            self.data.config_data["deshabilitar_altura"]["tool1"] = True
        else:
            self.data.config_data["deshabilitar_altura"]["tool1"] = False
        print("self.data.config_data[deshabilitar_altura][tool1]: ",self.data.config_data["deshabilitar_altura"]["tool1"])

    def onClicked_altura_tool2(self):
        if self.ui.checkBox_altura_tool2.isChecked():
            self.data.config_data["deshabilitar_altura"]["tool2"] = True
        else:
            self.data.config_data["deshabilitar_altura"]["tool2"] = False
        print("self.data.config_data[deshabilitar_altura][tool2]: ",self.data.config_data["deshabilitar_altura"]["tool2"])

    def onClicked_altura_tool3(self):
        if self.ui.checkBox_altura_tool3.isChecked():
            self.data.config_data["deshabilitar_altura"]["tool3"] = True
        else:
            self.data.config_data["deshabilitar_altura"]["tool3"] = False
        print("self.data.config_data[deshabilitar_altura][tool3]: ",self.data.config_data["deshabilitar_altura"]["tool3"])

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

