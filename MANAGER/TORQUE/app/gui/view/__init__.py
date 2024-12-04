# -*- coding: utf-8 -*-
"""
@author: MSc. Marco Rutiaga Quezada
"""

from PyQt5.QtWidgets import QDialog, QMainWindow, QPushButton, QLineEdit, QMessageBox, QAction, QFrame, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QTimer, QDateTime, QDate, QTime
from PyQt5.QtGui import QPixmap, QColor
from threading import Timer
from os.path import exists
from os import system 
import json 
from datetime import datetime, timedelta
from threading import Timer
from time import strftime, sleep
from copy import copy
import requests
import pandas as pd
from gui.view import resources_rc, main, login, scanner, img_popout, Tabla_horas, mtto1, Tabla_errores, message_pop
from gui.view.comm import MqttClient
from gui.model import Model
import math
import re
import pymysql
import matplotlib.pyplot as plt
class MainWindow (QMainWindow):

    output = pyqtSignal(dict)
    def quitar_numeros_enteros(self,cadena):
        # Utilizar una expresión regular para encontrar y reemplazar números enteros
        resultado = re.sub(r'\d+', '', cadena)
        return resultado
    def __init__(self, name = "GUI", topic = "gui", parent = None):
        super().__init__(parent)

        self.model = Model()
        self.ui = main.Ui_main()
        self.qw_login = Login(parent = self)
        self.qw_scanner = Scanner(parent = self)
        self.qw_img_popout = Img_popout(parent = self)
        self.pop_out = PopOut(self)
        self.qw_Tabla_horas = Tabla_hora_w(parent = self)
        self.uiManteniemiento= Mantenimiento_ui(parent=self)
        self.qw_message_pop= Message_pop(parent = self)
        
        self.client = MqttClient(self.model, self)
        self.client.subscribe.connect(self.input)
        self.output.connect(self.client.publish)
        

        self.model.name = name
        self.model.setTopic = topic.lower() + "/set"
        self.model.statusTopic = topic.lower() + "/status"
        self.ui.setupUi(self)
        self.ui.lbl_result.setText("")
        self.ui.lbl_steps.setText("")
        self.ui.lbl_nuts.setText("")
        self.ui.lbl_toolCurrent.setText("")
        self.ui.lbl_user.setText("")
        self.ui.lbl_info1.setText("")
        self.ui.lbl_info2.setText("")
        self.ui.lbl_info3.setText("")
        ######### Modificación para etiqueta PDC-R #########
        self.ui.lbl_boxPDCR.setText("")
        ######### Modificación para etiqueta PDC-R #########
        ######### Modificación para etiqueta MFB-P2 #########
        self.ui.lbl_boxMFBP2.setText("")
        ######### Modificación para etiqueta MFB-P2 #########
        ######### Modificación para etiqueta MFB-E #########
        self.ui.lbl_boxMFBE.setText("")
        ######### Modificación para etiqueta MFB-E #########
        ######### Modificación para etiqueta BATTERY-2 #########
        self.ui.lbl_boxBATTERY2.setText("")
        ######### Modificación para etiqueta BATTERY-2 #########
        ######### Modificación para etiqueta NEW #########
        self.ui.lbl_boxNEW.setText("")
        ########################################################
        self.ui.lbl_boxPDCP.setText("")
        self.ui.lbl_boxPDCD.setText("")
        self.ui.lbl_boxMFBP1.setText("")
        self.ui.lbl_boxMFBS.setText("")
        self.ui.lbl_boxBATTERY.setText("")
        ########################################################
        self.ui.lbl_instructions.setText("")
        self.ui.position.setText("")
        self.setWindowTitle(self.model.name)
        self.ui.lineEdit.setFocusPolicy(Qt.StrongFocus)
        self.ui.lineEdit.setPlaceholderText("Fuse boxes QR")
        self.ui.lineEdit.setFocus(True)
        self.ui.lineEdit.setVisible(False)

        self.ui.lineEditKey.setPlaceholderText("QR Key")
        self.ui.lineEditKey.setFocus(True)
        self.ui.lineEditKey.setVisible(False)


        self.ui.lbl_cant.setVisible(True)
        self.ui.lcdNumber.setVisible(True)
        self.ui.lineEditKey.setEchoMode(QLineEdit.Password)
        self.ui.lbl_boxEmergente1.setVisible(False)

        menu = self.ui.menuMenu
        actionLogin = QAction("Login",self)
        actionLogout = QAction("Logout",self)
        actionConfig = QAction("Config",self)
        actionWEB = QAction("WEB",self)
        #actionGDI = QAction("GDI",self) #se elimina la acción para mostrar/esconder GDI desde aquí
        menu.addAction(actionLogin)
        menu.addAction(actionLogout)
        menu.addAction(actionConfig)
        menu.addAction(actionWEB)
        #menu.addAction(actionGDI) #ya no se llama desde el menu
        menu.triggered[QAction].connect(self.menuProcess)
        

        self.ui.lineEditKey.returnPressed.connect(self.QR)
        self.ui.lineEdit.returnPressed.connect(self.qrBoxes)
        self.qw_login.ui.lineEdit.returnPressed.connect( self.login)
        self.qw_login.ui.btn_ok.clicked.connect(self.login)
        self.qw_scanner.ui.btn_ok.clicked.connect(self.scanner)
        self.qw_scanner.ui.lineEdit.returnPressed.connect(self.scanner)
        self.qw_scanner.ui.btn_cancel.clicked.connect(self.qw_scanner.ui.lineEdit.clear)
        self.ui.btn_hxh.clicked.connect(self.horaxhora)
        self.ui.btn_mtto.clicked.connect(self.mantenimiento)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.status)
        #self.timer.start(200)
        self.qw_message_pop.ui.btn_ok.clicked.connect(self.key_process)
        self.qw_message_pop.ui.btn_cancel.clicked.connect(self.cancel_key_process)
        
        self.allow_close        = True
        self.cycle_started      = False
        self.shutdown           = False

        self.login_show         = True
        
    def cancel_key_process(self):
        print("key no emit")
        
        self.output.emit({"keyboard_cancel":"true"})
        print("vamos a cancelar")
        self.qw_message_pop.close()
    def key_process(self):
        
        self.output.emit({"keyboard_ok":"true"})
        print("va a hacer algo con la llave")
    def horaxhora(self):
        #self.qw_Tabla_horas.show()
        print("vamos a calcular los hora por hora")
        horario_turno1={"7":0,
                        "8":0,
                        "9":0,
                        "10":0,
                        "11":0,
                        "12":0,
                        "13":0,
                        "14":0,
                        "15":0,
                        "16":0,
                        "17":0,
                        "18":0,
                        "19":0,
                        "20":0,
                        "21":0,
                        "22":0,
                        "23":0,
                        "00":0,
                        "01":0,
                        "02":0,
                        "03":0,
                        "04":0,
                        "05":0,
                        "06":0,
                        }
        
        try:
            turnos = {
            "1":["07-00","18-59"],
            "2":["19-00","06-59"],
            }
            endpoint = "http://{}/horaxhora/historial/FIN".format(self.model.server)
            response = requests.get(endpoint, data=json.dumps(turnos))
            response = response.json()
            print("response",response)
            
            print("response",response)
            arneses_turno=pd.DataFrame({'HM': response['HM'],
                   'INICIO': response['INICIO'],
                   'FIN': response['FIN'],
                   'RESULTADO': response['RESULTADO'],
                   'USUARIO': response['USUARIO']})
            
            
            arneses_turno['INICIO']=pd.to_datetime(arneses_turno['INICIO']).dt.tz_localize(None)
            #arneses_turno['INICIO']=datetime.strptime(arneses_turno['INICIO'], '%a, %d %b %Y %H:%M:%S GMT')
            arneses_turno['FIN']=pd.to_datetime(arneses_turno['FIN']).dt.tz_localize(None)
            # Extrae solo la parte de la fecha
            arneses_turno['INICIO'] = arneses_turno['INICIO']
            arneses_turno['FIN'] = arneses_turno['FIN']

            print("arneses del inicio",arneses_turno['INICIO'])
            print("arneses del fin",arneses_turno['FIN'])
            arneses_turno['RESULTADO']=arneses_turno['RESULTADO'].astype("string")
            #Calcula Duración de ciclo de los arneses
            arneses_turno["INTERVALO"]=arneses_turno['FIN']-arneses_turno['INICIO']
            print("arneses_turnoINTERVALO]",arneses_turno["INTERVALO"])
            total_minutos_perdidos={}
            Arneses_cada_hora={}
            promedio_ciclo={}
            mejor_tiempo_hora={}
            mejor_tiempo_hora_usuario={}
            mejor_tiempo = pd.to_timedelta('1 hours')
            peor_tiempo = pd.to_timedelta('0 hours')
            usuario=""
            for hora in horario_turno1:
                hora_inicio = pd.to_datetime(f'{hora}:00:00').time()
                
                if hora=="23":
                    hora_fin = pd.to_datetime('23:59:59').time()
                else:
                    hora_siguiente=str(int(hora)+1)
                    hora_fin = pd.to_datetime(f'{hora_siguiente}:00:00').time()
                
                # Aplicamos el filtro para seleccionar las filas dentro del intervalo de horas.
                #horario_turno1[hora] = arneses_turno[(arneses_turno['FIN'].dt.time >= hora_inicio) & (arneses_turno['FIN'].dt.time <= hora_fin) & (arneses_turno['RESULTADO']=="2")]
                
                base_temporal = arneses_turno[(arneses_turno['FIN'].dt.time >= hora_inicio) & (arneses_turno['FIN'].dt.time <= hora_fin) & (arneses_turno['RESULTADO']=="1")]
                print("base_temporal",base_temporal)

                promedio_ciclo[hora]=base_temporal['INTERVALO'].mean(skipna=True).total_seconds() / 60
                print("promedio_ciclo[hora]",promedio_ciclo[hora])
                mejor_tiempo_hora_usuario[hora]=base_temporal['INTERVALO'].min(skipna=True)
                mejor_tiempo_hora[hora]=base_temporal['INTERVALO'].min(skipna=True).total_seconds() / 60
                nuevo_usuario=base_temporal.loc[base_temporal['INTERVALO'] == mejor_tiempo_hora_usuario[hora], 'USUARIO']
                
                nuevo_mejor_tiempo=base_temporal['INTERVALO'].min(skipna=True)
                nuevo_peor_tiempo=base_temporal['INTERVALO'].max(skipna=True)
                
                # Verificamos si el resultado no es None o NaN antes de imprimir o usar el valor.
                if pd.notna(nuevo_mejor_tiempo):
                    if nuevo_mejor_tiempo<=mejor_tiempo:
                        mejor_tiempo=nuevo_mejor_tiempo
                        usuario=nuevo_usuario
                else:
                    print("No hay valores válidos en la columna 'intervalo'.")
                if pd.notna(nuevo_peor_tiempo):
                    if nuevo_peor_tiempo>=peor_tiempo:
                        peor_tiempo=nuevo_peor_tiempo
                else:
                    print("No hay valores válidos en la columna 'intervalo'.")
                #Se suman los tiemos de cada hora para saber cuanto tiempo estuvo la maquina sin trabajar
                # Convertimos la columna 'tiempos' a tipo timedelta.
                base_temporal['INTERVALO'] = pd.to_timedelta(base_temporal['INTERVALO'])
                print(" base_temporal['INTERVALO']",base_temporal['INTERVALO'])
                # Sumamos los tiempos y lo convertimos a minutos.
                total_minutos_perdidos[hora] =60 - base_temporal['INTERVALO'].sum(skipna=True).total_seconds() / 60
                
                Arneses_cada_hora[hora] = base_temporal.shape[0]
                #horario_turno1[hora]["Arneses_cada_hora"] =base_temporal.shape[0]
            print("total_minutos_perdidos",total_minutos_perdidos)
            print("Arneses_cada_hora",Arneses_cada_hora)
            print("promedio_ciclo",promedio_ciclo)
            print("mejor_tiempo",mejor_tiempo.total_seconds() / 60)
            print("peor_tiempo",peor_tiempo.total_seconds() / 60)
            
            #self.qw_scanner.setVisible(show["scanner"])
            #item = self.tableWidget.horizontalHeaderItem(1)
            #item.setText(_translate("Ui_Tabla_h", "Mejor Tiempo"))
            fila=0
            for hora in Arneses_cada_hora:
                
                # Rellena la cantidad de arneses en la tabla
                celda_cantidad_arneses = QTableWidgetItem("                 "+str(Arneses_cada_hora[hora]))
                if Arneses_cada_hora[hora]> 0:
                   celda_cantidad_arneses.setBackground(QColor("cyan"))
                
                self.qw_Tabla_horas.ui.tableWidget.setItem(fila,0,celda_cantidad_arneses)
                
                #Rellena el mejor tiempo en la tabla
                if isinstance(mejor_tiempo_hora[hora], float) and not (math.isnan(mejor_tiempo_hora[hora]) or math.isinf(mejor_tiempo_hora[hora])):
                    # Obtener la parte entera y decimal
                    parte_entera = int(mejor_tiempo_hora[hora])
                    parte_decimal = mejor_tiempo_hora[hora] - parte_entera
                    
                    # Convertir la parte decimal a segundos
                    segundos = round(parte_decimal * 60)
                    
                    celda_mejor_tiempo=QTableWidgetItem(f"   {parte_entera} minutos, {segundos} s." )
                else:
                    celda_mejor_tiempo=QTableWidgetItem("0")
                
                self.qw_Tabla_horas.ui.tableWidget.setItem(fila,1,celda_mejor_tiempo)
                
                #Rellena elpromedio de tiempo ciclo en la tabla
                if isinstance(promedio_ciclo[hora], float) and not (math.isnan(promedio_ciclo[hora]) or math.isinf(promedio_ciclo[hora])):
                    # Obtener la parte entera y decimal
                    parte_entera = int(promedio_ciclo[hora])
                    parte_decimal = promedio_ciclo[hora] - parte_entera
                    
                    # Convertir la parte decimal a segundos
                    segundos = round(parte_decimal * 60)
                    
                    celda_promedio_ciclo=QTableWidgetItem(f"   {parte_entera} minutos, {segundos} s." )
                else:
                    celda_promedio_ciclo=QTableWidgetItem("0")
                self.qw_Tabla_horas.ui.tableWidget.setItem(fila,2,celda_promedio_ciclo)
                #Rellena los minutos perdidos cada hora en la tabla
                if isinstance(total_minutos_perdidos[hora], float) and not (math.isnan(total_minutos_perdidos[hora]) or math.isinf(total_minutos_perdidos[hora])):
                    # Obtener la parte entera y decimal
                    parte_entera = int(total_minutos_perdidos[hora])
                    parte_decimal = total_minutos_perdidos[hora] - parte_entera
                    
                    # Convertir la parte decimal a segundos
                    segundos = round(parte_decimal * 60)
                    
                    celda_minutos_perdidos=QTableWidgetItem(f"   {parte_entera} minutos, {segundos} s." )
                else:
                    celda_minutos_perdidos=QTableWidgetItem("0")
                
                self.qw_Tabla_horas.ui.tableWidget.setItem(fila,3,celda_minutos_perdidos)
                fila+=1
            if mejor_tiempo.total_seconds() < self.model.mejor_tiempo:
                self.model.mejor_tiempo=float(mejor_tiempo.total_seconds())
            # Obtener la parte entera y decimal
            parte_entera = int(self.model.mejor_tiempo / 60)
            parte_decimal = (self.model.mejor_tiempo / 60) - parte_entera
            
            # Convertir la parte decimal a segundos
            segundos = round(parte_decimal * 60)
            
            self.qw_Tabla_horas.ui.label_3.setText(f"Tiempo record: {parte_entera} minutos, {segundos} s.")
            
            mejor_tiempo_str=str(mejor_tiempo.total_seconds() / 60)
            usuario=str(usuario)
            usuario=usuario.replace("Name: USUARIO, dtype: object","")
            usuario_sin_numeros = self.quitar_numeros_enteros(usuario)
            
            
            self.qw_Tabla_horas.ui.label_2.setText(f"{usuario_sin_numeros}     con el mejor Tiempo")
            
            
            
            self.qw_Tabla_horas.show()
            
        except Exception as ex:
            print("Error en el conteo ", ex)
        
    def mantenimiento(self):
        print("mantenimiento")
        self.output.emit({"Mantenimiento":True})
        self.uiManteniemiento.show()
        
    def menuProcess(self, q):
        try:
            case = q.text()               
            #if case == "Login":
            #    self.qw_login.setVisible(self.login_show) #se muestra u oculta login al presionar el botón
            #    self.qw_login.ui.lineEdit.setText("")
            #    self.qw_login.ui.lineEdit.setPlaceholderText("Escanea o escribe tu codigo")

            #    if self.login_show == True:#si estaba true para que se mostrara, ahora al volver a presionar el botón será false, entonces lo ocultará
            #        self.login_show = False
            #    else:
            #        self.login_show = True

            #    self.output.emit({"request":"login"})

            if case == "Logout":
                if self.cycle_started == False:
                    self.qw_login.ui.lineEdit.setText("")
                    self.qw_login.ui.lineEdit.setPlaceholderText("Escanea o escribe tu codigo")
                    self.output.emit({"request":"logout"})
                else:
                    self.pop_out.setText("Ciclo en proceso no se permite el logout")
                    self.pop_out.setWindowTitle("Warning")
                    QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
                    self.pop_out.exec()
            #elif case == "GDI": #ya no se manda llamar desde el menu, tienes que entrar a config
            #    self.output.emit({"request":"gdi"})
            elif case == "Config":
                if self.cycle_started == False:
                    self.output.emit({"request":"config"})
                else:
                    self.pop_out.setText("Ciclo en proceso no se permite la configuración")
                    self.pop_out.setWindowTitle("Warning")
                    QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
                    self.pop_out.exec()
            elif case == "WEB":
                if exists("C:\BIN\WEB.url"):
                    Timer(0.05, self.launchWEB).start()
                else:   
                    self.pop_out.setText("No se encontró la página WEB")
                    self.pop_out.setWindowTitle("Error")
                    QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
                    self.pop_out.exec()
        except Exception as ex:
            print("menuProcess() exceptión: ", ex)

    def launchWEB(self):
        self.output.emit({"WEB": "open"})
        system("C:\BIN\WEB.url")

    @pyqtSlot()
    def status (self):
        try:
            if self.isVisible() != self.model.status["visible"]["gui"]:
                self.model.status["visible"]["gui"] = self.isVisible()
                self.output.emit({"visible": {"gui": self.isVisible()}})
        
            if self.qw_login.isVisible() != self.model.status["visible"]["login"]:
                self.model.status["visible"]["login"] = self.qw_login.isVisible()
                self.output.emit({"visible": {"login": self.qw_login.isVisible()}})
                
            if self.qw_message_pop.isVisible() != self.model.status["visible"]["message_pop"]:
                self.model.status["visible"]["message_pop"] = self.qw_message_pop.isVisible()
                self.output.emit({"visible": {"message_pop": self.qw_message_pop.isVisible()}})
                
            if self.qw_scanner.isVisible() != self.model.status["visible"]["scanner"]:
                self.model.status["visible"]["scanner"] = self.qw_scanner.isVisible()
                self.output.emit({"visible": {"scanner": self.qw_scanner.isVisible()}})

            if self.pop_out.isVisible() != self.model.status["visible"]["pop_out"]:
                self.model.status["visible"]["pop_out"] = self.pop_out.isVisible()
                self.output.emit({"visible": {"pop_out": self.pop_out.isVisible()}})

        except Exception as ex:
            print("status() exception: ", ex)

    @pyqtSlot()
    def login (self):
        try:
            text = self.qw_login.ui.lineEdit.text()
            if len(text) > 0: 
                self.output.emit({"ID":text})
                self.qw_login.ui.lineEdit.setPlaceholderText("Código de acceso")
            else:
                self.qw_login.ui.lineEdit.setPlaceholderText("Código vacío intenta de nuevo.")
            self.qw_login.ui.lineEdit.clear()
            self.qw_login.ui.lineEdit.setFocus()
        except Exception as ex:
            print("login() exception: ", ex)

    @pyqtSlot()
    def scanner (self):
        try:
            text = self.qw_scanner.ui.lineEdit.text().upper()
            if len(text) > 0: 
                self.output.emit({"code":text})
                self.qw_scanner.ui.lineEdit.setPlaceholderText("Código Qr")
            else:
                self.qw_scanner.ui.lineEdit.setPlaceholderText("Código vacío intenta de nuevo.")
            self.qw_scanner.ui.lineEdit.clear()
            self.qw_scanner.ui.lineEdit.setFocus()
        except Exception as ex:
            print("scanner exception:", ex)

    @pyqtSlot()
    def QR (self):
        try:
            text = self.ui.lineEditKey.text().upper()
            text = text.replace("\n","")
            if len(text) > 0: 
                self.output.emit({"codeQR":text})
            self.ui.lineEditKey.clear()

        except Exception as ex:
            print("QR exception:", ex)


    @pyqtSlot()
    def qrBoxes (self):
        try:
            text = self.ui.lineEdit.text().upper()
            if len(text) > 0: 
                self.output.emit({"qr_box":text})
                self.ui.lineEdit.setPlaceholderText("Fuse boxes QR")
            else:
                self.ui.lineEdit.setPlaceholderText("Fuse boxes QR")
            self.ui.lineEdit.clear()
            #self.ui.lineEdit.setFocus()
        except Exception as ex:
            print("qrBoxes exception:", ex)

    @pyqtSlot(dict)
    def input(self, message):
        try:
            #print(message)
            if "shutdown" in message:
                if message["shutdown"] == True:
                    self.shutdown = True
                    QTimer.singleShot(4000, self.close)
            if "allow_close" in message:
                if type(message["allow_close"]) == bool:
                    self.allow_close = message["allow_close"]
                else:
                    raise ValueError('allow_close must a boolean.')
            if "cycle_started" in message:
                if type(message["cycle_started"]) == bool:
                    self.cycle_started = message["cycle_started"]
                else:
                    raise ValueError('allow_close must a boolean.')
            if "request" in message:
                if message["request"] == "status":
                    QTimer.singleShot(100, self.sendStatus)
            ######### Etiqueta Titulo Raffis #########
            if "lbl_boxTITLE" in message:
                self.ui.lbl_boxTITLE.setText(message["lbl_boxTITLE"]["text"])
                if "color" in message["lbl_boxTITLE"]:
                    self.ui.lbl_boxTITLE.setStyleSheet("color: " + message["lbl_boxTITLE"]["color"])
            
            if "lcdNumber" in message:
                if "value" in message["lcdNumber"]:

                    print("mememe mensaje: ",message["lcdNumber"])
                    self.ui.lcdNumber.display(message["lcdNumber"]["value"])
                if "visible" in message["lcdNumber"]:
                    #### Visualizacion del LCD
                    self.ui.lbl_cant.setVisible(message["lcdNumber"]["visible"])
                    self.ui.lcdNumber.setVisible(message["lcdNumber"]["visible"])
            if "lcdNumtiempo" in message:
                print("mensaje llegaa", message["lcdNumtiempo"])
                if "label_name" in message["lcdNumtiempo"]:
                    print(message["lcdNumtiempo"]["label_name"])
                    self.ui.lbl_cant2.setText(message["lcdNumtiempo"]["label_name"])

                if "value" in message["lcdNumtiempo"]:
                    self.ui.lcdNumtiempo.display(message["lcdNumtiempo"]["value"])
                if "visible" in message["lcdNumtiempo"]:
                    self.ui.lbl_cant2.setVisible(message["lcdNumtiempo"]["visible"])
                    self.ui.lcdNumtiempo.setVisible(message["lcdNumtiempo"]["visible"])
                if "color" in message["lcdNumtiempo"]:
                     color_back=message["lcdNumtiempo"]["color"]
                     self.ui.lbl_cant2.setStyleSheet("color: #214562; font-size:20px;background-color:" + message["lcdNumtiempo"]["color"]+ "; border-radius:20px; margin-bottom: 5px")

            if "lcdcronometro" in message:
                
                if "label_name" in message["lcdcronometro"]:
                    self.ui.lbl_cant3.setText(message["lcdcronometro"]["label_name"])
                if "value" in message["lcdcronometro"]:
                    self.ui.lcdcronometro.display(message["lcdcronometro"]["value"])
                if "visible" in message["lcdcronometro"]:
                    #### Visualizacion del LCD
                    self.ui.lbl_cant3.setVisible(message["lcdcronometro"]["visible"])
                    self.ui.lcdcronometro.setVisible(message["lcdcronometro"]["visible"])
                if "color" in message["lcdcronometro"]:
                     color_back=message["lcdcronometro"]["color"]
                     self.ui.lbl_cant3.setStyleSheet("color: #214562; font-size:20px;background-color:" + message["lcdcronometro"]["color"]+ "; border-radius:20px; margin-bottom: 5px")

            if "lineEdit" in message:
                
                if "lineEdit_focus" in message:
                    self.activateWindow()
                    self.raise_()
                    self.show()
                    self.ui.lineEdit.setFocus(True)
                

                elif "lineEditKey" in message:
                    
                    if "lineEditKey_focus" in message:
                        self.activateWindow()
                        self.raise_()
                        self.show()
                        self.ui.lineEditKey.setFocus(True)
                    else:
                        if message["lineEditKey"] == True:
                            self.ui.lineEditKey.setVisible(True)
                            
                        if message["lineEditKey"] == False:
                            self.ui.lineEditKey.setVisible(False)
                else:
                    if message["lineEdit"] == True:
                        self.ui.lineEdit.setVisible(True)
                    if message["lineEdit"] == False:
                        self.ui.lineEdit.setVisible(False)

            if "lineEdit_focus" in message:
                self.activateWindow()
                self.raise_()
                self.show()
                self.ui.lineEdit.setFocus(True)
                    
            if "lineEditKey" in message:
                    
                if "lineEditKey_focus" in message:
                    self.activateWindow()
                    self.raise_()
                    self.show()
                    self.ui.lineEditKey.setFocus(True)
                else:
                    if message["lineEditKey"] == True:
                        self.ui.lineEditKey.setVisible(True)
                        
                    if message["lineEditKey"] == False:
                        self.ui.lineEditKey.setVisible(False)
            if "lineEditKey_focus" in message:
                self.activateWindow()
                self.raise_()
                self.show()
                self.ui.lineEditKey.setFocus(True)
            if "lineEdit" in message:
                if message["lineEdit"] == True:
                    self.ui.lineEdit.setVisible(True)
                if message["lineEdit"] == False:
                    self.ui.lineEdit.setVisible(False)
            if "message_pop" in message:
                
                if "Visible" in message["message_pop"]:
                    self.qw_message_pop.setVisible(message["message_pop"]["Visible"])
                if "text" in message["message_pop"]:
                    self.qw_message_pop.ui.lbl_message_pop.setText(message["message_pop"]["text"])

                if "close" in message["message_pop"] and self.qw_message_pop.isVisible: 
                    self.qw_message_pop.ui.btn_cancel.click()
                    #self.pop_out.button(QMessageBox.Ok).click()
            ######### Modificación para etiqueta PDC-R #########
            if "lbl_boxPDCR" in message:
                self.ui.lbl_boxPDCR.setText(message["lbl_boxPDCR"]["text"])
                if "color" in message["lbl_boxPDCR"]:
                    self.ui.lbl_boxPDCR.setStyleSheet("color: " + message["lbl_boxPDCR"]["color"])
            ######################################################################################
            if "lbl_boxPDCP" in message:
                self.ui.lbl_boxPDCP.setText(message["lbl_boxPDCP"]["text"])
                if "color" in message["lbl_boxPDCP"]:
                    self.ui.lbl_boxPDCP.setStyleSheet("color: " + message["lbl_boxPDCP"]["color"])
            if "lbl_boxPDCD" in message:
                self.ui.lbl_boxPDCD.setText(message["lbl_boxPDCD"]["text"])
                if "color" in message["lbl_boxPDCD"]:
                    self.ui.lbl_boxPDCD.setStyleSheet("color: " + message["lbl_boxPDCD"]["color"])
            if "lbl_boxMFBP1" in message:
                self.ui.lbl_boxMFBP1.setText(message["lbl_boxMFBP1"]["text"])
                if "color" in message["lbl_boxMFBP1"]:
                    self.ui.lbl_boxMFBP1.setStyleSheet("color: " + message["lbl_boxMFBP1"]["color"])
            if "lbl_boxMFBS" in message:
                self.ui.lbl_boxMFBS.setText(message["lbl_boxMFBS"]["text"])
                if "color" in message["lbl_boxMFBS"]:
                    self.ui.lbl_boxMFBS.setStyleSheet("color: " + message["lbl_boxMFBS"]["color"])
            if "lbl_boxBATTERY" in message:
                self.ui.lbl_boxBATTERY.setText(message["lbl_boxBATTERY"]["text"])
                if "color" in message["lbl_boxBATTERY"]:
                    self.ui.lbl_boxBATTERY.setStyleSheet("color: " + message["lbl_boxBATTERY"]["color"])
            ######################################################################################
            ######### Modificación para etiqueta PDC-R #########
            ######### Modificación para etiqueta MFB-P2 #########
            if "lbl_boxMFBP2" in message:
                self.ui.lbl_boxMFBP2.setText(message["lbl_boxMFBP2"]["text"])
                if "color" in message["lbl_boxMFBP2"]:
                    self.ui.lbl_boxMFBP2.setStyleSheet("color: " + message["lbl_boxMFBP2"]["color"])
            ######### Modificación para etiqueta MFB-P2 #########
            ######### Modificación para etiqueta MFB-E #########
            if "lbl_boxMFBE" in message:
                self.ui.lbl_boxMFBE.setText(message["lbl_boxMFBE"]["text"])
                if "color" in message["lbl_boxMFBE"]:
                    self.ui.lbl_boxMFBE.setStyleSheet("color: " + message["lbl_boxMFBE"]["color"])
            ######### Modificación para etiqueta MFB-E #########
            ######### Modificación para etiqueta BATTERY-2 #########
            if "lbl_boxBATTERY2" in message:
                self.ui.lbl_boxBATTERY2.setText(message["lbl_boxBATTERY2"]["text"])
                if "color" in message["lbl_boxBATTERY2"]:
                    self.ui.lbl_boxBATTERY2.setStyleSheet("color: " + message["lbl_boxBATTERY2"]["color"])
             ######### Modificación para etiqueta BOX-NEW #########
            if "lbl_boxNEW" in message:
                self.ui.lbl_boxNEW.setText(message["lbl_boxNEW"]["text"])
                if "color" in message["lbl_boxNEW"]:
                    self.ui.lbl_boxNEW.setStyleSheet("color: " + message["lbl_boxNEW"]["color"])
            ######### Modificación para etiqueta BATTERY-2 #########
            if "lbl_instructions" in message:
                self.ui.lbl_instructions.setText(message["lbl_instructions"]["text"])
                if "color" in message["lbl_instructions"]:
                    self.ui.lbl_instructions.setStyleSheet("color: " + message["lbl_instructions"]["color"])
            if "position" in message:
                self.ui.position.setText(message["position"]["text"])
                if "color" in message["position"]:
                    self.ui.position.setStyleSheet("color: " + message["position"]["color"])
            if "lbl_info1" in message:
                self.ui.lbl_info1.setText(message["lbl_info1"]["text"])
                if "color" in message["lbl_info1"]:
                    self.ui.lbl_info1.setStyleSheet("color: " + message["lbl_info1"]["color"])
            if "lbl_info2" in message:
                self.ui.lbl_info2.setText(message["lbl_info2"]["text"])
                if "color" in message["lbl_info2"]:
                    self.ui.lbl_info2.setStyleSheet("color: " + message["lbl_info2"]["color"])
            if "lbl_info3" in message:
                self.ui.lbl_info3.setText(message["lbl_info3"]["text"])
                if "color" in message["lbl_info3"]:
                    self.ui.lbl_info3.setStyleSheet("color: " + message["lbl_info3"]["color"])
            if "lbl_nuts" in message:
                self.ui.lbl_nuts.setText(message["lbl_nuts"]["text"])
                if "color" in message["lbl_nuts"]:
                    self.ui.lbl_nuts.setStyleSheet("color: " + message["lbl_nuts"]["color"])
            ###
            if "lbl_toolCurrent" in message:
                self.ui.lbl_toolCurrent.setText(message["lbl_toolCurrent"]["text"])
                if "color" in message["lbl_toolCurrent"]:
                    self.ui.lbl_toolCurrent.setStyleSheet("color: " + message["lbl_toolCurrent"]["color"])
            ###
            if "lbl_result" in message:
                self.ui.lbl_result.setText(message["lbl_result"]["text"])
                if "color" in message["lbl_result"]:
                    self.ui.lbl_result.setStyleSheet("color: " + message["lbl_result"]["color"])
                if "color" in message["lbl_result"] and "font" in message["lbl_result"]:
                    self.ui.lbl_result.setStyleSheet("color: " + message["lbl_result"]["color"] + ";" + "font: " + message["lbl_result"]["font"])
            if "lbl_steps" in message:
                self.ui.lbl_steps.setText(message["lbl_steps"]["text"])
                if "color" in message["lbl_steps"]:
                    self.ui.lbl_steps.setStyleSheet("color: " + message["lbl_steps"]["color"])
                if "color" in message["lbl_steps"] and "font" in message["lbl_steps"]:
                    self.ui.lbl_steps.setStyleSheet("color: " + message["lbl_steps"]["color"] + ";" + "font: " + message["lbl_steps"]["font"])
            if "lbl_user" in message:
                self.ui.lbl_user.setText(message["lbl_user"]["type"] + "\n" + message["lbl_user"]["user"])
                if "color" in message["lbl_user"]:
                    self.ui.lbl_user.setStyleSheet("color: " + message["lbl_user"]["color"])
                self.model.user = message["lbl_user"]
                self.qw_login.setVisible(False)
            if "lbl_clock" in message:

                if "text" in message["lbl_clock"]:
                    self.ui.lbl_clock.setText(message["lbl_clock"]["text"])
                elif "fecha" in message["lbl_clock"]:

                    #<p style="background-color: #000033;">

                    texto = """
                    <head/>
                    <body>
                        <p>
                            <br>  <!-- Salto de línea -->    
                            <span style="font-size:11pt; font-style:Monospace; color:lightblue;">&nbsp;&nbsp;&nbsp;Fecha Fujikura:&nbsp; <!-- &nbsp; es un espacio vacío -->
                            </span>
                            <span style="font-size:11pt; font-style:Helvetica; color:#ffffff;">daay&nbsp;&nbsp;&nbsp;
                            </span>
                            <br>  <!-- Salto de línea -->
                            <span style="font-size:26pt; font-style:Helvetica; font-weight:bold; color:#ffffff;">&nbsp;&nbsp;&nbsp;&nbsp;daate&nbsp;&nbsp;&nbsp;</span>
                            <br>  <!-- Salto de línea -->
                        </p>
                    </body>
                    """

                    fecha = message["lbl_clock"]["fecha"]
                    fecha = fecha.split(" ")
                    fecha[1] = fecha[1][0:8]
                    fecha_mes = fecha[0].split("-")
                    if fecha_mes[1] == "1" or fecha_mes[1] == "01":
                        fecha_mes[1] = "Enero"
                    elif fecha_mes[1] == "2" or fecha_mes[1] == "02":
                        fecha_mes[1] = "Febrero"
                    elif fecha_mes[1] == "3" or fecha_mes[1] == "0":
                        fecha_mes[1] = "Marzo"
                    elif fecha_mes[1] == "4" or fecha_mes[1] == "0":
                        fecha_mes[1] = "Abril"
                    elif fecha_mes[1] == "5" or fecha_mes[1] == "0":
                        fecha_mes[1] = "Mayo"
                    elif fecha_mes[1] == "6" or fecha_mes[1] == "0":
                        fecha_mes[1] = "Junio"
                    elif fecha_mes[1] == "7" or fecha_mes[1] == "0":
                        fecha_mes[1] = "Julio"
                    elif fecha_mes[1] == "8" or fecha_mes[1] == "0":
                        fecha_mes[1] = "Agosto"
                    elif fecha_mes[1] == "9" or fecha_mes[1] == "0":
                        fecha_mes[1] = "Septiembre"
                    elif fecha_mes[1] == "10":
                        fecha_mes[1] = "Octubre"
                    elif fecha_mes[1] == "11":
                        fecha_mes[1] = "Noviembre"
                    elif fecha_mes[1] == "12":
                        fecha_mes[1] = "Diciembre"
                    fecha[0] = fecha_mes[2] + "-" + fecha_mes[1] + "-" + fecha_mes[0]
                    texto = texto.replace("daay",fecha[0])

                    formato_hora = ""
                    nueva_hora = "12"
                    string_hora = str(fecha[1]).split(":")
                    if int(string_hora[0]) < 12:
                        if int(string_hora[0]) != 12:
                            nueva_hora = str(int(string_hora[0]))
                        formato_hora = " am"
                    else:
                        if int(string_hora[0]) != 12:
                            nueva_hora = str(int(string_hora[0])-12)
                        formato_hora = " pm"

                    string_hora = nueva_hora + ":" + string_hora[1] + ":" + string_hora[2] + formato_hora

                    texto = texto.replace("daate",string_hora)
                    self.ui.lbl_clock.setStyleSheet("background-color: #000033; border-top-left-radius: 15px; border-top-right-radius: 15px; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;")
                    self.ui.lbl_clock.setText(texto)
            if "img_user" in message:
                 if message["img_user"] != "":
                    if exists(self.model.imgsPath + message["img_user"]):
                        self.ui.img_user.setPixmap(QPixmap(self.model.imgsPath + message["img_user"]).scaled(110, 110, Qt.KeepAspectRatio))
                    else:
                        self.ui.img_user.setPixmap(QPixmap(":/images/images/usuario_x.jpg").scaled(110, 110, Qt.KeepAspectRatio))
            if "img_nuts" in message:
                if message["img_nuts"] != "":
                    if exists(self.model.imgsPath + message["img_nuts"]):
                        #self.ui.img_nuts.setPixmap(QPixmap(self.model.imgsPath + message["img_nuts"]).scaled(110, 110, Qt.KeepAspectRatio))
                        pix = QPixmap(self.model.imgsPath + message["img_nuts"])
                        self.ui.img_nuts.setPixmap(pix)

                        if message["img_nuts"] != "blanco.jpg":
                            self.ui.img_nuts.setFrameShape(QFrame.Box)
                            self.ui.img_nuts.setLineWidth(4)
                            self.ui.img_nuts.setStyleSheet("color: green")
                        else:
                            self.ui.img_nuts.setStyleSheet("color: white")
            #####
            if "img_toolCurrent" in message:
                if message["img_toolCurrent"] != "":
                    if exists(self.model.imgsPath + message["img_toolCurrent"]):
                        #self.ui.img_toolCurrent.setPixmap(QPixmap(self.model.imgsPath + message["img_toolCurrent"]).scaled(110, 110, Qt.KeepAspectRatio))
                        pix = QPixmap(self.model.imgsPath + message["img_toolCurrent"])
                        self.ui.img_toolCurrent.setPixmap(pix)

                        if message["img_toolCurrent"] != "blanco.jpg":
                            self.ui.img_toolCurrent.setFrameShape(QFrame.Box)
                            self.ui.img_toolCurrent.setLineWidth(4)
                            self.ui.img_toolCurrent.setStyleSheet("color: green")
                        else:
                            self.ui.img_toolCurrent.setStyleSheet("color: white")
            #####
            if "img_center" in message: 
               if message["img_center"] != "":
                    if exists(self.model.imgsPath + message["img_center"]):
                        self.model.centerImage = self.model.imgsPath + message["img_center"]
                        self.ui.img_center.setPixmap(QPixmap(self.model.centerImage).scaled(self.ui.img_center.width(), self.ui.img_center.height(), Qt.KeepAspectRatio))
            if "show" in message:
                self.launcher(message["show"])         
            if "popOut" in message:
                self.launcher(message) 
            if "Paro_Emergencia" in message:
                print("llega mensaje a gui",message)
                self.model.paro_emergencia=message["Paro_Emergencia"]
            if "alarma_emergencia" in message:
                self.model.alarma_emergencia=message["alarma_emergencia"]
            if "lbl_boxEmergente1" in message:

                
                print(message["lbl_boxEmergente1"])

                if message["lbl_boxEmergente1"]["text"] == "" or message["lbl_boxEmergente1"]["text"] == False:
                    self.ui.lbl_boxEmergente1.setVisible(False)
                else:
                    self.ui.lbl_boxEmergente1.setVisible(True)
                
                self.ui.lbl_boxEmergente1.setText(message["lbl_boxEmergente1"]["text"])
            if "statusBar" in message:
                if type(message["statusBar"]) == str:
                    if message["statusBar"] == "clear":
                        self.ui.statusbar.clearMessage()
                    else:
                        self.ui.statusbar.showMessage(message["statusBar"])
        except Exception as ex:
            print("\ninput() exception : \nMessage: ", message, "\nException: ", ex)
            self.output.emit({"Exception":"Input error"})
    
    @pyqtSlot()
    def launcher(self, show):
        try:
            if "login" in show:
                self.qw_login.ui.lineEdit.setPlaceholderText("Escanea o escribe tu codigo")
                self.qw_login.setVisible(show["login"])
            if "message_pop" in show:
                self.qw_message_pop.setVisible(show["message_pop"])
            if "scanner" in show:
                self.qw_scanner.ui.lineEdit.setPlaceholderText("Escanea el Código Qr")
                self.qw_scanner.setVisible(show["scanner"])
            if "popOut" in show:
                if show["popOut"] == "close" and self.pop_out.isVisible: 
                    self.pop_out.button(QMessageBox.Ok).click()
                else:
                    self.pop_out.setText(show["popOut"])
                    self.pop_out.setWindowTitle("Info")
                    self.pop_out.exec()
            if "img_popOut" in show:
                if show["img_popOut"] == "close":
                    self.qw_img_popout.ui.label.setPixmap(QPixmap(":/images/images/blanco.png"))
                    self.qw_img_popout.close()
                else:
                    self.qw_img_popout.ui.label.setPixmap(QPixmap(self.model.imgsPath + show["img_popOut"]))
                    self.qw_img_popout.show()
        except Exception as ex:
            print("launcher exception: ", ex)

    @pyqtSlot()
    def sendStatus (self):
        try:
            self.output.emit(self.model.status)
        except Exception as ex:
            print("sendStatus() exception: ", ex)

    @pyqtSlot()
    def resizeEvent(self, event):
        try:
            self.ui.img_center.setPixmap(QPixmap(self.model.centerImage).scaled(self.ui.img_center.width(), self.ui.img_center.height(), Qt.KeepAspectRatio))
            #print("[1]", self.width()-self.ui.frame.width())
            #self.ui.frame.setMaximumWidth(self.width() - 328)
            #print("[2]", self.width()-self.ui.frame.width())
        except Exception as ex:
            print("resizeEvent() exception: ", ex)

    @pyqtSlot()
    def closeEvent(self, event):
        if self.shutdown == True:
            #self.shutdown = False
            self.timer.stop()
            self.output.emit({"gui": False})
            print ("Bye...")
            event.accept()
            self.deleteLater()
        elif self.allow_close == True:
            choice = QMessageBox.question(self, 'Salir', "Estas seguro de cerrar la aplicacion?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.timer.stop()
                self.output.emit({"gui": False})
                self.deleteLater()
                print ("Bye...")
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()
            self.pop_out.setText("No se permite cerrar esta ventana")
            self.pop_out.setWindowTitle("Warning")
            QTimer.singleShot(2000, self.pop_out.button(QMessageBox.Ok).click)
            self.pop_out.exec()


class Login (QDialog):
    def __init__(self, parent = None):
        self.model = Model()
        super().__init__(parent)
        self.modo_mantenimiento=False
        
        self.ui = login.Ui_login()
        self.ui.setupUi(self)
        self.ui.lineEdit.setEchoMode(QLineEdit.Password)
        self.ui.lineEdit.setStyleSheet('lineedit-password-character: 9679')
        self.ui.btn_ok.setFocusPolicy(Qt.NoFocus)
        self.ui.lineEdit.setFocus(True)
        
    def closeEvent(self, event):
        if self.modo_mantenimiento==False:
            event.ignore() 
            
            

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")
     
            
class Scanner (QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = scanner.Ui_scanner()
        self.ui.setupUi(self) 
        self.ui.lineEdit.setEchoMode(QLineEdit.Password)
        self.ui.lineEdit.setStyleSheet('lineedit-password-character: 9679')
        self.ui.btn_ok.setFocusPolicy(Qt.NoFocus)
        self.ui.btn_cancel.setFocusPolicy(Qt.NoFocus)
        self.ui.lineEdit.setFocus()

    def closeEvent(self, event):
        event.ignore() 

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")


class Img_popout (QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = img_popout.Ui_img_popout()
        self.ui.setupUi(self) 
        self.ui.label.setText("")
        
class Tabla_hora_w (QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Tabla_horas.Ui_Ui_Tabla_h()
        self.ui.setupUi(self) 
        
    def closeEvent(self, event):
        #event.ignore() 
        print("close event")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")
            

class Tabla_errores_c (QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.ui = Tabla_errores.Ui_TableErrors()
        self.ui.setupUi(self)
        
    def closeEvent(self, event):
        #event.ignore() 
        print("close event")
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")

class Mantenimiento_ui (QMainWindow):
    output = pyqtSignal(dict)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.model = Model()
        self.client = MqttClient(self.model, self)
        
        self.client.subscribe.connect(self.input)
        self.output.connect(self.client.publish)
        name = "GUI"
        topic = "gui"

        self.model.name = name
        self.model.setTopic = topic.lower() + "/set"
        self.model.statusTopic = topic.lower() + "/status"

        self.ui = mtto1.Mantenimiento_ui()
        self.qw_Tabla_errores = Tabla_errores_c(parent = self)
        self.qw_login_mtto = Login(parent = self)
        
        self.ui.setupUi(self) 
        
        self.login_show         = True


        self.ui.centralwidgetok.setEnabled(False)
        
        menu = self.ui.menuMenu
        #actionLogin = QAction("Login",self)
        #actionLogout = QAction("Logout",self)
        #actionGDI = QAction("GDI",self) #se elimina la acción para mostrar/esconder GDI desde aquí
        #menu.addAction(actionLogin)
        #menu.addAction(actionLogout)
        
        #menu.addAction(actionGDI) #ya no se llama desde el menu
        menu.triggered[QAction].connect(self.menuProcess)
        
        self.qw_login_mtto.ui.lineEdit.returnPressed.connect( self.login)
        self.qw_login_mtto.ui.btn_ok.clicked.connect(self.login)

        self.ui.dateTimeEdit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.ui.dateTimeEdit_2.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        
        fecha_actuaal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tomorrow=datetime.now() + timedelta(days=1, hours=5)
        
        print("str(fecha_actuaal)",str(fecha_actuaal))
        print("tomorrow",tomorrow.strftime("%Y-%m-%d %H:%M:%S"))
        actual_datetime=self.ui.dateTimeEdit_2.dateTimeFromText(str(fecha_actuaal))
        tomorrow_datetime=self.ui.dateTimeEdit.dateTimeFromText(str(tomorrow.strftime("%Y-%m-%d %H:%M:%S")))
        

        #self.ui.dateTimeEdit.setDateTime(QDateTime(QDate(2024, 2, 2), QTime(4, 4, 4)))
        self.ui.dateTimeEdit_2.setDateTime(actual_datetime)
        self.ui.dateTimeEdit.setDateTime(tomorrow_datetime)
        
        

        self.ui.checkBox_7.setChecked(False) #clamp PDC-R
        self.ui.checkBox_8.setChecked(False) #clamp PDC-RMID
        self.ui.checkBox_4.setChecked(False) #clamp MFB-P2
        self.ui.checkBox_3.setChecked(False) #clamp MFB-P1
        self.ui.checkBox.setChecked(False) #clamp PDC-D
        self.ui.checkBox_2.setChecked(False) #clamp PDC-P
        self.ui.checkBox_5.setChecked(False) #clamp MFB-S
        self.ui.checkBox_6.setChecked(False) #clamp MFB-E
        
        self.ui.checkBox_7.stateChanged.connect(self.onClicked_7)
        self.ui.checkBox_8.stateChanged.connect(self.onClicked_8)
        self.ui.checkBox_4.stateChanged.connect(self.onClicked_4)
        self.ui.checkBox_3.stateChanged.connect(self.onClicked_3)
        self.ui.checkBox.stateChanged.connect(self.onClicked)
        self.ui.checkBox_2.stateChanged.connect(self.onClicked_2)
        self.ui.checkBox_5.stateChanged.connect(self.onClicked_5)
        self.ui.checkBox_6.stateChanged.connect(self.onClicked_6)
        
        self.ui.pushButton_2.clicked.connect(self.graficas_reintentos)
        self.ui.pushButton_3.clicked.connect(self.Actualizar_fecha)
        self.ui.pushButton.clicked.connect(self.Tabla_fallas)
    @pyqtSlot()
    def login (self):
        try:
            text = self.qw_login_mtto.ui.lineEdit.text()
            if len(text) > 0: 
                self.output.emit({"MTTOuser":text})
                self.qw_login_mtto.ui.lineEdit.setPlaceholderText("Código de acceso")
            else:
                self.qw_login_mtto.ui.lineEdit.setPlaceholderText("Código vacío intenta de nuevo.")
            self.qw_login_mtto.ui.lineEdit.clear()
            self.qw_login_mtto.ui.lineEdit.setFocus()
        except Exception as ex:
            print("login() exception: ", ex)
    def menuProcess(self, q):
        try:
            case = q.text()               
            if case == "Login":
                self.qw_login_mtto.setVisible(self.login_show) #se muestra u oculta login al presionar el botón
                self.qw_login_mtto.ui.lineEdit.setText("")
                self.qw_login_mtto.ui.lineEdit.setPlaceholderText("Escanea o escribe tu codigo")
                self.qw_login_mtto.modo_mantenimiento=True
                #if self.login_show == True:#si estaba true para que se mostrara, ahora al volver a presionar el botón será false, entonces lo ocultará
                #    self.login_show = False
                #else:
                #    self.login_show = True

                self.output.emit({"request":"login"})

            elif case == "Logout":
                self.qw_login_mtto.setVisible(False) 
                self.qw_login_mtto.ui.lineEdit.setText("")
                self.qw_login_mtto.ui.lineEdit.setPlaceholderText("Escanea o escribe tu codigo")
                self.ui.centralwidgetok.setEnabled(False)
                
            #elif case == "GDI": #ya no se manda llamar desde el menu, tienes que entrar a config
            #    self.output.emit({"request":"gdi"})
        except Exception as ex:
            print("menuProcess() exceptión: ", ex)        

    def onClicked_7(self):     #clamp PDC-R
        if self.ui.checkBox_7.isChecked():
            """
            CLAMP PDC-R
            """
            self.output.emit({"PDC-R":True})
        else:
            self.output.emit({"PDC-R":False})
            
    def onClicked_8(self):     #clamp PDC-RMID
        if self.ui.checkBox_8.isChecked():
            """
            CLAMP PDC-RMID
            """
            self.output.emit({"PDC-RMID":True})
        else:
            self.output.emit({"PDC-RMID":False})
            
    def onClicked_4(self):     #clamp MFB-P2
        if self.ui.checkBox_4.isChecked():
            """
            #clamp MFB-P2
            """
            self.output.emit({"MFB-P2":True})
        else:
            self.output.emit({"MFB-P2":False})
     
    def onClicked_3(self):     #clamp MFB-P1
        if self.ui.checkBox_3.isChecked():
            """
            #clamp MFB-P1
            """
            self.output.emit({"MFB-P1":True})
        else:
            self.output.emit({"MFB-P1":False})
            
    def onClicked(self):     #clamp PDC-D
        if self.ui.checkBox.isChecked():
            """
            #clamp PDC-D
            """
            self.output.emit({"PDC-D":True})
        else:
            self.output.emit({"PDC-D":False})
     
    def onClicked_2(self):     #clamp PDC-P
        if self.ui.checkBox_2.isChecked():
            """
            #clamp PDC-P
            """
            self.output.emit({"PDC-P":True})
        else:
            self.output.emit({"PDC-P":False})
            
    def onClicked_5(self):     #clamp MFB-S
        if self.ui.checkBox_5.isChecked():
            """
            #clamp MFB-S
            """
            self.output.emit({"MFB-S":True})
        else:
            self.output.emit({"MFB-S":False})
           
    def onClicked_6(self):     #clamp MFB-E
        if self.ui.checkBox_5.isChecked():
            """
            #clamp MFB-E
            """
            self.output.emit({"MFB-E":True})
        else:
            self.output.emit({"MFB-E":False})

    def Actualizar_fecha(self):
        print("hoyy")
        fecha_actuaal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tomorrow=datetime.now() + timedelta(days=1, hours=5)
        
        print("str(fecha_actuaal)",str(fecha_actuaal))
        print("tomorrow",tomorrow.strftime("%Y-%m-%d %H:%M:%S"))
        actual_datetime=self.ui.dateTimeEdit_2.dateTimeFromText(str(fecha_actuaal))
        tomorrow_datetime=self.ui.dateTimeEdit.dateTimeFromText(str(tomorrow.strftime("%Y-%m-%d %H:%M:%S")))
        

        #self.ui.dateTimeEdit.setDateTime(QDateTime(QDate(2024, 2, 2), QTime(4, 4, 4)))
        self.ui.dateTimeEdit_2.setDateTime(actual_datetime)
        self.ui.dateTimeEdit.setDateTime(tomorrow_datetime)
    def graficas_reintentos(self):
        print("grafica de reintentos")
        # Configuración de la conexión ----------------------------------
        host = "127.0.0.1"
        #host = "10.71.82.11"
        user = "dedicado"
        password = "4dm1n_001"
        db = "et_mbi_2"
        #año-mes-dia hora:min:seg
        init_date = "2023-10-17 07:00:00"
        end_date = "2023-10-17 17:00:00"
        #----------------------------------------------------------------
        

        datetime_lecture1=self.ui.dateTimeEdit.dateTime()
        end_date=self.ui.dateTimeEdit.textFromDateTime(datetime_lecture1)
        
        datetime_lecture2=self.ui.dateTimeEdit_2.dateTime()
        init_date=self.ui.dateTimeEdit.textFromDateTime(datetime_lecture2)
        
        print("datetime_lecture1",datetime_lecture1)
        print("datet_text",end_date)
        
        try:
            ##############
            query = "SELECT INTENTOS_T, INICIO FROM "+ db +".historial WHERE INICIO >= '" + init_date + "' AND INICIO <= '" + end_date + "' AND INTENTOS_T != '{}'"
            response = self.get_response(host, user, password, db, query)
            ##############

            #print("tipo: ",type(response))
            #print("RESPONSE grafica reintentos: ",response)
            
            cantidad_reintentos = len(response["INTENTOS_T"])

            lista_resultados = response["INTENTOS_T"]
            lista_fechasxarnes=response["INICIO"]
            total_rows = len(response["INICIO"])
            fusibles_reintentados = 0 #para contar el total de fusibles reintentados, excepto RELX
            total_reintentos={}
            
            #Calculo de historico de Reintentos
            # Iterar sobre los registros
            data = []
            for i, intentos_str in enumerate(response['INTENTOS_T']):
                # Deserializar el string a un diccionario
                intentos_t = json.loads(intentos_str)
                inicio = response['INICIO'][i]
                
                # Iterar sobre el diccionario de intentos
                for caja, cavidades in intentos_t.items():
                    for cavidad, intentos in cavidades.items():
                        data.append({
                            "caja": caja,
                            "cavidad": cavidad,
                            "intentos": intentos,
                            "fecha": inicio
                        })

            # Crear el DataFrame
            df = pd.DataFrame(data)
            
            

            # Mostrar el DataFrame
            #print("df",df)

            # Determinar el rango de fechas
            min_date = df['fecha'].min()
            max_date = df['fecha'].max()
            date_range = max_date - min_date
            
            df['caja_cavidad'] = df['cavidad'] + "_" + df['caja']
            # Agrupar por cavidad y fecha
            df_cavity_grouped = df.groupby(['caja_cavidad', 'fecha'], as_index=False)['intentos'].sum()
            
            # Agrupar por cavidad para encontrar el total de intentos
            df_total_intentos = df.groupby('caja_cavidad')['intentos'].sum().reset_index()
            
            

            # Encontrar las 10 cavidades con más intentos
            top_10_cavidades = df_total_intentos.nlargest(10, 'intentos')['caja_cavidad']
            
            # Filtrar el DataFrame para incluir solo las top 10 cavidades
            df_top_10 = df[df['caja_cavidad'].isin(top_10_cavidades)]
            
            # Agrupar por cavidad y fecha para las top 10 cavidades
            df_top_10_grouped = df_top_10.groupby(['caja_cavidad', 'fecha'], as_index=False)['intentos'].sum()
            
            # Ordenar el DataFrame por la columna 'reintentos' de mayor a menor
            df_top_10_grouped = df_top_10_grouped.sort_values(by='intentos', ascending=False).reset_index(drop=True)
            
            # Pivotar los datos para que las cavidades sean las columnas y las fechas sean las filas
            df_top_10_pivot = df_top_10_grouped.pivot(index='fecha', columns='caja_cavidad', values='intentos').fillna(0)
            
            # Configuración de la gráfica
            plt.figure(figsize=(14, 8))
            
            # Verificar si el rango de fechas es mayor a un día
            if date_range > timedelta(days=1) and date_range< timedelta(weeks=2):
                # Graficar por días
                df_top_10_pivot.resample('D').sum().plot(kind='line', marker='o')
                plt.xlabel('Fecha')
                plt.ylabel('Cantidad de Intentos')
                plt.title('Top 10 de Intentos por Cavidad por Día')
            elif date_range > timedelta(weeks=2):
                # Graficar por días
                df_top_10_pivot.resample('W').sum().plot(kind='line', marker='o')
                plt.xlabel('Fecha')
                plt.ylabel('Cantidad de Intentos')
                plt.title('Top 10 de Intentos por Cavidad por semana')
            else:
                # Graficar por horas
                df_top_10_pivot.resample('H').sum().plot(kind='line', marker='o')
                plt.xlabel('Hora')
                plt.ylabel('Cantidad de Intentos')
                plt.title('Top 10 de Intentos por Cavidad por Hora')
            

            plt.legend(title=f'Cantidad total de filas: {total_rows}')
            # Leyenda basada en el mayor valor de reintentos
            #mayor_caja_cavidad = dforden.loc[0, 'caja_cavidad']  # El primer valor después de ordenar
            #plt.legend([f"Mayor: {mayor_caja_cavidad}"], loc="upper right")
            #leyenda = [f"{caja_cavidad} ({intentos})" for caja_cavidad, intentos in zip(df_top_10_pivot['caja_cavidad'], df_top_10_pivot['intentos'])]
            #plt.legend(leyenda, title="Caja_Cavidad (intentos)", loc="upper right")

            # Configurar la gráfica
            plt.xticks(rotation=45)  # Rotar las etiquetas de fecha para mejor visualización
            plt.grid(True)
            plt.tight_layout()  # Ajustar el diseño para que no se corten las etiquetas
            #plt.legend(title='Cavidad')
            plt.show()
            ####Calculos de Reintentos acumulados
            print("ok55")
            for i in range(len(lista_resultados)):

                arnes = json.loads(lista_resultados[i]) #cada elemento de la lista es un string, aquí se convierte a diccionario

                #print("arnes: ",arnes)
                for caja in arnes:
                    #print("caja: ",caja)
                    if not(caja in total_reintentos):
                        total_reintentos[caja] = {}

                    for fusible in arnes[caja]:
                        #print("fusible: ",fusible)
                        #print("reintentos: ",arnes[caja][fusible])

                        if fusible != "RELX" and fusible != "RELU": #si el fusible es diferente del RELX o de RELU

                            fusibles_reintentados += arnes[caja][fusible]

                            if not(fusible in total_reintentos[caja]):
                                total_reintentos[caja][fusible] = int(arnes[caja][fusible])
                            else:
                                total_reintentos[caja][fusible] = total_reintentos[caja][fusible] + int(arnes[caja][fusible])

            print("total_reintentos:::::", total_reintentos)

            contador_graficas=0
            # Crear una figura y dividirla en subtramas
            fig, axs = plt.subplots(4, 2)  # 2 filas y 2 columnas de subtramas
            print("total_reintentos.keys()",total_reintentos.keys())
            
            for caja in total_reintentos.keys():
                #print("caja",caja)
                claves = list(total_reintentos[caja].keys())
                valores = list(total_reintentos[caja].values())
    
                # Crear gráficos en cada subtrama
                if contador_graficas==0:
                    axs[0, 0].bar(claves, valores)
                    axs[0, 0].set_title(caja)
                elif contador_graficas==1:
    
                    axs[0, 1].bar(claves, valores, color='orange')
                    axs[0, 1].set_title(caja)
                elif contador_graficas==2:
                    axs[1, 0].bar(claves, valores, color='green')
                    axs[1, 0].set_title(caja)
                elif contador_graficas==3:
                    axs[1, 1].bar(claves, valores, color='red')
                    axs[1, 1].set_title(caja)
                elif contador_graficas==4:
                    axs[2, 0].bar(claves, valores, color='purple')
                    axs[2, 0].set_title(caja)
                elif contador_graficas==5:
                    axs[2, 1].bar(claves, valores, color='pink')
                    axs[2, 1].set_title(caja)
                elif contador_graficas==6:
                    axs[3, 0].bar(claves, valores, color='blue')
                    axs[3, 0].set_title(caja)
                elif contador_graficas==7:
                    axs[3, 1].bar(claves, valores, color='red')
                    axs[3, 1].set_title(caja)
                contador_graficas+=1
                #Ajustar el diseño de las subtramas
                plt.tight_layout()
                #plt.bar(claves, valores)  # Gráfico de barras
                #plt.xlabel('Eje X (Claves)')
                #plt.ylabel('Eje Y (Valores)')
                #plt.title('Gráfico de Ejemplo')

            # Obtén el administrador de la figura actual
            manager = plt.get_current_fig_manager()

            x = 10
            y = 80
            width = 750
            height = 900

            # Ajusta la posición de la ventana emergente
            manager.window.setGeometry(x, y, width, height)

            plt.show()  # Muestra el gráfico
        except Exception as ex:
           print("myJsonResponse connection Exception: ", ex)
           return {"exception": ex.args}
    def get_response(self, host, user, password, db, query):
        try:
            connection = pymysql.connect(host = host, user = user, passwd = password, database = db, cursorclass=pymysql.cursors.DictCursor)
        except Exception as ex:
            print("myJsonResponse connection Exception: ", ex)
            return {"exception": ex.args}

        print("query: ",query)
        try:
            with connection.cursor() as cursor:
                items = cursor.execute(query)
                result = cursor.fetchall()
                
                if len(result) == 1:
                    response = result[0]
                elif len(result) > 1:
                    response = {}
                    keys = list(result[0])
                    for key in keys:
                        response[key] = []
                        for item in result:
                            response[key].append(item.pop(key))         
                else:
                    response = {"items": items}

        except Exception as ex:
            print("myJsonResponse cursor Exception: ", ex)
            response = {"exception" : ex.args}
            
        cursor.close()
        connection.close()
        return response

    def Tabla_fallas(self):
        print("tablas de fallas")
        #self.qw_Tabla_errores.ui.tableWidget.setRowCount(0) #se setean a 0 renglones
        self.qw_Tabla_errores.ui.tableWidget.clearContents() #se manda a llamar clear para limpiar el contenido
        
        
        # Configuración de la conexión ----------------------------------
        host = "127.0.0.1"
        host = "10.71.82.52"
        
        user = "dedicado"
        password = "4dm1n_001"
        db = "et_mbi_2"
        #año-mes-dia hora:min:seg
        init_date = "2023-10-17 07:00:00"
        end_date = "2023-10-17 17:00:00"
        #----------------------------------Calculo de reintentos
        
        datetime_lecture1=self.ui.dateTimeEdit.dateTime()
        end_date=self.ui.dateTimeEdit.textFromDateTime(datetime_lecture1)
        
        datetime_lecture2=self.ui.dateTimeEdit_2.dateTime()
        init_date=self.ui.dateTimeEdit.textFromDateTime(datetime_lecture2)
        
        print("datetime_lecture1",datetime_lecture1)
        print("datet_text",end_date)
        try:
            ##############
            query = "SELECT INTENTOS_T, INICIO FROM "+ db +".historial WHERE INICIO >= '" + init_date + "' AND INICIO <= '" + end_date + "' AND INTENTOS_T != '{}'"
            response = self.get_response(host, user, password, db, query)
            ##############

            #print("tipo: ",type(response))
            print("RESPONSE: ",response["INTENTOS_T"])

            cantidad_reintentos = len(response["INTENTOS_T"])

            lista_resultados = response["INTENTOS_T"]
            fusibles_reintentados = 0 #para contar el total de fusibles reintentados, excepto RELX
            total_reintentos={}

            for i in range(len(lista_resultados)):

                arnes = json.loads(lista_resultados[i]) #cada elemento de la lista es un string, aquí se convierte a diccionario

                #print("arnes: ",arnes)
                for caja in arnes:
                    #print("caja: ",caja)
                    if not(caja in total_reintentos):
                        total_reintentos[caja] = {}

                    for fusible in arnes[caja]:
                        #print("fusible: ",fusible)
                        #print("reintentos: ",arnes[caja][fusible])

                        if fusible != "RELX" and fusible != "RELU": #si el fusible es diferente del RELX o de RELU

                            fusibles_reintentados += arnes[caja][fusible]

                            if not(fusible in total_reintentos[caja]):
                                total_reintentos[caja][fusible] = int(arnes[caja][fusible])
                            else:
                                total_reintentos[caja][fusible] = total_reintentos[caja][fusible] + int(arnes[caja][fusible])

            print("total_reintentos:::::", total_reintentos)

        except Exception as ex:
            print("datos de errores: ", ex)
            return {"exception": ex.args}
        
        #----------------------------------Calculo de top cavidades con mas reintentos
        # Aplanar el diccionario
        flattened_list = [(outer_key, inner_key, value) for outer_key, inner_dict in total_reintentos.items() for inner_key, value in inner_dict.items()]
        
        # Ordenar la lista de tuplas por los valores en orden descendente
        sorted_list = sorted(flattened_list, key=lambda x: x[2], reverse=True)
        fila=0
        colores=["cyan","silver","violet","salmon","lightgreen"]
        for cavidad_top in range(5):
            #sorted_list   [('MFB-P1', 'A46', 2998), ('MFB-P2', 'A20', 2847), ('BATTERY', 'BT', 2783), ('MFB-P2', 'A30', 1640), ('MFB-P2', 'A29', 1626), ('MFB-P2', 'A25', 1478), ('PDC-RMID', 'E1', 1416), ('MFB-P1', 'A41', 1360), ('MFB-P2', 'A21', 1317), ('MFB-P2', 'A26', 1317), ('MFB-P2', 'A24', 1166), ('PDC-P', 'E1', 1018), ('MFB-P2', 'A22', 883), ('PDC-D', 'E1', 817), ('MFB-P1', 'A43', 783), ('MFB-P1', 'A42', 697), ('MFB-P2', 'A23', 582), ('MFB-S', 'A51', 289), ('MFB-S', 'A54', 134), ('BATTERY-2', 'BT', 128), ('MFB-P1', 'A45', 115), ('MFB-E', 'E1', 109), ('MFB-P2', 'A27', 92), ('MFB-E', 'A1', 85), ('PDC-R', 'E1', 78), ('MFB-S', 'A53', 57), ('MFB-E', 'A2', 49), ('MFB-S', 'A52', 47), ('MFB-P1', 'A47', 0), ('MFB-P1', 'A44', 0), ('MFB-S', 'A55', 0), ('MFB-S', 'A56', 0), ('MFB-P2', 'A28', 0), ('PDC-RS', 'E1', 0)]
            cavidad_top1=sorted_list[cavidad_top][1]
            #----------------------------------Querys para consulta de torque info de las cavidades
            #query="SELECT * FROM et_mbi_2.torque_info where CICLO_manager LIKE '"+cavidad_top1+"' order by ID desc LIMIT 2;
            query="SELECT * FROM et_mbi_2.torque_info where result !=1 AND fase_driver >2 AND CICLO_manager LIKE '%"+cavidad_top1+"%' order by ID desc LIMIT 10;"""
            endpoint = "http://{}/query/get/{}".format(self.model.server, query)
            resp_ultimos_torques = requests.get(endpoint).json()
            print("resp_ultimos_torques",resp_ultimos_torques)
            
            color_celdas=colores[cavidad_top]
            
            for registro_torque in range(len(resp_ultimos_torques["angulo_final"])):
                
                #celda_mejor_tiempo=QTableWidgetItem(f"   {parte_entera} minutos, {segundos} s." )
                cavidad=QTableWidgetItem(cavidad_top1)
                cavidad.setBackground(QColor(color_celdas))
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,0,cavidad)
                

                fase_calculo=self.fase_torque(resp_ultimos_torques,registro_torque)
                fase=QTableWidgetItem(fase_calculo)
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,1,fase)
                
                angulo_final_calculo=str(resp_ultimos_torques["angulo_final"][registro_torque])
                angulo_final=QTableWidgetItem(angulo_final_calculo)
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,2,angulo_final)
                
                torque_final_calculo=str(resp_ultimos_torques["torque_final"][registro_torque])
                torque_final=QTableWidgetItem(torque_final_calculo)
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,3,torque_final)
                
                angulo_minimo_calculo=str(resp_ultimos_torques["angulo_minimo"][registro_torque])
                angulo_minimo=QTableWidgetItem(angulo_minimo_calculo)
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,4,angulo_minimo)
                
                angulo_maximo_calculo=str(resp_ultimos_torques["angulo_maximo"][registro_torque])
                angulo_maximo=QTableWidgetItem(angulo_maximo_calculo)
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,5,angulo_maximo)
                
                torque_minimo_calculo=str(resp_ultimos_torques["torque_minimo"][registro_torque])
                torque_minimo=QTableWidgetItem(torque_minimo_calculo)
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,6,torque_minimo)

                torque_maximo_calculo=str(resp_ultimos_torques["torque_maximo"][registro_torque])
                torque_maximo=QTableWidgetItem(torque_maximo_calculo)
                self.qw_Tabla_errores.ui.tableWidget.setItem(fila,7,torque_maximo)
                
                fila=fila+1
                    
            #query="SELECT * FROM et_mbi_2.torque_info where HERRAMIENTA='"+tool+"' order by ID desc LIMIT 2;"""
            ##query="SELECT INICIO, FIN FROM et_mbi_2.historial WHERE RESULTADO = 1 order by ID desc LIMIT 1;"
            #endpoint = "http://{}/query/get/{}".format(self.model.server, query)
            #resp_ultimos_torques = requests.get(endpoint).json()
            #print("resp_ultimos_torques",resp_ultimos_torques)
            #
        self.qw_Tabla_errores.show()


    def fase_torque(self,registros_torques={},registro=0):
        fase=""
        try:
            print("registro",registro)
            registro=registro-1
            #recopilar info de el torque anterior a la reversa
            angulo_minimo_torque=registros_torques["angulo_minimo"][registro]
            angulo_maximo_torque=registros_torques["angulo_maximo"][registro]
            
            if angulo_maximo_torque>2200:
                fase="Fase1"
            elif angulo_maximo_torque>1500 and angulo_maximo_torque<2200:
                fase="Fase2"
            elif angulo_maximo_torque>100 and angulo_maximo_torque<700:
                fase="Fase3"
            elif angulo_maximo_torque>1 and angulo_maximo_torque<100: 
                fase="Fase4"
            else:
                fase="Desconocido"

        except Exception as ex:
            print("error en la deteccion de fase: ", ex)
            return {"exception error en la deteccion de fase": ex.args}
        return fase
    def closeEvent(self, event):
        #event.ignore()
        
        self.ui.checkBox_7.setChecked(False)
        
        self.output.emit({"Mantenimiento":False})
        print("close event")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")
            
    @pyqtSlot(dict)
    def input(self, message):
        print(message)
        if "login_mtto" in message:
            self.qw_login_mtto.setVisible(message["login_mtto"])
                
        if "userOK" in message:
            if message["userOK"] == True:
                self.ui.centralwidgetok.setEnabled(True)
            else:
                self.ui.centralwidgetok.setEnabled(False)

        base_style = (
            "border: 3px solid black;\n"
            "border-top-left-radius: 8px;\n"
            "border-top-right-radius: 8px;\n"
            "border-bottom-left-radius: 8px;\n"
            "border-bottom-right-radius: 8px;"
        )
        mapping = {
            "A41": "label_12",
            "A42": "label_15",
            "A43": "label_17",
            "A44": "label_19",
            "A45": "label_21",
            "A46": "label_23",
            "A47": "label_25",
            "A20": "label_28",
            "A21": "label_30",
            "A22": "label_32",
            "A23": "label_34",
            "A24": "label_36",
            "A25": "label_38",
            "A26": "label_40",
            "A27": "label_42",
            "A28": "label_44",
            "A29": "label_48",
            "A30": "label_46",
            "A51": "label_51",
            "A52": "label_53",
            "A53": "label_55",
            "A54": "label_57",
            "A55": "label_59",
            "A56": "label_61",
            "A1": "label_64",
            "A2": "label_66",
            "E1": "label_68",
            "MFBP1_candado_limit": "label_71",
            "MFBP2_candado_limit": "label_73",
            "MFBS_candado_limit":  "label_75",
            "MFBE_candado_limit":  "label_77",
        }
        # Iterar sobre el diccionario para actualizar los estilos
        for key, label_name in mapping.items():
            
            if key in message:
                print("key si en message")
                color = "lime" if message[key] else "gray"
                style = f"background-color: {color}; {base_style}"
                getattr(self.ui, label_name).setStyleSheet(style)
                return
        
