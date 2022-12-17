import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(40,GPIO.OUT)
servo = GPIO.PWM(11,50)
servo.start(0)
time.sleep(1)
duty = 2
while duty <= 17:
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    duty = duty + 1
servo.ChangeDutyCycle(2)
time.sleep(1)
servo.ChangeDutyCycle(0)
servo1 = GPIO.PWM(40,50)
servo1.start(0)
time.sleep(1)
duty1 = 2
while duty1 <= 17:
    servo1.ChangeDutyCycle(duty1)
    time.sleep(1)
    duty1 = duty1 + 1
servo1.ChangeDutyCycle(2)
time.sleep(1)
servo1.ChangeDutyCycle(0)
Servo1.stop()
GPIO.cleanup()
