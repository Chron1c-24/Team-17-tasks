import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QSlider,
                             QGroupBox, QMessageBox)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Quality Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self.input_image = None
        self.output1_image = None
        self.output2_image = None
        self.current_viewport = 1  # 1 for output1, 2 for output2

        self.init_ui()

    def get_current_image(self):
        viewport_selector = {
            "Input": self.input_image,
            "Output 1": self.output1_image,
            "Output 2": self.output2_image
        }
        return viewport_selector.get(self.viewport_combo.currentText())

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()

        # Image display area
        display_layout = QHBoxLayout()

        # Input viewport
        input_group = QGroupBox("Input Image")
        input_layout = QVBoxLayout()
        self.input_label = QLabel()
        self.input_label.setMinimumSize(300, 300)

        # Add histogram button for input
        self.input_hist_btn = QPushButton("Show Histogram")
        self.input_hist_btn.clicked.connect(lambda: self.show_histogram(self.input_image))
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_hist_btn)
        input_group.setLayout(input_layout)

        # Output1 viewport
        output1_group = QGroupBox("Output 1")
        output1_layout = QVBoxLayout()
        self.output1_label = QLabel()
        self.output1_label.setMinimumSize(300, 300)

        # Add histogram button for output1
        self.output1_hist_btn = QPushButton("Show Histogram")
        self.output1_hist_btn.clicked.connect(lambda: self.show_histogram(self.output1_image))
        output1_layout.addWidget(self.output1_label)
        output1_layout.addWidget(self.output1_hist_btn)
        output1_group.setLayout(output1_layout)

        # Output2 viewport
        output2_group = QGroupBox("Output 2")
        output2_layout = QVBoxLayout()
        self.output2_label = QLabel()
        self.output2_label.setMinimumSize(300, 300)

        # Add histogram button for output2
        self.output2_hist_btn = QPushButton("Show Histogram")
        self.output2_hist_btn.clicked.connect(lambda: self.show_histogram(self.output2_image))
        output2_layout.addWidget(self.output2_label)
        output2_layout.addWidget(self.output2_hist_btn)
        output2_group.setLayout(output2_layout)

        display_layout.addWidget(input_group)
        display_layout.addWidget(output1_group)
        display_layout.addWidget(output2_group)

        # Controls area
        controls_layout = QVBoxLayout()  # Define controls_layout here

        # Add viewport selector at the top of controls
        viewport_group = QGroupBox("Active Viewport")
        viewport_layout = QVBoxLayout()

        self.viewport_combo = QComboBox()
        self.viewport_combo.addItems(["Input", "Output 1", "Output 2"])
        self.viewport_combo.currentIndexChanged.connect(self.change_viewport)

        viewport_layout.addWidget(QLabel("Select Target:"))
        viewport_layout.addWidget(self.viewport_combo)
        viewport_group.setLayout(viewport_layout)
        controls_layout.addWidget(viewport_group)

        # Load image button
        load_btn = QPushButton("Load Image")
        load_btn.clicked.connect(self.load_image)
        controls_layout.addWidget(load_btn)

        # Measure SNR/CNR button
        measure_btn = QPushButton("Measure SNR/CNR")
        measure_btn.clicked.connect(self.select_roi)
        controls_layout.addWidget(measure_btn)

        # SNR controls
        snr_group = QGroupBox("SNR")
        snr_layout = QVBoxLayout()

        # Noise types
        noise_combo = QComboBox()
        noise_combo.addItems(["Gaussian Noise", "Salt & Pepper", "Speckle Noise"])
        noise_btn = QPushButton("Apply Noise")
        noise_btn.clicked.connect(lambda: self.apply_noise(noise_combo.currentText()))

        # Denoising types
        denoise_combo = QComboBox()
        denoise_combo.addItems(["Gaussian Filter", "Median Filter", "Bilateral Filter"])
        denoise_btn = QPushButton("Apply Denoising")
        denoise_btn.clicked.connect(lambda: self.apply_denoising(denoise_combo.currentText()))

        snr_layout.addWidget(QLabel("Noise Type:"))
        snr_layout.addWidget(noise_combo)
        snr_layout.addWidget(noise_btn)
        snr_layout.addWidget(QLabel("Denoising Type:"))
        snr_layout.addWidget(denoise_combo)
        snr_layout.addWidget(denoise_btn)
        snr_group.setLayout(snr_layout)
        controls_layout.addWidget(snr_group)

        # CNR controls
        cnr_group = QGroupBox("CNR")
        cnr_layout = QVBoxLayout()

        # Brightness and contrast sliders
        brightness_slider = QSlider(Qt.Horizontal)
        brightness_slider.setMinimum(-100)
        brightness_slider.setMaximum(100)
        brightness_slider.valueChanged.connect(self.adjust_brightness_contrast)

        contrast_slider = QSlider(Qt.Horizontal)
        contrast_slider.setMinimum(-100)
        contrast_slider.setMaximum(100)
        contrast_slider.valueChanged.connect(self.adjust_brightness_contrast)

        # Contrast enhancement methods
        contrast_combo = QComboBox()
        contrast_combo.addItems(["Histogram Equalization", "CLAHE", "Gamma Correction"])
        enhance_btn = QPushButton("Enhance Contrast")
        enhance_btn.clicked.connect(lambda: self.enhance_contrast(contrast_combo.currentText()))

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["lowpass", "highpass"])
        filter_btn = QPushButton("Apply Filter")
        filter_btn.clicked.connect(self.apply_highpass_filter)

        cnr_layout.addWidget(QLabel("Brightness:"))
        cnr_layout.addWidget(brightness_slider)
        cnr_layout.addWidget(QLabel("Contrast:"))
        cnr_layout.addWidget(contrast_slider)
        cnr_layout.addWidget(QLabel("Enhancement Method:"))
        cnr_layout.addWidget(contrast_combo)
        cnr_layout.addWidget(enhance_btn)
        cnr_layout.addWidget(QLabel("Add Filter:"))
        cnr_layout.addWidget(self.filter_combo)
        cnr_layout.addWidget(filter_btn)

        cnr_group.setLayout(cnr_layout)
        controls_layout.addWidget(cnr_group)

        # Combine layouts
        layout.addLayout(display_layout)
        layout.addLayout(controls_layout)
        main_widget.setLayout(layout)
        # Resolution controls
        controls_layout.addWidget(self.init_resolution_controls())

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                   "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            # Load image in BGR format (OpenCV default)
            self.input_image = cv2.imread(file_name)
            # Convert BGR to RGB for display
            self.input_image_rgb = cv2.cvtColor(self.input_image, cv2.COLOR_BGR2RGB)
            self.display_image(self.input_image_rgb, self.input_label)

    def display_image(self, image, label):
        """Display an image in a QLabel"""
        if image is None:
            return

        # Convert the image to QImage
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(q_image)
        print(f"QPixmap size: {pixmap.size()}")  # Debug statement

        # Scale the pixmap to fit the label
        scaled_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Display the pixmap in the label
        label.setPixmap(scaled_pixmap)

    def show_histogram(self, image):
        if image is None:
            return

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        plt.figure(figsize=(8, 6))

        # Plot histogram for the grayscale image
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        plt.plot(hist, color='black', label='Grayscale Channel')

        plt.title('Grayscale Image Histogram')
        plt.xlabel('Pixel Intensity')
        plt.ylabel('Count')
        plt.legend()
        plt.show()

    def change_viewport(self, index):
        self.current_viewport = index + 1  # Convert to 1-based index

    def apply_transformation(self, transformed_image):
        """Helper method to apply transformation to correct viewport"""
        if transformed_image is None:
            return

        # Convert BGR to RGB for display
        transformed_image_rgb = cv2.cvtColor(transformed_image, cv2.COLOR_BGR2RGB)

        if self.current_viewport == 1:
            self.output1_image = transformed_image
            self.display_image(transformed_image_rgb, self.output1_label)
        else:
            self.output2_image = transformed_image
            self.display_image(transformed_image_rgb, self.output2_label)

    def apply_zoom(self, factor):
        """Apply zoom with selected interpolation method"""
        if self.input_image is None:
            return

        # Get the current interpolation method
        interp_method = self.interp_combo.currentText()

        # Map interpolation methods to OpenCV constants
        interpolation_map = {
            "Nearest Neighbor": cv2.INTER_NEAREST,
            "Linear": cv2.INTER_LINEAR,
            "Bilinear": cv2.INTER_LINEAR,  # OpenCV's bilinear is same as linear
            "Cubic": cv2.INTER_CUBIC
        }

        # Get interpolation method from map
        interpolation = interpolation_map.get(interp_method, cv2.INTER_LINEAR)

        # Calculate new dimensions
        scale = float(factor.replace('x', ''))

        # Get source image based on viewport
        source_image = self.input_image if self.current_viewport == 1 else self.output1_image
        if source_image is None:
            return

        height, width = source_image.shape[:2]
        new_height, new_width = int(height * scale), int(width * scale)

        # Apply resize with selected interpolation method
        resized = cv2.resize(source_image,
                             (new_width, new_height),
                             interpolation=interpolation)

        self.apply_transformation(resized)

    def init_resolution_controls(self):
        """Initialize resolution controls"""
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QVBoxLayout()

        # Zoom controls
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["0.5x", "1x", "2x", "4x"])
        self.zoom_combo.currentTextChanged.connect(self.apply_zoom)

        # Interpolation method
        self.interp_combo = QComboBox()  # Make it a class attribute
        self.interp_combo.addItems(["Nearest Neighbor", "Linear", "Bilinear", "Cubic"])

        # Add info labels
        resolution_layout.addWidget(QLabel("Zoom Factor:"))
        resolution_layout.addWidget(self.zoom_combo)
        resolution_layout.addWidget(QLabel("Interpolation Method:"))
        resolution_layout.addWidget(self.interp_combo)

        # Add Apply Zoom Button
        apply_zoom_btn = QPushButton("Apply Zoom")
        apply_zoom_btn.clicked.connect(lambda: self.apply_zoom(self.zoom_combo.currentText()))
        resolution_layout.addWidget(apply_zoom_btn)

        resolution_group.setLayout(resolution_layout)
        return resolution_group

    def apply_noise(self, noise_type):
        # Get source image based on viewport
        source_image = self.input_image if self.current_viewport == 1 else self.output1_image
        if source_image is None:
            return

        if noise_type == "Gaussian Noise":
            noise = np.random.normal(0, 25, source_image.shape).astype(np.uint8)
            noisy = cv2.add(source_image, noise)
        elif noise_type == "Salt & Pepper":
            noisy = source_image.copy()
            prob = 0.05
            thresh = 1 - prob
            rnd = np.random.random(source_image.shape[:2])
            noisy[rnd < prob] = 0
            noisy[rnd > thresh] = 255
        else:  # Speckle noise
            noise = np.random.normal(0, 1, source_image.shape[:2])
            noise = np.repeat(noise[:, :, np.newaxis], 3, axis=2)
            noisy = source_image + source_image * noise
            noisy = np.clip(noisy, 0, 255).astype(np.uint8)

        self.apply_transformation(noisy)

    def apply_denoising(self, filter_type):
        # Get source image based on viewport
        source_image = self.input_image if self.current_viewport == 1 else self.output1_image
        if source_image is None:
            return

        if filter_type == "Gaussian Filter":
            filtered = cv2.GaussianBlur(source_image, (5, 5), 0)
        elif filter_type == "Median Filter":
            filtered = cv2.medianBlur(source_image, 5)
        else:  # Bilateral Filter
            filtered = cv2.bilateralFilter(source_image, 9, 75, 75)

        self.apply_transformation(filtered)

    def enhance_contrast(self, method):
        # Get source image based on viewport
        source_image = self.input_image if self.current_viewport == 1 else self.output1_image
        if source_image is None:
            return

        if method == "Histogram Equalization":
            channels = cv2.split(source_image)
            eq_channels = [cv2.equalizeHist(ch) for ch in channels]
            enhanced = cv2.merge(eq_channels)
        elif method == "CLAHE":
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            channels = cv2.split(source_image)
            eq_channels = [clahe.apply(ch) for ch in channels]
            enhanced = cv2.merge(eq_channels)
        else:  # Gamma Correction
            gamma = 1.5
            lookup_table = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)]).astype(np.uint8)
            enhanced = cv2.LUT(source_image, lookup_table)

        self.apply_transformation(enhanced)

    def adjust_brightness_contrast(self):
        # Get source image based on viewport
        source_image = self.input_image if self.current_viewport == 1 else self.output1_image
        if source_image is None:
            return

        brightness = self.sender().value() if isinstance(self.sender(), QSlider) else 0
        contrast = self.sender().value() if isinstance(self.sender(), QSlider) else 0

        adjusted = cv2.convertScaleAbs(source_image,
                                       alpha=1 + contrast / 100,
                                       beta=brightness)
        self.apply_transformation(adjusted)

    def apply_highpass_filter(self):
        """Apply lowpass or highpass filter to the image"""
        # Get source image based on viewport
        source_image = self.get_current_image()
        if source_image is None:
            return

        # Convert to grayscale for filtering
        gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)

        # Get filter type (assuming filter_combo is saved as self.filter_combo in init_ui)
        filter_type = self.filter_combo.currentText()

        if filter_type == "lowpass":
            # Apply Gaussian blur for lowpass
            result = cv2.GaussianBlur(gray, (5, 5), 0)
        else:  # highpass
            # Apply Laplacian filter for better high-pass filtering
            kernel_size = 3
            result = cv2.Laplacian(gray, cv2.CV_64F, ksize=kernel_size)
            # Convert back to uint8 and normalize
            result = np.absolute(result)
            result = np.uint8(np.clip(result, 0, 255))

        # Convert back to BGR for display
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

        # Apply the transformation to the correct viewport
        self.apply_transformation(result)

    def select_roi(self):
        """Allow user to select ROIs and calculate SNR/CNR measurements for grayscale images"""
        # Get the current image based on viewport selection
        source_image = self.get_current_image()

        if source_image is None:
            QMessageBox.warning(self, "Warning",
                                f"No image available in {self.viewport_combo.currentText()} viewport!")
            return

        # Convert image to grayscale
        gray_image = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)

        # Instructions for the user
        QMessageBox.information(self, "ROI Selection Instructions",
                                f"Measuring {self.viewport_combo.currentText()} viewport:\n\n"
                                "1. Select signal ROI (object of interest)\n"
                                "2. Press ENTER to confirm\n"
                                "3. Select background/noise ROI\n"
                                "4. Press ENTER to confirm\n"
                                "5. Press ESC to finish selection")

        # Create a copy for display
        display_image = gray_image.copy()

        # Select first ROI (signal)
        roi1 = cv2.selectROI("Select Signal ROI", display_image, showCrosshair=True)
        if roi1 == (0, 0, 0, 0):
            cv2.destroyAllWindows()
            return

        # Draw the first ROI on the image
        cv2.rectangle(display_image,
                      (int(roi1[0]), int(roi1[1])),
                      (int(roi1[0] + roi1[2]), int(roi1[1] + roi1[3])),
                      255, 2)

        # Select second ROI (background/noise)
        roi2 = cv2.selectROI("Select Background/Noise ROI", display_image, showCrosshair=True)
        cv2.destroyAllWindows()

        if roi2 == (0, 0, 0, 0):
            return

        # Extract ROIs from grayscale image
        signal_roi = gray_image[int(roi1[1]):int(roi1[1] + roi1[3]),
                     int(roi1[0]):int(roi1[0] + roi1[2])]
        background_roi = gray_image[int(roi2[1]):int(roi2[1] + roi2[3]),
                         int(roi2[0]):int(roi2[0] + roi2[2])]

        # Calculate signal statistics
        signal_mean = np.mean(signal_roi)
        signal_std = np.std(signal_roi)

        # Calculate background statistics
        background_mean = np.mean(background_roi)
        background_std = np.std(background_roi)

        # Calculate SNR and CNR
        snr = signal_mean / background_std if background_std > 0 else float('inf')
        cnr = abs(signal_mean - background_mean) / background_std if background_std > 0 else float('inf')

        # Format results message
        message = f"Measurements for {self.viewport_combo.currentText()}:\n\n"
        message += "Grayscale Metrics:\n"
        message += f"Signal Mean: {signal_mean:.2f}\n"
        message += f"Signal Std: {signal_std:.2f}\n"
        message += f"Background Mean: {background_mean:.2f}\n"
        message += f"Background Std: {background_std:.2f}\n"
        message += f"SNR: {snr:.2f}\n"
        message += f"CNR: {cnr:.2f}"

        # Display results
        QMessageBox.information(self, "SNR and CNR Measurements", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
