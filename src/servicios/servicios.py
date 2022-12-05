from ast import Not
import os
import re
import traceback
import json
import epaycosdk.epayco as epayco
from flask import request, jsonify, send_file
from datetime import datetime
from flask_restful import Resource
#from src.modelos.modelos import User, db, Task
from werkzeug.utils import secure_filename
from src.utilities.utilities import allowed_file
from flask import current_app as app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
#from src.publisher import publish_task_queue
from sqlalchemy.sql import text

apiKey = "718dde0ecf0927abf30647f521a710c4"
privateKey = "db9f7a26a0e6da5a1769fe02354e5068"
lenguage = "ES"
test = False
options={"apiKey":apiKey,
         "privateKey":privateKey,
         "test":test,
         "lenguage":lenguage}


#APP STARTS HERE       
class Health(Resource):    
    def get(self):
        return {"resultado": "OK", "mensaje": "service is alive"}, 200
    
    
    
class Client(Resource):    
    #Post Method - Creates a new Client
    def post(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #create credit_card token
            credit_info = {
                "card[number]": request.json["cNumber"],
                "card[exp_year]": request.json["c_exp_year"],
                "card[exp_month]": request.json["c_exp_month"],
                "card[cvc]": request.json["c_cv"]
            }
            token=objepayco.token.create(credit_info)
            
            #create new client
            customer_info = {
                "token_card": token["id"],
                "name": request.json["client_name"],
                "last_name": request.json["client_lastname"], #This parameter is optional
                "email": request.json["client_email"],
                "phone": request.json["client_phone"],
                "default": True
            }
            customer=objepayco.customer.create(customer_info)
            
            #validar si el proceso por parte de epayco fue exitoso
            if customer["status"] == False:
                return {"resultado": "FALLO", "mensaje": "se presento un error al crear el cliente", "error": customer["message"] + " | " + customer["data"]["description"] + " | " + customer["data"]["errors"]}, 500
            
            #return a SUCCESS message and the newly created client
            return {"resultado": "OK", "mensaje": "cliente creado exitosamente", "cliente": customer}, 200
        
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al crear el cliente", "error": str(e)}, 500
        
    #Get Method - if client_id is 'all' it returns the list of all the clients, if client_id is a number it returns the client with that client_id
    def get(self,client_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #Checks if it will return the whole list or just one client
            if client_id == 'all':
                #Uses Epayco platform to obtain all the associated clients
                customers = objepayco.customer.getlist()  
                              
                #return a SUCCESS message and the list of clients
                return {"resultado": "OK", "mensaje": "se obtuvo la lista de clientes exitosamente", "customers": customers}, 200
            else:
                #Uses Epayco platform to obtain just one asociated client using the client_id field
                customer=objepayco.customer.get(client_id)
                
                #return a SUCCESS message and the newly created client
                return {"resultado": "OK", "mensaje": "se obtuvo el cliente exitosamente", "cliente": customer}, 200
            
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los clientes", "error": str(e)}, 500


    #Put Method - receives a client_id and the name of the field to update in the url and a value for said field on the json body
    def put(self,client_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #read dictionary with update fields and its values
            dicionaryString = request.json["dictionary"]
            dictionary = json.loads(dicionaryString)
            
            #field for the final response
            customer = None
            
            #Go trough the whole dictionary and updating the dictionary fields
            for key in dictionary:
                print(key)
                update_customer_info = {
                    key : dictionary[key]
                }
                customer = objepayco.customer.update(client_id,update_customer_info)
        
            #return a SUCCESS message and the newly updated client
            return {"resultado": "OK", "mensaje": "se actualizo el cliente exitosamente", "cliente": customer}, 200
        
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al actualizar el cliente", "error": str(e)}, 500        
    
    
class CreditCard(Resource):    
    #Delete Method - receives a client_id and the data of the card to delete in the json body
    def delete(self,client_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
        
            #creates the info of the card token to delete
            delete_customer_info = {
                "franchise": request.json["franchise"],
                "mask": request.json["dictiomasknary"],
                "customer_id":client_id
            }

            #deletes the card info
            response = objepayco.customer.delete(delete_customer_info)
            
            #return a SUCCESS message and the delete process response
            return {"resultado": "OK", "mensaje": "se elimino el token de tarjeta exitosamente exitosamente", "response": response}, 200
          
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al eliminar el token de tarjeta", "error": str(e)}, 500  
    #Post Method - Creates a new Client
    def post(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
        
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al crear el cliente", "error": str(e)}, 500
        
    #Get Method - if client_id is 'all' it returns the list of all the clients, if client_id is a number it returns the client with that client_id
    def get(self,client_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
                   
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los clientes", "error": str(e)}, 500


    #Put Method - receives a client_id and the name of the field to update in the url and a value for said field on the json body
    def put(self,client_id):
        #try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #create credit_card token
            credit_info = {
                "card[number]": request.json["cNumber"],
                "card[exp_year]": request.json["c_exp_year"],
                "card[exp_month]": request.json["c_exp_month"],
                "card[cvc]": request.json["c_cv"]
            }
            token=objepayco.token.create(credit_info)
            
            print(token)
            
            customer_info = {
                "customer_id":client_id,
                "token": token["id"],
                "franchise":token["card"]["name"],
                "mask":token["card"]["mask"]
            }
            customer=objepayco.customer.addDefaultCard(customer_info)
            print(customer)
            
            if customer["status"] == False:
                return {"resultado": "FALLO", "mensaje": "se presento un error al crear el cliente", "error": customer["message"]}, 500
            
            
            #return a SUCCESS message and the delete process response
            return {"resultado": "OK", "mensaje": "se elimino el token de tarjeta exitosamente exitosamente", "response": customer}, 200
        #except Exception as e:
          # print(str(e))
            #return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los clientes", "error": str(e)}, 500      
    
        
class PsePayment(Resource):    
    #Post Method - Creates a new PSE Payment
    def post(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #create pse payment object
            pse_info = {
                "bank": "1007",
                "invoice": "1472050778",
                "description": "pay test",
                "value": "116000",
                "tax": "16000",
                "tax_base": "100000",
                "currency": "COP",
                "type_person": "0",
                "doc_type": "CC",
                "doc_number": "10000000",
                "name": "testing",
                "last_name": "PAYCO",
                "email": "no-responder@payco.co",
                "country": "CO",
                "cell_phone": "3010000001",
                "ip": "190.000.000.000", #This is the client's IP, it is required,
                "url_response": "https://tudominio.com/respuesta.php",
                "url_confirmation": "https://tudominio.com/confirmacion.php",
                "metodoconfirmacion": "GET",
                #All extra parameters should be strings and not arrays.
                "extra1": "",
                "extra2": "",
                "extra3": "",
                "extra4": "",
                "extra5": "",
                "extra6": "",
                "extra7": ""
            }
            pse = objepayco.bank.create(pse_info)  
                  
            #return a SUCCESS message and the payment
            return {"resultado": "OK", "mensaje": "Se proceso el pago exitosamente", "cliente": pse}, 200
        
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al procesar el pago", "error": str(e)}, 500
        
        
        
class Payment(Resource):    
    #Post Method - Creates a new default (credit card) Payment
    def post(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #create redit card payment object
            payment_info = {
            "token_card": request.json["token_card"],
            "customer_id": request.json["customer_id"],
            "doc_type": request.json["doc_type"],
            "doc_number": request.json["doc_number"],
            "name": request.json["name"],
            "last_name": request.json["last_name"],
            "email": request.json["email"],
            "bill": request.json["bill"],
            "description": request.json["description"],
            "value": request.json["value"], #116000
            "tax": request.json["tax"], #16000
            "tax_base": request.json["tax_base"], #100000
            "currency": request.json["currency"], #COP
            "dues": request.json["dues"], # 12
            "ip":request.json["client_ip"],  #This is the client's IP, it is required
            "url_response": request.json["url_response"], #"https://tudominio.com/respuesta.php",
            "url_confirmation": request.json["url_confirmation"], #"https://tudominio.com/confirmacion.php",
            "method_confirmation": request.json["method_confirmation"], #"GET",
            "use_default_card_customer":True, # if the user wants to be charged with the card that the customer currently has as default = true
            #Los parámetros extras deben ser enviados tipo string, si se envía tipo array generara error.
            "extra1": "",
            "extra2": "",
            "extra3": "",
            "extra4": "",
            "extra5": "",
            "extra6": "",
            "extra7": ""
            }
            
            pay = objepayco.charge.create(payment_info)   
            print(pay) 
            
                 
            #return a SUCCESS message and the payment
            return {"resultado": "OK", "mensaje": "Se proceso el pago exitosamente", "cliente": pay}, 200
        
        except Exception as e:
            print(str(e))
            return {"resultado": "FALLO", "mensaje": "se presento un error al procesar el pago", "error": str(e)}, 500
        

        
            
    


# def validate_email(email):
#         pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
#         if re.match(pattern,email):
#             return True
#         return False

# def password_check(password):
#     """
#     Verify the strength of 'password'
#     Returns a dict indicating the wrong criteria
#     A password is considered strong if:
#         8 characters length or more
#         1 digit or more
#         1 symbol or more
#         1 uppercase letter or more
#         1 lowercase letter or more
#     """

#     # calculating the length
#     length_error = len(password) < 8

#     # searching for digits
#     digit_error = re.search(r"\d", password) is None

#     # searching for uppercase
#     uppercase_error = re.search(r"[A-Z]", password) is None

#     # searching for lowercase
#     lowercase_error = re.search(r"[a-z]", password) is None

#     # searching for symbols
#     symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

#     # overall result
#     password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

#     return password_ok

# def serialize(row):
#     return {
#         "id" : str(row.id),
#         "fileName" : row.fileName,
#         "newFormat" : row.newFormat,
#         "status" : row.status
#     } 

# def download_from_bucket(blob_name, file_path_destiny):
#     try:
#         bucket = storage_client.get_bucket('audioconverter-files')
#         blob = bucket.blob(blob_name)
#         with open(file_path_destiny, 'wb') as f:
#             storage_client.download_blob_to_file(blob, f)
#         return True
#     except Exception as e:
#         print(e)
#         return False

# class Tasks(Resource):
    
#     @jwt_required()
#     def get(self):
#         # current_user_id = request.json['id_usuario'] #for testing without JWT
#         current_user_id = get_jwt_identity()
#         args = request.args
#         try:
#             order = int(args.get("order"))
#         except:
#             order =0

#         try:
#             maxel = int(args.get("maxel"))
#         except:
#             maxel =0

#         if maxel>0:
#             if order==0:
#                 tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id')).limit(maxel).all()
#             else:
#                 tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id desc')).limit(maxel).all()
#         else:
#             if order==0:
#                 tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id')).all()
#             else:
#                 tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id desc')).all()

#         tasksResp =[serialize(x) for x in tasksList]
#         return jsonify({'tasks': tasksResp})

#     @jwt_required()
#     def post(self):
#         now = datetime.now()
#         dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
#         # id_usuario = request.values['id_usuario'] #for testing without JWT
#         id_usuario = get_jwt_identity()
#         if 'nombreArchivo' not in request.files:
#             return {"resultado": "ERROR", "mensaje": "La petición no contiene el archivo"}, 410
#         file = request.files["nombreArchivo"]
#         if file.filename == '':
#             return {"resultado": "ERROR", "mensaje": 'Debe seleccionar un archivo de audio para ser convertido'}, 411
#         print (file.filename)
#         if file and allowed_file(file.filename):
#             print (file.filename)
#             ct = datetime.now()
#             currentMilliseconds = str(ct.timestamp()).replace(".","")
            
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], currentMilliseconds+filename))
            
#             storage_client = storage.Client()
#             audio_bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])
            
#             filepath = str(app.config['UPLOAD_FOLDER'])+"/"+currentMilliseconds+filename
#             blob = audio_bucket.blob(str(filepath)[1:])
#             blob.upload_from_filename(filepath)

#             os.remove(filepath)
#         else:
#             print ("Formato invalido" + file.filename)
#             return {"resultado": "ERROR", "mensaje": 'Ingrese un formato de archivo válido'}, 412
#         usuario = User.query.get(id_usuario)
#         if usuario is None:
#             return {"resultado": "ERROR", "mensaje": 'El id de usuario ingresado no existe'}, 409
#         nueva_tarea = Task(fileName = filepath, newFormat = request.values['nuevoFormato'], \
#             timeStamp = dt_string, status = "uploaded", id_usuario = id_usuario)
#         db.session.add(nueva_tarea)
#         db.session.commit()

#         #Se envía tarea a la cola
#         mensaje = {"filepath":str(filepath), "newFormat":request.values['nuevoFormato'], "id": nueva_tarea.id}
#         q = publish_task_queue(mensaje)
#         return {"mensaje": "Tarea creada exitosamente", "id": nueva_tarea.id}
    
# class TaskR(Resource):

#     @jwt_required()
#     def get(self, taskId):
#         print("userid: "+taskId)
#         taskTmp = Task.query.filter(Task.id == taskId).first()
#         if(taskTmp is not None):
#             return {"id": taskTmp.id,
#                     "fileName" : taskTmp.fileName,
#                     "newFormat" : taskTmp.newFormat,
#                     "timeStamp" : taskTmp.timeStamp.strftime('%m/%d/%Y'),
#                     "status" : taskTmp.status}
#         else:
#             return {"resultado": "ERROR", "mensaje": "No se encontro la tarea"}, 400
    
#     @jwt_required()
#     def put(self, taskId):
#         # id_usuario = request.values['id_usuario'] #for testing without JWT
#         id_usuario = get_jwt_identity()
#         usuario = User.query.get(id_usuario)

#         if usuario is None:
#             return {"resultado": "ERROR", "mensaje": 'El id de usuario ingresado no existe'}, 409

#         tarea = Task.query.filter(Task.id == taskId and Task.id_usuario==id_usuario).first()
#         destinationFormat = tarea.newFormat
#         justFileName = tarea.fileName.split('.')[0]
#         destinationFileName = justFileName+"."+destinationFormat
#         if tarea.status =="processed":
#             if(os.path.isfile(destinationFileName)):
#                 os.remove(destinationFileName)
#         tarea.newFormat = request.values["nuevoFormato"]
#         tarea.status = "uploaded"

#         db.session.commit()
#         #Se envía tarea a la cola
#         mensaje = {"filepath":tarea.fileName, "newFormat":request.values['nuevoFormato'], "id": tarea.id}
#         q = publish_task_queue(mensaje)
#         return {"mensaje": "Tarea actualizada exitosamente", "tarea": serialize(tarea)},200
    
#     @jwt_required()
#     def delete(self, taskId):
#         print("idTask: "+taskId)
#         task = Task.query.get_or_404(taskId)
#         justFileName = task.fileName.split('.')[0]
#         destinationFormat = task.newFormat
#         print("justFileName: "+justFileName)
#         print("destinationFormat: "+destinationFormat)
#         destinationFileName = justFileName+"."+destinationFormat
#         print("destinationFileName: "+destinationFileName)

#         if(os.path.isfile(destinationFileName)):
#             os.remove(destinationFileName)
#         db.session.delete(task)
#         db.session.commit()
#         return {"mensaje": "Tarea eliminada exitosamente", "id": taskId},200

# class Auth(Resource):    
#     def post(self):
#         try:
#             email = request.json["email"]
#         except KeyError as e:
#             return {"resultado": "ERROR", "mensaje": "Debe proporcionar un correo electrónico"}, 400

#         try:
#             email = request.json["username"]
#         except KeyError as e:
#             return {"resultado": "ERROR", "mensaje": "Debe proporcionar un nombre de usuario"}, 400

#         try:
#             email = request.json["password1"]
#         except KeyError as e:
#             return {"resultado": "ERROR", "mensaje": "Debe proporcionar una contraseña"}, 400

#         try:
#             email = request.json["password2"]
#         except KeyError as e:
#             return {"resultado": "ERROR", "mensaje": "Debe proporcionar la confirmación de la contraseña"}, 400
        
#         if(validate_email(request.json["email"]) != True):
#             return {"resultado": "ERROR", "mensaje": "El correo electrónico suministrado no es válido"}, 400

#         if request.json["password1"] != request.json["password2"]:
#             return {"resultado": "ERROR", "mensaje": "La clave de confirmación no coincide"}, 400

#         if(password_check(request.json["password1"]) != True):
#             return {"resultado": "ERROR", "mensaje": "La clave suministrada no cumple criterios mínimos. Por favor suministre una clave \n1%"+
#         "con las siguientes características: \n1%"+
#         "8 o más caracteres \n1%"+
#         "1 o más dígitos \n1%"+
#         "1 o más símbolos \n1%"+
#         "1 o más letras mayúsculas \n1%"+
#         "1 o más letras minúsculas"}, 400

#         userTmpUsername = User.query.filter(User.username == request.json["username"]).first()
#         if(userTmpUsername is not None):
#             return {"resultado": "ERROR", "mensaje": "El usuario seleccionado ya existe"}, 400

#         userTmpEmail = User.query.filter(User.email == request.json["email"]).first()
#         if(userTmpEmail is not None):
#             return {"resultado": "ERROR", "mensaje": "El correo electrónico suministrado ya existe"}, 400
        
#         nuevoUsuario = User(username = request.json["username"], email = request.json["email"], password=request.json["password1"])
#         db.session.add(nuevoUsuario)
#         db.session.commit()
#         return {"resultado": "OK", "mensaje": "Usuario creado exitosamente"}, 200
       
    

# class AuthLogin(Resource):    
#     def post(self):
#         try:
#             username = request.json["username"]
#         except KeyError as e:
#             return {"resultado": "ERROR", "mensaje": "Debe proporcionar un nombre de usuario"}, 400

#         try:
#             password = request.json["password"]
#         except KeyError as e:
#             return {"resultado": "ERROR", "mensaje": "Debe proporcionar una contraseña"}, 400

#         user = User.query.filter(User.username == request.json["username"], User.password == request.json["password"]).first()
#         if(user is None):
#             return {"resultado": "ERROR", "mensaje": "Credenciales inválidas"}, 403

#         token_de_acceso = create_access_token(identity=user.id)
#         return {"resultado": "OK", "mensaje": "Inicio de sesión exitoso", "token": token_de_acceso}, 200

# class FilesR(Resource):   
#     @jwt_required()
#     def get(self, filename):
#         storage_client = storage.Client()
#         audio_bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])

#         filepath = str(app.config['UPLOAD_FOLDER'])+"/"+filename
#         blob = str(filepath)[1:]
#         local_filepath = str(app.config['UPLOAD_FOLDER'])+"/"+filename
#         file_downloaded = download_from_bucket(blob, local_filepath)

#         try:
#             return send_file(local_filepath, attachment_filename=filename)
#         except:
#             return {"resultado": "ERROR", "mensaje": 'El archivo no existe'}, 409