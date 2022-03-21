# Type 'sudo python3 qr_code_reader.py' to run this file  
import cv2
from api_call import DeliveryDetectorBox

# QR-Code reader for the raspberry pi client device
# Will use the OpenCV library to extract the QR-Code
# Will then use the extracted data to make an API call to the server 
def read_qr_code(): 
    vid = cv2.VideoCapture(0)
    box = DeliveryDetectorBox(1)
    while (True):
        ret, image = vid.read()
        qrCodeDetector = cv2.QRCodeDetector()
        decoded_text, points, _ = qrCodeDetector.detectAndDecode(image)
        if points is not None:
            print('Extracted ' + decoded_text + ' from the image')    
            cv2.imshow("Image", image)
            cv2.waitKey(2000)
            if decoded_text != '':
                check_qr_text(box, decoded_text)
            cv2.destroyAllWindows()
        else:
            print("QR code not detected")


def check_qr_text(box, text):
    text_list = text.split('-')
    if len(text_list) > 1:
        if text_list[1] == '1':
            box.check_user_box(text_list[0]) 
            box.send_alert(text_list[0])
    else:
        box.check_user_box(text)


if __name__ == '__main__':
    read_qr_code()

