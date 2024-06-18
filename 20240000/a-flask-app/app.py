from flask import Flask, render_template, request
import os
import json
import requests 

app = Flask(__name__)
class Persona:
    def __init__(self, nome, cognome):
        self.nome = nome
        self.cognome = cognome

    def getNome(self):
        return self.nome
    def getCognome(self):
        return self.cognome

class Dipendente(Persona):
    def __init__(self, nome, cognome, stipendio: float):
        super().__init__(nome, cognome)
        self.stipendio = stipendio

    def getStipendio(self):
        return self.stipendio
    def raiseSalary(self, perc):
        self.stipendio += self.stipendio * (perc / 100)

class Consulente(Persona):
    def __init__(self, nome, cognome, piva, tariffaOre, ore):
        super().__init__(nome, cognome)
        self.piva = piva
        self.tariffaOre = tariffaOre
        self.ore = ore

    def getPIva(self):
        return self.piva
    def getTariffaOre(self):
        return self.tariffaOre
    def getOre(self):
        return self.ore
    def calcoloRetribuzione(self):
        return self.tariffaOre * self.ore

d1 = Dipendente("Mario", "Rossi", 30000)
d2 = Dipendente("Luigi", "Verdi", 35000)
d3 = Dipendente("Anna", "Bianchi", 32000)
d1.raiseSalary(15)

c1 = Consulente("Giorgio", "Neri", "12345678901", 50, 100)
c2 = Consulente("Sofia", "Russo", "98765432109", 60, 80)
c3 = Consulente("Claudia", "Ferrari", "11223344556", 55, 120)

lista_dipendenti = [d1,d2,d3]
lista_consulenti = [c1,c2,c3]

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/autenticazione", methods = ["POST"])
def autenticazione():
    nomeStr = request.form.get("nome")
    cognomeStr = request.form.get("cognome")
    for utente in lista_dipendenti:
        if nomeStr == utente.getNome() and cognomeStr == utente.getCognome():
            loggedUser = utente
            url ="https://nodered-38317.azurewebsites.net/ciaone?nomeStr={}".format(nomeStr)
            r = requests.get(url)

            return render_template("homeDip.html", paramUser=loggedUser)
        else:
            for utente in lista_consulenti:
                if nomeStr == utente.getNome() and cognomeStr == utente.getCognome():
                    loggedUser = utente
                    return render_template("homeCons.html", paramUser=loggedUser)
    return render_template("fail.html")

@app.route("/task", methods=["GET"])
def task():
    nome = request.args.get("nome")
    cognome = request.args.get("cognome")
    
    for utente in lista_dipendenti + lista_consulenti:
        if utente.getNome() == nome and utente.getCognome() == cognome:
            return render_template("task.html", paramUser=utente)
    
    return render_template("fail.html")

if __name__ == "__main__":
    # https://learn.microsoft.com/en-us/azure/app-service/reference-app-settings
    # SERVER_PORT Read-only. The port the app should listen to.
    if "PORT" in os.environ:
        app.run(host="0.0.0.0", port=os.environ['PORT'])
    else:
        app.run(host="0.0.0.0")
