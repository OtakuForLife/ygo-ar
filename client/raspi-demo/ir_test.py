import RPi.GPIO as GPIO
import time
#pin_ira = 38
pin_ird = 19
 
def setup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin_ird, GPIO.IN)
 
def loop():
	while True:
		if GPIO.input(pin_ird) == GPIO.HIGH:
			print("Nothing's here")
		else:
			print("Hello there")
		time.sleep(0.1)

def destroy():
	GPIO.cleanup()

if __name__ == '__main__':
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()
