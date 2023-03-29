from PyQt5.QtCore import QState, pyqtSignal, QTimer
from paho.mqtt import publish
from datetime import datetime
from threading import Timer
from os.path import exists
from time import strftime, sleep
from pickle import load
from copy import copy
from os import system
import requests
import pprint
import json

from toolkit.admin import Admin

class Startup(QState):
    ok  = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        Timer(0.05, self.model.log, args = ("STARTUP",)).start() 
        if exists("data\config"):
            with open("data\config", "rb") as f:
                data = load(f)
                if "encoder_feedback" in data:
                    for i in data["encoder_feedback"]:
                        if type(data["encoder_feedback"][i]) == bool:
                            self.model.config_data["encoder_feedback"][i] = data["encoder_feedback"][i]
                if "retry_btn_mode" in data:
                    for i in data["retry_btn_mode"]:
                        if type(data["retry_btn_mode"][i]) == bool:
                            self.model.config_data[ "retry_btn_mode"][i] = data[ "retry_btn_mode"][i]
        self.model.config_data["untwist"] = False
        self.model.config_data["flexible_mode"] = False
        self.model.config_data["untangle_mode"] = False

        if self.model.local_data["user"]["type"] != "":
            Timer(0.05, self.logout, args = (copy(self.model.local_data["user"]),)).start()

        self.model.local_data["user"]["type"] = ""
        self.model.local_data["user"]["name"] = ""
        self.model.local_data["user"]["pass"] = ""
        command = {
            "lbl_info1" : {"text": "", "color": "black"},
            "lbl_info2" : {"text": "", "color": "green"},
            "lbl_info3" : {"text": "", "color": "black"},
            "lbl_boxTITLE" : {"text": "", "color": "black"},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            "lbl_result" : {"text": "Se requiere un login para continuar", "color": "green"},
            "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"},
            "img_user" : "blanco.jpg",
            "lbl_user" : {"type":"", "user": "", "color": "black"},
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lbl_nuts"  : {"text": "", "color": "black"},
            "lcdNumber": {"value": 0, "visible": False},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent"  : {"text": "", "color": "black"},
            "position" : {"text": "POSICIÓN 1", "color": "black"},
            "img_center" : "logo.jpg"
            }
         
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        
        command["position"]["text"] = "POSICIÓN 2"
        command["lcdNumber"]["value"] = "0"
        command["lcdNumber"]["visible"] = True

        #publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        HM = "HM000000068090"
        endpoint = "http://{}/api/get/historial/HM/=/{}/_/_/_".format(self.model.server_ET3, HM)
        response = requests.get(endpoint).json()
        print("HM UNICO EN EL HISTORIAL")
        print("SERIALES type: ",type(response["SERIALES"]))                                         #UN STRING - con formato de diccionario
        pprint.pprint(response["SERIALES"])
        pprint.pprint(response["ID"])

        HM = "HM000000060457"
        endpoint = "http://{}/api/get/historial/HM/=/{}/_/_/_".format(self.model.server_ET3, HM)
        response = requests.get(endpoint).json()
        print("HM REPETIDO TORQUE OK y NOK en HISTORIAL")
        print("SERIALES type: ",type(response["SERIALES"]))                                         #UNA LISTA DE STRINGS - con formato de diccionario
        pprint.pprint(response["SERIALES"])
        pprint.pprint(response["ID"])

        
        HM = "HM000000066106"
        endpoint = "http://{}/api/get/historial/HM/=/{}/_/_/_".format(self.model.server_ET3, HM)
        response = requests.get(endpoint).json()
        print("HM RESET en HISTORIAL, SIN RESULTADO OK, lo hicieron en TORQUE2")
        print("SERIALES type: ",type(response["SERIALES"]))                                         #UN STRING - con formato de diccionario, que solo contiene HM, FET, REF
        pprint.pprint(response["SERIALES"])
        pprint.pprint(response["ID"])

        #try:
        #    turnos = {
        #    "1":["07-00","18-59"],
        #    "2":["19-00","06-59"],
        #    }

        #    endpoint = "http://{}/contar/historial/FIN".format(self.model.server)
        #    response = requests.get(endpoint, data=json.dumps(turnos))
        #    response = response.json()
        #    print("response: ",response)
        #    print("Consulta Contador de Historial")

        #    command = {
        #            "lcdNumber" : {"value": response["conteo"]}
        #            }

        #    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        #except Exception as ex:
        #    print("Error en el conteo ", ex)


        #QTimer.singleShot(10, self.stopTorque)
        #QTimer.singleShot(15, self.kioskMode)
        #self.ok.emit()

    def stopTorque (self):
        publish.single(self.model.pub_topics["torque"]["tool1"],json.dumps({"profile" : 0}),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["torque"]["tool2"],json.dumps({"profile" : 0}),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["torque"]["tool3"],json.dumps({"profile" : 0}),hostname='127.0.0.1', qos = 2)

    def kioskMode(self):
        system("taskkill /f /im explorer.exe")
        publish.single("modules/set",json.dumps({"window" : False}),hostname='127.0.0.1', qos = 2)
        publish.single("visycam/set",json.dumps({"window" : False}),hostname='127.0.0.1', qos = 2)

    def logout(self, user):
        try:
            Timer(0.05, self.model.log, args = ("LOGOUT",)).start() 
            data = {
                "NAME": user["name"],
                "GAFET": user["pass"],
                "TYPE": user["type"],
                "LOG": "LOGOUT",
                "DATETIME": strftime("%Y/%m/%d %H:%M:%S"),
                }
            endpoint = "http://{}/api/post/login".format(self.model.server)
            resp = requests.post(endpoint, data=json.dumps(data))
        except Exception as ex:
            print("Logout Exception: ", ex)


class Login (QState):
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
    def onEntry(self, event):
        command = {
            "show":{"login": True},
            "allow_close": True
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)


