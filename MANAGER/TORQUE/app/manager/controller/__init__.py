from PyQt5.QtCore import QObject, QStateMachine, QState, pyqtSlot
from manager.controller import basics, torque, vision
from manager.view.comm import MqttClient
from manager.model import Model
from paho.mqtt import publish
from threading import Timer
import json
import requests
from datetime import datetime, timedelta, date, time
from PyQt5.QtCore import QThread    # Librería para ejecuciones en paralelo
from time import sleep              # Para usar la función sleep(segundos)

        

class Controller (QObject):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.model = Model(parent = self)
        self.client = MqttClient(self.model, parent = self)
        self.model.transitions = self.client
        self.model.mainWindow = parent
        self.stateMachine = QStateMachine(self)

        self.powerup        = QState()
        self.startup        = basics.Startup(self.model)
        self.show_login     = basics.Login(self.model)
        self.check_login    = basics.CheckLogin(self.model)
        self.process        = QState()
        self.start_cycle    = basics.StartCycle(self.model, self.process)
        self.config         = basics.Config(self.model)
        self.scan_qr        = basics.ScanQr(self.model, self.process)
        self.reset          = basics.Reset(self.model)
        self.check_qr       = basics.CheckQr(self.model, self.process)
        self.qr_rework      = basics.QrRework(self.model)
        self.torquing       = torque.Torquing(self.model)
        self.finish         = basics.Finish(model = self.model, parent = self.process)
        ##################  ###################################################



        self.objeto_mythread        = MyThread(model = self.model, parent = self.process)
        self.objeto_mythread.start()
        
        
        self.powerup.addTransition(self.client.conn_ok, self.startup)
        self.startup.addTransition(self.startup.ok, self.show_login)
        self.show_login.addTransition(self.client.ID, self.check_login)
        self.show_login.addTransition(self.client.login, self.show_login)
        self.check_login.addTransition(self.check_login.nok, self.show_login)
        self.check_login.addTransition(self.check_login.ok, self.start_cycle)
        self.start_cycle.addTransition(self.start_cycle.ok, self.scan_qr)
        self.scan_qr.addTransition(self.client.nok_code, self.scan_qr)
        self.scan_qr.addTransition(self.client.code, self.check_qr)
        self.scan_qr.addTransition(self.client.config, self.config)
        self.scan_qr.addTransition(self.client.logout, self.startup)
        self.config.addTransition(self.client.config_ok, self.start_cycle)

        self.check_qr.addTransition(self.check_qr.nok, self.scan_qr)
        self.check_qr.addTransition(self.check_qr.rework, self.qr_rework)
        self.qr_rework.addTransition(self.qr_rework.ok, self.check_qr)
        self.qr_rework.addTransition(self.client.nok_code, self.qr_rework)
        self.check_qr.addTransition(self.check_qr.ok, self.torquing)

        self.torquing.addTransition(self.torquing.finish, self.finish)
        self.finish.addTransition(self.finish.ok, self.start_cycle)

        self.process.addTransition(self.client.key, self.reset)
        self.torquing.addTransition(self.torquing.reset, self.reset)
        self.reset.addTransition(self.reset.ok, self.start_cycle)
                                                                   
        self.stateMachine.addState(self.powerup)
        self.stateMachine.addState(self.startup)
        self.stateMachine.addState(self.show_login)
        self.stateMachine.addState(self.check_login)
        self.stateMachine.addState(self.process)
        self.stateMachine.addState(self.config)
        self.stateMachine.addState(self.reset)
        self.stateMachine.addState(self.torquing)
        self.stateMachine.addState(self.qr_rework)

        self.process.setInitialState(self.start_cycle)
        self.stateMachine.setInitialState(self.powerup)
        self.stateMachine.start()

        #se llama al método clean de la clase Torquing, que posteriormente llama a método clean de la clase NewTool
        self.check_qr.ok.connect(self.torquing.clean)

        #se conecta la señal qr_box = pyqtSignal(str) que contiene un string, al método chkQrBoxes
        self.client.qr_box.connect(self.chkQrBoxes)

    @pyqtSlot(str)
    def chkQrBoxes(self, qr_box):
        try:
            if len(self.model.input_data["database"]["pedido"]):
                master_qr_boxes = json.loads(self.model.input_data["database"]["pedido"]["QR_BOXES"])
                rework_qr_boxes = self.model.input_data["database"]["qr_retrabajo"]
                ok = False
                ok_rework = False
                # Si la estación está en Modo Puntual Flexible o retrabajo:
                if self.model.config_data["flexible_mode"] or self.model.config_data["untwist"]:
                    print("Qr_retrabajo desde modelo: ",self.model.input_data["database"]["qr_retrabajo"])
                    for i in rework_qr_boxes:
                        print("i",i)
                        print("i codigo qr",rework_qr_boxes[i])
                        if qr_box == rework_qr_boxes[i]:
                            if not(i in self.model.input_data["plc"]["clamps"]) and i in self.model.input_data["database"]["modularity"]:
                                ok_rework = True
                                print("QR ACEPTADO: ")
                                print(qr_box)
                                print("Colocar Caja para retrabajo: ",i)
                                if i == "PDC-RS":
                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                else:
                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                command = {
                                    "lbl_steps" : {"text": f"Coloca la caja {i} en su lugar", "color": "black"}
                                    }
                                if i in self.model.boxPos1:
                                    self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                if i in self.model.boxPos2:
                                    self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                                Timer(10, self.boxTimeout, args = (i, qr_box)).start()

                                copy_i = i
                                #caja adecuada:
                                if "PDC-R" in i:
                                    if self.model.smallflag == True:
                                        copy_i = "PDC-RMID"
                                    if self.model.mediumflag == True:
                                        copy_i = "PDC-RMID"
                                    elif self.model.largeflag == True:
                                        copy_i = "PDC-R"
                                #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                self.model.cajas_habilitadas[copy_i] = 1
                                print("cajas habilitadas: ",self.model.cajas_habilitadas)
                            break
                    if not(ok_rework):
                        command = {
                            "lbl_steps" : {"text": "El código escaneado no pertenece a ninguna caja del arnés", "color": "red"}
                            }
                        self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                # Si la estación está en cualquier modo diferente a Puntual Flexible:
                else:
                    for i in master_qr_boxes:
                        # i para buscar en todas las cajas master_qr_boxes[i][0],  si ahí existe lo que escaneaste "qr_box" y aparte este es "true" entonces...
                        if master_qr_boxes[i][0] in qr_box and master_qr_boxes[i][1]:
                            # si la caja i (PDCR por ejemplo) está en plc clamps y en database modularity
                            if not(i in self.model.input_data["plc"]["clamps"]) and i in self.model.input_data["database"]["modularity"]:
                                ok = True
                                print("QR ACEPTADO: ")
                                print(qr_box)
                                print("Colocar Caja para clampear: ",i)
                                if i == "PDC-RS":
                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                else:
                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                command = {
                                    "lbl_steps" : {"text": f"Coloca la caja {i} en su lugar", "color": "black"}
                                    }
                                if i in self.model.boxPos1:
                                    self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                if i in self.model.boxPos2:
                                    self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                                Timer(10, self.boxTimeout, args = (i, qr_box)).start()

                                copy_i = i
                                #caja adecuada:
                                if "PDC-R" in i:
                                    if self.model.smallflag == True:
                                        copy_i = "PDC-RMID"
                                    if self.model.mediumflag == True:
                                        copy_i = "PDC-RMID"
                                    elif self.model.largeflag == True:
                                        copy_i = "PDC-R"
                                #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                self.model.cajas_habilitadas[copy_i] = 1
                                print("cajas habilitadas: ",self.model.cajas_habilitadas)
                            break
                    if not(ok):
                        command = {
                            "lbl_steps" : {"text": "CAJA INCORRECTA, VUELVA A INTENTARLO", "color": "red"}
                            }
                        self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                for item in self.model.torque_data:
                    if not(len(self.model.torque_data[item]["queue"])):
                       #self.client.client.publish(self.model.torque_data[item]["gui"],json.dumps(command), qos = 2)
                       pass
        except Exception as ex:
            print ("manager.controller.chkQrBoxes Exception: ", ex)

    def boxTimeout(self, i, qr_box):
        if not(i in self.model.input_data["plc"]["clamps"]):
            print("Caja DESCLAMPEADA: ",i)
            if i == "PDC-RS":
                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": False}), qos = 2)
            else:
                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: False}), qos = 2)
            command = {
                "lbl_steps" : {"text": f"Vuelve a escanear la caja {i}", "color": "black"},
                }
            if i in self.model.boxPos1:
                self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
            if i in self.model.boxPos2:
                self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

            copy_i = i
            #caja adecuada:
            if "PDC-R" in i:
                if self.model.smallflag == True:
                    copy_i = "PDC-RMID"
                if self.model.mediumflag == True:
                    copy_i = "PDC-RMID"
                elif self.model.largeflag == True:
                    copy_i = "PDC-R"

            #se avisa a la variable de cajas_habilitadas que se requiere escanear la caja
            self.model.cajas_habilitadas[copy_i] = 2
            print("cajas habilitadas: ",self.model.cajas_habilitadas)

            for item in self.model.torque_data:
                if not(len(self.model.torque_data[item]["queue"])):
                    #self.client.client.publish(self.model.torque_data[item]["gui"],json.dumps(command), qos = 2)
                    pass
        else:
            self.model.qr_codes[i] = qr_box
          

