from flask import Flask
from flask import Response, request, jsonify
import pandas as pd
import json
import ast





variables = pd.read_csv("variables.csv")
variables["id"] = variables.index
variables["level_size"] = 2
variables["filter_fields"] = [ [] for i in range(0, len(variables)) ]
variables["available_grids"] = variables["available_grids"].apply(ast.literal_eval)
variables.rename(columns={"var":"name"}, inplace=True)
num_individuales = len(variables.groupby("name").count().index)
variables_mun = pd.read_csv("variables_muns.csv")
variables_mun["id"] = variables_mun.index + num_individuales
variables_mun.set_index("id", inplace=True, drop=False)
variables_mun["level_size"] = 3
variables_mun["filter_fields"] = [ [] for i in range(0, len(variables_mun)) ]
variables_mun["available_grids"] = variables_mun["available_grids"].apply(ast.literal_eval)
variables_mun["bin"] = variables_mun["bin"].astype('str')
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
    lvars = variables[["name", "rango"]].groupby("name").count()
    lvars.rename(columns={"rango":"level_size"}, inplace=True)
    lvars["taxonomia"] = variables[["name", "taxonomia"]].groupby("name").max()
    lvars["available_grids"] = [["ensanut"] for _ in lvars.index]
    lvars["id"] = [ i for i in range(0, len(lvars.index))]
    lvars["info"] = [ {"labels": "labels from some dict",
                       "name_extendend":"some name from some dict"} for _ in lvars.index]
    lvars.reset_index(inplace=True)
    lvars_dict = lvars.to_dict("records")    

    mvars = variables_mun[["name", "rango", "bin"]].groupby(["name", "rango"]).count()
    mvars.rename(columns={"bin":"level_size"}, inplace=True)
    mvars["available_grids"] = [ ["mun"] for _ in mvars.index]
    mvars["taxonomia"] = variables_mun[["name", "rango", "taxonomia"]].groupby(["name", "rango"]).max()
    mvars["id"] = [ i + len(lvars.index) for i in range(0, len(mvars.index))]
    mvars["info"] = [ {"labels": "labels from some dict", "name_extendend":"some name from some dict"} for _ in mvars.index]
    mvars.reset_index(inplace=True)
    mvars_dict = mvars.to_dict("records")
    mvars_dict.extend(lvars_dict)
    return jsonify(mvars_dict)


@app.route("/variables/<id>")
def single_var(id):
    q = request.args.get('q', '*')
    datos = []
    if int(id) < num_individuales:
        for columna in ["name", "rango"]:
            datos.append({"level_id": columna, "id":id,  "data":{columna:variables.loc[variables["id"] == int(id), columna].values[0]}})
    else:
        for columna in ["name", "rango", "bin"]:
            datos.append({"level_id": columna, "id":id,  "data":{columna:variables_mun.loc[variables_mun["id"] == int(id), columna].values[0]}})
    respuesta = Response(response=json.dumps(datos), status=200, mimetype="application/json")
    return respuesta



@app.route('/get-data/<id>')
def get_data_id(id):
    """Obtiene datos específicos de una covariable por ID y filtros opcionales."""
    levels_id = request.args.get('levels_id', "[0]")
    levels_id = ast.literal_eval(levels_id)
    if int(id) < num_individuales:
        if len(levels_id) > variables.loc[int(id),"level_size"]:
            levels_id = levels_id[0:variables.loc[int(id)]["level_size"]]
        list_of_levels = variables.columns[2:4]
        levels_response = [variables.loc[variables["id"] == int(id), list_of_levels[i]].values[0] for i in levels_id]
        lista = ast.literal_eval(variables.loc[int(id)]["valores"])
        respuesta = [{"id": id, "grid_id":"ensanut", "level_id":levels_response,"n":len(lista), "cells":lista }]
    else:
        list_of_levels = variables_mun.columns[2:5]
        levels_response = [variables_mun.loc[variables_mun["id"] == int(id), list_of_levels[i]].values[0] for i in levels_id]
        lista = ast.literal_eval(variables_mun.loc[int(id)]["valores"])
        respuesta = [{"id": id, "grid_id":"mun", "level_id":levels_response,"n":len(lista), "cells":lista }]
        
    return Response(response=json.dumps(respuesta), mimetype="application/json")

@app.route('/info')
def info():
    informacion = {"name": "ENSANUT Continua 2021",
                    "description": "Datos de la ENSANUT 2021.",
                    "meta": {"url":"https://ensanut.insp.mx/encuestas/ensanutcontinua2021/descargas.php",
                         "info": "Bases de datos y diccionarios originales"}
                   }
    return jsonify(informacion)
    return Response(response=json.dumps(informacion), mimetype="application/json")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500)
