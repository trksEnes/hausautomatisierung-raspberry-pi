import time
import RPi.GPIO as GPIO
import threading

GPIO.setwarnings(False)

touch_pin = 21
led = 20
knopf = 27
right_pin = 22
left_pin = 17

sensor_pin = 5
motor_pins = [6, 13, 19, 26]
stepper_sequence = [[1, 0, 0, 1],
                    [1, 0, 0, 0],
                    [1, 1, 0, 0],
                    [0, 1, 0, 0],
                    [0, 1, 1, 0],
                    [0, 0, 1, 0],
                    [0, 0, 1, 1],
                    [0, 0, 0, 1]]

global Value
global Value1
global trash
trash = True
Value = 0
Value1 = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led, GPIO.OUT)
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)


def light_thread():
    global Value1
    global Value
    while True:
        touch = GPIO.input(21)
        if touch == 1 and Value == 0:
            print("Licht an")
            Value = 1
            Value1 = Value1 + 1
            GPIO.output(led, GPIO.HIGH)
        elif touch == 1 and Value == 1:
            print("Licht aus")
            Value = 0
            Value1 = Value1 - 1
            GPIO.output(led, GPIO.LOW)
        time.sleep(0.3)

light_t = threading.Thread(target=light_thread)


class MotorThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.paused = False
        self.pause_cond = threading.Condition(threading.Lock())

    def run(self):
        step = 0
        direction = 1
        motor_running_time = 15
        last_sensor_state = None

        while True:
            current_sensor_state = GPIO.input(sensor_pin)

            if current_sensor_state != last_sensor_state:
                last_sensor_state = current_sensor_state

                if current_sensor_state == GPIO.HIGH:
                    print("Licht erkannt - Schrittmotor dreht nach links")
                    direction = -1
                else:
                    print("Kein Licht - Schrittmotor dreht nach rechts")
                    direction = 1

                motor_start_time = time.monotonic()
                while (time.monotonic() - motor_start_time) < motor_running_time:
                    with self.pause_cond:
                        while self.paused:
                            self.pause_cond.wait()
                    for i in range(8):
                        for pin in range(4):
                            GPIO.output(motor_pins[pin], stepper_sequence[step][pin])
                        step += direction
                        if step >= 8:
                            step = 0
                        elif step < 0:
                            step = 7
                        time.sleep(0.001)

            print("Warte 15 Sekunden: ")
            for i in range(15, 0, -1):
                with self.pause_cond:
                    while self.paused:
                        self.pause_cond.wait()
                if trash:
                    print(i, end=' ', flush=True)
                else:
                    break
                time.sleep(1)
            print("")

            if not trash:
                print("Überprüfung gestoppt")
                break

    def pause(self):
        self.paused = True
        print("MotorThread pausiert")

    def resume(self):
        self.paused = False
        with self.pause_cond:
            self.pause_cond.notify()
        print("MotorThread fortgesetzt")



motor_t = MotorThread()
motor_t.start()
light_t.start()


def button_callback(channel):
    global trash
    if trash:
        trash = False
        print("Überprüfung ausgeschaltet")
        motor_t.pause()
    else:
        trash = True
        print("Überprüfung angeschaltet")
        motor_t.resume()


def manual_control_right():
    step = 0  # Variable step initialisieren
    while GPIO.input(right_pin) == GPIO.LOW:
        for pin in range(4):
            GPIO.output(motor_pins[pin], stepper_sequence[step][pin])
        step += 1
        if step >= 8:
            step = 0
        time.sleep(0.001)

def manual_control_left():
    step = 0  # Variable step initialisieren
    while GPIO.input(left_pin) == GPIO.LOW:
        for pin in range(4):
            GPIO.output(motor_pins[pin], stepper_sequence[7-step][pin]) # Änderung hier
        step += 1
        if step >= 8:
            step = 0
        time.sleep(0.001)




def button_callback_right(channel):
    if not trash:
        manual_control_right()

def button_callback_left(channel):
    if not trash:
        manual_control_left()
        


GPIO.setup(right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(right_pin, GPIO.FALLING, callback=button_callback_right, bouncetime=200)
GPIO.add_event_detect(left_pin, GPIO.FALLING, callback=button_callback_left, bouncetime=200)


GPIO.setup(knopf, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.FALLING, callback=button_callback, bouncetime=200) # setup button callback