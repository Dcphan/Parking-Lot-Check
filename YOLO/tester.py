from model import PlateRecognizerModel

class Tester: 
    def __init__(self, model, image):
        self.recognizer = PlateRecognizerModel(model, image)
    
    def menu(self):
        print("1. Recognize text")
        print("2. Display image")
        print("3. Display cropped plate")
        print("4. Exit")

        while True:
            choice = input("Enter choice: ")
            if choice == "1":
                self.recognizer.text()
            elif choice == "2":
                self.recognizer.display_image(self.recognizer.image)
            elif choice == "3":
                self.recognizer.display_crop(self.recognizer.image)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    Tester("platedetection.pt", "plate.jpg").menu()