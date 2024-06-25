from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import mysql.connector
import os
import qrcode
import io

app = Flask(__name__)
app.secret_key = os.urandom(128)

db_config = {
    'user': 'psqladmin',
    'password': 'H@Sh1CoR3!',
    'host': 'its-rizzoli-idt-mysql-25644.mysql.database.azure.com',
    'database': 'DigitalPark'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

class Persona:
    def __init__(self, email):
        self.email = email
        self.nome = None
        self.cognome = None
        self.cf = None
        self.password = None

    @staticmethod
    def get_by_email(email):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM persona WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()

        if user_data:
            user = Persona(email)
            user.nome = user_data['nome']
            user.cognome = user_data['cognome']
            user.cf = user_data['cf']
            user.password = user_data['password']
            return user
        return None

    def save(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO persona (nome, cognome, cf, email, password) VALUES (%s, %s, %s, %s, %s)",
            (self.nome, self.cognome, self.cf, self.email, self.password)
        )
        connection.commit()
        cursor.close()
        connection.close()
class Utente:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    @staticmethod
    def register(nome, cognome, cf, email, password):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Verifica se l'email esiste già
            cursor.execute("SELECT * FROM persona WHERE email = %s", (email,))
            if cursor.fetchone():
                return "Email già registrata. Per favore, usa un'altra email."

            # Inserisce il nuovo utente nel database
            cursor.execute("""
                INSERT INTO persona (nome, cognome, cf, email, password) 
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, cognome, cf, email, password))
            connection.commit()
            
            # Creazione dell'istanza dell'utente
            return Utente(nome, cognome, cf, email, password)
        
        except mysql.connector.Error as err:
            print(f"Errore: {err}")
            connection.rollback()
            return "Errore durante la registrazione. Riprova più tardi."
        
        finally:
            cursor.close()
            connection.close()
    @staticmethod
    def authenticate(email, password):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM persona WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()

        if user_data and user_data['password'] == password:
            persona = Persona.get_by_email(email)
            return Utente(email=email, password=password), persona
        return None, None
    
    def get_storico_prenotazioni(self):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prenotazioni WHERE cf = (SELECT cf FROM persona WHERE email = %s)", (self.email,))
        prenotazioni = cursor.fetchall()
        cursor.close()
        connection.close()
        return prenotazioni

    def aggiorna_password(self, nuova_password):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE persona SET password = %s WHERE email = %s", (nuova_password, self.email))
        connection.commit()
        cursor.close()
        connection.close()
# Classe per rappresentare una Macchina
'''class Macchina:
    def __init__(self, targa, id_posto, data, ora_inizio, ora_fine):
        self.targa = targa
        self.id_posto = id_posto
        self.data = data
        self.ora_inizio = ora_inizio
        self.ora_fine = ora_fine

    def prenota(self, cf):
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO prenotazioni (id, data_in, data_out, targa, cf, id_posto, id_ticket) VALUES (%s, %s, %s, %s, %s, %s)",
                (cf, self.id_posto, self.data, self.ora_inizio, self.ora_fine, self.targa)
            )

            cursor.execute("UPDATE posto_auto SET stato = 1 WHERE id_posto = %s", (self.id_posto,))
            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()'''
class PostoAuto:
    def __init__(self, id_posto, stato, id_piano):
        self.id_posto = id_posto
        self.stato = stato
        self.id_piano = id_piano

    @staticmethod
    def get_all():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM posto_auto")
        posti = cursor.fetchall()
        cursor.close()
        connection.close()
        return [PostoAuto(**posto) for posto in posti]

    def update_stato(self, nuovo_stato):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE posto_auto SET stato = %s WHERE id_posto = %s", (nuovo_stato, self.id_posto))
        connection.commit()
        cursor.close()
        connection.close()
        
class Prenotazione:
    def __init__(self, id, data_in, data_out, targa, cf, id_posto, id_ticket):
        self.id = id
        self.data_in = data_in
        self.data_out = data_out
        self.targa = targa
        self.cf = cf
        self.id_posto = id_posto
        self.id_ticket = id_ticket

    @staticmethod
    def get_by_cf(cf):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prenotazioni WHERE cf = %s", (cf,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return [Prenotazione(**row) for row in results]

    def save(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO prenotazioni (data_in, data_out, targa, cf, id_posto, id_ticket)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (self.data_in, self.data_out, self.targa, self.cf, self.id_posto, self.id_ticket))
        connection.commit()
        cursor.close()
        connection.close()

class Admin:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def authenticate(username, password):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cursor.fetchone()
        cursor.close()
        connection.close()

        if admin and admin['password'] == password:
            return Admin(username, password)
        return None

    def add_user(self, user):
        user.save()

    def remove_user(self, email):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM persona WHERE email = %s", (email,))
        connection.commit()
        cursor.close()
        connection.close()

    def view_all_prenotazioni(self):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prenotazioni")
        prenotazioni = cursor.fetchall()
        cursor.close()
        connection.close()
        return prenotazioni

@app.route('/', methods=['GET', 'POST'])
def index():
    images = [
        url_for('static', filename='Pohang-Apartment.jpeg'),
        url_for('static', filename='download.jpeg'),
        url_for('static', filename='Misagangbyeon-Apartment.jpeg')
    ]
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Utilizza il metodo authenticate della classe Utente
        utente, persona = Utente.authenticate(email, password)

        if utente:
            # Salva l'oggetto persona nella sessione
            session['user'] = {
                'email': persona.email,
                'nome': persona.nome,
                'cognome': persona.cognome,
                'cf': persona.cf
            }
            return redirect(url_for('home'))
        else:
            error = 'Credenziali non valide, riprova.'
            return render_template('index.html', images=images, error=error)
    
    return render_template('index.html', images=images)

@app.route('/register', methods=['GET', 'POST'])
def register():
    images = [
        url_for('static', filename='Box Brand Design _ 合子品牌設計有限公司.jpeg'),
        url_for('static', filename='Shenzhen-Building (1).jpeg'),
        url_for('static', filename='Shenzhen-Building.jpeg')
    ]
    
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        cf = request.form['cf']
        email = request.form['email']
        password = request.form['password']
        
        # Utilizzo del metodo di registrazione della classe Utente
        result = Utente.register(nome, cognome, cf, email, password)
        
        if isinstance(result, Utente):
            # Registrazione riuscita, memorizza i dettagli dell'utente nella sessione
            session['user'] = {
                'nome': result.nome,
                'cognome': result.cognome,
                'cf': result.cf,
                'email': result.email
            }
            return redirect(url_for('home'))
        else:
            # Gestione degli errori (ad esempio, email già esistente)
            error = result
            return render_template('register.html', images=images, error=error)
    
    return render_template('register.html', images=images)


@app.route('/prenotazione', methods=['GET', 'POST'])
def prenotazione():
    if request.method == 'POST':
        # Recupera i dati dalla pagina home.html
        data = request.form['data']
        ora_inizio = request.form['ora-inizio']
        ora_fine = request.form['ora-fine']

        # Salva data_in e data_out nella sessione
        session['data_in'] = f"{data} {ora_inizio}"  # Combina data e ora inizio
        session['data_out'] = f"{data} {ora_fine}"   # Combina data e ora fine

        # Recupera i posti auto disponibili
        posti = PostoAuto.get_all()

        # Reindirizza alla pagina prenotazione.html
        return render_template('prenotazione.html', posti=posti)

    # GET request, mostra la pagina iniziale o redirect a home
    return redirect(url_for('home'))



@app.route('/conferma', methods=['POST'])
def conferma():
    # Recupera dati dal form prenotazione.html
    id_posto = request.form['id_posto']
    targa = request.form['targa']
    
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    
    cf = user['cf']

    # Recupera data_in e data_out dalla sessione
    data_in = session.get('data_in')
    data_out = session.get('data_out')

    # Controlla che data_in e data_out siano presenti
    if not data_in or not data_out:
        flash('Le informazioni sulla data e l\'ora sono mancanti.')
        return redirect(url_for('prenotazione'))

    # Crea una nuova prenotazione
    prenotazione = Prenotazione(
        id=None,
        data_in=data_in,
        data_out=data_out,
        targa=targa,
        cf=cf,
        id_posto=id_posto,
        id_ticket=None
    )
    
    try:
        prenotazione.save()

        # Recupera l'id appena assegnato alla prenotazione
        prenotazione_id = prenotazione.id

        # Genera il contenuto del QR code
        qr_content = f"Prenotazione ID: {prenotazione_id}\nPosto: {id_posto}\nTarga: {targa}\nData Inizio: {data_in}\nData Fine: {data_out}"

        # Genera il QR code
        qr_img = qrcode.make(qr_content)

        # Salva il QR code come immagine temporanea nella cartella statica
        qr_filename = f"qrcode_{prenotazione_id}.png"
        qr_path = os.path.join('static', qr_filename)
        qr_img.save(qr_path)

        # Salva il nome del file del QR code nella sessione
        session['qr_filename'] = qr_filename

        # Aggiorna lo stato del posto auto
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE posto_auto SET stato = 1 WHERE id_posto = %s", (id_posto,))
        connection.commit()
        cursor.close()
        connection.close()

        # Rimuovi data_in e data_out dalla sessione
        session.pop('data_in', None)
        session.pop('data_out', None)

        # Reindirizza alla pagina del ticket
        return redirect(url_for('ticket'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if 'connection' in locals():
            connection.rollback()
        flash('Si è verificato un errore durante la prenotazione. Riprova.')
        return redirect(url_for('prenotazione'))


@app.route('/storico')
def storico():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    
    prenotazioni = Prenotazione.get_by_user(user['cf'])
    return render_template('storico.html', prenotazioni=prenotazioni)
@app.route('/home')
def home():
    # Verifica se l'utente è loggato
    if 'user' not in session:
        return redirect(url_for('index'))

    # Recupera l'email dell'utente dalla sessione
    user_email = session['user']['email']
    
    # Recupera i dettagli personali dell'utente
    user_details = Persona.get_by_email(user_email)
    
    if not user_details:
        # Se l'utente non è trovato, reindirizza alla pagina di login
        return redirect(url_for('index'))
    
    # Renderizza la pagina home con i dettagli dell'utente
    return render_template('home.html', user=user_details)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dati')
def dati():
    # Verifica se l'utente è loggato
    if 'user' not in session:
        return redirect(url_for('index'))

    # Recupera l'email dell'utente dalla sessione
    user_email = session['user']['email']
    
    # Recupera i dettagli personali dell'utente
    user_details = Persona.get_by_email(user_email)
    
    if not user_details:
        # Se l'utente non è trovato, reindirizza alla pagina di login
        return redirect(url_for('index'))
    
    # Renderizza la pagina dati.html con i dettagli dell'utente
    return render_template('dati.html', user=user_details)

@app.route('/ticket')
def ticket():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))

    qr_filename = session.get('qr_filename')
    if not qr_filename:
        flash('Non è stato possibile trovare il QR code della prenotazione.')
        return redirect(url_for('home'))

    return render_template('ticket.html', qr_filename=qr_filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')