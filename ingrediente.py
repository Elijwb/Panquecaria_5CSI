from flask import Flask, request, render_template
from contextlib import closing
import sqlite3

############################
#### Definições da API. ####
############################

app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html", mensagem = "")

@app.route("/administrativo")
def menu():
    return render_template("menu.html", mensagem = "")

@app.route("/ingrediente")
def listar_ingredientes_api():
    return render_template("listar_ingredientes.html", ingredientes = listar_ingredientes())

@app.route("/ingrediente/novo", methods = ["GET"])
def listar_criar_ingrediente_api():
    return render_template("criar_ingrediente.html")

@app.route("/ingrediente/novo", methods = ["POST"])
def criar_ingrediente_api():
    nome = request.form["nome"]
    peso = request.form["peso"]
    valor = request.form["valor"]
    id_ingrediente = criar_ingrediente(nome, peso,valor)
    return render_template("listar_ingredientes.html", ingredientes = listar_ingredientes())


@app.route("/ingrediente/novo", methods = ["GET"])
def form_criar_ingrediente_api():
    print(consultar_ingrediente("novo"))
    return render_template("form_ingredientes.html", id_ingrediente = "novo", nome = "", peso = "", valor = "")

@app.route("/ingrediente/<int:id_ingrediente>", methods = ["GET"])
def form_alterar_ingrediente_api(id_ingrediente):
    ingrediente = consultar_ingrediente(id_ingrediente)
    if ingrediente == None:
        return render_template("menu.html", mensagem = f"Esse ingrediente não existe."), 404
    return render_template("form_ingredientes.html", id = id_ingrediente, nome = ingrediente['nome_ingrediente'], peso = ingrediente['peso'], valor = ingrediente['valor'])

@app.route("/ingrediente/<int:id_ingrediente>", methods = ["POST"])
def alterar_ingrediente_api(id_ingrediente):
    nome = request.form["nome"]
    peso = request.form["peso"]
    valor = request.form["valor"]
    ingrediente = consultar_ingrediente(id_ingrediente)
    if ingrediente == None:
        return render_template("menu.html", mensagem = f"Esse ingrediente não existe mais."), 404
    editar_ingrediente(id_ingrediente, nome, valor, peso)
    return render_template("listar_ingredientes.html", ingredientes = listar_ingredientes())

@app.route("/ingrediente/<int:id_ingrediente>", methods = ["DELETE"])
def deletar_ingrediente(id_ingrediente):
    ingrediente = consultar_ingrediente(id_ingrediente)
    if ingrediente == None:
        return render_template("menu.html", mensagem = "Esse ingrediente nem mesmo existia mais."), 404
    deletar_ingrediente(id_ingrediente)
    return render_template("listar_ingredientes.html", ingredientes = listar_ingredientes())
###############################################
#### Funções auxiliares de banco de dados. ####
###############################################

# Converte uma linha em um dicionário.
def row_to_dict(description, row):
    if row == None:
        return None
    d = {}
    for i in range(0, len(row)):
        d[description[i][0]] = row[i]
    return d

# Converte uma lista de linhas em um lista de dicionários.
def rows_to_dict(description, rows):
    result = []
    for row in rows:
        result.append(row_to_dict(description, row))
    return result

####################################
#### Definições básicas de DAO. ####
####################################

sql_create = """
CREATE TABLE IF NOT EXISTS ingrediente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_ingrediente TEXT NOT NULL,
    peso FLOAT NOT NULL,
    valor FLOAT NOT NULL
);
"""

def conectar():
    return sqlite3.connect('panquecaria.db')

def criar_bd():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.executescript(sql_create)
        con.commit()

def listar_ingredientes():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT id, nome_ingrediente, peso,valor FROM ingrediente")
        return rows_to_dict(cur.description, cur.fetchall())

def listar_ingrediente_ordem():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT id, nome_ingrediente, peso, valor FROM ingrediente ORDER BY nome_ingrediente")
        return rows_to_dict(cur.description, cur.fetchall())

def verificar_serie(numero, turma):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT id_serie FROM serie WHERE numero = ? AND turma = ?", (numero, turma))
        t = cur.fetchone()
        return None if t == None else t[0]

def consultar_ingrediente(id_ingrediente):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * from ingrediente WHERE id = ?", (id_ingrediente, ))
        return row_to_dict(cur.description, cur.fetchone())

def criar_ingrediente(nome, peso, valor):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO ingrediente (nome_ingrediente, peso, valor) VALUES (?, ?, ?)", (nome, peso,valor))
        id_ingrediente = cur.lastrowid
        con.commit()
        return id_ingrediente

def editar_ingrediente(id_ingrediente, nome, valor, peso):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE ingrediente SET nome_ingrediente = ?, peso = ?, valor = ? WHERE id = ?", (nome, peso, valor, id_ingrediente))
        con.commit()

def deletar_ingrediente(id_ingrediente):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("DELETE FROM ingrediente WHERE id = ?", (id_ingrediente, ))
        con.commit()

########################
#### Inicialização. ####
########################

if __name__ == "__main__":
    criar_bd()
    app.run()
