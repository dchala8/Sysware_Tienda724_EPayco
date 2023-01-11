import os
from pathlib import Path
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from src.servicios.servicios import Client, Health, PsePayment, Payment, CreditCard, Bank
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)


api.add_resource(Health, '/health')
api.add_resource(Client, '/client/create', '/client/read/<client_id>')
api.add_resource(CreditCard, '/card/delete/<client_id>', '/card/update/default/<client_id>')
api.add_resource(PsePayment, '/payment/pse', '/payment/pse/validate/<pse_id>')
api.add_resource(Payment, '/payment')
api.add_resource(Bank, '/bank')

jwt = JWTManager(app)