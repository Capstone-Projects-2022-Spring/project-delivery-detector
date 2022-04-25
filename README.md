![logo](https://github.com/Capstone-Projects-2022-Spring/project-delivery-detector/blob/main/Delivery%20Detector-logos_black.png)

## Project Overview
The delivery detector is a complete assembly for users who want more protection regarding their deliveries. Our system is for single and multiple users to keep track of their deliveries and keep them secured. Users can add their information, like phone number and email, to receive various alerts and updates from the Delivery Detector. The Delivery Detector will feature a secure lock-box that can interface with an android device or a raspberry pi to run the client detection software. The client software will interact with a Delivery Detector server, through RESTful APIs, to complete all the event handling. 

Users will download client code which includes a user interface for configuring various parameters and setting up their account. Client software will send the data, through API calls, to the server for setting up their delivery settings. These settings can be updated at any time and the lock-box can be configured for more than one user. Once the essential settings are set by the user, the devices can be placed in the Delivery Detector box. The devices will run the detector client software and constantly stay looking for deliveries. 

The raspberry pi model will utilize the PiCamera for various detections and observations. Our system will use the OpenCV computer vision library for making critical observations of the delivery and the surroundings of the physical box. When a delivery person needs to drop a package off, they must use a certified Delivery Detector RFID or NFC card to unlock the box. The client software will then use the devices camera, and potentially other sensors, to verify that the package was delivered. It will then make API calls so the server can send the correct alerts to the account users. The camera will be utilized to make sure the package stays safe while inside the lock-box. Once the package has been placed in the box, the client software will verify that the package stays in it’s correct spot by using the camera module. If something goes wrong, or the box is successfully picked up by the user, the client software will use an API call to let the server know it must handle the event and send an alert. Below is a high-level diagram that illustrates this feature. 

## How to Run Program:

Package Recipient:
 So, working with the mindset that we are the user that has ordered and is receiving the package. So, the recipient would buy something online and them opt for the DeliveryDetector method to get their package. Once that is done, they would be redirected to the SellerPortal Website (http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/)![Website Homepage] 

![Website Homepage](https://user-images.githubusercontent.com/78056542/164817066-61b261f0-1aeb-4458-ac4f-60e33e6c5e8f.jpg)

, where they will need to make a username and password login for an account. In this process, they will need to input either or both their email and phone number to be contacted when the box has activity. 

![Website Sign-up](https://user-images.githubusercontent.com/78056542/164817214-3a62a3c1-0403-4d5d-a565-178ab010d61b.jpg)

 Once that is done, the “company” would send out a designated Delivery Detector Locker box to be set up by the consumer. This will require the user to use the website to connect the locker box to the appropriate Wi-Fi information and a reliable power source for it to work. Once that is complete, the user will be ready to enlist the services of DeliveryDetector. 

Looking from the other side of the interaction, with the delivery person’s point of view, they would also be given special credentials in the form of a QR code that would be sent for them to access the locker box to drop off the package. Their QR code would only work once to open and drop off the package in one interaction. If they were to reuse that QR code, an alert would be sent out to the recipient and even the landlord if they are set up as well. 

The final side of the interaction is the person who is selling the item and is shipping it using the DeliveryDetector service to facilitate that. They would go onto the website and create a sellers account where they will input similar information as a buyer i.e., username, legal name, phone number, email. 

![Website SellersPortal](https://user-images.githubusercontent.com/78056542/165021184-e6adb958-8408-4033-ac29-b059a3d79dbf.jpg)

Once that is done, they will be sent a QR code to be affixed to the package they are shipping out’s box. The seller would then go to their own locker box, scan the QR code on the box, and then place the package to be picked up by the delivery person in the box. 


## Contributors
Lewis Winnemore, Abrahim Javed, John Glatts, Brandon Bolden, Maxwell O'Donnell 
