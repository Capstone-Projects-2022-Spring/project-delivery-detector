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
            num_points = len(points)
            points = points.astype(int)
            for i in range(num_points):
                next_point_index = (i+1) % num_points
                cv2.line(image, tuple(points[i][0]), tuple(points[next_point_index][0]), (255,0,0), 5)
            print('Extracted ' + decoded_text + ' from the image')    
            cv2.imshow("Image", image)
            cv2.waitKey(2000)
            if decoded_text != '':
                box.check_user_box(decoded_text) 
            cv2.destroyAllWindows()
        else:
            print("QR code not detected")



if __name__ == '__main__':
    read_qr_code()

