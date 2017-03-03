import smtplib
import time
import mysqlManager

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#funzione che crea il testo del messaggio da inviare
def creaTesto(IMEI,idUtente):
	data=time.strftime("%d/%m/%Y")
	ora=time.strftime("%H:%M")
	link=mysqlManager.getConfigurazione('SERVER','LINK')	
	testo="In data "+data+" alle ore "+ora+" è stata richiesta la registrazione del seguente IMEI="+IMEI+". È possibile proseguire cliccando al seguente link "+link+""+str(idUtente)
	return testo

def sendMail(IMEI):
	try:
		email_admin=mysqlManager.getAdmin()[3]
		#recupero le credenziali dell'email emittente
		mitt=mysqlManager.getMittEmail()	
		#creo il messaggio
		msg = MIMEMultipart()
		msg['From'] = mitt[0]
		msg['To'] = email_admin
		msg['Subject'] = "Richiesta di registrazione utente"
		#recupero l'id dell'utente con il codice IMEI selezionato
		idUtente=mysqlManager.cercaUtenteIMEI(IMEI)[0]
		body = creaTesto(IMEI,idUtente)
		msg.attach(MIMEText(body, 'plain'))
		#imposto il server e la porta smtp	
		mailServer = smtplib.SMTP(mitt[2], int(mitt[3]))	
		#faccio partire tls utile per email gmail
		mailServer.starttls()	
		#effettuo il login
		mailServer.login(mitt[0], mitt[1])
		#invio la mail
		text = msg.as_string()
		mailServer.sendmail(mitt[0], [email_admin], text)
		mailServer.quit()
		#aggiorno il campo MAIL_INVIATA per l'utente selezionato		
		mysqlManager.eseguiQuery("UPDATE UTENTI SET MAIL_INVIATA='SI' WHERE ID_UTENTE="+str(idUtente),False)		
		return "Utente non presente,inviata una email all'amministratore con richiesta di registrazione"		
				
	except SMTPException:
		return "Impossibile inviare l'email"
