from flask import Flask, render_template
import mysql.connector
from mysql.connector import Error
import os
import requests

class User:
    username = None
    password = None
    email = None

    def __init__(self, u, p, e):
        self.username = u
        self.password = p
        self.email = e
    
    def getUsername(self):
        return self.username
    
    def getPassword(self):
        return self.password
    
    '''def __str__(self):
        return f"User: {self.username}, {self.password}, {self.email}"
    '''
    def __repr__(self):
        return f"Lista utenti: username {self.username}, password {self.password}, e-mail {self.email}"
    

antonio = User("antonio", "123456", "antonio@itsrizzoli.it")
davide = User("davide", "ciao", "d.longo@itsrizzoli.it")
aimane = User('aimane', 'yolo', 'a.jrada@itsrizzoli.it')
kristian = User('kristian', 'ciaone', 'k.salva@itsrizzoli.it')
listaUser = [antonio, davide, aimane, kristian]



appWeb = Flask(__name__)
def initialize_database():
    try:
        # Connessione senza specificare il database, per permettere la creazione del database stesso
        connection = mysql.connector.connect(
            host="its-rizzoli-idt-mysql-37828.mysql.database.azure.com",
            user="psqladmin",
            passwd="H@Sh1CoR3!"
        )
        cursor = connection.cursor()

        # Leggere il contenuto del file SQL
        with open('script.sql', 'r') as file:
            sql_commands = file.read().split(';')

        # Eseguire ogni comando SQL
        for command in sql_commands:
            if command.strip():  # Ignora comandi vuoti
                cursor.execute(command)

        # Commit delle modifiche
        connection.commit()

        cursor.close()
        connection.close()
    except Error as e:
        print(f"The error '{e}' occurred")

@appWeb.route("/")
def main():
    connection = None
    risposta = "nessuna risposta"
    try:
        connection = mysql.connector.connect(
            host="its-rizzoli-idt-mysql-37828.mysql.database.azure.com",
            user="psqladmin",
            passwd="H@Sh1CoR3!",
            database="ufs05db"
        )
        risposta = "Connection to MySQL DB successful"
        cursor = connection.cursor()

        query = ("SELECT first_name, last_name FROM employees")
        cursor.execute(query)

        for (first_name, last_name) in cursor:
            risposta = first_name +last_name
        cursor.close()
        connection.close()
    except Error as e:
        risposta = f"The error '{e}' occurred"
    return  risposta

@appWeb.route("/registrazione")
def registrazione():
    return render_template("registrazione.html")


@appWeb.route("/autenticazione", methods = ["POST"])
def autenticazione():
    usernameStr = request.form.get("username")
    passwordStr = request.form.get("password")
    for i in listaUser:
        u = i.getUsername()
        p = i.getPassword()
        if u == usernameStr and p == passwordStr:
            return render_template("home.html", paramUser = usernameStr)
                
    return render_template("fail.html") # messo fuori perché altrimenti non finisce il ciclo for, e si ferma alla prima iterazione
            
    '''if passwordStr == "123456":
        return render_template("home.html", paramUser = usernameStr)
    else:
        return render_template("fail.html")'''

    '''for i in listaUser:
        listaUser.append(usernameStr)
        return render_template("listaUser.html", paramUser = listaUser)'''

@appWeb.route("/saveuser", methods =["POST"])
def saveuser():
    usernameStr = request.form.get("username")
    passwordStr = request.form.get("password")
    emailStr = request.form.get("email")
    listaUser.append(User(usernameStr, passwordStr, emailStr))


    url ="https://nodered-32761.azurewebsites.net/ciaone?usernameStr={}&emailStr={}".format(usernameStr, emailStr)


# data = {'nome': 'anna', 'cognome': 'chiodo'}
# headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.get(url)

#2) aggiungere il body alla req

#html = response.read()

    return render_template("listaUtenti.html", paramList = listaUser)

if __name__ == "__main__":
        # Inizializza il database
    initialize_database()
    # https://learn.microsoft.com/en-us/azure/app-service/reference-app-settings
    # SERVER_PORT Read-only. The port the app should listen to.
    if "PORT" in os.environ:
        appWeb.run(host="0.0.0.0", port=os.environ['PORT'])
    else:
        appWeb.run(host="0.0.0.0")