class CheckLogin (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        command = {
            "lbl_result" : {"text": "ID recibido", "color": "green"},
            "lbl_steps" : {"text": "Validando usuario...", "color": "black"},
            "show":{"login": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        Timer(0.05,self.API_requests).start()

    def API_requests (self):
        try:
            endpoint = ("http://{}/api/get/usuarios/GAFET/=/{}/ACTIVE/=/1".format(self.model.server, self.model.input_data["gui"]["ID"]))
            response = requests.get(endpoint).json()

            if "TYPE" in response:
                self.model.local_data["user"]["type"] = response["TYPE"]
                self.model.local_data["user"]["name"] = response["NAME"]
                self.model.local_data["user"]["pass"] = copy(self.model.input_data["gui"]["ID"])
                data = {
                    "NAME": self.model.local_data["user"]["name"],
                    "GAFET":  self.model.local_data["user"]["pass"],
                    "TYPE": self.model.local_data["user"]["type"],
                    "LOG": "LOGIN",
                    "DATETIME": strftime("%Y/%m/%d %H:%M:%S"),
                    }
                endpoint = "http://{}/api/post/login".format(self.model.server)
                resp = requests.post(endpoint, data=json.dumps(data))

                command = {
                    "lbl_user" : {"type":self.model.local_data["user"]["type"],
                                  "user": self.model.local_data["user"]["name"], 
                                  "color": "black"
                                  },
                    "img_user" : self.model.local_data["user"]["name"] + ".jpg"
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.model.log, args = ("LOGIN",)).start() 
                self.ok.emit()
            else:
                 command = {
                    "lbl_result" : {"text": "Intentalo de nuevo", "color": "red"},
                    "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"}
                    }
                 publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                 publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                 self.nok.emit()
        except Exception as ex:
            print("Login request exception: ", ex)
            command = {
                "lbl_result" : {"text": "Intentalo de nuevo", "color": "red"},
                "lbl_steps" : {"text": "Ingresa tu código de acceso", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()


class StartCycle (QState):
    ok = pyqtSignal()
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.clamps = True

    def onEntry(self, event):

        command = {
                "lineEdit" : False,
                "lineEditKey" : True,
                }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        print("lineEdit desactivado")

        #para avisar que se finalizó el modo de revisión de candados
        self.model.estado_candados = False

        #para funcionamiento normal de llave
        self.model.reintento_torque = False
        command = {
            "DISABLE_PDC-R":False,
            "DISABLE_PDC-RMID":False,
            "DISABLE_MFB-S":False,
            "DISABLE_MFB-P1":False,
            "DISABLE_MFB-P2":False,
            "DISABLE_PDC-P":False,
            "DISABLE_PDC-D":False,
            "DISABLE_MFB-E":False,
            "DISABLE_BATTERY":False,
            "DISABLE_BATTERY-2":False
            }
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        self.model.cajas_habilitadas = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.model.raffi = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        for i in self.model.raffi:
            raffi_clear = {f"raffi_{i}":False}
            publish.single(self.model.pub_topics["plc"],json.dumps(raffi_clear),hostname='127.0.0.1', qos = 2)
        self.model.mediumflag = False
        self.model.largeflag = False
        self.model.smallflag = False
        self.model.pdcr_serie = ""
        self.model.mfbp2_serie = ""
        self.model.herramienta_activa = "0"     # Se resetea la herramienta activa en cada inicio de ciclo... para que el sistema pueda activar la herramienta requerida y no interfiera con las demás.

        self.model.reset()
        Timer(0.05, self.model.log, args = ("IDLE",)).start() 
        command = {
            "lbl_info1" : {"text": "", "color": "black"},
            "lbl_info2" : {"text": "", "color": "green"},
            "lbl_info3" : {"text": "", "color": "black"},
            "lbl_boxTITLE" : {"text": "", "color": "black"},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            "lbl_result" : {"text": "Esperando nuevo ciclo", "color": "green"},
            "lbl_steps" : {"text": "Escanea la etiqueta FET", "color": "black"},
            "lbl_instructions" : {"text": "                                 ", "color": "black"},
            "img_nuts" : "blanco.jpg",
            "lbl_nuts" : {"text": "", "color": "orange"},
            "img_toolCurrent" : "blanco.jpg",
            "lbl_toolCurrent" : {"text": "", "color": "orange"},
            "position" : {"text": "POSICIÓN 1", "color": "black"},
            "img_center" : "logo.jpg",
            "allow_close": False,
            "cycle_started": False,
            "statusBar": "clear"
            }
        if self.model.shutdown == True:
            Timer(0.05, self.logout, args = (copy(self.model.local_data["user"]),)).start()
            command["lbl_result"] = {"text": "Apagando equipo...", "color": "green"}
            command["lbl_steps"] = {"text": ""}
            command["shutdown"] = True
            self.clamps = False
            QTimer.singleShot(3000, self.torqueClamp)
        if self.model.config_data["trazabilidad"]:
            command["lbl_info3"] = {"text": "Trazabilidad\nActivada", "color": "green"}
        else:
            command["lbl_info3"] = {"text": "Trazabilidad\nDesactivada", "color": "red"}
        if self.model.config_data["untwist"]:
            command["lbl_info3"] = {"text": "MODO:\nREVERSA", "color": "purple"}
        if self.model.config_data["flexible_mode"]:
            command["lbl_info3"] = {"text": "MODO:\nRETRABAJO\nCAJA NUEVA", "color": "purple"}
        if self.model.config_data["untangle_mode"]:
            command["lbl_info3"] = {"text": "MODO:\nRETRABAJO\nTERMINALES", "color": "purple"}


        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command.pop("shutdown", None)
        command.pop("show", None)

        command["position"]["text"] = "POSICIÓN 2"
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        #command["position"]["text"] = "POSICIÓN 2"
      
        turnos = {
            "1":["07-00","18-59"],
            "2":["19-00","06-59"],
            }

        endpoint = "http://{}/contar/historial/FIN".format(self.model.server)
        response = requests.get(endpoint, data=json.dumps(turnos))
        response = response.json()
        print("response: ",response)
        print("He aqui el elefante de la habitacion")

        command = {
                "lcdNumber" : {"value": response["conteo"]},
                    "position" : {"text": response["conteo"]}
                }

        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        
        QTimer.singleShot(100, self.stopTorque)

        if not(self.model.shutdown):
            self.ok.emit()
        
    
            


    def torqueClamp (self):
        command = {}
        for i in self.model.torque_cycles:
             command[i] = self.clamps
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def stopTorque (self):
        for i in self.model.pub_topics["torque"]:
            profile = self.model.torque_data[i]["stop_profile"]
            publish.single(self.model.pub_topics["torque"][i],json.dumps({"profile" : profile}),hostname='127.0.0.1', qos = 2)

    def logout(self, user):
        try:
            Timer(0.05, self.model.log, args = ("LOGOUT",)).start() 
            data = {
                "NAME": user["name"],
                "GAFET": user["pass"],
                "TYPE": user["type"],
                "LOG": "LOGOUT",
                "DATETIME": strftime("%Y/%m/%d %H:%M:%S"),
                }
            endpoint = "http://{}/api/post/login".format(self.model.server)
            resp = requests.post(endpoint, data=json.dumps(data))
        except Exception as ex:
            print("Logout Exception: ", ex)


class Config (QState):
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model
        self.admin = None

    def onEntry(self, event):
        Timer(0.05, self.model.log, args = ("CONFIG",)).start() 
        admin = Admin(data = self.model)

        command = {
            "lbl_result" : {"text": "Sistema en configuración", "color": "green"},
            "lbl_steps" : {"text": "Ciclo de operación deshabilitado", "color": "black"}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def onExit (self, event):
        if exists("data\config"):
            with open("data\config", "rb") as f:
                data = load(f)

                if "encoder_feedback" in data:
                    for i in data["encoder_feedback"]:
                        if type(data["encoder_feedback"][i]) == bool:
                            self.model.config_data["encoder_feedback"][i] = data["encoder_feedback"][i]
                if "retry_btn_mode" in data:
                    for i in data["retry_btn_mode"]:
                        if type(data["retry_btn_mode"][i]) == bool:
                            self.model.config_data[ "retry_btn_mode"][i] = data[ "retry_btn_mode"][i]
                
                #modo untangle (Retrabajo sin cambio de caja, desenredar terminales)
                if "untangle_mode" in data:
                    if type(data["untangle_mode"]) == bool:
                        self.model.config_data["untangle_mode"] = data["untangle_mode"]

                #modo flexible (Retrabajo con cambio de caja)
                if "flexible_mode" in data:
                    if type(data["flexible_mode"]) == bool:
                        self.model.config_data["flexible_mode"] = data["flexible_mode"]

                #modo desapriete
                if "untwist" in data:
                    if type(data["untwist"]) == bool:
                        self.model.config_data["untwist"] = data["untwist"]


class ScanQr (QState):
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        command = {
            "show":{"scanner": True}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command.pop("show")
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = True
        print("model qr_keyboard = True")

    def onExit(self, QEvent):
        command = {
            "show":{"scanner": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = False
        print("model qr_keyboard = False")


class CheckQr (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()
    rework  = pyqtSignal()

    pedido = None
    dbEvent = None
    coincidencias = 0
    pdcrVariantes = ""

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):
        command = {
            "lbl_result" : {"text": "Datamatrix escaneado", "color": "green"},
            "lbl_steps" : {"text": "Validando Etiqueta", "color": "black"}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        Timer(0.05, self.Formato_Etiqueta).start()

    def Formato_Etiqueta (self):
        print("Revisando Formato de Etiqueta")
        try:
            #se guarda la etiqueta escaneada
            self.model.qr_codes["FET"] = self.model.input_data["gui"]["code"]
            #se crea una lista con el contenido de la etiqueta de cada string separado por espacios
            temp = self.model.input_data["gui"]["code"].split (" ")
            #se inicializan estas variables con "--"
            self.model.qr_codes["HM"] = "--"
            self.model.qr_codes["REF"] = "--"
            found_EL = False
            #############################################################################################################
            #############################################################################################################
            ######################################## REVISION DE FORMATO DE ETIQUETA ####################################
            #############################################################################################################
            #############################################################################################################

            correct_lbl = True #inicia correcta la etiqueta
            for i in temp:
                if "HM" in i:                           #se busca el HM
                    self.model.qr_codes["HM"] = i
                else:
                    if self.model.qr_codes["HM"] == "--":
                        correct_lbl = False
                if "IL" in i or "IR" in i:              #se busca la referencia
                    self.model.qr_codes["REF"] = i
                else:
                    if self.model.qr_codes["REF"] == "--":
                        correct_lbl = False
                if "EL." in i:                          #se busca que sea una etiqueta de FET
                    correct_lbl = True
                    found_EL = True
                else:
                    if found_EL == False:
                        correct_lbl = False

            #correct_lbl solo será True si se encontró un HM, una referencia y EL. en la etiqueta.

            #casos únicos para deshabilitar en automático la trazabilidad
            if self.model.qr_codes["HM"] == "HM000000011936":
                self.model.config_data["trazabilidad"] = False
            if self.model.qr_codes["HM"] == "HM000000011925":
                self.model.config_data["trazabilidad"] = False
            if self.model.qr_codes["HM"] == "HM000000011920":
                self.model.config_data["trazabilidad"] = False
            if self.model.config_data["trazabilidad"] == False:
                command = {
                    "lbl_info3" : {"text": "Trazabilidad\nDesactivada", "color": "red"}
                }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            ###############################################################

            if correct_lbl == False:
                command = {
                        "lbl_result" : {"text": "Datamatrix incorrecto", "color": "red"},
                        "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                        }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.nok.emit()
                return
            else:
                command = {
                        "lbl_result" : {"text": "Formato Etiqueta OK", "color": "green"},
                        "lbl_steps" : {"text": "Validando Trazabilidad", "color": "black"}
                        }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.Revision_Trazabilidad).start()

        except Exception as ex:
            print("Exeption Formato Etiqueta: ", ex) 
            command = {
                "lbl_result" : {"text": ex, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()

    def Revision_Trazabilidad (self):

        print("REVISION DE TAZABILIDAD - Estado de Sistema de Trazabilidad: ",self.model.config_data["trazabilidad"])
        try:

            #############################################################################################################
            #############################################################################################################
            ######################################## REVISION DE TRAZABILIDAD ###########################################
            #############################################################################################################
            #############################################################################################################

            if self.model.config_data["trazabilidad"]==False and self.model.config_data["untwist"]==False and self.model.config_data["flexible_mode"]==False and self.model.config_data["untangle_mode"]==False:
                print("||MODO Trazabilidad DESHABILITADA")
                command = {
                        "lbl_result" : {"text": "Trazabilidad Deshabilitada", "color": "green"},
                        "lbl_steps" : {"text": "Buscando Contenido del Arnés", "color": "black"}
                        }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.Busqueda_Pedido).start()
            elif self.model.config_data["untwist"]==True:
                print("||MODO DESAPRIETE")
                print("||No se borra su trazabilidad - porque CALIDAD autorizó este desapriete y deben borrar su trazabilidad para poder volverlo a pasar")
                print("||Ya sea desapriete completo o de algunas terminales")
                command = {
                        "lbl_result" : {"text": "MODO DESAPRIETE", "color": "green"},
                        "lbl_steps" : {"text": "Buscando Contenido del Arnés", "color": "black"}
                        }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.Busqueda_Pedido).start()
            elif self.model.config_data["untangle_mode"]==True:
                print("||MODO RETRABAJO DE TERMINALES")
                print("||En este MODO no hay problema con Trazabilidad porque no se quita ninguna caja, incluso se pide QR anterior")
                command = {
                        "lbl_result" : {"text": "MODO RETRABAJO DE TERMINALES", "color": "green"},
                        "lbl_steps" : {"text": "Buscando Contenido del Arnés", "color": "black"}
                        }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.Busqueda_Pedido).start()
            elif self.model.config_data["flexible_mode"]==True:
                print("||MODO RETRABAJO CON CAMBIO DE CAJA") 
                print("||INDUCCION - solamente si se desaprieta una caja PDCD,PDCP,PDCR - se deberá borrar ENTINDUCCION,SALINDUCCION,ENTVISION,SALVISION y cambiar ubicación a SALIDA_DE_INSERCION")
                print("||VISION - solamente si se desaprieta  una caja PDCD,PDCP,PDCR - se deberá borrar ENTVISION,SALVISION y cambiar ubicación a SALIDA_DE_INSERCION")

                command = {
                        "lbl_result" : {"text": "MODO RETRABAJO CON CAMBIO DE CAJA", "color": "green"},
                        "lbl_steps" : {"text": "Buscando Contenido del Arnés", "color": "black"}
                        }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.Busqueda_Pedido).start()
            #si la trazabilidad está HABILITADA - y es un ciclo NORMAL
            else:
                print("||||||||||||Consulta de HM a FAMX2||||||||||||")
                try:
                    endpoint = "http://{}/seghm/get/seghm/NAMEPREENSAMBLE/=/INTERIOR/HM/=/{}".format(self.model.server,self.model.qr_codes["HM"])
                    famx2response = requests.get(endpoint).json()
                    print("||Respuesta de FAMX2: \n",famx2response)

                    #No existen coincidencias del HM en FAMX2
                    if "items" in famx2response:
                        print("||ITEMS en response - no se encontraron coincidencias en FAMX2")
                        command = {
                            "lbl_result" : {"text": "HM no registrado en Sistema de Trazabilidad", "color": "red"},
                            "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                            }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return
                    else:
                        self.model.famx2response = famx2response
                except Exception as ex:
                        print("||Conexión con FAMX2 exception: ", ex)
                        command = {
                                "lbl_result" : {"text": "Error de Conexión con Sistema de Trazabilidad", "color": "red", "font": "40pt"},
                                "lbl_steps" : {"text": "Verifique su conexión o deshabilite el Sistema de Trazabilidad", "color": "black", "font": "22pt"}
                                }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return
                #si la trazabilidad está habilitada y no está en modo desapriete, modo cambio de caja ni modo desenredar
                if self.model.config_data["trazabilidad"]==True and self.model.config_data["untwist"]==False and self.model.config_data["flexible_mode"]==False and self.model.config_data["untangle_mode"]==False:
                    print("||MODO Ciclo Normal")
                    try:
                        ubicacion_str = str(famx2response["UBICACION"])
                        ubicacion_str = ubicacion_str.replace(" ","")

                        print("||FAMX2 Salida de FET: \n",famx2response["SALFET"])
                        print("||FAMX2 Ubicación: \n",ubicacion_str)

                        #Si la columna que indica la hora de salida de FET, es diferente a None, significa que tiene registro de una fecha de FET.
                        if famx2response["SALFET"] != None:
                            print("||El arnés ya tiene registro de fecha de FET")
                            #Si la ubicación del HM del Arnés es SALIDA_DE_FET

                            if ubicacion_str == "SALIDA_DE_FET" or ubicacion_str == "ENTRADA_A_TORQUE":
                                print("||La ubicación del arnés es SALIDA_DE_FET o ENTRADA_A_TORQUE")
                                #Arnés con fecha SALFET, ubicación: SALIDA_DE_FET, y la referencia de trazabilidad y etiqueta coinciden
                                if famx2response["REFERENCIA"] == self.model.qr_codes["REF"]:
                                    print("||La referencia en Trazabilidad y en la etiqueta es la misma")
                                    #Se guarda el id del arnés de FAMX2 en el modelo para realizar updates en el servidor de FAMX2.
                                    self.model.id_HM = famx2response["id"]
                                    self.model.datetime = datetime.now()
                                    ##################### Trazabilidad FAMX2 Update de Información########################
                                    print("||Realizando el Update de ENTRADA a Trazabilidad en FAMX2")
                                    print("||ID a la que se realizará el Update para Trazabilidad",self.model.id_HM)
                                    entTrazabilidad = {
                                        "ENTTORQUE": self.model.datetime.strftime("%Y/%m/%d %H:%M:%S"),
                                        "UBICACION": "ENTRADA_A_TORQUE",
                                        "NAMETORQUE": self.model.serial
                                        }
                                    endpointUpdate = "http://{}/seghm/update/seghm/{}".format(self.model.server,self.model.id_HM)

                                    #variable local inicia como True
                                    traza_ok = True

                                    #una respuesta correcta regresa: response = {"items": 1}
                                    respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(entTrazabilidad))
                                    respTrazabilidad = respTrazabilidad.json()
                                    print("Resp del update: ",respTrazabilidad)

                                    if "exception" in respTrazabilidad:
                                        sleep(0.5)
                                        respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(entTrazabilidad))
                                        respTrazabilidad = respTrazabilidad.json()
                                        print("Resp del update: ",respTrazabilidad)

                                        if "exception" in respTrazabilidad:
                                            sleep(0.5)
                                            respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(entTrazabilidad))
                                            respTrazabilidad = respTrazabilidad.json()
                                            print("Resp del update: ",respTrazabilidad)

                                            if "exception" in respTrazabilidad:

                                                print("no se logró hacer el update en trazabilidad")
                                                command = {
                                                            "lbl_result" : {"text": "No se logró hacer el update de Trazabilidad", "color": "red"},
                                                            "lbl_steps" : {"text": "Intenta Ingresar nuevamente arnés", "color": "black"}
                                                            }
                                                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                                traza_ok = False
                                                self.nok.emit()
                                                return


                                    #si el update de trazabilidad se hizo correcatmente...
                                    if traza_ok == True: 
                                        command = {
                                                "lbl_result" : {"text": "Trazabilidad OK", "color": "green"},
                                                "lbl_steps" : {"text": "Buscando Arnés en Base de Datos", "color": "black"}
                                                }
                                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                        Timer(0.05, self.Busqueda_Pedido_Nivel).start()

                                #si la referencia de trazabilidad NO coincide con la que viene en la etiqueta...
                                else:
                                    print("||La REFERENCIA no coincide con Trazabilidad, NO puede entrar a Torque")
                                    command = {
                                    "lbl_result" : {"text": "REFERENCIA de etiqueta no coincide con Trazabilidad", "color": "red"},
                                    "lbl_steps" : {"text": "Avisar a mesa de FET", "color": "black"}
                                    }
                                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                    self.nok.emit()
                                    return

                            #la ubicación del HM es diferente a SALIDA_DE_FET
                            else:
                                print("||El Arnés se encuentra en una Ubicación Diferente a SALIDA_DE_FET o ENTRADA_A_TORQUE")
                                command = {
                                "lbl_result" : {"text": "Ubicación de HM: " + ubicacion_str, "color": "red"},
                                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                }
                                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                self.nok.emit()
                                return

                        #Si la columna que indica la hora de salida de FET es None, significa que no ha completado esa estación y NO puede entrar aún a Torque.
                        else:
                            print("||El Arnés no ha pasado por la estación anterior (FET) por lo que no puede entrar a Torque")
                            command = {
                            "lbl_result" : {"text": "Arnés sin Historial de FET", "color": "red"},
                            "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                            }
                            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            self.nok.emit()
                            return
                    except Exception as ex:
                        print("||Conexión con FAMX2 exception: ", ex)
                        command = {
                                "lbl_result" : {"text": "Error de Contenido de Trazabilidad", "color": "red", "font": "40pt"},
                                "lbl_steps" : {"text": "Verifique Información de Arnés con IT", "color": "black", "font": "22pt"}
                                }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return
                    
        except Exception as ex:
            print("Exeption Revisión Trazabilidad: ", ex) 
            command = {
                "lbl_result" : {"text": ex, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()

    def Busqueda_Pedido (self):

        self.pedido = None
        self.dbEvent = None
        self.coincidencias = 0
        self.pdcrVariantes = ""

        try:
            #############################################################################################################
            #############################################################################################################
            ########################## BUSCAR PEDIDO (REFERENCIA) EN LOS EVENTOS LOCALES ################################
            #############################################################################################################
            #############################################################################################################
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++++++++ BUSCANDO REFERENCIA EN EVENTOS ++++++++++++++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("+++++++++++++++++++++++++++++++++++++++++++++++ Busqueda en DB Local +++++++++++++++++++++++++++++++++++++++++++++++++++++")

            #se obtiene la lista de eventos
            endpoint = "http://{}/api/get/eventos".format(self.model.server)
            eventos = requests.get(endpoint).json()
            #print("Lista eventos:\n",eventos)
            for key in eventos["eventos"].keys():
                print("++++++++++++++++++++++++++++ Evento Actual ++++++++++++++++++++++++++++: ",key)
                print("++++++++++++++++++++++++++++ ACTIVE: ",eventos["eventos"][key][1])
                #si el evento está ACTIVO
                if eventos["eventos"][key][1] == 1:
                    endpoint = "http://{}/api/get/{}/pedidos/PEDIDO/=/{}/ACTIVE/=/1".format(self.model.server, key, self.model.qr_codes["REF"])
                    response = requests.get(endpoint).json()

                    #PEDIDO tiene la estructura:

                    #pedido[ID] = 404                                               ID en la base de datos
                    #pedido[PEDIDO] = ILX29620231008788                             Referencia
                    #pedido[DATETIME] = 2023-01-24 01:44:05                         Fecha de creación
                    #pedido[MODULOS_VISION] =                                       Modulos de visión (Son todos los módulos del .DAT)  
                    #{"INTERIOR": ["A2965404821", "A2965404900", "A2965405003", "A2965405021", "A2965405118", "A2965405120", "A2965405416", "A2965405518", "A2965405621", "A2965406021", "A2965406119", "A2965406303", "A2965406421", "A2965406603", "A2965406621", "A2965406719", "A2965406818", "A2965406821", "A2965407000", "A2965407021", "A2965407022", "A2965407203", "A2965407216", "A2965407221", "A2965407300", 
                    #"A2965407416", "A2965407503", "A2965407516", "A2965407519", "A2965407620", "A2965407803", "A2965407814", "A2965407820", "A2965407928", "A2965408000", "A2965408100", "A2965408122", "A2965408200", "A2965408322", "A2965408403", "A2965408423", "A2965408623", "A2965408718", "A2965408722", "A2965408803", "A2965408900", "A2965408922", "A2965409014", "A2965409023", "A2965409322", "A2965409423", 
                    #"A2965409500", "A2965409507", "A2965409511", "A2965409518", "A2965409522", "A2965409600", "A2965409700", "A2965409708", "A2965409712", "A2965409718", "A2965409922", "A2968210900", "A2968211000", "A2968211100", "A2968211200", "A2968211300", "A2968211400", "A2968211500", "A2968211600", "A2968211700", "A2968211800", "A2968605000", "A2975402001", "A2975407316", "A2975848402", "A2239060302", 
                    #"A2239060602", "A2239061002", "A2955452900", "A2963205200", "A2965400024", "A2965400224", "A2965400424", "A2965400519", "A2965400608", "A2965400708", "A2965400713", "A2965400921", "A2965401008", "A2965401021", "A2965401121", "A2965401213", "A2965401614", "A2965401624", "A2965401814", "A2965402100", "A2965402224", "A2965402319", "A2965402414", "A2965402500", "A2965402514", "A2965402624", 
                    #"A2965403008", "A2965403013", "A2965403014", "A2965403029", "A2965403224", "A2965403300", "A2965403314", "A2965403400", "A2965403418", "A2965403514", "A2965403600", "A2965403618", "A2965403714", "A2965403718", "A2965403800", "A2965403814", "A2965403818", "A2965403908", "A2965404000", "A2965404015", "A2965404115", "A2965404215", "A2965404319", "A2965404400", "A2965404500", "A2965404518", 
                    #"A2965404603", "A2965404700", "A2965404712", "A2965404727"]}
                    #pedido[MODULOS_TORQUE] =                                       Modulos de torque (Son todos los módulos del .DAT)
                    #{"INTERIOR": ["A2965404821", "A2965404900", "A2965405003", "A2965405021", "A2965405118", "A2965405120", "A2965405416", "A2965405518", "A2965405621", "A2965406021", "A2965406119", "A2965406303", "A2965406421", "A2965406603", "A2965406621", "A2965406719", "A2965406818", "A2965406821", "A2965407000", "A2965407021", "A2965407022", "A2965407203", "A2965407216", "A2965407221", "A2965407300", 
                    #"A2965407416", "A2965407503", "A2965407516", "A2965407519", "A2965407620", "A2965407803", "A2965407814", "A2965407820", "A2965407928", "A2965408000", "A2965408100", "A2965408122", "A2965408200", "A2965408322", "A2965408403", "A2965408423", "A2965408623", "A2965408718", "A2965408722", "A2965408803", "A2965408900", "A2965408922", "A2965409014", "A2965409023", "A2965409322", "A2965409423", 
                    #"A2965409500", "A2965409507", "A2965409511", "A2965409518", "A2965409522", "A2965409600", "A2965409700", "A2965409708", "A2965409712", "A2965409718", "A2965409922", "A2968210900", "A2968211000", "A2968211100", "A2968211200", "A2968211300", "A2968211400", "A2968211500", "A2968211600", "A2968211700", "A2968211800", "A2968605000", "A2975402001", "A2975407316", "A2975848402", "A2239060302", 
                    #"A2239060602", "A2239061002", "A2955452900", "A2963205200", "A2965400024", "A2965400224", "A2965400424", "A2965400519", "A2965400608", "A2965400708", "A2965400713", "A2965400921", "A2965401008", "A2965401021", "A2965401121", "A2965401213", "A2965401614", "A2965401624", "A2965401814", "A2965402100", "A2965402224", "A2965402319", "A2965402414", "A2965402500", "A2965402514", "A2965402624", 
                    #"A2965403008", "A2965403013", "A2965403014", "A2965403029", "A2965403224", "A2965403300", "A2965403314", "A2965403400", "A2965403418", "A2965403514", "A2965403600", "A2965403618", "A2965403714", "A2965403718", "A2965403800", "A2965403814", "A2965403818", "A2965403908", "A2965404000", "A2965404015", "A2965404115", "A2965404215", "A2965404319", "A2965404400", "A2965404500", "A2965404518", 
                    #"A2965404603", "A2965404700", "A2965404712", "A2965404727"]}
                    #pedido[MODULOS ALTURA] =                                       Modulos de altura (Son todos los módulos del .DAT)
                    #{"INTERIOR": ["A2965404821", "A2965404900", "A2965405003", "A2965405021", "A2965405118", "A2965405120", "A2965405416", "A2965405518", "A2965405621", "A2965406021", "A2965406119", "A2965406303", "A2965406421", "A2965406603", "A2965406621", "A2965406719", "A2965406818", "A2965406821", "A2965407000", "A2965407021", "A2965407022", "A2965407203", "A2965407216", "A2965407221", "A2965407300", 
                    #"A2965407416", "A2965407503", "A2965407516", "A2965407519", "A2965407620", "A2965407803", "A2965407814", "A2965407820", "A2965407928", "A2965408000", "A2965408100", "A2965408122", "A2965408200", "A2965408322", "A2965408403", "A2965408423", "A2965408623", "A2965408718", "A2965408722", "A2965408803", "A2965408900", "A2965408922", "A2965409014", "A2965409023", "A2965409322", "A2965409423", 
                    #"A2965409500", "A2965409507", "A2965409511", "A2965409518", "A2965409522", "A2965409600", "A2965409700", "A2965409708", "A2965409712", "A2965409718", "A2965409922", "A2968210900", "A2968211000", "A2968211100", "A2968211200", "A2968211300", "A2968211400", "A2968211500", "A2968211600", "A2968211700", "A2968211800", "A2968605000", "A2975402001", "A2975407316", "A2975848402", "A2239060302", 
                    #"A2239060602", "A2239061002", "A2955452900", "A2963205200", "A2965400024", "A2965400224", "A2965400424", "A2965400519", "A2965400608", "A2965400708", "A2965400713", "A2965400921", "A2965401008", "A2965401021", "A2965401121", "A2965401213", "A2965401614", "A2965401624", "A2965401814", "A2965402100", "A2965402224", "A2965402319", "A2965402414", "A2965402500", "A2965402514", "A2965402624", 
                    #"A2965403008", "A2965403013", "A2965403014", "A2965403029", "A2965403224", "A2965403300", "A2965403314", "A2965403400", "A2965403418", "A2965403514", "A2965403600", "A2965403618", "A2965403714", "A2965403718", "A2965403800", "A2965403814", "A2965403818", "A2965403908", "A2965404000", "A2965404015", "A2965404115", "A2965404215", "A2965404319", "A2965404400", "A2965404500", "A2965404518", 
                    #"A2965404603", "A2965404700", "A2965404712", "A2965404727"]}
                    #pedido[QR_BOXES] =                                             Códigos QR de cajas y las que están habilitadas para ese pedido
                    #{"PDC-R": ["", false], 
                    #"PDC-RMID": ["12239061502", true], 
                    #"PDC-RS": ["", false], 
                    #"PDC-D": ["12239060402", true], 
                    #"PDC-P": ["12239060702", true], 
                    #"MFB-P1": ["12975402001", true], 
                    #"MFB-S": ["12235403215", true], 
                    #"MFB-E": ["12975403015", true], 
                    #"MFB-P2": ["12975407316", true]}
                    #pedido[ACTIVE] = 1                                             Si se encuentra activo

                    #si se encuentra el PEDIDO en este evento en la Base de Datos LOCAL
                    if "PEDIDO" in response:
                        print("++++++++++++++++++++++++++++ REFERENCIA ENCONTRADA EN ESTE EVENTO")
                        self.dbEvent = key #se guarda el nombre del evento donde se encontró
                        self.coincidencias += 1 #se suma el contador de coincidencias para saber en cuantos eventos está cargada la referencia(también conocido como pedido,dat o modularidad)
                        self.pedido = response # se guarda el pedido del evento donde se encontró coincidencia
                    
                    
            #Si no se encontró ninguna coincidencia ... se busca el mismo PEDIDO en los eventos de las Bases de Datos de las otras Estaciones
            if self.coincidencias == 0:
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("------------------------------------------- Busqueda en DB de otras ESTACIONES -------------------------------------------")
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                #se obtiene la lista de eventos
                endpoint = "http://{}/api/get/eventos".format(self.model.server_ET1)
                eventos = requests.get(endpoint).json()
                for key in eventos["eventos"].keys():
                    print("++++++++++++++++++++++++++++ Evento Actual ET-MBI-1 ++++++++++++++++++++++++++++: ",key)
                    print("++++++++++++++++++++++++++++ ACTIVE: ",eventos["eventos"][key][1])
                    #si el evento está ACTIVO
                    if eventos["eventos"][key][1] == 1:
                        endpoint = "http://{}/api/get/{}/pedidos/PEDIDO/=/{}/ACTIVE/=/1".format(self.model.server_ET1, key, self.model.qr_codes["REF"])
                        response = requests.get(endpoint).json()
                        #si se encuentra el PEDIDO en este evento en la Base de Datos LOCAL
                        if "PEDIDO" in response:
                            print("++++++++++++++++++++++++++++ REFERENCIA ENCONTRADA EN ESTE EVENTO")
                            self.dbEvent = key #se guarda el nombre del evento donde se encontró
                            self.coincidencias += 1 #se suma el contador de coincidencias para saber en cuantos eventos está cargada la referencia(también conocido como pedido,dat o modularidad)
                            self.pedido = response # se guarda el pedido del evento donde se encontró coincidencia
            #Si no se encontró ninguna coincidencia ... se busca el mismo PEDIDO en los eventos de las Bases de Datos de las otras Estaciones
            if self.coincidencias == 0:
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("------------------------------------------- Busqueda en DB de otras ESTACIONES -------------------------------------------")
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                #se obtiene la lista de eventos
                endpoint = "http://{}/api/get/eventos".format(self.model.server_ET3)
                eventos = requests.get(endpoint).json()
                for key in eventos["eventos"].keys():
                    print("++++++++++++++++++++++++++++ Evento Actual ET-MBI-1 ++++++++++++++++++++++++++++: ",key)
                    print("++++++++++++++++++++++++++++ ACTIVE: ",eventos["eventos"][key][1])
                    #si el evento está ACTIVO
                    if eventos["eventos"][key][1] == 1:
                        endpoint = "http://{}/api/get/{}/pedidos/PEDIDO/=/{}/ACTIVE/=/1".format(self.model.server_ET3, key, self.model.qr_codes["REF"])
                        response = requests.get(endpoint).json()
                        #si se encuentra el PEDIDO en este evento en la Base de Datos LOCAL
                        if "PEDIDO" in response:
                            print("++++++++++++++++++++++++++++ REFERENCIA ENCONTRADA EN ESTE EVENTO")
                            self.dbEvent = key #se guarda el nombre del evento donde se encontró
                            self.coincidencias += 1 #se suma el contador de coincidencias para saber en cuantos eventos está cargada la referencia(también conocido como pedido,dat o modularidad)
                            self.pedido = response # se guarda el pedido del evento donde se encontró coincidencia

            print("++Coincidencias = ",self.coincidencias)
            #si se encontró el PEDIDO en un evento, el valor de dbEvent será diferente de None
            if self.dbEvent != None:
                print("++La Modularidad pertenece al Evento: ",self.dbEvent)
                if self.coincidencias != 1:
                    print("++Datamatrix Redundante")
                    command = {
                        "lbl_result" : {"text": "Datamatrix redundante", "color": "red"},
                        "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                        }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    self.nok.emit()
                    return
                else:
                    print("Datamatrix Correcto")
                    command = {
                            "lbl_result" : {"text": "Arnés Encontrado en Base de Datos", "color": "green"},
                            "lbl_steps" : {"text": "Revisando Variante de Caja", "color": "black"}
                            }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                    Timer(0.05, self.Revision_Variante).start()

            #No se encontró el Pedido en ningún evento...
            else:
                print("La Modularidad NO pertenece a ningún evento")
                command = {
                    "lbl_result" : {"text": "Datamatrix no registrado", "color": "red"},
                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.nok.emit()
                return

        except Exception as ex:
            print("Exeption Busqueda PEDIDO: ", ex) 
            command = {
                "lbl_result" : {"text": ex, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()

    def Busqueda_Pedido_Nivel (self):

        self.pedido = None
        self.dbEvent = None
        self.coincidencias = 0
        self.pdcrVariantes = ""
        
        if "IL" in self.model.qr_codes["REF"]:
            self.model.conduccion = "izquierda"
            print("arnés izquierdo")
            if "296" in self.model.qr_codes["REF"]:
                print("arnés 296")
                self.model.numero = "x296"
            if "294" in self.model.qr_codes["REF"]:
                print("arnés 294")
                self.model.numero = "x294"

        if "IR" in self.model.qr_codes["REF"]:
            self.model.conduccion = "derecha"
            print("arnés derecho")
            if "296" in self.model.qr_codes["REF"]:
                print("arnés 296")
                self.model.numero = "x296"
            if "294" in self.model.qr_codes["REF"]:
                print("arnés 294")
                self.model.numero = "x294"


        try:
            #############################################################################################################
            #############################################################################################################
            ########################## BUSCAR PEDIDO (REFERENCIA) EN LOS EVENTOS LOCALES ################################
            #############################################################################################################
            #############################################################################################################
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++++++++ BUSCANDO REFERENCIA EN EVENTOS ++++++++++++++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("+++++++++++++++++++++++++++++++++++++++++++++++ Busqueda en DB Local +++++++++++++++++++++++++++++++++++++++++++++++++++++")

            #se obtiene la lista de eventos
            endpoint = "http://{}/api/get/eventos".format(self.model.server)
            eventos = requests.get(endpoint).json()
            #print("Lista eventos:\n",eventos)
            for key in eventos["eventos"].keys():
                print("++++++++++++++++++++++++++++ Evento Actual ++++++++++++++++++++++++++++: ",key)
                print("++++++++++++++++++++++++++++ ACTIVE: ",eventos["eventos"][key][1])
                #si el evento está ACTIVO
                if eventos["eventos"][key][1] == 1:
                    endpoint = "http://{}/api/get/{}/pedidos/PEDIDO/=/{}/ACTIVE/=/1".format(self.model.server, key, self.model.qr_codes["REF"])
                    response = requests.get(endpoint).json()

                    #PEDIDO tiene la estructura:

                    #pedido[ID] = 404                                               ID en la base de datos
                    #pedido[PEDIDO] = ILX29620231008788                             Referencia
                    #pedido[DATETIME] = 2023-01-24 01:44:05                         Fecha de creación
                    #pedido[MODULOS_VISION] =                                       Modulos de visión (Son todos los módulos del .DAT)  
                    #{"INTERIOR": ["A2965404821", "A2965404900", "A2965405003", "A2965405021", "A2965405118", "A2965405120", "A2965405416", "A2965405518", "A2965405621", "A2965406021", "A2965406119", "A2965406303", "A2965406421", "A2965406603", "A2965406621", "A2965406719", "A2965406818", "A2965406821", "A2965407000", "A2965407021", "A2965407022", "A2965407203", "A2965407216", "A2965407221", "A2965407300", 
                    #"A2965407416", "A2965407503", "A2965407516", "A2965407519", "A2965407620", "A2965407803", "A2965407814", "A2965407820", "A2965407928", "A2965408000", "A2965408100", "A2965408122", "A2965408200", "A2965408322", "A2965408403", "A2965408423", "A2965408623", "A2965408718", "A2965408722", "A2965408803", "A2965408900", "A2965408922", "A2965409014", "A2965409023", "A2965409322", "A2965409423", 
                    #"A2965409500", "A2965409507", "A2965409511", "A2965409518", "A2965409522", "A2965409600", "A2965409700", "A2965409708", "A2965409712", "A2965409718", "A2965409922", "A2968210900", "A2968211000", "A2968211100", "A2968211200", "A2968211300", "A2968211400", "A2968211500", "A2968211600", "A2968211700", "A2968211800", "A2968605000", "A2975402001", "A2975407316", "A2975848402", "A2239060302", 
                    #"A2239060602", "A2239061002", "A2955452900", "A2963205200", "A2965400024", "A2965400224", "A2965400424", "A2965400519", "A2965400608", "A2965400708", "A2965400713", "A2965400921", "A2965401008", "A2965401021", "A2965401121", "A2965401213", "A2965401614", "A2965401624", "A2965401814", "A2965402100", "A2965402224", "A2965402319", "A2965402414", "A2965402500", "A2965402514", "A2965402624", 
                    #"A2965403008", "A2965403013", "A2965403014", "A2965403029", "A2965403224", "A2965403300", "A2965403314", "A2965403400", "A2965403418", "A2965403514", "A2965403600", "A2965403618", "A2965403714", "A2965403718", "A2965403800", "A2965403814", "A2965403818", "A2965403908", "A2965404000", "A2965404015", "A2965404115", "A2965404215", "A2965404319", "A2965404400", "A2965404500", "A2965404518", 
                    #"A2965404603", "A2965404700", "A2965404712", "A2965404727"]}
                    #pedido[MODULOS_TORQUE] =                                       Modulos de torque (Son todos los módulos del .DAT)
                    #{"INTERIOR": ["A2965404821", "A2965404900", "A2965405003", "A2965405021", "A2965405118", "A2965405120", "A2965405416", "A2965405518", "A2965405621", "A2965406021", "A2965406119", "A2965406303", "A2965406421", "A2965406603", "A2965406621", "A2965406719", "A2965406818", "A2965406821", "A2965407000", "A2965407021", "A2965407022", "A2965407203", "A2965407216", "A2965407221", "A2965407300", 
                    #"A2965407416", "A2965407503", "A2965407516", "A2965407519", "A2965407620", "A2965407803", "A2965407814", "A2965407820", "A2965407928", "A2965408000", "A2965408100", "A2965408122", "A2965408200", "A2965408322", "A2965408403", "A2965408423", "A2965408623", "A2965408718", "A2965408722", "A2965408803", "A2965408900", "A2965408922", "A2965409014", "A2965409023", "A2965409322", "A2965409423", 
                    #"A2965409500", "A2965409507", "A2965409511", "A2965409518", "A2965409522", "A2965409600", "A2965409700", "A2965409708", "A2965409712", "A2965409718", "A2965409922", "A2968210900", "A2968211000", "A2968211100", "A2968211200", "A2968211300", "A2968211400", "A2968211500", "A2968211600", "A2968211700", "A2968211800", "A2968605000", "A2975402001", "A2975407316", "A2975848402", "A2239060302", 
                    #"A2239060602", "A2239061002", "A2955452900", "A2963205200", "A2965400024", "A2965400224", "A2965400424", "A2965400519", "A2965400608", "A2965400708", "A2965400713", "A2965400921", "A2965401008", "A2965401021", "A2965401121", "A2965401213", "A2965401614", "A2965401624", "A2965401814", "A2965402100", "A2965402224", "A2965402319", "A2965402414", "A2965402500", "A2965402514", "A2965402624", 
                    #"A2965403008", "A2965403013", "A2965403014", "A2965403029", "A2965403224", "A2965403300", "A2965403314", "A2965403400", "A2965403418", "A2965403514", "A2965403600", "A2965403618", "A2965403714", "A2965403718", "A2965403800", "A2965403814", "A2965403818", "A2965403908", "A2965404000", "A2965404015", "A2965404115", "A2965404215", "A2965404319", "A2965404400", "A2965404500", "A2965404518", 
                    #"A2965404603", "A2965404700", "A2965404712", "A2965404727"]}
                    #pedido[MODULOS ALTURA] =                                       Modulos de altura (Son todos los módulos del .DAT)
                    #{"INTERIOR": ["A2965404821", "A2965404900", "A2965405003", "A2965405021", "A2965405118", "A2965405120", "A2965405416", "A2965405518", "A2965405621", "A2965406021", "A2965406119", "A2965406303", "A2965406421", "A2965406603", "A2965406621", "A2965406719", "A2965406818", "A2965406821", "A2965407000", "A2965407021", "A2965407022", "A2965407203", "A2965407216", "A2965407221", "A2965407300", 
                    #"A2965407416", "A2965407503", "A2965407516", "A2965407519", "A2965407620", "A2965407803", "A2965407814", "A2965407820", "A2965407928", "A2965408000", "A2965408100", "A2965408122", "A2965408200", "A2965408322", "A2965408403", "A2965408423", "A2965408623", "A2965408718", "A2965408722", "A2965408803", "A2965408900", "A2965408922", "A2965409014", "A2965409023", "A2965409322", "A2965409423", 
                    #"A2965409500", "A2965409507", "A2965409511", "A2965409518", "A2965409522", "A2965409600", "A2965409700", "A2965409708", "A2965409712", "A2965409718", "A2965409922", "A2968210900", "A2968211000", "A2968211100", "A2968211200", "A2968211300", "A2968211400", "A2968211500", "A2968211600", "A2968211700", "A2968211800", "A2968605000", "A2975402001", "A2975407316", "A2975848402", "A2239060302", 
                    #"A2239060602", "A2239061002", "A2955452900", "A2963205200", "A2965400024", "A2965400224", "A2965400424", "A2965400519", "A2965400608", "A2965400708", "A2965400713", "A2965400921", "A2965401008", "A2965401021", "A2965401121", "A2965401213", "A2965401614", "A2965401624", "A2965401814", "A2965402100", "A2965402224", "A2965402319", "A2965402414", "A2965402500", "A2965402514", "A2965402624", 
                    #"A2965403008", "A2965403013", "A2965403014", "A2965403029", "A2965403224", "A2965403300", "A2965403314", "A2965403400", "A2965403418", "A2965403514", "A2965403600", "A2965403618", "A2965403714", "A2965403718", "A2965403800", "A2965403814", "A2965403818", "A2965403908", "A2965404000", "A2965404015", "A2965404115", "A2965404215", "A2965404319", "A2965404400", "A2965404500", "A2965404518", 
                    #"A2965404603", "A2965404700", "A2965404712", "A2965404727"]}
                    #pedido[QR_BOXES] =                                             Códigos QR de cajas y las que están habilitadas para ese pedido
                    #{"PDC-R": ["", false], 
                    #"PDC-RMID": ["12239061502", true], 
                    #"PDC-RS": ["", false], 
                    #"PDC-D": ["12239060402", true], 
                    #"PDC-P": ["12239060702", true], 
                    #"MFB-P1": ["12975402001", true], 
                    #"MFB-S": ["12235403215", true], 
                    #"MFB-E": ["12975403015", true], 
                    #"MFB-P2": ["12975407316", true]}
                    #pedido[ACTIVE] = 1                                             Si se encuentra activo

                    #si se encuentra el PEDIDO en este evento en la Base de Datos LOCAL
                    if "PEDIDO" in response:
                        print("++++++++++++++++++++++++++++ REFERENCIA ENCONTRADA EN ESTE EVENTO")
                        self.dbEvent = key #se guarda el nombre del evento donde se encontró
                        self.coincidencias += 1 #se suma el contador de coincidencias para saber en cuantos eventos está cargada la referencia(también conocido como pedido,dat o modularidad)
                        self.pedido = response # se guarda el pedido del evento donde se encontró coincidencia
                    
                    
            #Si no se encontró ninguna coincidencia ... se busca el mismo PEDIDO en los eventos de las Bases de Datos de las otras Estaciones
            if self.coincidencias == 0:
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("------------------------------------------- Busqueda en DB de otras ESTACIONES -------------------------------------------")
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                #se obtiene la lista de eventos
                endpoint = "http://{}/api/get/eventos".format(self.model.server_ET1)
                eventos = requests.get(endpoint).json()
                for key in eventos["eventos"].keys():
                    print("++++++++++++++++++++++++++++ Evento Actual ET-MBI-1 ++++++++++++++++++++++++++++: ",key)
                    print("++++++++++++++++++++++++++++ ACTIVE: ",eventos["eventos"][key][1])
                    #si el evento está ACTIVO
                    if eventos["eventos"][key][1] == 1:
                        endpoint = "http://{}/api/get/{}/pedidos/PEDIDO/=/{}/ACTIVE/=/1".format(self.model.server_ET1, key, self.model.qr_codes["REF"])
                        response = requests.get(endpoint).json()
                        #si se encuentra el PEDIDO en este evento en la Base de Datos LOCAL
                        if "PEDIDO" in response:
                            print("++++++++++++++++++++++++++++ REFERENCIA ENCONTRADA EN ESTE EVENTO")
                            self.dbEvent = key #se guarda el nombre del evento donde se encontró
                            self.coincidencias += 1 #se suma el contador de coincidencias para saber en cuantos eventos está cargada la referencia(también conocido como pedido,dat o modularidad)
                            self.pedido = response # se guarda el pedido del evento donde se encontró coincidencia
            #Si no se encontró ninguna coincidencia ... se busca el mismo PEDIDO en los eventos de las Bases de Datos de las otras Estaciones
            if self.coincidencias == 0:
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("------------------------------------------- Busqueda en DB de otras ESTACIONES -------------------------------------------")
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                #se obtiene la lista de eventos
                endpoint = "http://{}/api/get/eventos".format(self.model.server_ET3)
                eventos = requests.get(endpoint).json()
                for key in eventos["eventos"].keys():
                    print("++++++++++++++++++++++++++++ Evento Actual ET-MBI-1 ++++++++++++++++++++++++++++: ",key)
                    print("++++++++++++++++++++++++++++ ACTIVE: ",eventos["eventos"][key][1])
                    #si el evento está ACTIVO
                    if eventos["eventos"][key][1] == 1:
                        endpoint = "http://{}/api/get/{}/pedidos/PEDIDO/=/{}/ACTIVE/=/1".format(self.model.server_ET3, key, self.model.qr_codes["REF"])
                        response = requests.get(endpoint).json()
                        #si se encuentra el PEDIDO en este evento en la Base de Datos LOCAL
                        if "PEDIDO" in response:
                            print("++++++++++++++++++++++++++++ REFERENCIA ENCONTRADA EN ESTE EVENTO")
                            self.dbEvent = key #se guarda el nombre del evento donde se encontró
                            self.coincidencias += 1 #se suma el contador de coincidencias para saber en cuantos eventos está cargada la referencia(también conocido como pedido,dat o modularidad)
                            self.pedido = response # se guarda el pedido del evento donde se encontró coincidencia

            print("++Coincidencias = ",self.coincidencias)
            #si se encontró el PEDIDO en un evento, el valor de dbEvent será diferente de None
            if self.dbEvent != None:
                print("++La Modularidad pertenece al Evento: ",self.dbEvent)
                if self.coincidencias != 1:
                    print("++Datamatrix Redundante")
                    command = {
                        "lbl_result" : {"text": "Datamatrix redundante", "color": "red"},
                        "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                        }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    self.nok.emit()
                    return
                else:
                    print("Datamatrix Correcto")
                    command = {
                            "lbl_result" : {"text": "Arnés Encontrado en Base de Datos", "color": "green"},
                            "lbl_steps" : {"text": "Revisando Variante de Caja", "color": "black"}
                            }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                    Timer(0.05, self.Revision_Variante).start()

            #No se encontró el Pedido en ningún evento...
            else:
                print("La Modularidad NO pertenece a ningún evento")
                command = {
                    "lbl_result" : {"text": "Datamatrix no registrado", "color": "red"},
                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                self.nok.emit()
                return

        except Exception as ex:
            print("Exeption Busqueda PEDIDO: ", ex) 
            command = {
                "lbl_result" : {"text": ex, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()

    def Revision_Variante(self):

        try:
            print("++REVISANDO VARIANTE DE CAJA")
            ######################################## VARIANTE PDCR del evento ###########################################
            endpoint = "http://{}/api/get/{}/pdcr/variantes".format(self.model.server, self.dbEvent)
            self.pdcrVariantes = requests.get(endpoint).json()
            print("++Lista Final de Variantes PDC-R:\n",self.pdcrVariantes)

            command = {
                    "lbl_result" : {"text": "Variante de caja Encontrada", "color": "green"},
                    "lbl_steps" : {"text": "Revisando Historial de Arnés", "color": "black"}
                    }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            Timer(0.05, self.Revision_Historial).start()

        except Exception as ex:
            print("Exeption Revisión Variante: ", ex) 
            command = {
                "lbl_result" : {"text": ex, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()

    def Revision_Historial (self):
        try:
            #############################################################################################################
            #############################################################################################################
            ########################################### HISTORIAL - RETRABAJOS ##########################################
            #############################################################################################################
            #############################################################################################################

            ## EJEMPLO CONSULTA DE HISTORIAL DE HM EN OTRA ESTACION CON SU RESPECTIVA API##
            #HM = "HM000000068090"
            #endpoint = "http://{}/api/get/historial/HM/=/{}/_/_/_".format(self.model.server_ET3, HM)
            #response = requests.get(endpoint).json()
            #print(response)

            #response de Historial:

            #{'ALTURA':     '{}',
            #'ANGULO':      '{"PDC-P": {"E1": 16.6}, 
            #                "PDC-D": {"E1": 16.5}, 
            #                "BATTERY": {"BT": 17.6}, 
            #                "BATTERY-2": {"BT": null}, 
            #                "MFB-P1": {"A47": null, "A46": 19.1, "A45": 19.5, "A44": null, "A43": 18.3, "A41": 20.3, "A42": 19.3}, 
            #                "MFB-S": {"A51": null, "A52": null, "A53": null, "A54": null, "A55": null, "A56": null}, 
            #                "MFB-E": {"E1": null, "A1": null, "A2": null}, 
            #                "MFB-P2": {"A20": 21.6, "A26": 17.7, "A30": 20.2, "A25": 16.1, "A21": 16.9, "A29": 16.2, "A22": 18.7, "A28": null, "A23": null, "A27": null, "A24": 25.0}, 
            #                "PDC-R": {"E1": null}, 
            #                "PDC-RS": {"E1": null}, 
            #                "PDC-RMID": {"E1": 30.1}}',
            #'FIN':         'Sat, 11 Feb 2023 11:05:33 GMT',
            #'HM':          'HM000000068090',
            #'ID':          7586,
            #'INICIO':      'Sat, 11 Feb 2023 10:52:04 GMT',
            #'INTENTOS_T':  '{"PDC-P": {"E1": 0}, 
            #                "PDC-D": {"E1": 0}, 
            #                "BATTERY": {"BT": 0}, 
            #                "BATTERY-2": {"BT": 0}, 
            #                "MFB-P1": {"A47": 0, "A46": 0, "A45": 0, "A44": 0, "A43": 0, "A41": 2, "A42": 0}, 
            #                "MFB-S": {"A51": 0, "A52": 0, "A53": 0, "A54": 0, "A55": 0, "A56": 0}, 
            #                "MFB-E": {"E1": 0, "A1": 0, "A2": 0}, 
            #                "MFB-P2": {"A20": 0, "A26": 0, "A30": 1, "A25": 0, "A21": 1, "A29": 0, "A22": 0, "A28": 0, "A23": 0, "A27": 0, "A24": 0}, 
            #                "PDC-R": {"E1": 0}, 
            #                "PDC-RS": {"E1": 0}, 
            #                "PDC-RMID": {"E1": 1}}',
            #'INTENTOS_VA': '{}',
            #'NOTAS':       '{"TORQUE": ["APRIETE", "OK"]}',
            #'RESULTADO':    1,
            #'SCRAP':       '{"PDC-RMID": {"E1": 1}, 
            #                "MFB-P2": {"A21": 1, "A30": 1}, 
            #                "MFB-P1": {"A41": 2}}',
            #'SERIALES':    '{"FET": "A 294 540 91 00 EL. LTG.SATZ LL RBA ZGS\\u00d1 007 X294 PRO3 HM000000068090 ILX29420231009183 6352941 FET 4 02-09-23 21\\u00d112\\u00d159", 
            #                "HM": "HM000000068090", 
            #                "REF": "ILX29420231009183", 
            #                "PDC-RMID": "122390615022231907751601002053000000", 
            #                "PDC-P": "122390607022233101870302003043000000", 
            #                "PDC-D": "                            122390604022303100769202003033000000", 
            #                "MFB-P1": "                 129754020012229100215301004020000000", 
            #                "MFB-P2": "129754073162232100588201001020000000"}',
            #'TORQUE':      '{"PDC-P": {"E1": 8.06}, 
            #                "PDC-D": {"E1": 8.04}, 
            #                "BATTERY": {"BT": 6.6}, 
            #                "BATTERY-2": {"BT": null}, 
            #                "MFB-P1": {"A41": 16.05, "A47": null, "A43": 8.02, "A46": 16.13, "A44": null, "A42": 8.02, "A45": 7.99}, 
            #                "MFB-S": {"A51": null, "A52": null, "A53": null, "A54": null, "A55": null, "A56": null}, 
            #                "MFB-E": {"E1": null, "A1": null, "A2": null}, 
            #                "MFB-P2": {"A20": 16.16, "A26": 8.06, "A30": 16.1, "A25": 16.13, "A21": 8.06, "A29": 8.06, "A22": 8.06, "A28": null, "A23": null, "A27": null, "A24": 8.06}, 
            #                "PDC-R": {"E1": null}, 
            #                "PDC-RS": {"E1": null}, 
            #                "PDC-RMID": {"E1": 16.03}}',
            #'USUARIO':     'SUPERUSUARIO: IVAN ORTIZ',
            #'VISION':      '{}'}

            endpoint = "http://{}/api/get/historial/HM/=/{}/_/_/_".format(self.model.server, self.model.qr_codes["HM"])
            response = requests.get(endpoint).json()
            

            #si un arnés no tiene historial de haber pasado, la respuesta será {"items":0}
            #si un arnés ya ha pasado por la estación, la respuesta dará contenido y no existirá "items" en response, entonces se emitirá self.rework.emit() para pedir llave
            #si a un arnés procesado anteriormente ya fue autorizado para entrar, self.model.local_data["qr_rework"] será = true
            #si se habilita el modo desapriete self.model.config_data["untwist"] = true
            #si se habilita el modo retrabajo cambio caja self.model.config_data["flexible_mode"] = true
            #si se habilita el modo retrabajo terminales enredadas self.model.config_data["untangle_mode"] = true

            #si {"items":0}(sin historial) o rework=true o untwist=true o modo_retrabajo_caja=true o modo_terminales_enredadas=true
            if ("items" in response and not(response["items"])) or self.model.local_data["qr_rework"] or self.model.config_data["untwist"] or self.model.config_data["flexible_mode"] or self.model.config_data["untangle_mode"]:
                
                #El modo de Retrabajo de Terminales y Desapriete requieren que exista un historial de los seriales del arnés
                if self.model.config_data["untangle_mode"] or self.model.config_data["untwist"]:
                    if "SERIALES" in response:

                        #response["SERIALES"] regresa un string con formato de diccionario o una lista de strings que tienen formato de diccionario según las veces que aparezca en el Historial
                        copia_seriales = copy(response["SERIALES"])
                        seriales_finales = {}

                        #si hay más de un registro en el historial
                        if isinstance(copia_seriales, list):

                            for serial_historial in copia_seriales:

                                #se elimina lo guardado en la etiqueta de FET, el HM y la referencia
                                if "FET" in copia_seriales:
                                    copia_seriales.pop("FET")
                                if "HM" in copia_seriales:
                                    copia_seriales.pop("HM")
                                if "REF" in copia_seriales:
                                    copia_seriales.pop("REF")

                        

                        

                        #si no tiene contenido aparte de la etiqueta
                        if len(copia_seriales) == 0:
                            print("")


                    else:
                        print("NO TIENE SERIALES")


                #se guarda la respuesta del historial del arnés en la variable del model
                self.model.HM_historial = response

                if ("items" in response and not(response["items"])):
                    command = {
                            "lbl_result" : {"text": "Arnés sin Historial Previo", "color": "green"},
                            "lbl_steps" : {"text": "Obteniendo Contenido", "color": "black"}
                            }
                else:
                    command = {
                            "lbl_result" : {"text": "Retrabajo de Arnés", "color": "green"},
                            "lbl_steps" : {"text": "Obteniendo Contenido", "color": "black"}
                            }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.05, self.Construccion_Pedido).start()
            #si no hay ningún modo especial activado y tampoco se recibió "items 0" quiere decir que si se encontró registro de un arnés en el historial con ese HM
            else:
                self.rework.emit()
                return

        except Exception as ex:
            print("Exeption Revision Historial ", ex) 
            command = {
                "lbl_result" : {"text": ex, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()

    def Construccion_Pedido (self):
        try:
            print("")
        except Exception as ex:
            print("Exeption Construccion PEDIDO: ", ex) 
            command = {
                "lbl_result" : {"text": ex, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.nok.emit()

    def API_requests (self):
        try:
            
                response = self.model.HM_historial
                
                if self.model.config_data["untangle_mode"]:

                    if "SERIALES" in response:
                        print("asdasdKLJASDKJASDHJKASD")
                        #for serial in response["SERIALES"]:
                        #    if serial != "FET":
                        #        #se guarda en la misma respuesta el serial pero eliminando los espacios, excepto en la etiqueta de FET
                        #        response["SERIALES"][serial] = str(response["SERIALES"][serial]).replace(" ","")
                    else:
                        print("ASDIUADHKAJSDHAJAKS AQYU VITY TAMBUIENASIHK SDJAS")



                #Obtener SERIALES si ya ha pasado por aquí el arnés
                if self.model.config_data["untangle_mode"] or self.model.config_data["flexible_mode"] or self.model.config_data["untwist"]:

                    #{"FET": "A 294 540 91 00 EL. LTG.SATZ LL RBA ZGS: 007 X294 PRO3 HM000000063699 ILX29420231008041 6306332 FET 1 01/31/23 11:25:32", 
                    #"HM": "HM000000063699", 
                    #"REF": "ILX29420231008041", 
                    #"PDC-RMID": "122390615022230400360601002053000000",  #si es PDC-RMID solo trae esta
                    #"PDC-R": "122390616022223800807601001043000000",     #si es PDC-R solo trae esta
                    #"PDC-P": "122390607022231505395302003043000000", 
                    #"PDC-D": "122390604022224803667202003033000000",
                    #"MFB-P1": "129754020012229002818301004020000000", 
                    #"MFB-P2": "129754073162227800700201001020000000", 
                    #"MFB-E": "129754030152111200024101001E10958560",
                    #"MFB-S": "122354032152230604244301002030000000",
                    #}

                    #Si el arnés ya ha pasado por la máquina anteriormente, y se va a retrabajar (debe tener SERIALES en response), hará lo siguiente:      
                    if "SERIALES" in response:
                        print("Response*******: ",response["SERIALES"])
                        if type(response["SERIALES"]) != list:
                            print("ES UN SOLO REGISTRO!")
                            #De la base de datos en el historial para ese HM se carga el json de la columna SERIALES
                            qr_retrabajo = json.loads(response["SERIALES"])
                            [qr_retrabajo.pop(key, None) for key in ['FET','HM','REF']]
                            self.model.input_data["database"]["qr_retrabajo"] = qr_retrabajo
                            if "PDC-P" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["PDC-P"] = "009"
                            if "MFB-E" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["MFB-E"] = "004"
                            print("Qr_retrabajo modelo: ",self.model.input_data["database"]["qr_retrabajo"])
                        else:
                            print("ES UNA LISTA DE REGISTROS!") #porque hay varios registros de este arnés en el historial

                            qr_retrabajo = json.loads(response["SERIALES"][-1])
                            [qr_retrabajo.pop(key, None) for key in ['FET','HM','REF']]
                            self.model.input_data["database"]["qr_retrabajo"] = qr_retrabajo
                            if "PDC-P" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["PDC-P"] = "009"
                            if "MFB-E" in self.model.input_data["database"]["qr_retrabajo"]:
                                self.model.input_data["database"]["qr_retrabajo"]["MFB-E"] = "004"
                            print("Qr_retrabajo modelo: ",self.model.input_data["database"]["qr_retrabajo"])
                    # Si el arnés que intentan retrabajar es la primera vez que entra a la máquina indicará un error al usuario
                    else:
                        command = {
                            "lbl_result" : {"text": "ERROR DE RETRABAJO", "color": "red"},
                            "lbl_steps" : {"text": "No se encontró registro de este arnés", "color": "black"}
                            }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return


                modules = json.loads(self.pedido["MODULOS_TORQUE"])
                modules = modules[list(modules)[0]]
                modules_v = json.loads(self.pedido["MODULOS_VISION"])
                modules_v = modules_v[list(modules_v)[0]]

                print(f"\n\t\tMODULOS_VISION:\n{modules_v}")
                print("\n\t+++++++++++MODULARIDAD REFERENCIA+++++++++++\n",self.model.qr_codes["REF"])
                print(f"\n\t\tMODULOS_TORQUE:\n{modules}")
                #### MODIFICACIÓN PDCR ####
                flag_s = False
                flag_m = False
                flag_l = False
                flag_variantes = True
                flag_mfbp2_der = False
                flag_mfbp2_izq = False
                mfbp2_serie = ""
                mfbeBox = ""
                battery2Box = ""
                flag_294 = False
                flag_296 = False
                if "294" in self.model.qr_codes["REF"]:
                    print("Evento 294")
                    flag_294 = True
                if "296" in self.model.qr_codes["REF"]:
                    print("Evento 296")
                    flag_296 = True
                    #print("Aqui",pdcrVariantes)
                for s in self.pdcrVariantes["small"]:
                    if s in modules:
                        #print("Tiene un modulo de caja SMALL")
                        flag_s = True
                for m in self.pdcrVariantes["medium"]:
                    if m in modules:
                        #print("Tiene un modulo de caja Medium")
                        flag_m = True
                for l in self.pdcrVariantes["large"]:
                    if l in modules:
                        #print("Tiene un modulo de caja LARGE")
                        flag_l = True
                if "IL" in self.model.qr_codes["REF"]:
                    print("Modularidad de MFB-P2 Izquierda")
                    flag_mfbp2_izq = True
                if "IR" in self.model.qr_codes["REF"]:
                    print("Modularidad de MFB-P2 Derecha")
                    flag_mfbp2_der = True

                print("\t\tFLAGS:\n Flag S - ",flag_s," Flag M - ",flag_m," Flag L - ",flag_l,"\n Flag MFB-P2 DER - ",flag_mfbp2_der," Flag MFB-P2 IZQ - ",flag_mfbp2_izq)
                if flag_s == False and flag_m == False and flag_l == False:
                    flag_variantes = False

                #para mensajes que se publican
                if flag_l == True:
                    varianteDominante = "PDC-R"
                    self.model.largeflag = True
                    self.model.pdcr_serie = "12239061602"
                if flag_m == True and flag_l == False:
                    varianteDominante = "PDC-RMID"
                    self.model.mediumflag = True
                    self.model.pdcr_serie = "12239061502"
                if flag_s == True and flag_m == False and flag_l == False:
                    varianteDominante = "PDC-RS"
                    self.model.smallflag = True
                    self.model.pdcr_serie = "12239061402"

                if flag_mfbp2_der == True and flag_mfbp2_izq == False:
                    self.model.mfbp2_serie = "12975407216"
                if flag_mfbp2_der == False and flag_mfbp2_izq == True:
                    self.model.mfbp2_serie = "12975407316"
                if flag_mfbp2_der == False and flag_mfbp2_izq == False:
                    self.model.mfbp2_serie = "Sin especificar"


                ################################################## SE CONSTRUYE LA MODULARIDAD ###################################################
                #Utilizando cada módulo(obtenidos del pedido, estos son los .DAT
                #y la configuración modulos_torques(obtenida) 
                for i in modules:
                    endpoint = "http://{}/api/get/{}/modulos_torques/MODULO/=/{}/_/=/_".format(self.model.server, self.dbEvent, i)
                    response = requests.get(endpoint).json()
                    if "MODULO" in response:
                        if type(response["MODULO"]) != list:
                            temp = {}
                            for i in response:
                                if "CAJA_" in i:
                                    temp.update(json.loads(response[i]))
                            for i in temp:
                                newBox = False
                                #print("Caja: ******: ",i)
                                if len(temp[i]) == 0:
                                    continue
                                if not(i in self.model.input_data["database"]["modularity"]):
                                    newBox = True
                                for j in temp[i]:
                                    if temp[i][j] == True:
                                        if newBox:
                                            if flag_296 == True or flag_294 == True:
                                                if flag_variantes == True:
                                                    #si hay una caja PDC-R se modifica por la variable PDC-R dominante
                                                    if i == "PDC-R" or i == "PDC-RMID" or i == "PDC-RS":
                                                        i = varianteDominante
                                                else:
                                                    #print("LA MODULARIDAD NO CONTIENE MÓDULOS QUE ESPECIFIQUEN SU VARIANTE EN LA PDC-R")
                                                    command = {
                                                        "lbl_result" : {"text": "La Modularidad no contiene módulos que especifiquen su variante en la PDC-R", "color": "red"},
                                                        "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                                        }
                                                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                                                    self.model.input_data["database"]["modularity"].clear()
                                                    self.model.torque_data["tool1"]["queue"].clear()
                                                    self.model.torque_data["tool2"]["queue"].clear()
                                                    self.model.torque_data["tool3"]["queue"].clear()
                                                    self.nok.emit()
                                            self.model.input_data["database"]["modularity"][i] = []
                                            #print(" AQUI ESTÁ EL NUEVO I!!!!!!!!!: ",i)#### MODIFICACIÓN PDCR ####
                                            newBox = False
                                        if not(j in self.model.input_data["database"]["modularity"][i]):
                                            self.model.input_data["database"]["modularity"][i].append(j)
                                            #print(" AQUI ESTÁ EL J valor!!!!!!!!!: ",j)#### MODIFICACIÓN PDCR ####
                                if not(newBox):
                                    #Si la caja es MFB-P2, se acomodan sus torques de manera inversa (A29,A28...) a excepción de los torques para la Tool de 8mm (A20,A25 y A30)
                                    if i == "MFB-P2":
                                        self.model.input_data["database"]["modularity"][i].sort(reverse=True)
                                        if "A20" in self.model.input_data["database"]["modularity"][i]:
                                            self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A20"))
                                            self.model.input_data["database"]["modularity"][i].append("A20")
                                        if "A25" in self.model.input_data["database"]["modularity"][i]:
                                            self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A25"))
                                            self.model.input_data["database"]["modularity"][i].append("A25")
                                        if "A30" in self.model.input_data["database"]["modularity"][i]:
                                            self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A30"))
                                            self.model.input_data["database"]["modularity"][i].append("A30")
                                    #El resto de cajas ordenan sus torques de manera ascendente
                                    else:
                                        self.model.input_data["database"]["modularity"][i].sort()
                        else:
                            command = {
                                    "lbl_result" : {"text": "Módulos de torque redundantes", "color": "red"},
                                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                  }
                            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            self.nok.emit()
                            return
                    else:
                        command = {
                                "lbl_result" : {"text": "Modulos de torque no encontrados", "color": "red"},
                                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return

                ################# VISION #################
                for i in modules_v:
                    #petición a la base de datos local para ver que fusibles lleva cada modulo
                    endpoint = "http://{}/api/get/{}/modulos_fusibles/MODULO/=/{}/_/=/_".format(self.model.server, self.dbEvent, i)
                    response = requests.get(endpoint).json()
                    #si encuentra el módulo en la respuesta (que si existe en la base de datos local)...
                    if "MODULO" in response:
                        #si la respuesta para ese módulo no es de tipo lista ( esto quiere decir que no hay más de un módulo de este tipo)
                        if type(response["MODULO"]) != list:
                            current_module = {}
                            for i in response:
                                #si i tiene "CAJA_" y además no está vacío el objeto
                                if "CAJA_" in i and len(response[i]):
                                    if "PDC-R" in i:
                                        #si la caja determinante es PDC-R en los módulos pueden existir PDC-RS, PDC-RMID y PDC-R
                                        if varianteDominante == "PDC-R":
                                            if "PDC-RS" in i:
                                                i = i.replace("PDC-RS",varianteDominante)
                                            if "PDC-RMID" in i:
                                                i = i.replace("PDC-RMID",varianteDominante)
                                        #si la caja determinante es PDC-RMID en los módulos pueden existir PDC-RS y PDC-RMID
                                        if varianteDominante == "PDC-RMID":
                                            if "PDC-RS" in i:
                                                i = i.replace("PDC-RS",varianteDominante)
                                        #si la caja determinante es PDC-RS en los módulos solo pueden existir PDC-RS, entonces no se hace nada

                                    #a current_module le añades esa información
                                    current_module.update(json.loads(response[i]))

                            #recorremos las cajas en current_module
                            for box in current_module:
                                #Solamente se tomarán en cuenta los fusibles pertenecientes a la caja PDC-R para posteriormente en base a ellos determinar cuales CANDADOS revisará el PALPADOR
                                if "PDC-R" in box:                                 
                                    #recorremos las cavidades de los datos del modulo que tienen esa misma caja
                                    for cavity in current_module[box]:
                                        #nunca debería de llega una información de la base de datos de los modulos con un vacío, pero si llegara, no entrará al if
                                        if current_module[box][cavity] != "vacio":
                                            #si la cavidad no se encuentra en esa caja... y no es una cavidad vacía...
                                            if not(cavity in self.model.input_data["database"]["fuses"]):
                                                self.model.input_data["database"]["fuses"].append(cavity)
                        else:
                            command = {
                                    "lbl_result" : {"text": "Módulos de visión redundantes", "color": "red"},
                                    "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                    }
                            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                            self.nok.emit()
                            return
                    else:
                        command = {
                                "lbl_result" : {"text": "Modulos de visión no encontrados", "color": "red"},
                                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                                }
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                        self.nok.emit()
                        return

                ###############################
                for i in self.model.input_data["database"]["modularity"]:
                    print("cajas dentro de modularity: ",i)
                    current_boxx = i
                    current_boxx = current_boxx.replace("-","")

                    if "PDC-R" in i:
                        if self.model.smallflag == True:    
                            self.model.cajas_habilitadas["PDC-RMID"] = 2
                        if self.model.mediumflag == True:
                            self.model.cajas_habilitadas["PDC-RMID"] = 2
                        if self.model.largeflag == True:
                            self.model.cajas_habilitadas["PDC-R"] = 2
                        current_boxx = "PDCR"
                    else:
                        self.model.cajas_habilitadas[i] = 2

                    serie = ""
                    if i == "MFB-P2":
                        serie = self.model.mfbp2_serie

                        
                        #print("ANTES")
                        #print(self.model.input_data["database"]["modularity"][i])
                        if i == "MFB-P2":
                            serie = self.model.mfbp2_serie

                        #print("ANTES")
                        #print(self.model.input_data["database"]["modularity"][i])
                        for terminal in self.model.input_data["database"]["modularity"][i]:
                            
                            if 'A29' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A29"))
                                self.model.input_data["database"]["modularity"][i].append("A29")                           
                            if 'A22' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A22"))
                                self.model.input_data["database"]["modularity"][i].append("A22")
                            if 'A27' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A27"))
                                self.model.input_data["database"]["modularity"][i].append("A27")
                            if 'A23' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A23"))
                                self.model.input_data["database"]["modularity"][i].append("A23")
                            if 'A26' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A26"))
                                self.model.input_data["database"]["modularity"][i].append("A26")
                            if 'A21' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A21"))
                                self.model.input_data["database"]["modularity"][i].append("A21")
                            if 'A24' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A24"))
                                self.model.input_data["database"]["modularity"][i].append("A24")
                            if 'A28' in self.model.input_data["database"]["modularity"][i]:
                                self.model.input_data["database"]["modularity"][i]
                                self.model.input_data["database"]["modularity"][i].pop(self.model.input_data["database"]["modularity"][i].index("A28"))
                                self.model.input_data["database"]["modularity"][i].append("A28")
                      
                    #print(self.model.input_data["database"]["modularity"][i])     
                    #print('I love YOU')   

                    if "PDC-R" in i:
                        serie = self.model.pdcr_serie

                    #copia de la caja actual, para utilizar en publish
                    pub_i = i

                    #cajas que no requieren escanearse (se inician en blue)
                    if i == "BATTERY" or i == "BATTERY-2":
                        command = {f"lbl_box{current_boxx}" : {"text": f"{pub_i}", "color": "blue"}}

                    #cajas que requieren escanearse (se inician en purple) #ESTO ES PARA SABER QUE LA LLEVA EL ARNÉS, PERO AÚN NO ESTÁN HABILITADAS POR EL PLC (por eso se requieren estos publish a los gui)
                    else:

                        #si no se activan estas banderas es porque es R LARGE
                        if "PDC-R" in i:
                            if self.model.smallflag == True:
                                pub_i = "PDC-RSMALL"
                            if self.model.mediumflag == True:
                                pub_i = "PDC-RMID"
                            if self.model.largeflag == True:
                                pub_i = "PDC-R"

                        command = {f"lbl_box{current_boxx}" : {"text": f"{pub_i}\n{serie}", "color": "purple"}}

                    #SE HACE EL PUBLISH PARA LA GUI CORRESPONDIENTE A ESA CAJA
                    if i in self.model.boxPos1:
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    if i in self.model.boxPos2:
                        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)


                print("cajas habilitadas CICLO: ",self.model.cajas_habilitadas)

                ###############################
                print("\t\tCOLECCIÓN TORQUE:\n", self.model.input_data["database"]["modularity"])
                #print("\t\tCOLECCIÓN FUSIBLES PDC-R:\n", self.model.input_data["database"]["fuses"]) #Descomentar para ver en consola las cavidades que llevan fusibles para la PDC-R
                #Se recorre la variable del modelo que indica qué cavidades pertenecen a c/candado; "s" = nombre del candado (Ejemplo: S1,S2...S10)
                for s in self.model.configCandados:
                    #Después se recorren las cavidades (cav) de cada candado del modelo (self.model.configCandados[s])
                    for cav in self.model.configCandados[s]:
                        #Si alguna cavidad se encuentra dentro de la colección de cavidades de la PDC-R que se está torqueando, se procede a agregar el candado correspondiente a la colección de candados...
                        if cav in self.model.input_data["database"]["fuses"]:
                            #Si el candado aún no existe en la colección de candados, se agrega (esta condición es para evitar que existan candados repetidos)
                            if not(s in self.model.input_data["database"]["candados"]):
                                self.model.input_data["database"]["candados"].append(s)
                print("\t\tCOLECCIÓN CANDADOS PDC-R:\n", self.model.input_data["database"]["candados"])
                self.model.input_data["database"]["pedido"] = self.pedido
                self.model.datetime = datetime.now()

                if self.model.local_data["qr_rework"]:
                    self.model.local_data["qr_rework"] = False

                if flag_296 == True or flag_294 == True:
                    print("dbEvent: ",self.dbEvent)
                    event = self.dbEvent.upper()
                    evento = event.replace('_',' ')
                    #Se agrega el nombre del evento a una variable en el modelo, el cual servirá para definir el oracle de las tuercas en caso de pertenecer a PRO1
                    self.model.evento = evento
                    command = {
                        "lbl_result" : {"text": "Datamatrix OK", "color": "green"},
                        "lbl_steps" : {"text": "Comenzando etapa de torque", "color": "black"},
                        "statusBar" : self.pedido["PEDIDO"] +" "+self.model.qr_codes["HM"]+" "+evento,
                        "cycle_started": True
                    }
                else:
                    command = {
                        "lbl_result" : {"text": "Datamatrix OK", "color": "green"},
                        "lbl_steps" : {"text": "Comenzando etapa de torque", "color": "black"},
                        "statusBar" : self.pedido["PEDIDO"],
                        "cycle_started": True
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                command = {
                    "position" : {"text": "POSICIÓN 1", "color": "black"},
                    "lbl_boxTITLE" : {"text": "||Cajas a utilizar||", "color": "black"},
                    "lbl_result" : {"text": "Datamatrix OK", "color": "green"},
                    "lbl_steps" : {"text": "Comenzando etapa de torque", "color": "black"},
                    "statusBar" : self.pedido["PEDIDO"] +" "+self.model.qr_codes["HM"]+" "+evento,
                    "cycle_started": True
                }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                command = {
                    "position" : {"text": "POSICIÓN 2", "color": "black"},
                    "lbl_boxTITLE" : {"text": "||Cajas a utilizar||", "color": "black"}
                }
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                Timer(0.1, self.torqueClamp).start()
                Timer(0.05, self.model.log, args = ("RUNNING",)).start() 
                self.ok.emit()
            
        except Exception as ex:
            print("Datamatrix request exception: ", ex) 
            if flag_variantes == False:
                print("La Modularidad no contiene módulos que especifiquen su variante en la PDC-R")
                temp = "La Modularidad no contiene módulos que especifiquen su variante en la PDC-R"
            else:
                temp = f"Database Exception: {ex.args}"
            command = {
                "lbl_result" : {"text": temp, "color": "red"},
                "lbl_steps" : {"text": "Inténtalo de nuevo", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            self.model.input_data["database"]["modularity"].clear()
            self.model.torque_data["tool1"]["queue"].clear()
            self.model.torque_data["tool2"]["queue"].clear()
            self.model.torque_data["tool3"]["queue"].clear()
            self.nok.emit()

    def torqueClamp (self):
        command = {}
        master_qr_boxes = json.loads(self.model.input_data["database"]["pedido"]["QR_BOXES"])
        print(f"\t\tQR_BOXES:\n{master_qr_boxes}\n")
        for i in self.model.torque_cycles:
            command[i] = False
            if i in self.model.input_data["database"]["modularity"]:
                if i in master_qr_boxes:
                    if not(master_qr_boxes[i][1]):
                        command[i] = True
                else:
                    command[i] = True
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)


class QrRework (QState):
    ok = pyqtSignal()
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

        self.model.transitions.key.connect(self.rework)
        self.model.transitions.code.connect(self.noRework)

    def onEntry(self, QEvent):
        command = {
            "lbl_result" : {"text": "Datamatrix procesado anteriormente", "color": "red"},
            "lbl_steps" : {"text": "Escanea otro código o gira la llave para continuar", "color": "black"},
            "show":{"scanner": True}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        command.pop("show")
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = True
        print("model qr_keyboard = True")

    def onExit(self, QEvent):
        command = {
            "show":{"scanner": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        self.model.qr_keyboard = False
        print("model qr_keyboard = False")

    def rework (self):
        self.model.local_data["qr_rework"] = True
        Timer(0.05, self.ok.emit).start()

    def noRework(self):
        Timer(0.05, self.ok.emit).start()

class Finish (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):

        #para avisar que se finalizó el modo de revisión de candados
        self.model.estado_candados = False

        command = {
            "DISABLE_PDC-R":False,
            "DISABLE_PDC-RMID":False,
            "DISABLE_MFB-S":False,
            "DISABLE_MFB-P1":False,
            "DISABLE_MFB-P2":False,
            "DISABLE_PDC-P":False,
            "DISABLE_PDC-D":False,
            "DISABLE_MFB-E":False,
            "DISABLE_BATTERY":False,
            "DISABLE_BATTERY-2":False
            }
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        # Fragmento de código para guardar solamente los RE-intentos
        print("||||||| Intentos en Modelo: ",self.model.tries)
        for i in self.model.tries:
            for j in self.model.tries[i]:
                self.model.tries[i][j] -= 1
                if self.model.tries[i][j] <= 0:
                    self.model.tries[i][j] = 0
        print("||||||| RE-intentos en Modelo FINAL: ",self.model.tries)

        #para funcionamiento normal de llave
        self.model.reintento_torque = False

        self.model.cajas_habilitadas = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.model.raffi = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        for i in self.model.raffi:
            raffi_clear = {f"raffi_{i}":False}
            publish.single(self.model.pub_topics["plc"],json.dumps(raffi_clear),hostname='127.0.0.1', qos = 2)
        self.model.mediumflag = False
        self.model.largeflag = False
        self.model.smallflag = False
        self.model.pdcr_serie = ""
        self.model.mfbp2_serie = ""

        lblbox_clean = {
            "lbl_boxTITLE" : {"text": "", "color": "black"},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(lblbox_clean),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(lblbox_clean),hostname='127.0.0.1', qos = 2)

        flag_1 = False
        historial = {
            "HM": self.model.qr_codes["HM"],
            "RESULTADO": "1",
            "VISION": {},
            "ALTURA":{},
            "INTENTOS_VA": {},
            "TORQUE": self.model.result,
            "ANGULO": self.model.resultAngle,
            "INTENTOS_T": self.model.tries,
            "SERIALES": self.model.qr_codes,
            "INICIO": self.model.datetime.isoformat(),
            "FIN": strftime("%Y/%m/%d %H:%M:%S"),
            "USUARIO": self.model.local_data["user"]["type"] + ": " + self.model.local_data["user"]["name"],
            "NOTAS": {"TORQUE": ["OK"]},
            "SCRAP": self.model.local_data["nuts_scrap"]
            }
        print("|||||||||||| HISTORIAL INICIO: ",historial["INICIO"])
        print("|||||||||||| HISTORIAL FIN: ",historial["FIN"])
        if self.model.config_data["untwist"]:
            historial["RESULTADO"] = "0"
            historial["NOTAS"]["TORQUE"].insert(0,"DESAPRIETE")
            self.model.config_data["untwist"] = False
        else:
            historial["NOTAS"]["TORQUE"].insert(0,"APRIETE")
            flag_1 = True
        if self.model.config_data["flexible_mode"]:
            historial["NOTAS"]["TORQUE"].insert(-1, "FLEXIBLE")
            self.model.config_data["flexible_mode"] = False
            #flag_1 = False
        endpoint = "http://{}/api/post/historial".format(self.model.server)
        resp = requests.post(endpoint, data=json.dumps(historial))
        resp = resp.json()

        #### Trazabilidad FAMX2 Update de Información
        if self.model.config_data["trazabilidad"] and self.model.config_data["untwist"]==False and self.model.config_data["flexible_mode"]==False and self.model.config_data["untangle_mode"]==False:
            if flag_1:
                try:
                    print("||Realizando el Update de SALIDA a Trazabilidad en FAMX2")
                    print("ID a la que se realizará el Update para Trazabilidad",self.model.id_HM)
                    salTrazabilidad = {
                        "SALTORQUE": historial["FIN"],
                        "UBICACION": "SALIDA_DE_TORQUE",
                        "NAMETORQUE": self.model.serial
                        }
                    endpointUpdate = "http://{}/seghm/update/seghm/{}".format(self.model.server,self.model.id_HM)
                    respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(salTrazabilidad))
                    respTrazabilidad = respTrazabilidad.json()
                    sleep(0.1)
                    respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(salTrazabilidad))
                    respTrazabilidad = respTrazabilidad.json()
                    sleep(0.1)
                    respTrazabilidad = requests.post(endpointUpdate, data=json.dumps(salTrazabilidad))
                    respTrazabilidad = respTrazabilidad.json()
                    print("respTrazabilidad del update: ",respTrazabilidad)

                    print("||Realizando el POST de valores en FAMX2")
                    historial["INICIO"] = self.model.datetime.strftime("%Y/%m/%d %H:%M:%S") #Se modifica el formato de la fecha de Inicio, para que coincida con el esperado por el servidor
                    endpointPost = "http://{}/seghm/post/seghm_valores".format(self.model.server)
                    respPost = requests.post(endpointPost, data=json.dumps(historial))
                    respPost = respPost.json()
                    print("respuesta del POST a FAMX2 Valores: ",respPost)

                    sleep(0.1)
                    if "exception" in respPost:
                        respPost = requests.post(endpointPost, data=json.dumps(historial))
                        respPost = respPost.json()
                        print("respuesta del POST a FAMX2 Valores: ",respPost)

                        sleep(0.1)
                        if "exception" in respPost:
                            respPost = requests.post(endpointPost, data=json.dumps(historial))
                            respPost = respPost.json()
                            print("respuesta del POST a FAMX2 Valores: ",respPost)

                except Exception as ex:
                    print("Excepción al momento de guardar datos en FAMX2", ex)
        #### Trazabilidad FAMX2 Update de Información

        if "items" in resp:
            if resp["items"] == 1:
                label = {
                    "DATE":  "FECHA"+ self.model.datetime.strftime("%Y/%m/%d %H:%M:%S"),
                    "REF":   "REF" + self.model.qr_codes["REF"],
                    "QR":    self.model.input_data["database"]["pedido"]["PEDIDO"],
                    "TITLE": "Estación de torques en arnes Interior" ,
                    "HM":    "HM" + self.model.qr_codes["HM"]
                }
                for i in self.model.result:
                    temp = []
                    for j in self.model.result[i]:
                        temp.append(str(self.model.result[i][j]))
                    label[i] = i + ": " + str(temp)

                #publish.single(self.model.pub_topics["printer"], json.dumps(label), hostname='127.0.0.1', qos = 2)
                
                if "HM000000011936" in self.model.qr_codes["HM"]:
                    self.model.config_data["trazabilidad"] = True
                        
                if "HM000000011925" in self.model.qr_codes["HM"]:
                    self.model.config_data["trazabilidad"] = True

                if "HM000000011920" in self.model.qr_codes["HM"]:
                    self.model.config_data["trazabilidad"] = True


                if self.model.config_data["trazabilidad"] == True:
                    command = {
                        "lbl_info3" : {"text": "Trazabilidad\nActivada", "color": "green"}
                    }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                self.finalMessage()
                Timer(4, self.ok.emit).start()
                #QTimer.singleShot(50, self.finalMessage)
                #QTimer.singleShot(4050,self.ok.emit)
                
            else:
                command = {
                    "lbl_result" : {"text": "Error al guardar los datos", "color": "red"},
                    "lbl_steps" : {"text": "Gire la llave de reset", "color": "black"}
                    }
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        else:
            command = {
                "lbl_result" : {"text": "Error de conexión con la base de datos", "color": "red"},
                "lbl_steps" : {"text": "Gire la llave de reset", "color": "black"}
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

    def finalMessage(self):
        self.model.id_HM = None
        command = {
            "lbl_result" : {"text": "C I C L O\tT E R M I N A D O", "color": "green"},
            "lbl_steps" : {"text": "RETIRA LAS CAJAS", "color": "blue"},
            "img_center" : "AMTC.png"
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        turnos = {
                "1":["07-00","18-59"],
                "2":["19-00","06-59"],
                }

        endpoint = "http://{}/contar/historial/FIN".format(self.model.server)
        response = requests.get(endpoint, data=json.dumps(turnos))
        response = response.json()
        #print("response: ",response)

        command = {
                "lcdNumber" : {"text": response["conteo"]}
                }
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

class Reset (QState):
    ok      = pyqtSignal()
    nok     = pyqtSignal()
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model = model

    def onEntry(self, event):

        if "HM000000011936" in self.model.qr_codes["HM"]:
            self.model.config_data["trazabilidad"] = True
                        
        if "HM000000011925" in self.model.qr_codes["HM"]:
            self.model.config_data["trazabilidad"] = True

        if "HM000000011920" in self.model.qr_codes["HM"]:
            self.model.config_data["trazabilidad"] = True


        if self.model.config_data["trazabilidad"] == True:
            command = {
                "lbl_info3" : {"text": "Trazabilidad\nActivada", "color": "green"}
            }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        #para avisar que se finalizó el modo de revisión de candados
        self.model.estado_candados = False

        command = {
            "show":{"login": False}
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        # Fragmento de código para guardar solamente los RE-intentos
        print("||||||| Intentos en Modelo: ",self.model.tries)
        for i in self.model.tries:
            for j in self.model.tries[i]:
                self.model.tries[i][j] -= 1
                if self.model.tries[i][j] <= 0:
                    self.model.tries[i][j] = 0
        print("||||||| RE-intentos en Modelo FINAL: ",self.model.tries)
        self.model.id_HM = None
        #para funcionamiento normal de llave
        self.model.reintento_torque = False

        self.model.cajas_habilitadas = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.model.raffi =             {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        for i in self.model.raffi:
            raffi_clear = {f"raffi_{i}":False, f"DISABLE_{i}":False, i:False}
            publish.single(self.model.pub_topics["plc"],json.dumps(raffi_clear),hostname='127.0.0.1', qos = 2)
        self.model.mediumflag = False
        self.model.largeflag = False
        self.model.smallflag = False
        self.model.pdcr_serie = ""
        self.model.mfbp2_serie = ""

        command = {
            "lbl_result" : {"text": "Se giró la llave de reset", "color": "green"},
            "lbl_steps" : {"text": "Reiniciando", "color": "black"},
            "lbl_boxPDCR" : {"text": "", "color": "black"},
            "lbl_boxPDCP" : {"text": "", "color": "black"},
            "lbl_boxPDCD" : {"text": "", "color": "black"},
            "lbl_boxMFBP1" : {"text": "", "color": "black"},
            "lbl_boxMFBP2" : {"text": "", "color": "black"},
            "lbl_boxMFBE" : {"text": "", "color": "black"},
            "lbl_boxMFBS" : {"text": "", "color": "black"},
            "lbl_boxBATTERY" : {"text": "", "color": "black"},
            "lbl_boxBATTERY2" : {"text": "", "color": "black"},
            "lbl_boxNEW" : {"text": "", "color": "black"},
            }
        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

        command = {}
        for i in self.model.torque_cycles:
             command[i] = False
        publish.single(self.model.pub_topics["plc"],json.dumps(command),hostname='127.0.0.1', qos = 2)
        if self.model.datetime != None:
            historial = {
                "HM": self.model.qr_codes["HM"],
                "RESULTADO": "0",
                "VISION": {},
                "ALTURA":{},
                "INTENTOS_VA": {},
                "TORQUE": self.model.result,
                "ANGULO": self.model.resultAngle,
                "INTENTOS_T": self.model.tries,
                "SERIALES": self.model.qr_codes,
                "INICIO": self.model.datetime.isoformat(),
                "FIN": strftime("%Y/%m/%d %H:%M:%S"),
                "USUARIO": self.model.local_data["user"]["type"] + ": " + self.model.local_data["user"]["name"],
                "NOTAS": {"TORQUE": ["RESET"]},
                "SCRAP": self.model.local_data["nuts_scrap"]
                }

            if self.model.config_data["untwist"]:
                historial["NOTAS"]["TORQUE"].insert(0, "DESAPRIETE")
                self.model.config_data["untwist"] = False
            elif self.model.config_data["flexible_mode"]:
                historial["NOTAS"]["TORQUE"].insert(0, "CAMBIO DE CAJA")
                self.model.config_data["flexible_mode"] = False
            elif self.model.config_data["untangle_mode"]:
                historial["NOTAS"]["TORQUE"].insert(0, "CABLES ENREDADOS")
                self.model.config_data["untangle_mode"] = False

            endpoint = "http://{}/api/post/historial".format(self.model.server)
            resp = requests.post(endpoint, data=json.dumps(historial))
            resp = resp.json()
            
            if "items" in resp:
                if resp["items"] == 1:
                    pass
                else:
                    command = {
                        "lbl_result" : {"text": "Error de conexión", "color": "red"},
                        "lbl_steps" : {"text": "Datos no guardados", "color": "black"}
                        }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                    publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                turnos = {
                    "1":["07-00","18-59"],
                    "2":["19-00","06-59"],
                }

                endpoint = "http://{}/contar/historial/FIN".format(self.model.server)
                response = requests.get(endpoint, data=json.dumps(turnos))
                response = response.json()
                #print("response: ",response)

                command = {
                        "lcdNumber" : {"text": response["conteo"]}
                        }
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)


        QTimer.singleShot(500,self.ok.emit)
