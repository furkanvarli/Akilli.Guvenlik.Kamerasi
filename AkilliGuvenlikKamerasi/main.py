#Tanımlar
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import RPi.GPIO as GPIO
import time
import smtplib
a=0

#Mail ayarları
mail_gonderici = "gönderici_maili@gmail.com" #Bu kısıma kendi gönderici mail adresini yazın
mail_sifresi = "şifre" ### Gönderici maili şifreniz
kime_gidecek = "alıcı_mail@outlook.com" #Mesajı göndereceğiniz mail adresi
mesaj = "Kapinizda biri tespit edildi, 192.168.#ip adresiniz#:8081"

#Servo Pin Ayarları
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 100)
pwm.start(5)
GPIO.setwarnings(False)

###
x=0
y=0
k=0
###
#Açılıştaki ilk servo konumu
angle=110
duty=float(angle)/10.0 + 2.5
pwm.ChangeDutyCycle(duty)

## PiCamera ayarları
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

#OpenCV face xml dosyası
face_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_alt.xml')


#Yüz tespit algoritması        
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	
    image = frame.array
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x,y,w,h) in faces:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
        # x1,y1 ---------
        # |              |
        # |              |
        # |              |
        # -------------x2,y2 
        # Kare içine alınan yüzlerin koordinatları
        #x1=x, x2=x+w olduğuna göre tam ortası x+w/2

        ## Servo yüz takip algoritması
        k=x+w/2
        if(k>320):
            angle=angle-10
            if(angle<30):
                angle=30
                
        elif(k<320):
            angle=angle+10
            if(angle>200):
                angle=200

            
            
    duty = float(angle) / 10.0 + 2.5
    pwm.ChangeDutyCycle(duty)
    rawCapture.truncate(0)
    
    # Yüz tespit edilirse Mail gönderip 30 işlem süresi boyunca beklemek
    # için geliştirilen timer algoritması
    if len(faces)>0 :
        print(len(faces),"yuz tespit edildi")
            
        if a==0:   
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(mail_gonderici, mail_sifresi)
            server.sendmail(mail_gonderici,kime_gidecek , mesaj)
            print("mail atıldı")
            
        a=a+1
        if a==30: ###30 işlem süresi bekleme aynı yüzü 30 defa tespit ederse 
            a=0
            
