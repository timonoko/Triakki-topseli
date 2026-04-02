
import socket

import network,time,machine
from machine import Pin,Timer

relayON=Pin(5, Pin.OUT)  
BUTTON=Pin(4, Pin.IN)

SininenLedi = Pin(2, Pin.OUT)  
SininenLedi.value(1)

LO=0;HI=1

relayState=0
relayON.value(0)

goal_speed = 1  # -10 to 10
step_counter = 0


def apply_power(t):
    global step_counter
    if step_counter == 0:
        step_counter = goal_speed
        if step_counter < 0: relayON.value(1)
        else: relayON.value(0)
    elif step_counter < 0:
        relayON.value(0)
        step_counter+=1
    else:
        relayON.value(1)
        step_counter-=1

SPEED=0
        
tim = Timer(-1)

def set_speed(value):
    global goal_speed,tim,SPEED
    SPEED=value
    tim.init(period=11, mode=Timer.PERIODIC, callback=apply_power)
    goal_speed = round(value/5.-10)
    if goal_speed==0: goal_speed=1
    print(f"Motor speed set to: {goal_speed}")

def web_page():
    RS=" button2"
    if relayState==1: RS=""
    menu="""<p><a href="/ON"><button class="button%s">ON</button> </a>"""%(RS)
    menu+="""<a href="/OFF"><button class="button button3">OFF</button> </a><p>"""
    menu+="""<a href="/MINUS"><button class="button button4">-</button> </a>"""
    menu+="  "+str(SPEED)+"  "
    menu+="""<a href="/PLUS"><button class="button button4">+</button> </a>"""
    sta_if = network.WLAN(network.STA_IF)
    this_ip=sta_if.ifconfig()[0]
    html = """
     <html><head> 
     <title>TYRISTORI</title>
     <meta http-equiv="refresh" content="3;url=http://"""+this_ip+"""/">
     <meta name="viewport" content="width=device-width, initial-scale=1"> 
     <link rel="icon" href="data:,">
     <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #ff0000; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4a798a;}
  .button3{background-color: #3f7749;}
  .button4{background-color: #cd0e0e;}
   </style>
     </head>
      <body>
     <h1>TYRISTORI</h1> 
     """ + menu + """ <p>
     """ + this_ip + """ <p>
      </body>
   </html>"""
    return html


def buttoni():
   global relayState
   if BUTTON.value()==LO:
       pitka=0
       SininenLedi.value(0)
       while BUTTON.value()==LO:
           time.sleep(0.1)
           pitka+=1
           if pitka>10:
               SininenLedi.value(1)
               relayState=1
               vauhti=(pitka-20)
               tim.deinit()
               print('vauhti=',vauhti)
               set_speed(vauhti)
       if pitka<11:
           tim.deinit()
           if relayState==1:
               SPEED=0
               relayState=0
               relayON.value(0)
           else:
               SPEED=100
               relayState=1
               relayON.value(1)
       SininenLedi.value(1)
       time.sleep(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    s.settimeout(0.2)
    try:
        conn, addr = s.accept()
        request = conn.recv(1024)
        request = str(request)
        s.settimeout(5.0)
        if request.find('/ON') == 6:
            SPEED=100
            tim.deinit() # This kills the background timer completely
            relayState=1
            relayON.value(1)
        if request.find('/OFF') == 6:
            SPEED=0
            relayState=0
            relayON.value(0)
            tim.deinit() # This kills the background timer completely
            print("Motor Hard Stopped and Timer Deactivated")
        if request.find('/10S') == 6:
            relayON.value(1)
            time.sleep(10)
            relayON.value(0)
            relayState=0
        if request.find('/S') == 6:
            relayState=1
            vauhti=eval(request[8]+request[9])
            tim.deinit()
            print('vauhti=',vauhti)
            set_speed(vauhti)
        if request.find('/PLUS') == 6:
            relayState=1
            SPEED+=1
            tim.deinit()
            print('vauhti=',SPEED)
            set_speed(SPEED)
        if request.find('/MINUS') == 6:
            relayState=1
            SPEED-=1
            tim.deinit()
            print('vauhti=',SPEED)
            set_speed(SPEED)
        if request.find('/LED/ON') == 6:
            SininenLedi.value(0)
        if request.find('/LED/OFF') == 6:
            SininenLedi.value(1)
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    except OSError:
        buttoni() 




