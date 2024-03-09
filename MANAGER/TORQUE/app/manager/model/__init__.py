from cv2 import imread, imwrite, rectangle
from time import strftime
from pickle import load
import requests
import json
from datetime import datetime, timedelta, date, time
class Model (object):

    def __init__(self, parent = None):

        self.shutdown = False
        self.mainWindow = None
        self.transitions = None
        self.imgs_path = "data/imgs/"
        self.datetime = None
        self.imgs = {}
        self.config_data = {
            "encoder_feedback": {
                "tool1": True,
                "tool2": True,
                "tool3": True
            },
            "retry_btn_mode": {
                "tool1": False,
                "tool2": False,
                "tool3": False  
            },
            "constraints": {
                "tools": [["tool1", "tool3"]]
            },
            "cajas_repetidas":True,
            "comparacion_cajasDP":True,
            "untwist": False,
            "flexible_mode": False,
            "hora_servidor":True,
            "gdi": False,
            "trazabilidad": True
        }
        self.server = "127.0.0.1:5000"
        self.serial = "ET-MBI-2"
        #Ruta de archivos estandarizada
        self.ruta_principal="C:/BIN/"
        self.parametros={}
        self.fechaAnterior = self.get_currentTime() #se inicializa con la fecha del servidor
        self.fechaLocalAnterior = datetime.now() #se inicializa con la fecha local actual
        self.cronometro_ciclo=False

        self.id_HM = None
        self.tareas_actuales = {}
        self.llave = False
        ###############################
        #3: cajas terminadas en ciclo, 2:cajas que requieren QR, 1:cajas que no requieren QR, 0:cajas que no solicita el ciclo
        self.cajas_habilitadas = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.raffi = {"PDC-P": 0,"PDC-D": 0,"MFB-P1": 0,"MFB-P2": 0,"PDC-R": 0,"PDC-RMID": 0,"BATTERY": 0,"BATTERY-2": 0,"MFB-S": 0,"MFB-E": 0}
        self.reintento_torque = False
        self.largeflag = False
        self.mediumflag = False
        self.smallflag = False
        self.pdcr_serie = ""
        self.mfbp2_serie = ""
        self.boxPos1 = ["PDC-R","PDC-RMID","PDC-RS","MFB-P1","MFB-S","MFB-E","BATTERY","BATTERY-2"]
        self.boxPos2 = ["MFB-P2","PDC-D","PDC-P"]
        self.name_FET=""
        self.qr_FET=""
        ###############################
        #variable para iniciar el estado de revisión de candados con el palpador
        self.estado_candados = False
        #Estados para Revisión de Candados en ejecución Paralela
        self.CheckZonePalpador = False
        #variable para guardar la caja correspondiente que se liberará de las tareas al terminar los candados
        self.save_box_candados = ""
        #variable para guardar el torque correspondiente que se liberará de las tareas al terminar los candados
        self.save_current_trq_candados = ""
        #variable para mostrar al inicio lo que ya está guardado
        self.palpador_iniciado = False
        self.en_ciclo=False

        self.contador_focus=0
        self.qr_box_actual=""
        self.caja_repetida_hm_asociado=""
        self.qr_validado=[]
        self.key_calidad_caja_repetida=False
        self.caja_por_validar=""
        self.total_hms_caja_repetida=[]
        self.retrabajo=False

        self.key_calidad_caja_sin_FET=False
        self.cajas_repetidas_habilitado=False
        self.comparacion_PD_habilitado=False
        self.arnes_misma_caja=False
        self.qr_coincide_FET=False
        self.qr_error=""
        self.validacion_conectores_pdcp=False
        #señal para dejar un delay entre cada candado
        self.nuevo_pin = False

        #variable para contar el tiempo que se debe mantener la herramienta en posición de zona de activación
        self.tiempo = {
                         "tool1":"",
                         "tool2":"",
                         "tool3":""
                      }
        #variable para habilitar herramienta pasado cierto tiempo
        self.activar_tool = {
                                "tool1":False,
                                "tool2":False,
                                "tool3":False
                            }

        #variable para verificar la altura de la zona en cada caja para cada herramienta
        self.altura_zone = {
                        "tool1":False,
                        "tool2":False,
                        "tool3":False
            }

        #variable para detectar en qué estado se encontraba la tool antes de que llegara un clampeo o terminara una caja y Entrara a ToolsManger
        #con esto se puede regresar a ERRORNOK, BACKWARD, QINTERVENTION o CHECKPROFILE
        self.estado_actual = {
            "tool1":"",
            "tool2":"",
            "tool3":""
            }

        #Variable para indicar que la caja pdcr se escaneó y esta en proceso de torque
        self.pdcr_iniciada=False

        #variable para detectar caja PDCR, e ir al estado de revisión de candados
        self.contains_PDCR = False

        #variable para dar llave al ciclo
        self.llave = False

        #para hacer pop de la lista de candados solamente cuando se recibió la señal estando en la zona del candado (waiting_pin)
        self.pin_pressed = False

        self.qr_keyboard = False
        self.qr_scan_cont = 0

        #variable para permitir volver a activar o desactivar un raffi después de cierto tiempo definido en comm.py, para que no se active muy rápido
        self.timer_raffi = False
        #variable para controlar la activación de los raffi, dependiendo del valor actual, por ejemplo de keyboard_F4 = True / keyboard_F4 = False
        self.bool_state = True
        #variable para guardar la caja del raffi activado (convertirla desde la señal pyqt a string dentro de  torque.py)
        self.current_box_raffi = ""
        #variable para guardar la caja del raffi activado (se guarda en el modelo desde comm.py al presionar un raffi)
        self.current_raffi_key = ""
        #variable para indicar la tecla "F" que se presionó correspondiente al actual raffi activado
        self.keyboard_raffi_pressed = ""

        #Variable para bloquear la activación de los raffis según la caja
        self.active_lock = {"PDC-P": False,"PDC-D": False,"MFB-P1": False,"MFB-P2": False,"PDC-R": False,"PDC-RMID": False,"BATTERY": False,"BATTERY-2": False,"MFB-S": False,"MFB-E": False}
        #variable para bloequear la activación de los raffi según la herramienta activa
        self.active_lock_tool = {"tool1": False,"tool2": False,"tool3": False}
        #variable para habilitar la llave normal o la del proceso
        self.backward_key_tool = {"tool1": False,"tool2": False,"tool3": False, "raffi": False}
        #variable para evitar recibir una señal falsa de la reversa después de salir de este estado
        self.lock_backward = {"tool1": False,"tool2": False,"tool3": False}
        #variable para monitorear el perfil actual de cada herramienta
        self.torque_bin = {
            "tool1": {
                "bin1": 0,
                "bin2": 0,
                "bin3": 0,
                "send_profile": 0,
                "current_profile":0},
            "tool2": {
                "bin1": 0,
                "bin2": 0,
                "bin3": 0,
                "send_profile": 0,
                "current_profile":0},
            "tool3": {
                "bin1": 0,
                "bin2": 0,
                "bin3": 0,
                "send_profile": 0,
                "current_profile":0}
            }
        ###############################

        #variable para guardar las tareas actuales de cada herramienta
        self.current_queue = {
            "tool1": [],
            "tool2": [],
            "tool3": []
            }

        #variable para guardar las tareas de la herramienta m8 para poder acceder a estas a la vez
        self.mfbp2_queue = []

        #Variable para guardar el candado actual a trabajar
        self.current_task_candado = None
        ###############################

        self.BB = {   
            'MFB-P1': {'A41': [(533, 349), (575, 393)], 'A42': [(597, 389), (631, 421)], 'A43': [(479, 352), (513, 389)], 'A44': [(431, 354), (466, 386)], 'A45': [(391, 356), (420, 384)], 'A46': [(334, 349), (373, 384)], 'A47': [(266, 352), (310, 388)]},
            'MFB-P2': {'A20': [(527, 272), (576, 313)], 'A21': [(258, 463), (292, 497)], 'A22': [(312, 464), (343, 493)], 'A23': [(362, 464), (393, 493)], 'A24': [(409, 465), (442, 493)], 'A25': [(470, 466), (512, 509)], 'A26': [(538, 463), (572, 497)], 'A27': [(587, 464), (622, 498)], 'A28': [(638, 466), (674, 499)], 'A29': [(687, 464), (725, 496)], 'A30': [(403, 267), (449, 308)]},
            'MFB-S': {'A51': [(447, 265), (493, 311)], 'A52': [(315, 402), (357, 442)], 'A53': [(379, 410), (415, 444)], 'A54': [(430, 411), (464, 447)], 'A55': [(478, 410), (513, 443)], 'A56': [(528, 409), (564, 441)]}, 
            'MFB-E': {'E1': [(1700, 650), (2250, 1250)], 'A1': [(2600, 1700), (3150, 2300)], 'A2': [(750, 1700), (1300, 2300)]}, 
            'PDC-D': {'E1': [(358, 467), (396, 507)]}, 
            'PDC-P': {'E1': [(361, 460), (396, 495)]}, 
            'PDC-R': {'E1': [(408, 330), (443, 358)],"s1":[(178, 415), (269, 377)],"s2":[(269, 377), (349, 413)],"s3":[(142, 322), (177, 413)],"s4":[(361, 411), (404, 324)],"s5":[(141, 238), (182, 322)],"s6":[(193, 274), (264, 318)],"s7":[(268, 275), (337, 318)],"s8":[(358, 324), (405, 233)],"s9":[(180, 221), (264, 264)],"s10":[(262, 222), (347, 263)]}, 
            'PDC-RMID': {'E1': [(408, 330), (443, 358)]}, 
            'PDC-RS': {'E1': [(408, 330), (443, 358)]}, 
            'BATTERY': {'BT': [(85, 285), (155, 355)]}, 
            'BATTERY-2': {'BT': [(335, 210), (420, 275)]}  
            }
        #with open("data/BB/BB", "rb") as f:
        #    self.BB= load(f)
             
        self.result = {
            "PDC-P": {
                "E1": None},
            "PDC-D": {
                "E1": None},
            "BATTERY": {
                "BT": None},
            "BATTERY-2": {
                "BT": None},
            "MFB-P1": {
                "A47": None,
                "A46": None,
                "A45": None,
                "A44": None,
                "A43": None,
                "A41": None, 
                "A42": None},
            "MFB-S": {
                "A51": None,
                "A52": None,
                "A53": None,
                "A54": None,
                "A55": None,
                "A56": None},
            "MFB-E": {
                "E1": None,
                "A1": None,
                "A2": None},
            "MFB-P2": {
                "A20": None,
                "A21": None,
                "A22": None,
                "A23": None,
                "A24": None,
                "A25": None,
                "A26": None, 
                "A27": None, 
                "A28": None, 
                "A29": None, 
                "A30": None},
            "PDC-R": {
                "E1": None},
            "PDC-RS": {
                "E1": None},
            "PDC-RMID": {
                "E1": None}
            }

        self.resultAngle = {
            "PDC-P": {
                "E1": None},
            "PDC-D": {
                "E1": None},
            "BATTERY": {
                "BT": None},
            "BATTERY-2": {
                "BT": None},
            "MFB-P1": {
                "A47": None,
                "A46": None,
                "A45": None,
                "A44": None,
                "A43": None,
                "A41": None, 
                "A42": None},
            "MFB-S": {
                "A51": None,
                "A52": None,
                "A53": None,
                "A54": None,
                "A55": None,
                "A56": None},
            "MFB-E": {
                "E1": None,
                "A1": None,
                "A2": None},
            "MFB-P2": {
                "A20": None,
                "A21": None,
                "A22": None,
                "A23": None,
                "A24": None,
                "A25": None,
                "A26": None, 
                "A27": None, 
                "A28": None, 
                "A29": None, 
                "A30": None},
            "PDC-R": {
                "E1": None},
            "PDC-RS": {
                "E1": None},
            "PDC-RMID": {
                "E1": None}
            }

        self.tries = {
            "PDC-P": {
                "E1": 0},
            "PDC-D": {
                "E1": 0},
            "BATTERY": {
                "BT": 0},
            "BATTERY-2": {
                "BT": 0},
            "MFB-P1": {
                "A47": 0,
                "A46": 0,
                "A45": 0,
                "A44": 0,
                "A43": 0,
                "A41": 0, 
                "A42": 0},
            "MFB-S": {
                "A51": 0,
                "A52": 0,
                "A53": 0,
                "A54": 0,
                "A55": 0,
                "A56": 0},
            "MFB-E": {
                "E1": 0,
                "A1": 0,
                "A2": 0},
            "MFB-P2": {
                "A20": 0,
                "A21": 0,
                "A22": 0,
                "A23": 0,
                "A24": 0,
                "A25": 0,
                "A26": 0, 
                "A27": 0, 
                "A28": 0, 
                "A29": 0, 
                "A30": 0},
            "PDC-R": {
                "E1": 0},
            "PDC-RS": {
                "E1": 0},
            "PDC-RMID": {
                "E1": 0}
            }

        self.configCandados = {
            "s1": ["F400","F401","F402","F403","F404","F405"],
            "s2": ["F406","F407","F408","F409","F410","F411"],
            "s3": ["F413","F414","F415","F416","F417"],
            "s4": ["F418","F419","F420"],
            "s5": ["F421","F422","F423","F424","F425","F426"],
            "s6": ["F430","F431","F437","F438","F439","F440","F441"],
            "s7": ["F432","F433","F436","F442","F443","F444","F445","F446"],
            "s8": ["F447","F448","F449"],
            "s9": ["F450","F451","F452","F453","F454","F455"],
            "s10": ["F456","F457","F458","F459","F460","F461"],
            "s11": ["F462","F463","F464"]
            }

        self.qr_codes = {
            "FET": "--",
            "HM": "--",
            "REF": "--"
            }

        self.evento = ""
        self.numero=""
        self.conduccion=""
        self.torque_cycles = {
            "PDC-P": {
                "E1": ["tool1",2,"6mm Nut"]},
            "PDC-D": {
                "E1": ["tool1",2,"6mm Nut"]},
            "BATTERY": {
                "BT": ["tool2",9,"Battery Nut"]},
            "BATTERY-2": {
                "BT": ["tool2",10,"Battery Nut"]},
            "MFB-P1": {
                "A47": ["tool3",10,"8mm Nut"],
                "A46": ["tool3",5,"8mm Nut"],
                "A45": ["tool2",3,"6mm Nut"],
                "A44": ["tool2",4,"6mm Nut"],
                "A43": ["tool2",6,"6mm Nut"],
                "A41": ["tool3",4,"8mm Nut"], 
                "A42": ["tool2",5,"6mm Nut"]},
            "MFB-S": {
                "A51": ["tool3",9,"8mm Nut"],
                "A52": ["tool3",2,"8mm Nut"],
                "A53": ["tool2",2,"6mm Nut"],
                "A54": ["tool2",8,"6mm Nut"],
                #"A55": ["tool2",12,"6mm Nut"],
                "A55": ["tool2",7,"6mm Nut"],
                "A56": ["tool2",7,"6mm Nut"]},
            "MFB-E": {
                "E1": ["tool3",13,"8mm Nut"],
                "A1": ["tool3",14,"8mm Nut"],
                "A2": ["tool3",15,"8mm Nut"]},
            "MFB-P2": {
                "A20": ["tool3",7,"8mm Nut"],
                "A25": ["tool3",3,"8mm Nut"], 
                "A30": ["tool3",8,"8mm Nut"],
                "A21": ["tool1",8,"6mm Nut"],
                "A26": ["tool1",6,"6mm Nut"], 

                "A22": ["tool1",5,"6mm Nut"],
                "A27": ["tool1",10,"6mm Nut"], 

                "A23": ["tool1",4,"6mm Nut"],
                "A28": ["tool1",11,"6mm Nut"],

                "A24": ["tool1",7,"6mm Nut"],
                "A29": ["tool1",9,"6mm Nut"]
                }, 
            "PDC-R": {
                "E1": ["tool3",11,"8mm Nut"]},
            "PDC-RS": {
                "E1": ["tool3",6,"8mm Nut"]},
            "PDC-RMID": {
                "E1": ["tool3",6,"8mm Nut"]}
            }

        self.sub_topics = {
                        "keyboard": "Keyboard/status",
                        "plc": "PLC/1/status",
                        #"torque_1": "torque/1/status",
                        #"torque_2": "torque/2/status",
                        #"torque_3": "torque/3/status",
                        "torque_1": "TorqueModbus/2/status",
                        "torque_2": "TorqueModbus/3/status",
                        "torque_3": "TorqueModbus/4/status",
                        "gui": "gui/status",
                        "gui_2": "gui_2/status",
                        "config": "config/status"
                        }

        self.pub_topics = {
                        "gui": "gui/set",
                        "gui_2": "gui_2/set",
                        "plc": "PLC/1",
                        "torque": {
                                   #"tool1": "torque/1/set",
                                   #"tool2": "torque/2/set",
                                   #"tool3": "torque/3/set"
                                   "tool1": "TorqueModbus/2",
                                   "tool2": "TorqueModbus/3",
                                   "tool3": "TorqueModbus/4"
                                   },
                        "printer": "printer/set",
                        "config": "config/set"
                        }

        

        self.local_data = {
                            "user": {"type":"", "pass":"", "name":""},
                            "lbl_info1_text": "",
                            "lbl_info1.2_text": "",
                            "lbl_info2_text": "",
                            "lbl_info3_text": "",
                            "qr_rework" : False,
                            "nuts_scrap":{}
                            }
        #zonas de candados

        self.candados_zonas= {
            "s1":False,
            "s2":False,
            "s3":False,
            "s4":False,
            "s5":False,
            "s6":False,
            "s7":False,
            "s8":False,
            "s9":False,
            "s10":False,
            }


        self.input_data = {
            "database":{
                "modularity": {},
                "fuses": [],
                "candados": [],
                "pedido": {},
                "qr_retrabajo": {}
                },
            "plc": {
                "emergency": True,
                "encoder_1": {"zone": "0"},# el valor de "zone" debe ser de la forma: '{"caja": "torque_name"}'
                "encoder_2": {"zone": "0"},
                "encoder_3": {"zone": "0","candado":"0"},
                "encoder_4": {"candado": "0"}, # Encoder correspondiente a altura
                "retry_btn": False,
                "clamps": ["PDC-P", "PDC-D", "BATTERY", "MFB-P1", "MFB-S", "MFB-P2", "PDC-R"]}, # Debe inicializarce vacío
            "torque":{
                "tool1": {},
                "tool2": {},
                "tool3": {}},
            "gui": {
                "request": "", 
                "ID": "", 
                "code": "", 
                "visible":{}}
            }

        self.torque_data = {
            "tool1" : {
                "stop_profile": 0,
                "backward_profile": 1, 
                "current_trq": None,   #["PDC-P", "E1", 3, "tuerca_x"]
                "queue": [], #[["PDC-P", "E1", 3, "tuerca_x"]]
                "rqst": False,
                "gui": self.pub_topics["gui_2"],
                "past_trq": None,
                "img": None,
                "error": False,
                "enable" : False,
                },
            "tool2" : {
                "stop_profile": 0,
                "backward_profile": 1, 
                "current_trq": None,
                "queue": [], #[["PDC-P", "E1", 3, "tuerca_x"]]
                "rqst": False,
                "gui": self.pub_topics["gui"],
                "past_trq": None,
                "img": None,
                "error": False,
                "enable" : False
                },
            "tool3" : {
                "stop_profile": 0,
                "backward_profile": 1, 
                "current_trq": None,
                "queue": [], #[["PDC-P", "E1", 3, "tuerca_x"]]
                "rqst": False,
                "gui": self.pub_topics["gui"],
                "past_trq": None,
                "img": None,
                "error": False,
                "enable" : False
                }
            }

    def reset (self):
        self.current_task_candado = None 
        self.datetime = None
        for i in self.result:
            for j in self.result[i]:
                self.result[i][j] = None
        for i in self.tries:
            for j in self.tries[i]:
                self.tries[i][j] = 0
        for i in self.resultAngle:
            for j in self.resultAngle[i]:
                self.resultAngle[i][j] = None

        for i in list(self.BB):
            temp = self.imgs_path +"boxes/" + i + ".jpg"
            self.imgs[i] = imread(temp)
        
        self.qr_codes.clear()
        self.qr_codes["FET"]    = "--"
        self.qr_codes["HM"]     = "--"
        self.qr_codes["REF"]    = "--"

        self.local_data["lbl_info1_text"]   = ""
        self.local_data["lbl_info1.2_text"] = ""
        self.local_data["lbl_info2_text"]   = ""
        self.local_data["lbl_info3_text"]   = ""
        self.local_data["qr_rework"]        = False
        self.local_data["nuts_scrap"].clear()

        self.input_data["database"]["modularity"].clear()
        self.input_data["database"]["pedido"].clear()
        self.input_data["database"]["fuses"].clear()
        self.input_data["database"]["candados"].clear()
        self.input_data["database"]["qr_retrabajo"].clear()
        self.input_data["plc"]["emergency"]         = True
        self.input_data["plc"]["encoder_1"]["zone"] = "0"
        self.input_data["plc"]["encoder_2"]["zone"] = "0"
        self.input_data["plc"]["encoder_3"]["zone"] = "0"
        self.input_data["plc"]["retry_btn"]         = False
        self.input_data["gui"]["request"]           = ""
        self.input_data["gui"]["ID"]                = ""
        self.input_data["gui"]["code"]              = ""
        self.input_data["plc"]["clamps"].clear()
        self.input_data["gui"]["visible"].clear()
        for i in self.input_data["torque"]: self.input_data["torque"][i].clear()
        
        for i in self.torque_data:
            self.torque_data[i]["current_trq"]  = None
            self.torque_data[i]["rqst"]         = False
            self.torque_data[i]["past_trq"]     = None
            self.torque_data[i]["img"]          = None
            self.torque_data[i]["error"]        = False
            self.torque_data[i]["enable"]       = False
            self.torque_data[i]["queue"].clear()

    def drawBB (self, img = None, BB = ["PDC-P", "E1"], color = (255,255,255)):
        #red     = (255, 0, 0)
        #orange  = (31, 186, 226)
        #green   = (0, 255, 0)
        #White   = (255, 255, 255)
        try:
            #print("BB-----------------------------",BB)
            #print("self.BB-----------------------------",self.BB)
            if type(BB[0]) == list:
                for i in BB:
                    pts = self.BB[i[0]][i[1]]
                    if "PDC-R" in pts[0]:
                        tickness = 1
                    else:
                        tickness = 3
                    rectangle(img, pts[0], pts[1], color, tickness)
            else:
                pts = self.BB[BB[0]][BB[1]]
                if "PDC-R" in pts[0]:
                    tickness = 1
                else:
                    tickness = 3
                rectangle(img, pts[0], pts[1], color, tickness)
        except Exception as ex:
            print("Model.drawBB exception: ", ex)
        return img

    def log(self, state):
        try:
            data = {
                "PEDIDO":self.qr_codes["HM"],
                "ESTADO": state,
                "DATETIME": self.get_currentTime().strftime("%Y/%m/%d %H:%M:%S"),
                }
            endpoint = "http://{}/api/post/log".format(self.server)
            resp = requests.post(endpoint, data=json.dumps(data))
        except Exception as ex:
            print("Log request Exception: ", ex)

    def get_currentTime(self):
        if self.config_data["hora_servidor"]==True:
            fecha_actuaal = None
            try:
                endpoint = "http://{}/server_famx/hora_servidor".format(self.server) #self.model.server
                respuesta_hora = requests.get(endpoint).json()
                if "exception" in respuesta_hora:
                    fecha_actuaal = datetime.now() #se toma la hora local de la PC
                    print("////////// fecha_local")
                else:
                    fecha_actuaal = datetime.strptime(respuesta_hora["HORA_ACTUAL"], "%Y-%m-%d %H:%M:%S") #se toma la hora del servidor en el formato deseado
                    print("////////// fecha_servidor")
            except Exception as ex:
                print("exception hora_servidor: ",ex)
                fecha_actuaal = datetime.now()
                print("////////// fecha_local")
            print("//////// Actualizando Fecha: ",fecha_actuaal)
            return fecha_actuaal
        else:
            fecha_actuaal = None
            print("////////// fecha_local")
            fecha_actuaal = datetime.now()
            return fecha_actuaal

    def update_fecha_actual(self,fechaLocalActual,fechaActual):

        #print("fechaActual: ",fechaActual)
        segundos_transcurridos = fechaLocalActual - self.fechaLocalAnterior #se obtiene la diferencia del tiempo transcurrido en cada iteración de la ejecución paralela

        self.fechaLocalAnterior = fechaLocalActual
        #print("segundos_transcurridos por iteración: ",segundos_transcurridos)
        
        diferencia = fechaActual - self.fechaAnterior #se obtiene el tiempo total que ha transcurrido desde la última actualización de la hora desde el servidor (donde se han ido acumulando los segundos transcurridos de cada iteración y la fecha original obtenida del servidor)
        # Compara si han pasado más de 3 minutos (180 segundos)
        #print("diferenciaLocalAcumulada: ",diferencia)

        if diferencia > timedelta(minutes=3) or diferencia < timedelta(minutes=0):
            #print("Han pasado más de 3 minutos. Actualizando hora desde servidor...")
            fechaActual = self.get_currentTime() #se actualiza del servidor la fecha
            print("update pedido desde update_fecha_actual")
            self.fechaAnterior = fechaActual #se guarda la última fecha obtenida de la actualización del servidor
        else:
            fechaActual = fechaActual + segundos_transcurridos
            #print("tiempo transcurrido: ",diferencia)

        return fechaActual
