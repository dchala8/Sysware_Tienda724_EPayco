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

apiKey = ""
privateKey = ""
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
                
                if customers["status"] == False:
                    return {"resultado": "FALLO", "mensaje": "se presento un error al buscar el cliente", "error": customers["message"] + " | " + customers["data"]["description"]}, 500 
                              
                #return a SUCCESS message and the list of clients
                return {"resultado": "OK", "mensaje": "se obtuvo la lista de clientes exitosamente", "customers": customers}, 200
            else:
                #Uses Epayco platform to obtain just one asociated client using the client_id field
                customer=objepayco.customer.get(client_id)
                
                if customer["status"] == False:
                    return {"resultado": "FALLO", "mensaje": "se presento un error al buscar el cliente", "error": customer["message"] + " | " + customer["data"]["description"]}, 500 
                
                #return a SUCCESS message and the newly created client
                return {"resultado": "OK", "mensaje": "se obtuvo el cliente exitosamente", "cliente": customer}, 200
            
        except Exception as e:
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
                update_customer_info = {
                    key : dictionary[key]
                }
                customer = objepayco.customer.update(client_id,update_customer_info)
        
            #return a SUCCESS message and the newly updated client
            return {"resultado": "OK", "mensaje": "se actualizo el cliente exitosamente", "cliente": customer}, 200
        
        except Exception as e:
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
                "mask": request.json["mask"],
                "customer_id":client_id
            }

            #deletes the card info
            response = objepayco.customer.delete(delete_customer_info)
            
            #validates if the card was deleted or if we got a internal server error
            if response["status"] == False:
                return {"resultado": "FALLO", "mensaje": "se presento un error al eliminar el token de tarjeta", "error": response["message"] + " | " + response["data"]["description"]}, 500  
            
            #return a SUCCESS message and the delete process response
            return {"resultado": "OK", "mensaje": "se elimino la tarjeta exitosamente exitosamente", "response": response}, 200
          
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al eliminar el token de tarjeta", "error": str(e)}, 500  
    #Post Method - Creates a new Client
    def post(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
        
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al crear el cliente", "error": str(e)}, 500
        
    #Get Method - if client_id is 'all' it returns the list of all the clients, if client_id is a number it returns the client with that client_id
    def get(self,client_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
                   
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los clientes", "error": str(e)}, 500


    #Put Method - receives a client_id and the name of the field to update in the url and a value for said field on the json body
    def put(self,client_id):
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

            
            #validates if token had a bad response and throws exception in that case
            if token["status"]==False:
                return {"resultado": "FALLO", "mensaje": "La tarjeta de credito no existe", "error": token["message"]}, 500
            
            #prepares the customaer info for the new card
            customer_info = {
                "customer_id":client_id,
                "token": token["id"],
                "franchise":token["card"]["name"],
                "mask":token["card"]["mask"]
            }
            #asociates the new card to the customer as its new default card
            customer=objepayco.customer.addDefaultCard(customer_info)
            
            #validates if the asociation was made correctly and throws a exception if not
            if customer["status"] == False:
                return {"resultado": "FALLO", "mensaje": "se presento un error al actualizar el token de tarjeta de credito", "error": customer["message"]}, 500
            
            
            #return a SUCCESS message and the delete process response
            return {"resultado": "OK", "mensaje": "se actualizo el token de tarjeta exitosamente exitosamente", "response": customer}, 200
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los clientes", "error": str(e)}, 500      



class Bank(Resource):    
    #Get Method - Returns a the list of avaiable PSE banks
    # def get(self):
    #     try:
    #         #Create API connection with EPAYCO
    #         objepayco=epayco.Epayco(options)
            
    #         #obtain the bank list
    #         bankList = objepayco.bank.pseBank()
                  
    #         #return a SUCCESS message and the bank list
    #         return {"resultado": "OK", "mensaje": "Se obtuvo el listado de bancos adecuadamente", "bancos": bankList}, 200
        
    #     except Exception as e:
    #         return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los bancos", "error": str(e)}, 500
    
    def get(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #obtain the bank list
            bankList = {
                "success": True,
                "title_response": "Ok",
                "text_response": "Bancos consultados exitosamente PseController",
                "last_action": "Query Bancos",
                "data": [
                    {
                        "bankCode": "10400",
                        "bankName": "Banco Agrario"
                    },
                    {
                        "bankCode": "1052",
                        "bankName": "Banco AV Villas"
                    },
                    {
                        "bankCode": "1013",
                        "bankName": "BANCO BBVA COLOMBIA S.A."
                    },
                    {
                        "bankCode": "1032",
                        "bankName": "BANCO CAJA SOCIAL"
                    },
                    {
                        "bankCode": "1051",
                        "bankName": "BANCO DAVIVIENDA"
                    },
                    {
                        "bankCode": "1001",
                        "bankName": "BANCO DE BOGOTA"
                    },
                    {
                        "bankCode": "1023",
                        "bankName": "BANCO DE OCCIDENTE"
                    },
                    {
                        "bankCode": "1012",
                        "bankName": "BANCO GNB SUDAMERIS"
                    },
                    {
                        "bankCode": "1006",
                        "bankName": "BANCO ITAU"
                    },
                    {
                        "bankCode": "1002",
                        "bankName": "BANCO POPULAR"
                    },
                    {
                        "bankCode": "1007",
                        "bankName": "BANCOLOMBIA"
                    },
                    {
                        "bankCode": "1009",
                        "bankName": "CITIBANK"
                    },
                    {
                        "bankCode": "1019",
                        "bankName": "SCOTIABANK COLPATRIA"
                    }
                ],
                "enpruebas": False
            }
                  
            #return a SUCCESS message and the bank list
            return {"resultado": "OK", "mensaje": "Se obtuvo el listado de bancos adecuadamente", "bancos": bankList}, 200
        
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los bancos", "error": str(e)}, 500
        
    
        
class PsePayment(Resource):    
    #Get Method - Obtains the transaccion created and its status with pse_id
    def get(self,pse_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #Obtain the PSE transaction
            pse = objepayco.bank.pseTransaction(pse_id)
                  
            #return a SUCCESS message and the transaction
            return {"resultado": "OK", "mensaje": "Su transaccion es", "Transaccion": pse}, 200
        
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al obtener la transaccion", "error": str(e)}, 500
        
    #Post Method - Creates a new PSE Payment
    def post(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #create pse payment object
            pse_info = {
                "bank": request.json["bank"],
                "invoice": request.json["invoice"],
                "description": request.json["description"],
                "value": request.json["value"],
                "tax": request.json["tax"],
                "tax_base": request.json["tax_base"],
                "currency": request.json["currency"],
                "type_person": request.json["type_person"],
                "doc_type": request.json["doc_type"],
                "doc_number": request.json["doc_number"],
                "name": request.json["name"],
                "last_name": request.json["last_name"],
                "email": request.json["email"],
                "country": request.json["country"],
                "cell_phone": request.json["cell_phone"],
                "ip": request.json["ip"], #This is the client's IP, it is required,
                "url_response": request.json["url_response"],
                "url_confirmation": request.json["url_confirmation"],
                "metodoconfirmacion": request.json["metodoconfirmacion"],
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
                  
            if pse["success"] == False:
                return {"resultado": "FALLO", "mensaje": "se presento un error al procesar el pago", "error": pse["title_response"] + " | " + pse["text_response"] + " | " + pse["data"]["errores"][0]["codError"] + " | " + pse["data"]["errores"][0]["errorMessage"]}, 500
            #return a SUCCESS message and the payment
            return {"resultado": "OK", "mensaje": "Se proceso el pago exitosamente", "cliente": pse}, 200
        
        except Exception as e:
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
            
            #return a SUCCESS message and the payment
            return {"resultado": "OK", "mensaje": "Se proceso el pago exitosamente", "cliente": pay}, 200
        
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al procesar el pago", "error": str(e)}, 500