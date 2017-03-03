from flask import Flask, redirect, url_for, request, render_template, current_app
import mysqlManager
import mailSender
app = Flask(__name__)

@app.route('/inviaComando', methods=['POST'])
def inviaComando():	
	imei=request.form['imei']
	return mysqlManager.verificaUtente(imei)		

@app.route('/aggiungiNuovo/<idN>')
def aggiungiNuovo(idN):
	#recupero l'IMEI in base all'id
	utente=mysqlManager.cercaUtenteID(idN)
	if utente is None:
		return "IMEI NON PRESENTE"	
	imei=utente[5]	
	
	return render_template('login.html',imei=imei,prossimaAzione='registrazione')    

@app.route('/gestioneUtenti')
def gestioneUtenti():
	return render_template('login.html',prossimaAzione='gestioneUtenti')	

@app.route('/login', methods=['POST'])
def login():	
	email=request.form['email']
	password=request.form['password']
	imei=request.form['imei']
	prossimaAzione=request.form['prossimaAzione']
	messaggio=mysqlManager.loginUtente(email,password)
	if messaggio>=0:
		#l'utente si è loggato correttamente
		if prossimaAzione=='registrazione':
			#può procedere alla registrazione dell'IMEI
			return render_template('registrazione.html',imei=imei,idUtenteLoggato=messaggio)
		elif prossimaAzione=='gestioneUtenti':
			return gestioneUtentiElenco(messaggio,'')
	else:
		return render_template('login.html',imei=imei,err=messaggio)

@app.route('/registrazione', methods=['POST'])
def registrazione():		
	nome=request.form['nome']	
	cognome=request.form['cognome']	
	imei=request.form['imei']		
	idUtenteLoggato=request.form['idUtenteLoggato']
	msg=mysqlManager.aggiornaNomeCognome(nome,cognome,imei,idUtenteLoggato)
	return render_template('risultato.html',msg=msg)

@app.route('/gestioneUtenti/elenco')
def gestioneUtentiElenco(idUtenteLoggato,msg):	
	#recupero l'elenco degli utenti abilitati
	elencoAbilitati=mysqlManager.getElencoUtenti(True)
	if elencoAbilitati is None:
		elencoAbilitati="NESSUN UTENTE ABILITATO"	
	elencoDisabilitati=mysqlManager.getElencoUtenti(False)
	return render_template('gestioneUtenti.html', abilitati=elencoAbilitati,disabilitati=elencoDisabilitati,idUtenteLoggato=idUtenteLoggato,msg=msg)


@app.route('/gestioneUtenti/<azione>',methods=['POST'])
def abilitaDisabilitaUtente(azione):
	if azione=='disabilita' :
		#recupero l'id dell'utente da disabilitare
		id_utente=request.form['abilitati']
		abilita=False
	elif azione=='abilita':
		#recupero l'id dell'utente da abilitare
		id_utente=request.form['disabilitati']
		abilita=True
	idUtenteLoggato=request.form['idUtenteLoggato']
	msg=mysqlManager.abilitaDisabilita(id_utente,abilita,idUtenteLoggato)
	return gestioneUtentiElenco(idUtenteLoggato,msg)

if __name__ == '__main__':
   app.run(host='0.0.0.0')
