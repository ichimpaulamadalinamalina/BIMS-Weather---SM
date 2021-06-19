from flask import Flask, render_template
import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import smtplib
from RPLCD import CharLCD
from email.mime.text import MIMEText

app=Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

DHT11_pin=17

green_led=2
red_led=3
blue_led=4

GPIO.setup(green_led,GPIO.OUT)
GPIO.setup(red_led,GPIO.OUT)
GPIO.setup(blue_led,GPIO.OUT)

password="bimspassword"
email="bimsweather"
receivers=['bazganalina@yahoo.com','malinaichim940@gmail.com','modiga.camelia04@gmail.com','sstefanalexandra59@gmail.com']


lcd = CharLCD(cols=16, rows=2, pin_rs=26, pin_e=19, pins_data=[13,6,5,11],numbering_mode=GPIO.BCM)

@app.route("/")

def main():
        return render_template('main.html')


def send_mail(message):
        server=smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(email,password)
        email_content=MIMEText(message,'plain')
        email_content['Subject']='BIMS Weather'
        server.sendmail(email,receivers,email_content.as_string())
        server.quit()
        
@app.route("/index")

def action():

        temperature=''
        humidity=''

        humi,temp=dht.read_retry(dht.DHT11,DHT11_pin)
        if humi is None and temp is None:
                print("Failed to read from DHT sensor")
        else:
                temperature='{} '.format(temp)
                humidity='Humidity: {}'.format(humi)

                templateData={
                'temperature':temperature,
                'humidity':humidity
                }

                lcd.cursor_pos = (0, 0)
                lcd.write_string("Temp:{}C".format(temperature))
                lcd.cursor_pos = (1, 0)
                lcd.write_string("Humidity:{} RH".format(humi))


                if temp>=32:
                        GPIO.output(red_led,GPIO.HIGH)
                        GPIO.output(green_led,GPIO.LOW)
                        GPIO.output(blue_led,GPIO.LOW)

                        msg="Looks like it's going to be a hot day today! Temperature: " + str(temp) + " C Humidity: " + str(humi)
                        send_mail(msg)

                if 32> temp >= 20:
                        GPIO.output(green_led,GPIO.HIGH)
                        GPIO.output(blue_led,GPIO.LOW)
                        GPIO.output(red_led,GPIO.LOW)

                        msg="It's a sunny day. Enjoy it! Temperature: " + str(temp) + " C Humidity: " + str(humi)
                        send_mail(msg)

                if temp<20:
                        GPIO.output(blue_led,GPIO.HIGH)
                        GPIO.output(red_led,GPIO.LOW)
                        GPIO.output(green_led,GPIO.LOW)

                        msg="There is a chance of some rain today, so don’t leave home without your umbrella! Temperature: " + str(temp) + " Humidity: " + str(humi)
                        send_mail(msg)

                return render_template('main.html',**templateData)
if __name__=="__main__":
        app.run(host='0.0.0.0')
        GPIO.cleanup()