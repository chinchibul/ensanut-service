from flask import Flask
from flask import Response
import pandas as pd
import json
import ast





variables = pd.read_csv("variables.csv")
variables["id"] = variables.index
variables["level_size"] = 1
variables["filter_fields"] = [ [] for i in range(0, len(variables)) ] 
mallas = [ ["ensanut"] for i in range(0, len(variables)) ]
variables["available_grids"] = mallas
variables.rename(columns={"var":"name"}, inplace=True)



app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello!</p>"


@app.route("/variables")
def me_api():
    return Response(response=variables[["id", "name", "level_size", "filter_fields", "available_grids"]].to_json(orient="records"), status=200, mimetype="application/json")



@app.route('/get-data/<id>')
def get_data_id(id):
    """Obtiene datos específicos de una covariable por ID y filtros opcionales."""
    print(type(id), id)

    lista = ast.literal_eval(variables.loc[int(id)]["valores"])
    print(len(lista))
                             
    respuesta = [{"id": id, "grid_id":"ensanut", "level_id":"1","n":len(lista), "cells":lista }]
    return Response(response=json.dumps(respuesta), mimetype="application/json")


