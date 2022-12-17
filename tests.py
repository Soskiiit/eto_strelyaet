def povorot():
    import RPi.GPIO as IO
    IO.setwarnings(False)
    IO.setmode (IO.BCM)
    IO.setup(11,IO.OUT)
    p = IO.PWM(19,100)
    p.start(7.5)
    while True:
        p.ChangeDutyCycle(7.5)
        time.sleep(1)
        p.ChangeDutyCycle(12.5)
        time.sleep(1)
        p.ChangeDutyCycle(2.5)
        time.sleep(1)


povorot()