from flask import Flask
from flask import Response, request
import pandas as pd
import json
import ast





variables = pd.read_csv("variables.csv")
variables["id"] = variables.index
variables["level_size"] = 1
variables["filter_fields"] = [ [] for i in range(0, len(variables)) ]
variables["available_grids"] = variables["available_grids"].apply(ast.literal_eval)
variables.rename(columns={"var":"name"}, inplace=True)
variables_mun = pd.read_csv("variables_muns.csv")
variables_mun["id"] = variables_mun.index + len(variables)
variables_mun["level_size"] = 1
variables_mun["filter_fields"] = [ [] for i in range(0, len(variables_mun)) ]
variables_mun["available_grids"] = variables_mun["available_grids"].apply(ast.literal_eval)
variables_mun.rename(columns={"var":"name"}, inplace=True)

lista_var = variables[["id", "name", "level_size", "filter_fields", "available_grids"]].to_dict(orient='records')
lista_var_muns = variables_mun[["id", "name", "level_size", "filter_fields", "available_grids"]].to_dict(orient='records')

lista_var.extend(lista_var_muns)
lista_total = json.dumps(lista_var)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello!</p>"


@app.route("/variables/")
def me_api():
    respuesta = Response(response=lista_total, status=200, mimetype="application/json")
    return respuesta

@app.route("/variables/<id>")
def single_var(id):
    q = request.args.get('q', '*')
    datos = []
    level_id = 0
    print(variables.columns)
    for columna in ["name", "rango"]:
        datos.append({"level_id": level_id, "id":id,  columna:variables.loc[variables["id"] == int(id), columna].values[0]})
        level_id = level_id + 1
    respuesta = Response(response=json.dumps(datos), status=200, mimetype="application/json")
    return respuesta



@app.route('/get-data/<id>')
def get_data_id(id):
    """Obtiene datos específicos de una covariable por ID y filtros opcionales."""
    levels_id = request.args.get('levels_id', "[0]")
    levels_id = ast.literal_eval(levels_id)
    list_of_levels = variables.columns[2:4]
    levels_response = [variables.loc[variables["id"] == int(id), list_of_levels[i]].values[0] for i in levels_id]
    lista = ast.literal_eval(variables.loc[int(id)]["valores"])
    respuesta = [{"id": id, "grid_id":"ensanut", "level_id":levels_response,"n":len(lista), "cells":lista }]
    return Response(response=json.dumps(respuesta), mimetype="application/json")


