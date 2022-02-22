# Delivery Detector 

## Project Overview
The delivery detector is a complete assembly for users who want more protection regarding their deliveries. Our system is for single and multiple users to keep track of their deliveries and keep them secured. Users can add their information, like phone number and email, to receive various alerts and updates from the Delivery Detector. The Delivery Detector will feature a secure lock-box that can interface with an android device or a raspberry pi to run the client detection software. The client software will interact with a Delivery Detector server, through RESTful APIs, to complete all the event handling. 

Users will download client code which includes a user interface for configuring various parameters and setting up their account. Client software will send the data, through API calls, to the server for setting up their delivery settings. These settings can be updated at any time and the lock-box can be configured for more than one user. Once the essential settings are set by the user, the devices can be placed in the Delivery Detector box. The devices will run the detector client software and constantly stay looking for deliveries. 

The raspberry pi model will utilize the PiCamera for various detections and observations. Our system will use the OpenCV computer vision library for making critical observations of the delivery and the surroundings of the physical box. When a delivery person needs to drop a package off, they must use a certified Delivery Detector RFID or NFC card to unlock the box. The client software will then use the devices camera, and potentially other sensors, to verify that the package was delivered. It will then make API calls so the server can send the correct alerts to the account users. The camera will be utilized to make sure the package stays safe while inside the lock-box. Once the package has been placed in the box, the client software will verify that the package stays in it’s correct spot by using the camera module. If something goes wrong, or the box is successfully picked up by the user, the client software will use an API call to let the server know it must handle the event and send an alert. Below is a high-level diagram that illustrates this feature. 

## How To Run HelloWorld
- Make sure you have python(3+) and pip installed on your machine
- Open up a terminal window to download the required libraries
- Type **pip install django** to download django
- Type **pip install djangorestframework** to download the REST framework
- Within the terminal, cd to a directory to store this project
- Type **git clone https://github.com/Capstone-Projects-2022-Spring/project-delivery-detector.git** to clone the repo
- Type **cd project-delivery-detector** 
- Type **git pull origin HelloWorld** to pull the code from the HelloWorld branch
- Type **python manage.py runserver 0.0.0.0:8000** to start the development server
- You can access the server from a web broswer using local host or the machine's public LAN ip. 

## Example API call using curl
![example API call using curl](https://github.com/Capstone-Projects-2022-Spring/project-delivery-detector/blob/HelloWorld/screenshots/curl%20example.png)

## Contributors
Lewis Winnemore, Abrahim Javed, John Glatts, Brandon Bolden, Maxwell Odonnell 