class PopOut (QMessageBox):
    def __init__(self, parent = None):
        self.model = Model()
        super().__init__(parent)
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Ok)
        self.button(QMessageBox.Ok).setVisible(False)

    def closeEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed for PopOut")

class Message_pop (QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = message_pop.Ui_message_pop()
        self.ui.setupUi(self)
        self.ui.btn_ok.setFocusPolicy(Qt.NoFocus)
        self.ui.btn_cancel.setFocusPolicy(Qt.NoFocus)
        #self.ui.lineEdit.setFocus()

    def closeEvent(self, event):
        event.ignore() 

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Escape key was pressed")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    Window = Login()
    Window.show()
    sys.exit(app.exec_())
    


    #{'CICLO_manager': ["['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']"], 'FECHA': ['Thu, 20 Jun 2024 14:20:55 GMT', 'Thu, 20 Jun 2024 13:54:18 GMT', 'Thu, 20 Jun 2024 13:53:47 GMT', 'Thu, 20 Jun 2024 13:53:25 GMT', 'Thu, 20 Jun 2024 13:23:44 GMT', 'Thu, 20 Jun 2024 13:00:43 GMT', 'Thu, 20 Jun 2024 12:23:40 GMT', 'Thu, 20 Jun 2024 11:28:17 GMT', 'Thu, 20 Jun 2024 09:11:34 GMT', 'Thu, 20 Jun 2024 09:10:16 GMT'], 'HERRAMIENTA': ['tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3'], 'HM': ['HM000000288412', 'HM000000288401', 'HM000000288401', 'HM000000288401', 'HM000000288378', 'HM000000288317', 'HM000000288314', 'HM000000288242', 'HM000000287653', 'HM000000287653'], 'ID': [871492, 871422, 871418, 871414, 871372, 871290, 871246, 871084, 870476, 870472], 'REGISTRO': ['{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": -0.4000000059604645, "PostSeatingTorque": 9.571611404418945, "RundownSpeed": 0.0, "SeatingTorque": 9.571611404418945, "SetErrorcode": 16448.0, "ToolCount": 57854.0, "TorqueCorrection": 1.0, "angle": -0.4000000059604645, "angle_max": 500.0, "angle_min": 10.0, "angle_target": 0.0, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 9.571611404418945, "torque_max": 3.0, "torque_min": 0.5, "torque_target": 2.9000000953674316, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1665.2000732421875, "PostSeatingTorque": 6.028872013092041, "RundownSpeed": 0.0, "SeatingTorque": 6.028872013092041, "SetErrorcode": 16448.0, "ToolCount": 57838.0, "TorqueCorrection": 1.0, "angle": 1665.2000732421875, "angle_max": 1845.2000732421875, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 6.028872013092041, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1691.2000732421875, "PostSeatingTorque": 5.065495491027832, "RundownSpeed": 0.0, "SeatingTorque": 5.065495491027832, "SetErrorcode": 16448.0, "ToolCount": 57836.0, "TorqueCorrection": 1.0, "angle": 1691.2000732421875, "angle_max": 1871.2000732421875, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 5.065495491027832, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 0.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1632.7000732421875, "PostSeatingTorque": 6.028872013092041, "RundownSpeed": 0.0, "SeatingTorque": 6.028872013092041, "SetErrorcode": 16448.0, "ToolCount": 57834.0, "TorqueCorrection": 1.0, "angle": 1632.7000732421875, "angle_max": 1812.7000732421875, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 6.028872013092041, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 98.20000457763672, "PostSeatingTorque": 2.8590526580810547, "RundownSpeed": 0.0, "SeatingTorque": 2.8590526580810547, "SetErrorcode": 16448.0, "ToolCount": 57826.0, "TorqueCorrection": 1.0, "angle": 98.20000457763672, "angle_max": 60.0, "angle_min": 10.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 4.0, "result": 2.0, "torque": 2.8590526580810547, "torque_max": 17.600000381469727, "torque_min": 14.399999618530273, "torque_target": 16.0, "torque_trend": "Torque below"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 0.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1677.800048828125, "PostSeatingTorque": 5.997795581817627, "RundownSpeed": 0.0, "SeatingTorque": 5.997795581817627, "SetErrorcode": 16448.0, "ToolCount": 57806.0, "TorqueCorrection": 1.0, "angle": 1677.800048828125, "angle_max": 1857.800048828125, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 5.997795581817627, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 0.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1685.5, "PostSeatingTorque": 5.997795581817627, "RundownSpeed": 0.0, "SeatingTorque": 5.997795581817627, "SetErrorcode": 16448.0, "ToolCount": 57796.0, "TorqueCorrection": 1.0, "angle": 1685.5, "angle_max": 1865.5, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 5.997795581817627, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 0.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1652.0, "PostSeatingTorque": 6.091025352478027, "RundownSpeed": 0.0, "SeatingTorque": 6.091025352478027, "SetErrorcode": 16448.0, "ToolCount": 57758.0, "TorqueCorrection": 1.0, "angle": 1652.0, "angle_max": 1832.0, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 6.091025352478027, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 2754.60009765625, "PostSeatingTorque": 0.031076660379767418, "RundownSpeed": 0.0, "SeatingTorque": 0.031076660379767418, "SetErrorcode": 16448.0, "ToolCount": 57638.0, "TorqueCorrection": 1.0, "angle": 2754.60009765625, "angle_max": 2800.0, "angle_min": 2500.0, "angle_target": 2750.0, "angle_trend": "Angle OK", "fase": 4.0, "result": 2.0, "torque": 0.031076660379767418, "torque_max": 4.900000095367432, "torque_min": 0.10000000149011612, "torque_target": 0.0, "torque_trend": "Torque below"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1603.2000732421875, "PostSeatingTorque": 5.997795581817627, "RundownSpeed": 0.0, "SeatingTorque": 5.997795581817627, "SetErrorcode": 16448.0, "ToolCount": 57636.0, "TorqueCorrection": 1.0, "angle": 1603.2000732421875, "angle_max": 1783.2000732421875, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 5.997795581817627, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}'], 
    # 'angle_target': [0.0, 4.7, 4.7, 4.7, 0.0, 4.7, 4.7, 4.7, 2750.0, 4.7], 
    # 'angle_trend': ['Angle below', 'Angle below', 'Angle below', 'Angle below', 'Angle over', 'Angle below', 'Angle below', 'Angle below', 'Angle OK', 'Angle below'], 
    # 'angulo_final':  [-0.4,      1665.2,        1691.2,    1632.7,         98.2,           1677.8,         1685.5,     1652.0, 2754.6, 1603.2], 
    # 'angulo_maximo': [500.0,     1845.2,        1871.2,    1812.7,         60.0,           1857.8,         1865.5,     1832.0, 2800.0, 1783.2],
    # 'angulo_minimo': [10.0,      1692.0,        1692.0,    1692.0,         10.0,           1692.0,         1692.0,     1692.0, 2500.0, 1692.0],
    # 'columns': ['ID', 'HERRAMIENTA', 'REGISTRO', 'FECHA', 'CICLO_manager', 'estado_actual', 'perfil_driver', 'fase_driver', 'HM', 'angulo_final', 'torque_final', 'torque_minimo', 'torque_maximo', 'angulo_minimo', 'angulo_maximo', 'angle_trend', 'torque_trend', 'angle_target', 'torque_target', 'result'], 'estado_actual': ['', '', '', '', '', '', '', '', '', ''], 'fase_driver': [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0], 'perfil_driver': [3.0, 3.0, 3.0, 0.0, 3.0, 0.0, 0.0, 0.0, 3.0, 3.0], 'result': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0], 
    # 'torque_final':  [9.57161, 6.02887,         5.0655,    6.02887,        2.85905,        5.9978,         5.9978,     6.09103, 0.0310767, 5.9978], 
    # 'torque_maximo': [3.0,      4.9,            4.9,       4.9,            17.6,           4.9,            4.9,        4.9, 4.9, 4.9], 
    # 'torque_minimo': [0.5,      0.0,            0.0,       0.0,            14.4,           0.0,            0.0,        0.0, 0.1, 0.0], 
    # 'torque_target': [2.9,      0.0,            0.0,       0.0,            16.0,           0.0,            0.0,        0.0, 0.0, 0.0], 
    # 'torque_trend': ['Torque over', 'Torque over', 'Torque over', 'Torque over', 'Torque below', 'Torque over', 'Torque over', 'Torque over', 'Torque below', 'Torque over']}
    #                  FASE3     FASE2            FASE2      FASE2           FASE4           FASE2           FASE2      FASE2    FASE1  FASE2
    #                  
    #{'CICLO_manager': ["['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']"], 'FECHA': ['Thu, 20 Jun 2024 14:21:09 GMT', 'Thu, 20 Jun 2024 13:55:08 GMT', 'Thu, 20 Jun 2024 13:54:01 GMT', 'Thu, 20 Jun 2024 13:53:36 GMT', 'Thu, 20 Jun 2024 13:23:54 GMT', 'Thu, 20 Jun 2024 13:00:57 GMT', 'Thu, 20 Jun 2024 12:23:51 GMT', 'Thu, 20 Jun 2024 11:28:31 GMT', 'Thu, 20 Jun 2024 09:11:47 GMT', 'Thu, 20 Jun 2024 09:11:27 GMT'], 'HERRAMIENTA': ['tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3'], 'HM': ['HM000000288412', 'HM000000288401', 'HM000000288401', 'HM000000288401', 'HM000000288378', 'HM000000288317', 'HM000000288314', 'HM000000288242', 'HM000000287653', 'HM000000287653'], 'ID': [871494, 871424, 871420, 871416, 871374, 871292, 871248, 871086, 870478, 870474], 'REGISTRO': ['{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5927.80029296875, "PostSeatingTorque": 6.650405406951904, "RundownSpeed": 0.0, "SeatingTorque": 6.650405406951904, "SetErrorcode": 16448.0, "ToolCount": 57855.0, "TorqueCorrection": 1.0, "angle": 5927.80029296875, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.650405406951904, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5878.10009765625, "PostSeatingTorque": 7.178708553314209, "RundownSpeed": 0.0, "SeatingTorque": 7.178708553314209, "SetErrorcode": 16448.0, "ToolCount": 57839.0, "TorqueCorrection": 1.0, "angle": 5878.10009765625, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 7.178708553314209, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 6088.5, "PostSeatingTorque": 6.836865425109863, "RundownSpeed": 0.0, "SeatingTorque": 6.836865425109863, "SetErrorcode": 16448.0, "ToolCount": 57837.0, "TorqueCorrection": 1.0, "angle": 6088.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.836865425109863, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 6088.5, "PostSeatingTorque": 7.489475250244141, "RundownSpeed": 0.0, "SeatingTorque": 7.489475250244141, "SetErrorcode": 16448.0, "ToolCount": 57835.0, "TorqueCorrection": 1.0, "angle": 6088.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 7.489475250244141, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5319.5, "PostSeatingTorque": 6.650405406951904, "RundownSpeed": 0.0, "SeatingTorque": 6.650405406951904, "SetErrorcode": 16448.0, "ToolCount": 57827.0, "TorqueCorrection": 1.0, "angle": 5319.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.650405406951904, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5785.5, "PostSeatingTorque": 6.89901876449585, "RundownSpeed": 0.0, "SeatingTorque": 6.89901876449585, "SetErrorcode": 16448.0, "ToolCount": 57807.0, "TorqueCorrection": 1.0, "angle": 5785.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.89901876449585, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 6088.5, "PostSeatingTorque": 7.147632122039795, "RundownSpeed": 0.0, "SeatingTorque": 7.147632122039795, "SetErrorcode": 16448.0, "ToolCount": 57797.0, "TorqueCorrection": 1.0, "angle": 6088.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 7.147632122039795, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5742.2001953125, "PostSeatingTorque": 7.582705020904541, "RundownSpeed": 0.0, "SeatingTorque": 7.582705020904541, "SetErrorcode": 16448.0, "ToolCount": 57759.0, "TorqueCorrection": 1.0, "angle": 5742.2001953125, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 7.582705020904541, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 4012.300048828125, "PostSeatingTorque": 6.743635177612305, "RundownSpeed": 0.0, "SeatingTorque": 6.743635177612305, "SetErrorcode": 16448.0, "ToolCount": 57639.0, "TorqueCorrection": 1.0, "angle": 4012.300048828125, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle OK", "fase": 1.0, "result": 2.0, "torque": 6.743635177612305, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5648.80029296875, "PostSeatingTorque": 6.99224853515625, "RundownSpeed": 0.0, "SeatingTorque": 6.99224853515625, "SetErrorcode": 16448.0, "ToolCount": 57637.0, "TorqueCorrection": 1.0, "angle": 5648.80029296875, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.99224853515625, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}'], 'angle_target': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'angle_trend': ['Angle over', 'Angle over', 'Angle over', 'Angle over', 'Angle over', 'Angle over', 'Angle over', 'Angle over', 'Angle OK', 'Angle over'], 'angulo_final': [5927.8, 5878.1, 6088.5, 6088.5, 5319.5, 5785.5, 6088.5, 5742.2, 4012.3, 5648.8], 'angulo_maximo': [5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0], 'angulo_minimo': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 'columns': ['ID', 'HERRAMIENTA', 'REGISTRO', 'FECHA', 'CICLO_manager', 'estado_actual', 'perfil_driver', 'fase_driver', 'HM', 'angulo_final', 'torque_final', 'torque_minimo', 'torque_maximo', 'angulo_minimo', 'angulo_maximo', 'angle_trend', 'torque_trend', 'angle_target', 'torque_target', 'result'], 'estado_actual': ['BACKWARD', 'BACKWARD', 'BACKWARD', 'BACKWARD', 'BACKWARD', 'BACKWARD', 'BACKWARD', 'BACKWARD', 'BACKWARD', 'BACKWARD'], 'fase_driver': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 'perfil_driver': [17.0, 17.0, 17.0, 17.0, 17.0, 17.0, 17.0, 17.0, 17.0, 17.0], 'result': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0], 'torque_final': [6.65041, 7.17871, 6.83687, 7.48948, 6.65041, 6.89902, 7.14763, 7.58271, 6.74364, 6.99225], 'torque_maximo': [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0], 'torque_minimo': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0], 'torque_target': [18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0], 'torque_trend': ['Torque OK', 'Torque OK', 'Torque OK', 'Torque OK', 'Torque OK', 'Torque OK', 'Torque OK', 'Torque OK', 'Torque OK', 'Torque OK']}
    #{'CICLO_manager': ["['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']", "['MFB-P2', 'A25', 3, '8mm Nut']"], 'FECHA': ['Thu, 20 Jun 2024 14:21:09 GMT', 'Thu, 20 Jun 2024 14:20:55 GMT', 'Thu, 20 Jun 2024 13:55:08 GMT', 'Thu, 20 Jun 2024 13:54:18 GMT', 'Thu, 20 Jun 2024 13:54:01 GMT', 'Thu, 20 Jun 2024 13:53:47 GMT', 'Thu, 20 Jun 2024 13:53:36 GMT', 'Thu, 20 Jun 2024 13:53:25 GMT', 'Thu, 20 Jun 2024 13:23:54 GMT', 'Thu, 20 Jun 2024 13:23:44 GMT'], 'HERRAMIENTA': ['tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3', 'tool3'], 'HM': ['HM000000288412', 'HM000000288412', 'HM000000288401', 'HM000000288401', 'HM000000288401', 'HM000000288401', 'HM000000288401', 'HM000000288401', 'HM000000288378', 'HM000000288378'], 'ID': [871494, 871492, 871424, 871422, 871420, 871418, 871416, 871414, 871374, 871372], 'REGISTRO': ['{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5927.80029296875, "PostSeatingTorque": 6.650405406951904, "RundownSpeed": 0.0, "SeatingTorque": 6.650405406951904, "SetErrorcode": 16448.0, "ToolCount": 57855.0, "TorqueCorrection": 1.0, "angle": 5927.80029296875, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.650405406951904, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": -0.4000000059604645, "PostSeatingTorque": 9.571611404418945, "RundownSpeed": 0.0, "SeatingTorque": 9.571611404418945, "SetErrorcode": 16448.0, "ToolCount": 57854.0, "TorqueCorrection": 1.0, "angle": -0.4000000059604645, "angle_max": 500.0, "angle_min": 10.0, "angle_target": 0.0, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 9.571611404418945, "torque_max": 3.0, "torque_min": 0.5, "torque_target": 2.9000000953674316, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5878.10009765625, "PostSeatingTorque": 7.178708553314209, "RundownSpeed": 0.0, "SeatingTorque": 7.178708553314209, "SetErrorcode": 16448.0, "ToolCount": 57839.0, "TorqueCorrection": 1.0, "angle": 5878.10009765625, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 7.178708553314209, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1665.2000732421875, "PostSeatingTorque": 6.028872013092041, "RundownSpeed": 0.0, "SeatingTorque": 6.028872013092041, "SetErrorcode": 16448.0, "ToolCount": 57838.0, "TorqueCorrection": 1.0, "angle": 1665.2000732421875, "angle_max": 1845.2000732421875, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 6.028872013092041, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 6088.5, "PostSeatingTorque": 6.836865425109863, "RundownSpeed": 0.0, "SeatingTorque": 6.836865425109863, "SetErrorcode": 16448.0, "ToolCount": 57837.0, "TorqueCorrection": 1.0, "angle": 6088.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.836865425109863, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1691.2000732421875, "PostSeatingTorque": 5.065495491027832, "RundownSpeed": 0.0, "SeatingTorque": 5.065495491027832, "SetErrorcode": 16448.0, "ToolCount": 57836.0, "TorqueCorrection": 1.0, "angle": 1691.2000732421875, "angle_max": 1871.2000732421875, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 5.065495491027832, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 6088.5, "PostSeatingTorque": 7.489475250244141, "RundownSpeed": 0.0, "SeatingTorque": 7.489475250244141, "SetErrorcode": 16448.0, "ToolCount": 57835.0, "TorqueCorrection": 1.0, "angle": 6088.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 7.489475250244141, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 0.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 1632.7000732421875, "PostSeatingTorque": 6.028872013092041, "RundownSpeed": 0.0, "SeatingTorque": 6.028872013092041, "SetErrorcode": 16448.0, "ToolCount": 57834.0, "TorqueCorrection": 1.0, "angle": 1632.7000732421875, "angle_max": 1812.7000732421875, "angle_min": 1692.0001220703125, "angle_target": 4.700000286102295, "angle_trend": "Angle below", "fase": 4.0, "result": 2.0, "torque": 6.028872013092041, "torque_max": 4.900000095367432, "torque_min": 0.0, "torque_target": 0.0, "torque_trend": "Torque over"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 17.0, "FinalSpeed": 258.0, "PostSeatingRealTorque": 5319.5, "PostSeatingTorque": 6.650405406951904, "RundownSpeed": 0.0, "SeatingTorque": 6.650405406951904, "SetErrorcode": 16448.0, "ToolCount": 57827.0, "TorqueCorrection": 1.0, "angle": 5319.5, "angle_max": 5000.0, "angle_min": 1.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 1.0, "result": 2.0, "torque": 6.650405406951904, "torque_max": 20.0, "torque_min": 2.0, "torque_target": 18.0, "torque_trend": "Torque OK"}', '{"AngularThreshold": 0.0, "CurrentMonitor": 0.0, "CycleSelected": 3.0, "FinalSpeed": 6.0, "PostSeatingRealTorque": 98.20000457763672, "PostSeatingTorque": 2.8590526580810547, "RundownSpeed": 0.0, "SeatingTorque": 2.8590526580810547, "SetErrorcode": 16448.0, "ToolCount": 57826.0, "TorqueCorrection": 1.0, "angle": 98.20000457763672, "angle_max": 60.0, "angle_min": 10.0, "angle_target": 0.0, "angle_trend": "Angle over", "fase": 4.0, "result": 2.0, "torque": 2.8590526580810547, "torque_max": 17.600000381469727, "torque_min": 14.399999618530273, "torque_target": 16.0, "torque_trend": "Torque below"}'], 'angle_target': [0.0, 0.0, 0.0, 4.7, 0.0, 4.7, 0.0, 4.7, 0.0, 0.0], 'angle_trend': ['Angle over', 'Angle below', 'Angle over', 'Angle below', 'Angle over', 'Angle below', 'Angle over', 'Angle below', 'Angle over', 'Angle over'], 'angulo_final': [5927.8, -0.4, 5878.1, 1665.2, 6088.5, 1691.2, 6088.5, 1632.7, 5319.5, 98.2], 'angulo_maximo': [5000.0, 500.0, 5000.0, 1845.2, 5000.0, 1871.2, 5000.0, 1812.7, 5000.0, 60.0], 'angulo_minimo': [1.0, 10.0, 1.0, 1692.0, 1.0, 1692.0, 1.0, 1692.0, 1.0, 10.0], 'columns': ['ID', 'HERRAMIENTA', 'REGISTRO', 'FECHA', 'CICLO_manager', 'estado_actual', 'perfil_driver', 'fase_driver', 'HM', 'angulo_final', 'torque_final', 'torque_minimo', 'torque_maximo', 'angulo_minimo', 'angulo_maximo', 'angle_trend', 'torque_trend', 'angle_target', 'torque_target', 'result'], 'estado_actual': ['BACKWARD', '', 'BACKWARD', '', 'BACKWARD', '', 'BACKWARD', '', 'BACKWARD', ''], 'fase_driver': [1.0, 4.0, 1.0, 4.0, 1.0, 4.0, 1.0, 4.0, 1.0, 4.0], 'perfil_driver': [17.0, 3.0, 17.0, 3.0, 17.0, 3.0, 17.0, 0.0, 17.0, 3.0], 'result': [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0], 'torque_final': [6.65041, 9.57161, 7.17871, 6.02887, 6.83687, 5.0655, 7.48948, 6.02887, 6.65041, 2.85905], 'torque_maximo': [20.0, 3.0, 20.0, 4.9, 20.0, 4.9, 20.0, 4.9, 20.0, 17.6], 'torque_minimo': [2.0, 0.5, 2.0, 0.0, 2.0, 0.0, 2.0, 0.0, 2.0, 14.4], 'torque_target': [18.0, 2.9, 18.0, 0.0, 18.0, 0.0, 18.0, 0.0, 18.0, 16.0], 'torque_trend': ['Torque OK', 'Torque over', 'Torque OK', 'Torque over', 'Torque OK', 'Torque over', 'Torque OK', 'Torque over', 'Torque OK', 'Torque below']}



#    {'INTENTOS_T': ['{"PDC-P": {"E1": 0}, 
#                    "PDC-D": {"E1": 0}, 
#                    "BATTERY": {"BT": 0}, 
#                    "BATTERY-2": {"BT": 0}, 
#                    "MFB-P1": {"A47": 0, "A46": 0, "A45": 0, "A44": 0, "A43": 0, "A41": 0, "A42": 0}, 
#                    "MFB-S": {"A51": 0, "A52": 0, "A53": 0, "A54": 0, "A55": 0, "A56": 0}, 
#                    "MFB-E": {"E1": 0, "A1": 0, "A2": 0}, 
#                    "MFB-P2": {"A20": 0, "A21": 0, "A22": 0, "A23": 0, "A24": 0, "A25": 0, "A26": 0, "A27": 0, "A28": 0, "A29": 0, "A30": 0}, 
#                    "PDC-R": {"E1": 0}, "PDC-RS": {"E1": 0}, 
#                    "PDC-RMID": {"E1": 0}}', 
#                    
#
#                    '{"PDC-P": {"E1": 0}, 
#                    "PDC-D": {"E1": 1}, 
#                    "BATTERY": {"BT": 0}, 
#                    "BATTERY-2": {"BT": 0}, 
#                    "MFB-P1": {"A47": 0, "A46": 0, "A45": 0, "A44": 0, "A43": 0, "A41": 0, "A42": 0}, 
#                    "MFB-S": {"A51": 0, "A52": 0, "A53": 0, "A54": 0, "A55": 0, "A56": 0}, 
#                    "MFB-E": {"E1": 0, "A1": 0, "A2": 0}, 
#                    "MFB-P2": {"A20": 0, "A21": 0, "A22": 0, "A23": 0, "A24": 0, "A25": 0, "A26": 0, "A27": 0, "A28": 0, "A29": 0, "A30": 0}, 
#                    "PDC-R": {"E1": 0},
#                   "PDC-RS": {"E1": 0}, 
#                   "PDC-RMID": {"E1": 0}}'
#                    ],
#    
#                   
#                   
#    'INICIO': [datetime.datetime(2024, 9, 2, 9, 11, 49),
#              datetime.datetime(2024, 9, 2, 9, 24, 33)]}
#                               datetime.datetime(2024, 9, 2, 9, 35, 35), 
#                               datetime.datetime(2024, 9, 2, 10, 2, 19), 
#                               datetime.datetime(2024, 9, 2, 10, 14, 3), 
#                               datetime.datetime(2024, 9, 2, 10, 22, 35), 
#                               datetime.datetime(2024, 9, 2, 10, 30, 20), 
#                               datetime.datetime(2024, 9, 2, 10, 39, 39), 
#                               datetime.datetime(2024, 9, 2, 10, 45, 46), 
#                               datetime.datetime(2024, 9, 2, 11, 1, 44), 
#                               datetime.datetime(2024, 9, 2, 11, 9, 9),
#                              datetime.datetime(2024, 9, 2, 11, 18, 40), 
#                              datetime.datetime(2024, 9, 2, 11, 26, 52), 
#                              datetime.datetime(2024, 9, 2, 11, 38, 55), 
#                              datetime.datetime(2024, 9, 2, 11, 49, 18), 
#                              datetime.datetime(2024, 9, 2, 11, 55, 46), 
#                              datetime.datetime(2024, 9, 2, 12, 36, 5), 
#                              datetime.datetime(2024, 9, 2, 12, 48, 52), 
#                              datetime.datetime(2024, 9, 2, 12, 59, 15), 
#                              datetime.datetime(2024, 9, 2, 13, 11, 42), 
#                              datetime.datetime(2024, 9, 2, 13, 20, 2), 
#                              datetime.datetime(2024, 9, 2, 13, 27, 49), 
#                              datetime.datetime(2024, 9, 2, 13, 37, 39), 
#                              datetime.datetime(2024, 9, 2, 13, 46, 1), 
#                              datetime.datetime(2024, 9, 2, 13, 55, 31), 
#                              datetime.datetime(2024, 9, 2, 14, 4, 42), 
#                              datetime.datetime(2024, 9, 2, 14, 27, 37), 
#                              datetime.datetime(2024, 9, 2, 14, 35, 34), 
#                              datetime.datetime(2024, 9, 2, 14, 42, 18), 
#                              datetime.datetime(2024, 9, 2, 14, 50, 47), 
#                              datetime.datetime(2024, 9, 2, 14, 57, 15), 
#                              datetime.datetime(2024, 9, 2, 15, 5, 11), 
#                              datetime.datetime(2024, 9, 2, 15, 14, 17), 
#                              datetime.datetime(2024, 9, 2, 15, 21, 50), 
#                              datetime.datetime(2024, 9, 2, 15, 34, 8), 
#                              datetime.datetime(2024, 9, 2, 15, 41, 14), 
#                              datetime.datetime(2024, 9, 2, 15, 51, 53), 
#                              datetime.datetime(2024, 9, 2, 16, 1, 26), 
#                              datetime.datetime(2024, 9, 2, 16, 15, 29),
#                             datetime.datetime(2024, 9, 2, 16, 25, 40),
#                            datetime.datetime(2024, 9, 2, 16, 36, 20),
#                           datetime.datetime(2024, 9, 2, 16, 44, 12),
#                          datetime.datetime(2024, 9, 3, 7, 7, 21),
#                         datetime.datetime(2024, 9, 3, 7, 15, 21), datetime.datetime(2024, 9, 3, 7, 22, 54), datetime.datetime(2024, 9, 3, 7, 29, 52), datetime.datetime(2024, 9, 3, 7, 35, 49), datetime.datetime(2024, 9, 3, 7, 46, 30), datetime.datetime(2024, 9, 3, 7, 56, 36), datetime.datetime(2024, 9, 3, 8, 8, 7), datetime.datetime(2024, 9, 3, 8, 17, 37), datetime.datetime(2024, 9, 3, 8, 26, 36)]}
#