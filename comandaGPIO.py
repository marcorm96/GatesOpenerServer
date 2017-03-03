import RPi.GPIO as GPIO
import time

def apriCancello():
	#imposto la modalità BCM per chiamare i pin in base al numero BCM GPIO
	GPIO.setmode(GPIO.BCM)
	#definisco cha la GPIO 24 (pin 18) è un'uscita
	GPIO.setup(24,GPIO.OUT)
	#dato che il relay funziona logica invertita
	#imposto il GPIO 24 a LOW per accendere il relay
	GPIO.output(24,GPIO.LOW)
	#aspetto 2 secondi
	time.sleep(2)
	#imposto il GPIO 24 ad HIGH per spegnere il relay
	GPIO.output(24,GPIO.HIGH)
	#ripulisco il GPIO
	GPIO.cleanup()
	return "Aperto"

