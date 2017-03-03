#!/bin/sh
echo -n "Inserisci l'indirizzo gmail per GatesOpener: "
read MAILGO
sed -i "s/MAILGO/"${MAILGO}"/g" script_db.sql

echo -n "Inserisci la password dell'indirizzo gmail: "
read PWDGO
sed -i "s/PWDGO/"${PWDGO}"/g" script_db.sql

echo -n "Inserisci il nome dell'amministratore: "
read NOMEADMIN
sed -i "s/NOMEADMIN/"${NOMEADMIN}"/g" script_db.sql

echo -n "Inserisci il cognome dell'amministratore: "
read COGADMIN
sed -i "s/COGADMIN/"${COGADMIN}"/g" script_db.sql

echo -n "Inserisci l'indirizzo email dell'amministratore: "
read MAILADMIN
sed -i "s/MAILADMIN/"${MAILADMIN}"/g" script_db.sql

echo -n "Inserisci la password dell'amministratore: "
read PWDADMIN
sed -i "s/PWDADMIN/"${PWDADMIN}"/g" script_db.sql

echo -n "Inserisci l'IMEI del cellulare dell'amministratore: "
read IMEIADMIN
sed -i "s/IMEIADMIN/"${IMEIADMIN}"/g" script_db.sql

echo -n "Inserisci l'indirizzo IP statico del tuo raspberry: "
read IP
#cambio il valore nel file script_db.sql
sed -i "s/IPRPI/"${IP}"/g" script_db.sql
cd ..
cd templates
#cambio i valori nei files html
sed -i "s/IPRPI/"${IP}"/g" *.html
