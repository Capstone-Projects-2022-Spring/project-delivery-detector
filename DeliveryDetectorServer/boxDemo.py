
boxes= {
    "0" : 0,
    "1" : 0,
    "2" : 0,
    "3" : 0
    }
    
orders = []


def createOrderRecord(list, box):
    orderRecord = {
            "Order_Name" : list[0],
            "Order_Number": list[1],
            "Box": box
            }
    return orderRecord
def findVacantBox():
    if boxes["0"] == 0:
        return 0
    elif boxes["1"] == 0:
        return 1
    elif boxes["2"] == 0:
        return 2
    elif boxes["3"] == 0:
        return 3
    else:
        return None

def deposite(list):
    if(list[2] == "1"):
        box = findVacantBox()
        if box != None:
            orderRecord = createOrderRecord(list, box)
            orders.append(orderRecord)
            boxes[str(box)] = 1
            print(list[0] + " package delivered")
        else:
            print("Box is full, sorry " + list[0])
    else:
        print("I think you have a pickup code bud")

        
def pickUp(list):
    if( list[2] == "0"):
        for order in orders:
            if(list[1] == order["Order_Number"]):
                if(list[0] == order["Order_Name"]):
                    print("opening box number: " + str(order["Box"]))
                    boxes[str(order["Box"])] = 0
                    orders.remove(order)
                    return
        print("Order number not recognized")
    else:
        ("I think you have a delivery code bud")

def main():
    delivery_order1 = [ "John" , "1","1"]
    delivery_order2 = [ "Max", "2", "1"]
    delivery_order3 = [ "Lewis" , "3", "1"]
    delivery_order4 = [ "Brandon" , "4", "1"]
    delivery_order5 = [ "Abe", "5", "1"]
    delivery_order6 = [ "Charlie", "6", "1"]

    pickup_order1 = [ "John" , "1", "0"]
    pickup_order2 = [ "Max", "2","0"]
    pickup_order3 = [ "Lewis" , "3","0"]
    pickup_order4 = [ "Brandon" , "4","0"]
    pickup_order5 = [ "Abe", "5","0"]
    pickup_order6 = [ "Charlie", "6","0"]

    
#Deposite 4 packages
    deposite(delivery_order1)
    deposite(delivery_order2)
    deposite(delivery_order3)
    deposite(delivery_order4)
    
#Attempt to deposite 5
    deposite(delivery_order5)

#Pickup one making space
    pickUp(pickup_order1)
    
#Attempt to deposite 5 ( Abe )
    deposite(delivery_order5)

#John Attempts to use code to pickup twice
    deposite(pickup_order1)
    pickUp(pickup_order1)

    print(boxes)
    for order in orders:
        print(order)

main()




            