#EJECUCIÓN EN PARALELO
class MyThread(QThread):
    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model  = model
        
        print("se crea un objeto de la clase MyThread con padre QThread")
        print("con entrada del objeto model de la clase model que está en model.py")
        print("y el objeto client de la clase MqttClient que está en comm.py")
        
    def run(self):

        while 1:
             sleep(5)
             command = {
                "lineEdit" : True, 
                "lcdNumber": {"visible": True}
                }

             publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
             print("Focus de lineEdit enviado")
             try:
                print("Corriendo en Paralelo")
                #endpoint = "http://{}/api/get/tableros/ID/>/0/_/_/_".format(self.model.server)
                #print("Endpoint: ",endpoint)
                #response = requests.get(endpoint).json()
                #print("Response: \n",response)

                #data = []
                #if "items" in response:
                #    #print("no hay tableros en la base de datos local")
                #    pass
                #else:
                #    if isinstance(response["TABLERO"],str):
                #        temp = []
                #        #temp.append(response["ID"])
                #        temp.append(response["HM"])
                #        temp.append("      "+response["TABLERO"])
                #        response["DATETIME"] = self.translate_day(response["DATETIME"])
                #        temp.append(response["DATETIME"])
                #        data.append(temp)
                #    if isinstance(response["TABLERO"],list):
                #        filas = len(response["ID"])
                #        #print("Cantidad de filas: ",filas)
                #        for fila in range(filas):
                #            temp = []
                #            #temp.append(response["ID"][fila])
                #            temp.append(response["HM"][fila])
                #            temp.append("      "+response["TABLERO"][fila])
                #            response["DATETIME"][fila] = self.translate_day(response["DATETIME"][fila])
                #            temp.append(response["DATETIME"][fila])
                #            #print(temp)
                #            data.append(temp)
                #print("DATA FINAL: ", data)
                #command = {
                #    "tbl_info" : {"clear":True}
                #}
                #publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                #command = {
                #    "tbl_info" : {"data":data}
                #}
                #publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                ############################################ CONTADOR DE PIEZAS #####################################
             #fecha actual
                fechaActual = datetime.today()
                #delta time de un día
                td = timedelta(1)
                #afterfechaActual es la fecha actual mas un día (mañana)
                afterfechaActual = fechaActual + td
                #beforefechaActual es la fecha actual menos un día (ayer)
                beforefechaActual = fechaActual - td

                #se obtiene la hora actual (int)
                horaActual = datetime.today().hour
                print("hora Actual: ",horaActual)

                #si la hora actual es menor de las 7am
                if horaActual < 7:
                    dia_inicial = beforefechaActual.strftime('%Y-%m-%d')
                    dia_final = fechaActual.strftime('%Y-%m-%d')
                else:
                    dia_inicial = fechaActual.strftime('%Y-%m-%d')
                    dia_final = afterfechaActual.strftime('%Y-%m-%d')    
                    
                        
                dia_inicial = str(dia_inicial) + "-07"
                dia_final = str(dia_final) + "-07"

                print("Fecha actual: ",dia_inicial)
                print("Fecha mañana: ",dia_final)

                ########################################## Consulta Local ##################################
                endpoint = "http://{}/api/get/et_mbi_2/historial/fin/>/{}/</{}_/_".format(self.model.server,dia_inicial,dia_final)
                contresponse = requests.get(endpoint).json()
                #print(contresponse)
                #No existen coincidencias
                if "items" in contresponse: ## LOCAL
                    print("No se han liberado arneses el día de hoy")
                    command = {
                            "lcdNumber" : {"value": 0}
                            }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                #si la respuesta es un entero, quiere decir que solo hay un arnés
                elif isinstance(contresponse["ID"],int):
                    command = {
                            "lcdNumber" : {"value": 1}
                            }
                    publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)

                #Si existe más de un registro (contresponse["ID"] es una lista)
                else:
                    #se eliminan los que se repiten en la búsqueda, para solo contar los arneses diferentes que hayan pasado
                    result = []
                    for item in contresponse["HM"]:
                        #ejemplo: "AMTC - HM000000000003" ó "HM000000000003 - AMTC", se convierten en "HM00000000003"
                        indice = item.index("HM")
                        item = item[indice:indice+14]
                        
                        #si el arnés no está en la lista anteriormente, no suma
                        if item not in result:
                            result.append(item)

                    #si el contador revasa los 999, se seguirá mostrando este número, ya que si no se reinicia a 0
                    if len(result) > 999:
                        command = {
                                "lcdNumber" : {"value": 999}
                                }
                    else:
                        command = {
                                "lcdNumber" : {"value": len(result)} ## cantidad de arneses sin repetirse que han liberado el día de hoy
                                }
                        
                        publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                ############################################################################################################
              
             except Exception as ex:
                print("Excepción al consultar los tableros en DB LOCAL Paralelo: ", ex)

                "
            
            