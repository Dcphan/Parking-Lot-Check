import cv2
from ultralytics import YOLO
import easyocr



class PlateRecognizerModel:

    # Constructor and Private Attributes

    def __init__(self, model, image_path):
        self.__model = YOLO(model) # Load YOLO model
        self.image_path = image_path 
        self.image = self.load_image()
        self.__results = self.__model(self.image) # Get results from YOLO
        self.__OCR = easyocr.Reader(['en'], gpu=False)
    
    # Methods
    def load_image(self):
        return cv2.imread(self.image_path)

    def get_boxes_and_names(self):
        for result in self.__results:
            return result.boxes, result.names
        return [], []

    def find_license_plate_box(self, target_name="License_Plate"):
        boxes, names = self.get_boxes_and_names()
        plate_positions = []

        for box in boxes:
            for cls in box.cls:
                if names[cls.item()] == target_name:
                    plate_positions.append(box.xyxy.tolist())

        return plate_positions

    def crop_plate(self, coords):
        x1, y1, x2, y2 = [int(coord) for coord in coords]
        return self.image[y1:y2, x1:x2]

    def recognize_text(self, cropped_image):
        result = self.__OCR.readtext(cropped_image)
        if result:
            text = result[0][1].replace(" ", "")
            return text
        return ""
    
    def display_crop(self, image):
        plate_boxes = self.find_license_plate_box()
        if not plate_boxes:
            print("No license plate found.")
            return

        plate_coords = plate_boxes[0][0]  # Take first detected plate
        cropped_plate = self.crop_plate(plate_coords)
        self.display_image(cropped_plate, "Cropped Plate")

    def display_image(self, image, window_name="Image"):
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def text(self):
        plate_boxes = self.find_license_plate_box()
        if not plate_boxes:
            print("No license plate found.")
            return

        plate_coords = plate_boxes[0][0]  # Take first detected plate
        cropped_plate = self.crop_plate(plate_coords)
        plate_text = self.recognize_text(cropped_plate)

        return plate_text
