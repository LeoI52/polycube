import requests
import time
import math
import pyxel




url1 = "http://10.198.155.113/get?accX&accY&accZ"
url2= "http://10.198.155.203:8080/get?accX&accY&accZ"



Tab1_accY=[0]
Tab2_accY=[0]
c1=0
c2=0

while True:
    try:
        r1 = requests.get(url1)
        data1 = r1.json()

        r2=requests.get(url2)
        data2=r2.json()


       

        if(c1!=1):
            accY_1 = data1["buffer"]["accY"]["buffer"][-1]
            if(accY_1==Tab1_accY[-1]):
                c1=1
        
            Tab1_accY.append(accY_1)

      

        if(c2!=1):
            accY_2=data2["buffer"]["accY"]["buffer"][-1]
            if(accY_2==Tab2_accY[-1]):
                c2=1
            Tab2_accY.append(accY_2)

         # if(accY_1==Tab1_accY[-2]):
        #     c1=1
        # if(accY_2==Tab2_accY[-2]):
        #     c2=1

        if(c1==1 and c2==1):
            break

        # print(f"Y={accY:.2f} ")

        time.sleep(0.1)  # 10 mesures par seconde

    except Exception as e:
        print("Erreur :", e)
        time.sleep(1)

  

    
    
    
g = 9.81
theta1 = math.asin(-Tab1_accY[-1] / g)
theta2= math.asin(-Tab2_accY[-1] / g)

theta1_deg = math.degrees(theta1)
theta2_deg = math.degrees(theta2)

print(f"Angle Tir= {theta1_deg:.2f} degres")
print(f"Angle Tir= {theta2_deg:.2f} degres")

# if (theta1_deg<=20 and theta1_deg>=-20):
#     print("Cool")
# if(theta2_deg<=20 and theta2_deg>=-20):
#     print("Cool")


def angle_valide(Tab):
    theta=math.degrees(math.asin(-Tab[-1] / g))
    if (theta<=20 and theta>=-20):
        return True
    return False

def gagnant(Tab1,Tab2):
    if(angle_valide(Tab1)==True and angle_valide(Tab2)==True ):
        if(len(Tab1)>len(Tab2)):
            print("Player 1 won")
        elif(len(Tab1)<len(Tab2)):
            print("Player 2 won")
        else:
            
            print("Players died")


    elif(angle_valide(Tab1)):
        print("Player 1 won")

    elif(angle_valide(Tab2)):
        print("Player 2 won")
    
    else:
        print("Bande de nul, apprennez a tirer")


gagnant(Tab1_accY, Tab2_accY)
print(len(Tab1_accY))
print(len(Tab2_accY))

    

