#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import mailSender
import time
import comandaGPIO

#funzione che esegue la query passata
def eseguiQuery(query,multi):
	try:
		con = mdb.connect('localhost', 'gatesopener', 'gopwd', 'gatesopenerdb');

		cur = con.cursor()
		cur.execute(query)

		con.commit()
    
	except mdb.Error:
		if con:
			con.rollback()        
			return "Error %s:" % e.args[0]
    
	finally:    
        
		if con:			
			if multi is True:
				#mi aspetto più righe
				row=cur.fetchall()
			else:
				row=cur.fetchone()						
			con.close() 			
			if row is None:
				#si presuppone che sia un'operazione di insert e tutto sia andato bene
				return "OK"			
			return row

#funzione che recupera le credenziali dell'amministatore dal db
def getAdmin():	
	return eseguiQuery("SELECT * FROM UTENTI WHERE ADMINISTRATOR='SI'",False)

#funzione che esegue l'inserimento di un nuovo utente
def inserisciUtente(nome,cognome,email,imei,abilitato):	
	query=("INSERT INTO UTENTI (NOME,COGNOME,EMAIL,IMEI,ABILITATO) VALUES('"+nome+"','"+cognome+"','"+email+"','"+imei+"','"+abilitato+"');")	
	return eseguiQuery(query,False)
	
#funzione che cerca nella tabella UTENTI il record corrispondente al codice IMEI passato
def cercaUtenteIMEI(IMEI):		
	query=("SELECT * FROM UTENTI WHERE IMEI='"+IMEI+"'")		
	msg=eseguiQuery(query,False)
	if msg=="OK":
		#non ho trovato l'utente
		return None
	return msg

#funzione che cerca nella tabella UTENTI il record corrispondente all'id passato
def cercaUtenteID(idUtente):		
	query=("SELECT * FROM UTENTI WHERE ID_UTENTE="+idUtente+"")		
	msg=eseguiQuery(query,False)
	if msg=="OK":
		#non ho trovato l'utente
		return None
	return msg
	
#funzione che cerca nella tabella UTENTI i record con ABILITATO='SI'
def getElencoUtenti(abilitato):		
	query="SELECT ID_UTENTE,NOME,COGNOME,IMEI FROM UTENTI WHERE ADMINISTRATOR='NO' AND ABILITATO="
	if abilitato is True:
		query=query+"'SI'"
	else:
		query=query+"'NO'"
	msg=eseguiQuery(query,True)
	if msg=="OK":
		#non ho trovato nulla
		return None
	return msg	
		
#funzione che verifica se l'utente esiste ed è abilitato
def verificaUtente(IMEI):
	#cerco l'utente in base all'imei
	utente = cercaUtenteIMEI(IMEI)	
	if utente is None:
		#non è stato trovato alcun utente con quel codice IMEI
		#inserisco un nuovo record nella tabella UTENTI con solo il codice IMEI e abilitato con valore NO
		msg=inserisciUtente('','','',IMEI,'NO')		
		if msg=="OK":
			#invio una mail all'amministratore per abilitare l'utente
			return mailSender.sendMail(IMEI)			
	#se l'utente esiste,verifico che sia abilitato
	if utente[6]=="NO":
		#verifico la data di disabilitazione
		if utente[7] is not None:
			#dato che la data è stata caricata l'utente è stato disabilitato dall'amministratore
			return "Utente non abilitato"
		#verifico se è un utente che ha inviato la mail ed aspetta risposta
		if utente[8]=="SI":
			#dato che la data di disabilitazione è null,l'utente è disabilitato solo perchè
			#l'amministratore deve registrarlo
			return "In attesa di registrazione da parte dell'amministratore"
		return "Utente non abilitato"
	scriviLog("APERTURA","APERTURA CANCELLO",utente[0])
	return comandaGPIO.apriCancello()

#funzione che recupera il valore della configurazione dal db
def getConfigurazione(tipo,nome):
	conf=eseguiQuery("SELECT * FROM CONFIGURAZIONI WHERE TIPO='"+tipo+"' AND NOME='"+nome+"'",False)
	if conf is not None:
		return conf[3]
	return None

#funzione che recupera le credenziali dell'email mittente dal db
def getMittEmail():
	tipo='MAIL'
	indirizzo=getConfigurazione(tipo,'INDIRIZZO')
	if indirizzo is None:
		return "Mail non presente"
	password=getConfigurazione(tipo,'PASSWORD')
	if password is None:
		return "Errore nel recupero delle credenziali per inviare la mail"
	smtplib=getConfigurazione(tipo,'SMTP')
	if smtplib is None:
		return "Errore smtplib"
	porta=getConfigurazione(tipo,'PORTA')
	if porta is None:
		return "Errore porta"	
	emittente=[indirizzo,password,smtplib,porta]
	#l'elemento 3 identifica il campo valore
	return emittente

#funzione che effettua il login
def loginUtente(email,password):
	query=("SELECT * FROM UTENTI WHERE EMAIL='"+email+"' AND PASSWORD='"+password+"'")
	utente=eseguiQuery(query,False)
	if utente=="OK":		
		return "Credenziali non valide"
	scriviLog("LOGIN","ACCESSO UTENTE",utente[0])
	if utente[9]=="SI":
		#l'utente è un amministratore
		return utente[0]
	else:
		return "Utente non amministratore"

#funzione che aggiorna Nome e Cognome di un utente già inserito
def aggiornaNomeCognome(nome,cognome,imei,idUtente):
	query=("UPDATE UTENTI SET NOME='"+nome+"',COGNOME='"+cognome+"',ABILITATO='SI' WHERE IMEI='"+imei+"'")
	messaggio=eseguiQuery(query,False)	
	if messaggio=="OK":
		mex="AGGIORNATI NOME e COGNOME per il seguente IMEI="+imei
		scriviLog("AGGIORNAMENTO",mex,idUtente)
		return "Inserimento effettuato con successo"
	
#funzione che abilita o disabilita un utente
def abilitaDisabilita(idUtente,abilita,idUtenteLoggato):
	idUtenteStr=str(idUtente)
	if abilita is True:
		#abilito l'utente
		query=("UPDATE UTENTI SET ABILITATO='SI',DATA_DISABILITAZIONE=NULL WHERE ID_UTENTE="+idUtenteStr)
		mex="Abilitato utente con id="+idUtenteStr
	else:
		#disabilito l'utente
		query=("UPDATE UTENTI SET ABILITATO='NO',DATA_DISABILITAZIONE=CURRENT_TIMESTAMP WHERE ID_UTENTE="+idUtenteStr)
		mex="Disabilitato utente con id="+idUtenteStr
		
	messaggio=eseguiQuery(query,False)
	if messaggio=="OK":		
		scriviLog("GESTIONE_UTENTI",mex,idUtenteLoggato)
		return "Operazione effettuata con successo"
		
#funzione che scrive i log
def scriviLog(tipo,messaggio,idUtente):	
	query="INSERT INTO LOG (TIPO,MESSAGGIO,UTENTE) VALUES ('"+tipo+"','"+messaggio+"',"+str(idUtente)+")"
	eseguiQuery(query,False)

