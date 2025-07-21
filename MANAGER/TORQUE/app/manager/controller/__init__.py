from PyQt5.QtCore import QObject, QStateMachine, QState, pyqtSlot
from manager.controller import basics, torque, vision
from manager.view.comm import MqttClient
from manager.model import Model
from paho.mqtt import publish
from threading import Timer
import json
from PyQt5.QtCore import QThread    # Librería para ejecuciones en paralelo
from time import sleep              # Para usar la función sleep(segundos)
from datetime import datetime, timedelta
import requests
import pandas as pd
import math
from copy import copy
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
        #self.objeto_mythread        = MyThread(model = self.model, parent = self.process)
        #self.objeto_mythread.start()
        self.reloj_mythread         = MyThreadReloj(self.model, self.process)
        self.reloj_mythread.start()
        
        self.powerup.addTransition(self.client.conn_ok, self.startup)
        self.startup.addTransition(self.startup.ok, self.show_login)
        self.show_login.addTransition(self.client.ID, self.check_login)
        self.show_login.addTransition(self.client.login, self.show_login)
        self.check_login.addTransition(self.check_login.nok, self.show_login)
        self.check_login.addTransition(self.check_login.ok, self.start_cycle)
        self.start_cycle.addTransition(self.start_cycle.ok, self.scan_qr)

        #se agrega un logout automático que se envía después de las 5pm y 7pm
        self.start_cycle.addTransition(self.start_cycle.autologout, self.startup)

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
            if "QRALTURASTOOL1" in qr_box:
                print("qrAlturasTool1 ok")
                self.model.qrAlturasTool1=True
                return
            if "QRALTURASTOOL2" in qr_box:
                print("qrAlturasTool2 ok")
                self.model.qrAlturasTool2=True
                return
            if "QRALTURASTOOL3" in qr_box:
                print("qrAlturasTool3 ok ")
                self.model.qrAlturasTool3=True
                return
            #Busca entre las cajas "P" D O R y te DEJA ESCANEAR, si no es alguna de estas verifica si esta en modo candado si esta en modo candado no te deja escanear ...
            permite_escanear=False
            master_qr_boxes = self.model.input_data["database"]["pedido"]["QR_BOXES"]
            for box in master_qr_boxes:
            #    #si se trata de la caja MFB-P2, inicia esta bandera en False, solo se activa si es una caja nueva de derecha
            #    bandera_mfbp2_derecha_nueva = False
            #    print("aqui esta la caja master_qr_boxes xox",box)
            #    if box == "MFB-P2":
            #        print("si entró masterqrboxes",master_qr_boxes["MFB-P2"][0])
            #        #si trae en los qr master el qr perteneciente a la caja de derecha
            #        if "12975407216" in  master_qr_boxes["MFB-P2"][0]:
            #            print("si esta en masterkrboxes")
            #            if "12975407830" in qr_box:
            #                print("aqui la bandera se hace true")
            #                bandera_mfbp2_derecha_nueva = True
            #                print("qrbox1",qr_box)
            #                qr_box = qr_box.replace("12975407830","12975407216")
            #                print("qrbox2",qr_box)
                            
                # i para buscar en todas las cajas master_qr_boxes[i][0](seriales maestros),  si ahí existe algo similar a lo que escaneaste "qr_box"(serial) y aparte este es "true" entonces...
                if master_qr_boxes[box] in qr_box and master_qr_boxes[box][1]:
                    # si la caja i (PDCR por ejemplo) NO está en plc clamps y existe en el contenido de database modularity (si ya se torqueó ya no estará aquí)
                    if not(box in self.model.input_data["plc"]["clamps"]) and box in self.model.input_data["database"]["modularity"]:
                        if box =="PDC-D" or box=="PDC-P":
                            permite_escanear=True
                        else:
                            permite_escanear=True
                            if self.model.estado_candados == True or self.model.pdcr_iniciada==True:
                                permite_escanear=False
                                print("CANDADOS INCIADOS, no se puede clampear otra caja hasta terminar")
                                command = {
                                    "lbl_steps" : {"text": "Terminar CANDADOS para poder clampear cajas", "color": "red"}
                                    }
                                self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                else:
                    print("else de candados iniciados")
                    command = {
                        "lbl_steps" : {"text": "El código escaneado no pertenece a ninguna caja del arnés", "color": "red"}
                        }
                    self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                    self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

            #si hay tareas en el pedido y no está en el estado de candados...
            if len(self.model.input_data["database"]["pedido"]) and permite_escanear==True:

                master_qr_boxes = self.model.input_data["database"]["pedido"]["QR_BOXES"]
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
                                        self.model.pdcr_iniciada=True
                                    if self.model.mediumflag == True:
                                        copy_i = "PDC-RMID"
                                        self.model.pdcr_iniciada=True
                                    elif self.model.largeflag == True:
                                        copy_i = "PDC-R"
                                        self.model.pdcr_iniciada=True
                                #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                self.model.cajas_habilitadas[copy_i] = 1
                                print("cajas habilitadas: ",self.model.cajas_habilitadas)
                            else:
                                print("QR NEGADO")
                                break;
                    if not(ok_rework):
                        print("fff ok_rework")
                        command = {
                            "lbl_steps" : {"text": "El código escaneado no pertenece a ninguna caja del arnés", "color": "red"}
                            }
                        self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                # Si la estación está en cualquier modo diferente a Puntual Flexible:
                else:
                    for i in master_qr_boxes:
                        #si se trata de la caja MFB-P2, inicia esta bandera en False, solo se activa si es una caja nueva de derecha
                        #bandera_mfbp2_derecha_nueva = False
                        print("aqui esta la caja master_qr_boxes i",i)
                        if i == "MFB-P2":
                            print("si entró ")
                            #si trae en los qr master el qr p   erteneciente a la caja de derecha
                            #if "12975407216" in  master_qr_boxes["MFB-P2"][0]:
                            #    if "12975407830" in qr_box:
                            #        bandera_mfbp2_derecha_nueva = True
                            #        qr_box = qr_box.replace("12975407830","12975407216")

                        # i para buscar en todas las cajas master_qr_boxes[i][0],  si ahí existe lo que escaneaste "qr_box" y aparte este es "true" entonces...
                        if master_qr_boxes[i] in qr_box:
                            # si la caja i (PDCR por ejemplo) está en plc clamps y en database modularity
                            if not(i in self.model.input_data["plc"]["clamps"]) and i in self.model.input_data["database"]["modularity"]:
                                ok = True
                                if self.model.config_data["cajas_repetidas"]==True and self.model.config_data["comparacion_cajasDP"]==True:
                                    print("cajas_repetidas:True,comparacion_cajasDP:True")
                                    print("caja i:",i)
                                    if i== "PDC-D":
                                        
                                        respuesta_FET=self.caja_match_FET_consulta(i,qr_box,self.model.qr_codes["HM"])
                                        
                                        if respuesta_FET !=None:

                                            self.model.qr_box_actual=qr_box
                                            
                                            if self.model.qr_coincide_FET==False and qr_box not in self.model.qr_validado:
                                                self.model.key_calidad_caja_sin_FET=True
                                                self.model.caja_por_validar=i

                                                self.enviar_mensaje_gui(i,condicion="calidad",gui="ambos",error="qr_coincide_FET")
                                                
                                            elif self.model.qr_coincide_FET==False and qr_box in self.model.qr_validado:
                                                print("caja validada por calidad", self.model.qr_validado)
                                                self.model.key_calidad_caja_sin_FET=False
                                                print("QR ACEPTADO: ",qr_box)
                                                
                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")
                                                if i == "PDC-RS":
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                                else:
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                    
                                                self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                                
                                                #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                                self.model.cajas_habilitadas[i] = 1
                                                print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                                self.model.qr_codes[i] = qr_box

                                                Timer(15, self.boxTimeout, args = (i, qr_box)).start()

                                            elif self.model.qr_coincide_FET==True:
                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")
                                                if i == "PDC-RS":
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                                else:
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                    print("zonas en else")

                                                self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")

                                                
                                                #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                                self.model.cajas_habilitadas[i] = 1
                                                print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                                self.model.qr_codes[i] = qr_box

                                                Timer(15, self.boxTimeout, args = (i, qr_box)).start()

                                    elif i== "PDC-P":
                                        
                                        respuesta_FET=self.caja_match_FET_consulta(i,qr_box,self.model.qr_codes["HM"])
                                        if respuesta_FET !=None:
                                            
                                            self.model.qr_box_actual=qr_box
                                            
                                            if self.model.qr_coincide_FET==False and qr_box not in self.model.qr_validado:
                                                self.model.key_calidad_caja_sin_FET=True
                                                self.model.caja_por_validar=i
                                                self.enviar_mensaje_gui(i,condicion="calidad",gui="ambos",error="qr_coincide_FET")
                                                
                                            elif self.model.qr_coincide_FET==False and qr_box in self.model.qr_validado:
                                                print("caja validada por calidad", self.model.qr_validado)
                                                self.model.key_calidad_caja_sin_FET=False
                                                print("QR ACEPTADO: ",qr_box)

                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")

                                                if self.model.config_data["conectoresPDCP"]==True:
                                                    self.inspeccion_conectores_PDCP(habilitado=True,qr_box=qr_box)
                                                else:
                                                    self.inspeccion_conectores_PDCP(habilitado=False,qr_box=qr_box)
                                            elif self.model.qr_coincide_FET==True:
                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")
                                                if self.model.config_data["conectoresPDCP"]==True:
                                                    self.inspeccion_conectores_PDCP(habilitado=True,qr_box=qr_box)
                                                else:
                                                    self.inspeccion_conectores_PDCP(habilitado=False,qr_box=qr_box)

                                    
                                    else:
                                        self.model.qr_box_actual=qr_box
                                        caja_repetida=self.check_duplicate_qr(qr_box,i)
                                        print("caja repetida, ",caja_repetida)
                                        print("caja",i)
                                        if caja_repetida and qr_box not in self.model.qr_validado and self.model.arnes_misma_caja==False:
                                                                                
                                            self.model.key_calidad_caja_repetida=True
                                            self.model.caja_por_validar=i

                                            
                                            self.enviar_mensaje_gui(i,condicion="calidad",gui="automatico",error="caja_repetida",respuesta_FET_HM="")
                                            
                                            print("si sale del mensaje")
                                        elif (caja_repetida and qr_box in self.model.qr_validado) or self.model.arnes_misma_caja==True:
                                            print("caja validada por calidad", self.model.qr_validado)
                                            ok = True
                                            self.model.key_calidad_caja_repetida=False
                                            print("QR ACEPTADO: ",qr_box)
                                            
                                            #serial de la caja
                                            print("------QR ACEPTADO: "+str(qr_box))
                                            print("------Colocar Caja "+ str(i) +" para clampear: ")
                                            if i == "PDC-RS":
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                            else:
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                print("zonas en else")

                                            self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")

                                            #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                            self.model.cajas_habilitadas[i] = 1
                                            print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                            self.model.qr_codes[i] = qr_box

                                            Timer(15, self.boxTimeout, args = (i, qr_box)).start()
                                        elif caja_repetida==False:
                                            
                                            #serial de la caja
                                            print("------QR ACEPTADO: "+str(qr_box))
                                            print("------Colocar Caja "+ str(i) +" para clampear: ")
                                            if i == "PDC-RS":
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                            else:
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                print("zonas en else")
                                            self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                            
                                            
                                            #caja adecuada:
                                            if "PDC-R" in i:
                                                if self.model.smallflag == True:
                                                    i = "PDC-RMID"
                                                    self.model.pdcr_iniciada=True
                                                if self.model.mediumflag == True:
                                                    i = "PDC-RMID"
                                                    self.model.pdcr_iniciada=True
                                                    print("medium flag activacion")
                                                elif self.model.largeflag == True:
                                                    i = "PDC-R"
                                                    self.model.pdcr_iniciada=True
                                            #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                            self.model.cajas_habilitadas[i] = 1
                                            print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                            #if bandera_mfbp2_derecha_nueva == True:
                                            #   bandera_mfbp2_derecha_nueva = False
                                            #   qr_box = qr_box.replace("12975407216","12975407830")
                                            #variable donde se guardan los seriales de cada caja (si se acaba el tiempo se reemplazará al escanear nuevamente para clampear)
                                            self.model.qr_codes[i] = qr_box

                                            Timer(15, self.boxTimeout, args = (i, qr_box)).start()

                                elif self.model.config_data["cajas_repetidas"]==True and self.model.config_data["comparacion_cajasDP"]==False:
                                    print("cajas_repetidas:True,comparacion_cajasDP:False")
                                    self.model.qr_box_actual=qr_box
                                    caja_repetida=self.check_duplicate_qr(qr_box,i)
                                    print("caja repetida, ",caja_repetida)
                                    print("caja",i)
                                    if caja_repetida and qr_box not in self.model.qr_validado and self.model.arnes_misma_caja==False:
                                    
                                        self.model.key_calidad_caja_repetida=True
                                        self.model.caja_por_validar=i

                                        self.enviar_mensaje_gui(i,condicion="calidad",gui="ambos",error="caja_repetida")
                                        

                                    elif (caja_repetida and qr_box in self.model.qr_validado) or self.model.arnes_misma_caja==True:
                                        if i== "PDC-P":
                                            self.model.qr_box_actual=qr_box
                                            self.model.key_calidad_caja_sin_FET=False
                                            print("QR ACEPTADO: ",qr_box)
                                            
                                            #serial de la caja
                                            print("------QR ACEPTADO: "+str(qr_box))
                                            print("------Colocar Caja "+ str(i) +" para clampear: ")
                                            
                                            if self.model.config_data["conectoresPDCP"]==True:
                                                    self.inspeccion_conectores_PDCP(habilitado=True,qr_box=qr_box)
                                            else:
                                                self.inspeccion_conectores_PDCP(habilitado=False,qr_box=qr_box)
                                        else:
                                            print("caja validada por calidad", self.model.qr_validado)
                                            ok = True
                                            self.model.key_calidad_caja_repetida=False
                                            print("QR ACEPTADO: ",qr_box)
                                            
                                            #serial de la caja
                                            print("------QR ACEPTADO: "+str(qr_box))
                                            print("------Colocar Caja "+ str(i) +" para clampear: ")
                                            if i == "PDC-RS":
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                            else:
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                print("zonas en else")

                                            self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                            
                                            #caja adecuada:
                                            if "PDC-R" in i:
                                                if self.model.smallflag == True:
                                                    i = "PDC-RMID"
                                                    self.model.pdcr_iniciada=True
                                                if self.model.mediumflag == True:
                                                    i = "PDC-RMID"
                                                    self.model.pdcr_iniciada=True
                                                    print("medium flag activacion")
                                                elif self.model.largeflag == True:
                                                    i = "PDC-R"
                                                    self.model.pdcr_iniciada=True
                                            #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                            self.model.cajas_habilitadas[i] = 1
                                            print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                            self.model.qr_codes[i] = qr_box

                                            Timer(15, self.boxTimeout, args = (i, qr_box)).start()
                                    elif caja_repetida==False:
                                        if i== "PDC-P":
                                            self.model.qr_box_actual=qr_box
                                            self.model.key_calidad_caja_sin_FET=False
                                            print("QR ACEPTADO: ",qr_box)
                                            
                                            #serial de la caja
                                            print("------QR ACEPTADO: "+str(qr_box))
                                            print("------Colocar Caja "+ str(i) +" para clampear: ")
                                            
                                            if self.model.config_data["conectoresPDCP"]==True:
                                                    self.inspeccion_conectores_PDCP(habilitado=True,qr_box=qr_box)
                                            else:
                                                self.inspeccion_conectores_PDCP(habilitado=False,qr_box=qr_box)
                                        else:
                                            #serial de la caja
                                            print("------QR ACEPTADO: "+str(qr_box))
                                            print("------Colocar Caja "+ str(i) +" para clampear: ")
                                            if i == "PDC-RS":
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                            else:
                                                self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                print("zonas en else")
                                            self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                            
                                            #caja adecuada:
                                            if "PDC-R" in i:
                                                if self.model.smallflag == True:
                                                    i = "PDC-RMID"
                                                    self.model.pdcr_iniciada=True
                                                if self.model.mediumflag == True:
                                                    i = "PDC-RMID"
                                                    self.model.pdcr_iniciada=True
                                                    print("medium flag activacion")
                                                elif self.model.largeflag == True:
                                                    i = "PDC-R"
                                                    self.model.pdcr_iniciada=True
                                            #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                            self.model.cajas_habilitadas[i] = 1
                                            print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                            self.model.qr_codes[i] = qr_box

                                            Timer(15, self.boxTimeout, args = (i, qr_box)).start()

                                elif self.model.config_data["cajas_repetidas"]==False and self.model.config_data["comparacion_cajasDP"]==True:
                                    print("cajas_repetidas:False,comparacion_cajasDP:True")
                                    if i== "PDC-D":
                                        
                                        respuesta_FET=self.caja_match_FET_consulta(i,qr_box,self.model.qr_codes["HM"])
                                        if respuesta_FET !=None:
                                            
                                            self.model.qr_box_actual=qr_box
                                            
                                            if self.model.qr_coincide_FET==False and qr_box not in self.model.qr_validado:
                                                self.model.key_calidad_caja_sin_FET=True
                                                self.model.caja_por_validar=i
                                                self.enviar_mensaje_gui(i,condicion="calidad",gui="ambos",error="qr_coincide_FET",respuesta_FET_HM=respuesta_FET["HM"])
                                                
                                            elif self.model.qr_coincide_FET==False and qr_box in self.model.qr_validado:
                                                print("caja validada por calidad", self.model.qr_validado)
                                                self.model.key_calidad_caja_sin_FET=False
                                                print("QR ACEPTADO: ",qr_box)
                                                
                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")
                                                if i == "PDC-RS":
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                                else:
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                    print("zonas en else")
                                                    
                                                self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                                
                                                #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                                self.model.cajas_habilitadas[i] = 1
                                                print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                                self.model.qr_codes[i] = qr_box

                                                Timer(15, self.boxTimeout, args = (i, qr_box)).start()

                                            elif self.model.qr_coincide_FET==True:
                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")
                                                if i == "PDC-RS":
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                                else:
                                                    self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                                    print("zonas en else")

                                                self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                                
                                                #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                                self.model.cajas_habilitadas[i] = 1
                                                print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                                self.model.qr_codes[i] = qr_box

                                                Timer(15, self.boxTimeout, args = (i, qr_box)).start()

                                    elif i== "PDC-P":
                                        
                                        respuesta_FET=self.caja_match_FET_consulta(i,qr_box,self.model.qr_codes["HM"])
                                        if respuesta_FET !=None:
                                            
                                            self.model.qr_box_actual=qr_box
                                            
                                            if self.model.qr_coincide_FET==False and qr_box not in self.model.qr_validado:
                                                self.model.key_calidad_caja_sin_FET=True
                                                self.model.caja_por_validar=i

                                                self.enviar_mensaje_gui(i,condicion="calidad",gui="ambos",error="qr_coincide_FET")
                                                
                                            elif self.model.qr_coincide_FET==False and qr_box in self.model.qr_validado:
                                                print("caja validada por calidad", self.model.qr_validado)
                                                self.model.key_calidad_caja_sin_FET=False
                                                print("QR ACEPTADO: ",qr_box)
                                                
                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")
                                                
                                                if self.model.config_data["conectoresPDCP"]==True:
                                                    self.inspeccion_conectores_PDCP(habilitado=True,qr_box=qr_box)
                                                else:
                                                    self.inspeccion_conectores_PDCP(habilitado=False,qr_box=qr_box)

                                            elif self.model.qr_coincide_FET==True:
                                                #serial de la caja
                                                print("------QR ACEPTADO: "+str(qr_box))
                                                print("------Colocar Caja "+ str(i) +" para clampear: ")
                                                if self.model.config_data["conectoresPDCP"]==True:
                                                    self.inspeccion_conectores_PDCP(habilitado=True,qr_box=qr_box)
                                                else:
                                                    self.inspeccion_conectores_PDCP(habilitado=False,qr_box=qr_box)
                                   
                                    else:
                                        #serial de la caja
                                        print("------QR ACEPTADO: "+str(qr_box))
                                        print("------Colocar Caja "+ str(i) +" para clampear: ")
                                        if i == "PDC-RS":
                                            self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                        else:
                                            self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                            print("zonas en else")

                                        self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                        
                                        #caja adecuada:
                                        if "PDC-R" in i:
                                            if self.model.smallflag == True:
                                                i = "PDC-RMID"
                                                self.model.pdcr_iniciada=True
                                            if self.model.mediumflag == True:
                                                i = "PDC-RMID"
                                                self.model.pdcr_iniciada=True
                                                print("medium flag activacion")
                                            elif self.model.largeflag == True:
                                                i = "PDC-R"
                                                self.model.pdcr_iniciada=True
                                        #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                        self.model.cajas_habilitadas[i] = 1
                                        print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                        self.model.qr_codes[i] = qr_box

                                        Timer(15, self.boxTimeout, args = (i, qr_box)).start()
                                
                                elif self.model.config_data["cajas_repetidas"]==False and self.model.config_data["comparacion_cajasDP"]==False:
                                    print("cajas_repetidas:False,comparacion_cajasDP:False")
                                    if i== "PDC-P":
                                        
                                        self.model.qr_box_actual=qr_box
                                        
                                       
                                        self.model.key_calidad_caja_sin_FET=False
                                        print("QR ACEPTADO: ",qr_box)
                                        
                                        #serial de la caja
                                        print("------QR ACEPTADO: "+str(qr_box))
                                        print("------Colocar Caja "+ str(i) +" para clampear: ")
                                        
                                        if self.model.config_data["conectoresPDCP"]==True:
                                            self.inspeccion_conectores_PDCP(habilitado=True,qr_box=qr_box)
                                        else:
                                            self.inspeccion_conectores_PDCP(habilitado=False,qr_box=qr_box)
                                    else:

                                        #serial de la caja
                                        print("------QR ACEPTADO: "+str(qr_box))
                                        print("------Colocar Caja "+ str(i) +" para clampear: ")
                                        if i == "PDC-RS":
                                            self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-RMID": True}), qos = 2)
                                        else:
                                            self.client.client.publish(self.model.pub_topics["plc"],json.dumps({i: True}), qos = 2)
                                            print("zonas en else")
                                        self.enviar_mensaje_gui(i,condicion="ok",gui="automatico",error="ninguno")
                                        
                                        #caja adecuada:
                                        if "PDC-R" in i:
                                            if self.model.smallflag == True:
                                                i = "PDC-RMID"
                                                self.model.pdcr_iniciada=True
                                            if self.model.mediumflag == True:
                                                i = "PDC-RMID"
                                                self.model.pdcr_iniciada=True
                                                print("medium flag activacion")
                                            elif self.model.largeflag == True:
                                                i = "PDC-R"
                                                self.model.pdcr_iniciada=True
                                        #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
                                        self.model.cajas_habilitadas[i] = 1
                                        print("cajas habilitadas: ",self.model.cajas_habilitadas)
                                        self.model.qr_codes[i] = qr_box

                                        Timer(15, self.boxTimeout, args = (i, qr_box)).start()
                            else:
                                print("else general")
                                command = {
                                "lbl_steps" : {"text": "El código escaneado no pertenece a ninguna caja del arnés", "color": "red"}
                                }
                                self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
                                self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
                            break
                        
                    if not(ok):
                        
                        
                        command = {
                            "lbl_steps" : {"text": "Vuelve a escanear la caja", "color": "red"},
                            "lbl_result" : {"text": "", "color": "red"},
                            "lbl_boxNEW" : {"text":"", "color": "green"},
                            }
                        self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
            
        except Exception as ex:
            print ("manager.controller.chkQrBoxes Exception: ", ex)
                

    def boxTimeout(self, i, qr_box):
        
        #la variable self.model.input_data["plc"]["clamps"] guarda lo que está clampeado
        #si cuando se activa esta función aún NO se ha clampeado la caja, se vuelve a deshabilitar el Nido
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
                    self.model.pdcr_iniciada=False
                    copy_i = "PDC-RMID"

                if self.model.mediumflag == True:
                    self.model.pdcr_iniciada=False
                    copy_i = "PDC-RMID"
                elif self.model.largeflag == True:
                    self.model.pdcr_iniciada=False
                    copy_i = "PDC-R"

            #se avisa a la variable de cajas_habilitadas que se requiere escanear la caja
            self.model.cajas_habilitadas[copy_i] = 2
            print("cajas habilitadas: ",self.model.cajas_habilitadas)

    def enviar_mensaje_gui(self,caja,condicion="ninguna",gui="automatico",error="ninguno",respuesta_FET_HM=""):
        """
        enviar_mensaje_gui(self,caja,condicion="ninguna",gui="automatico",error="ninguno",respuesta_FET_HM="")

        :condicion "ok":          Coloca la caja {i} en su lugar
                   "calidad":     Escanea Gafet de calidad para autorizar
                   "conectoresPDCP":  Coloca la caja {i} para validar CONECTORES
                   "reintentar": Vuelve a escanear la caja

        :gui:      "ambos"  :en ambas pantallas
                   "pantalla1"
                   "pantalla2"
                   "automatico": se evalua la posicion de la caja y de acuerdo a eso, selecciona una pantalla

        :error:    "ninguno"
                   "trazabilidad_caja_FET"
                   "qr_coincide_FET"
                   "caja_registrada_diferente_arnes"
                   "caja_repetida"
        respuesta_FET_HM:

        """ 
        #self.enviar_mensaje_gui(self,i,condicion="reintentar",gui="ambos",error="trazabilidad_caja_FET")
        
        condiciones={"ninguna": "",
                     "ok": f"Coloca la caja "+ caja +" en su lugar",
                     "calidad": "Escanea Gafet de calidad para autorizar",
                     "conectoresPDCP": f"Coloca la caja "+ caja +" para validar CONECTORES",
                     "reintentar":"Vuelve a escanear la caja",
                     
                     }
        error_dict={"ninguno": "",
               "trazabilidad_caja_FET": "Error de Trazabilidad al buscar la caja "+ caja +" en FET",
               "qr_coincide_FET":       f"caja "+ caja +" no coincide con registros de FET",
               "caja_registrada_diferente_arnes" : f"caja "+ caja +" pertenece a otro arnés",
               "caja_repetida": f"caja repetida, Vuelve a escanear la caja " + caja,
               }
        
        try:
            label_steps=condiciones[condicion]
            label_result=error_dict[error]
        except Exception as ex:
            label_result=""
            print("condicion o error no definidos: ", ex)


        if gui=="ambos":
            command = {
            "lbl_steps" : {"text": label_steps, "color": "black"},
            "lbl_result" : {"text": label_result, "color": "red"},
            "lbl_boxNEW" : {"text":"", "color": "green"},
            }

            self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)
            self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)


        elif gui=="pantalla1":
            command = {
            "lbl_steps" : {"text": label_steps, "color": "black"},
            "lbl_result" : {"text": label_result, "color": "red"},
            "lbl_boxNEW" : {"text":"", "color": "green"},
            }
            if condicion=="conectoresPDCP":
                command["img_center"]="PDCP_CANDADOS.JPG"
            if error=="caja_repetida":
                command["lbl_boxNEW"]={"text":"HM Asociado \n"+self.model.caja_repetida_hm_asociado, "color": "green"}
                
            self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)


        elif gui=="pantalla2":
            command = {
            "lbl_steps" : {"text": label_steps, "color": "black"},
            "lbl_result" : {"text": label_result, "color": "red"},
            "lbl_boxNEW" : {"text":"", "color": "green"},
            }
            if condicion=="conectoresPDCP":
                command["img_center"]="PDCP_CANDADOS.JPG"
            if error=="caja_registrada_diferente_arnes":
                command["lbl_boxNEW"]={"text":"HM Asociado \n"+respuesta_FET_HM, "color": "green"}
            self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
        elif gui=="automatico":
            
            if caja in self.model.boxPos1:
                print("pos1")
                command = {
                "lbl_steps" : {"text": label_steps, "color": "black"},
                "lbl_result" : {"text": label_result, "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                print("command",command)
                if condiciones[condicion]=="conectoresPDCP":
                    command["img_center"]="PDCP_CANDADOS.JPG"
                if error_dict[error]=="caja_registrada_diferente_arnes":
                    command["lbl_boxNEW"]={"text":"HM Asociado \n"+respuesta_FET_HM, "color": "green"}
                if error_dict[error]=="caja_repetida":
                    command["lbl_boxNEW"]={"text":"HM Asociado \n"+respuesta_FET_HM, "color": "green"}
                print("command2",command)
                self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                command = {
                "lbl_steps" : {"text": "", "color": "black"},
                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

            if caja in self.model.boxPos2:
                
                command = {
                "lbl_steps" : {"text": "", "color": "black"},
                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                command = {
                "lbl_steps" : {"text": label_steps, "color": "black"},
                "lbl_result" : {"text": label_result, "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                "img_center" : ""
                }
                
                if condicion=="conectoresPDCP":
                    command["img_center"]="PDCP_CANDADOS.JPG"
                if error=="caja_registrada_diferente_arnes":
                    command["lbl_boxNEW"]={"text":"HM Asociado \n"+respuesta_FET_HM, "color": "green"}
                if error=="caja_repetida":
                    command["lbl_boxNEW"]={"text":"HM Asociado \n"+respuesta_FET_HM, "color": "green"}
                
                self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)
        else:
            
            if caja in self.model.boxPos1:
                
                command = {
                "lbl_steps" : {"text": label_steps, "color": "black"},
                "lbl_result" : {"text": label_result, "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                if condicion=="conectoresPDCP":
                    command["img_center"]="PDCP_CANDADOS.JPG"
                if error=="caja_registrada_diferente_arnes":
                    command["lbl_boxNEW"]={"text":"HM Asociado \n"+respuesta_FET_HM, "color": "green"}
                self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                command = {
                "lbl_steps" : {"text": "", "color": "black"},
                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

            if caja in self.model.boxPos2:
                command = {
                "lbl_steps" : {"text": "", "color": "black"},
                "lbl_result" : {"text": "", "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                self.client.client.publish(self.model.pub_topics["gui"],json.dumps(command), qos = 2)

                command = {
                "lbl_steps" : {"text": label_steps, "color": "black"},
                "lbl_result" : {"text": label_result, "color": "red"},
                "lbl_boxNEW" : {"text":"", "color": "green"},
                }
                if condicion=="conectoresPDCP":
                    command["img_center"]="PDCP_CANDADOS.JPG"
                if error=="caja_registrada_diferente_arnes":
                    command["lbl_boxNEW"]={"text":"HM Asociado \n"+respuesta_FET_HM, "color": "green"}
                self.client.client.publish(self.model.pub_topics["gui_2"],json.dumps(command), qos = 2)

    def inspeccion_conectores_PDCP(self,habilitado=True,qr_box=""):
        if habilitado==True:
            self.model.validacion_conectores_pdcp=True

            self.enviar_mensaje_gui("PDC-P",condicion="conectoresPDCP",gui="automatico",error="ninguno")
            
            #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
            self.model.cajas_habilitadas["PDC-P"] = 1
            print("cajas habilitadas: ",self.model.cajas_habilitadas)
            self.model.qr_codes["PDC-P"] = qr_box

            #Timer(15, self.boxTimeout, args = (i, qr_box)).start()
        else:
            self.model.validacion_conectores_pdcp=False

            self.enviar_mensaje_gui("PDC-P",condicion="ok",gui="automatico",error="ninguno")
            
            #se avisa a la variable de cajas_habilitadas que ya se escaneó la caja
            self.model.cajas_habilitadas["PDC-P"] = 1
            print("cajas habilitadas: ",self.model.cajas_habilitadas)
            self.model.qr_codes["PDC-P"] = qr_box
            self.client.client.publish(self.model.pub_topics["plc"],json.dumps({"PDC-P": True}), qos = 2)
            Timer(15, self.boxTimeout, args = ("PDC-P", qr_box)).start()

    def check_duplicate_qr (self, qr,caja ):

        ####################### REVISAR SI QR ES REPETIDO ####################
        inicio_consulta = datetime.now()
        # Obtener la fecha actual
        fecha_actual = datetime.now()
        # Restar días requeridos para consultar en ese intervalo de tiempo
        fecha_atras = fecha_actual - timedelta(days=7)  # Suponiendo 31 días por mes (3 meses)
        # Formatear la fecha en el mismo formato
        fecha_inicio = fecha_atras.strftime("%Y-%m-%d")
        # Obtener la fecha del día de mañana para buscar también en las del día de hoy (aunque en la consulta se usa un =, no es necesario)
        fecha_tomorrow = fecha_actual + timedelta(days=1)
        # Se da el mismo formato a la fecha de fin
        fecha_fin = fecha_tomorrow.strftime("%Y-%m-%d")
        print("fecha_inicio: ",fecha_inicio)
        print("fecha_fin: ",fecha_fin)
        self.model.caja_duplicada=False

        try:
            endpoint = ("http://{}/api/get_col/historial/Fin/>=/{}/FIN/<=/{}/SERIALES/{}/{}".format(self.model.server,fecha_inicio,fecha_fin,qr,caja))
            response = requests.get(endpoint).json()
            print("response[SERIALES]",response["SERIALES"])
            if "HM" in response["SERIALES"][0]:
                self.model.total_hms_caja_repetida=response["SERIALES"]
                print("")
                caja_repetida = True
                self.model.caja_repetida_hm_asociado=response["SERIALES"][-1]
                print("self.model.caja_repetida_hm_asociado",self.model.caja_repetida_hm_asociado)
                self.model.caja_duplicada=True
            else:
                self.model.caja_duplicada=False
            self.model.arnes_misma_caja=False
            if self.model.qr_codes["HM"] in response["SERIALES"] and self.model.retrabajo==True:
                self.model.arnes_misma_caja=True
            
        except Exception as ex:
            print("Login request exception: ", ex)
          
        print("inicio de consulta: ")
        print(inicio_consulta.isoformat())
        print("fin de consulta: ")
        print(datetime.now().isoformat())

        return self.model.caja_duplicada

    def caja_match_FET_consulta(self,caja,qr,hm):
        famx2response=None
        caja_original=copy(caja)
        if caja=="PDC-D":
            caja="PDC_P"
        elif caja=="PDC-P":
            caja="PDC_D"
        try:
            print("||||||||||||Consulta de HM a FAMX2...")
            endpoint = "http://{}/seghm/get/SEGHM_BOX/HM/=/{}/_/_/_".format(self.model.server,hm)
            famx2response = requests.get(endpoint).json()
            #No existen coincidencias del HM en FAMX2
            if "items" in famx2response:
                print("No se encontró HM en tabla donde se guardan las cajas PDCP Y PDCD")
                famx2response=None
                print(caja)
                self.model.qr_error="Hm no encontrado"
                self.enviar_mensaje_gui(caja_original,condicion="reintentar",gui="ambos",error="trazabilidad_caja_FET")
            #Si existe el HM en FAMX2
            else:
                print("FAMX2 ",famx2response)

                if qr in famx2response[caja]:
                    print("si coincide")
                    self.model.qr_coincide_FET=True
                    return famx2response

                else:
                    self.model.qr_error="Qr no coincide"
                    print("no coincide")
                    self.model.qr_coincide_FET=False
                    self.model.qr_FET=famx2response[caja]

                    return famx2response
                
        except Exception as ex:
            print ("caja_match_FET_consulta exception ", ex)
            famx2response=None
        return famx2response


class MyThreadReloj(QThread):

    #check_material = pyqtSignal()

    def __init__(self, model = None, parent = None):
        super().__init__(parent)
        self.model  = model

        print("MyThreadReloj")
        print("se crea un objeto de la clase MyThread con padre QThread")
        print("con entrada del objeto model de la clase model que está en model.py")
        print("y el objeto client de la clase MqttClient que está en comm.py")
        
    def run(self):

        fechaActual = self.model.get_currentTime() #se obtiene la fecha desde el servidor por primera vez
        print("update pedido desde MyThreadReloj inicial")

        
        toma_tiempo=True
        while 1:

            #tiempo de espera para no alentar las ejecuciones de otros procesos
            sleep(1)
            if self.model.cronometro_ciclo==True:
                if toma_tiempo:
                    hora_inicial = datetime.now()
                    toma_tiempo=False
                #print("self.model.timer_cyc: " + str(self.model.timer_cyc) + " seg.")
                hora_actual = datetime.now()
                # Calcula la diferencia de tiempo en segundos como un valor de punto flotante
                #diferencia_tiempo = (hora_actual - hora_anterior).total_seconds()
                diferencia_tiempo = (hora_actual - hora_inicial).total_seconds()
                
                minutoss = int(diferencia_tiempo//60)
                segundoss = int(diferencia_tiempo - (minutoss*60))
                segundoss_int = copy(segundoss)
                if minutoss < 10:
                    minutoss = "0" + str(minutoss)
                else:
                    minutoss = str(minutoss)
                if segundoss < 10:
                    segundoss = "0" + str(segundoss)
                else:
                    segundoss = str(segundoss)
                string_timer_cyc = minutoss + ":" + segundoss

                command = {
                    "lcdcronometro" : {"value": string_timer_cyc},
                          }
                publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
                publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            else:
                
                toma_tiempo=True
            fechaLocalActual = datetime.now() #se actualiza la fecha local Actual
            fechaActual = self.model.update_fecha_actual(fechaLocalActual,fechaActual)

            #td = timedelta(1)
            #beforefechaActual = fechaActual - td
            #afterfechaActual = fechaActual + td
            #hoy = fechaActual.strftime('%Y-%m-%d')
            #mañana = afterfechaActual.strftime('%Y-%m-%d')
            #hora_actual = fechaActual.time()

            command = {
                    "lbl_clock":{"fecha":str(fechaActual)},
                    }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2) 
            publish.single(self.model.pub_topics["gui_2"],json.dumps(command),hostname='127.0.0.1', qos = 2)
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

            #tiempo de espera para no alentar las ejecuciones de otros procesos
            sleep(10)  

            command = {
                "lineEdit" : True
                }
            publish.single(self.model.pub_topics["gui"],json.dumps(command),hostname='127.0.0.1', qos = 2)
            print("Focus de lineEdit enviado")