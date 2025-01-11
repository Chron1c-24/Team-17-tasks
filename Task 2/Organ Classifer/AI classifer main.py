import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, Label, Button

# Check if GPU is available
device = torch.device("cpu")

# Define Classes
class_names = ['brain', 'heart', 'limbs', 'Liver']  # Replace with actual class names

# Define Transforms (same as used during training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load Pre-trained ResNet Model and Modify
def load_pretrained_model(num_classes):
    # Load a pre-trained ResNet18 model
    model = models.resnet18(pretrained=True)
    
    # Freeze all layers except the final layer
    for param in model.parameters():
        param.requires_grad = False
    
    # Modify the last fully connected layer to match the number of classes
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    model = model.to(device)
    model.eval()  # Set the model to evaluation mode
    
    return model

# Function to Load Model Weights
def load_model_weights(model, model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    return model

# Initialize Model
model = load_pretrained_model(len(class_names))

# Load Model Weights
model_path = 'organ_classifier.pth'  # Path to your saved weights
model = load_model_weights(model, model_path)

# Function to Make Predictions
def predict(image_path, model, transform):
    # Open the image file
    image = Image.open(image_path).convert('RGB')
    
    # Preprocess the image
    image = transform(image).unsqueeze(0)  # Add batch dimension
    image = image.to(device)
    
    # Make prediction
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        predicted_class = class_names[predicted.item()]
    
    return predicted_class

# GUI Application
class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Medical Image Classifier")
        self.root.geometry("600x400")
        
        self.label = Label(root, text="Choose an image to classify the organ")
        self.label.pack(pady=20)
        
        self.result_label = Label(root, text="", font=("Arial", 16))
        self.result_label.pack(pady=20)
        
        self.image_label = Label(root)
        self.image_label.pack()
        
        self.load_button = Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

    def load_image(self):
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            # Load and display the image
            image = Image.open(file_path)
            image = image.resize((224, 224))
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.config(image=photo)
            self.image_label.image = photo
            
            # Predict the organ
            predicted_organ = predict(file_path, model, transform)
            self.result_label.config(text=f"Predicted Organ: {predicted_organ}")

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
