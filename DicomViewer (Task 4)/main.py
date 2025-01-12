import os
import pydicom
import random
import string
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QTextEdit, \
    QFileDialog, QGridLayout, QSlider
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
# Anonymization Function
def anonymize_tag(tag_value, prefix):
    return prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=6))

class DICOMViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DICOM Viewer")
        self.layout = QVBoxLayout()
        self.dicom_data = None
        self.dicom_files = []
        self.current_file_index = 0
        self.image_timer = QTimer(self)
        self.image_timer.timeout.connect(self.update_video_frame)
        self.current_video_frame = 0
        self.image_data_3d = None
        self.image_grid = QGridLayout()
        self.is_folder_view = False

        self.slice_slider = None
        self.current_slice_label = QLabel("Slice Range Start: -", self)
        self.slices_per_grid = 4
        self.init_ui()

    def init_ui(self):
        # Add load folder button
        self.load_folder_button = QPushButton("Load DICOM Folder", self)
        self.load_folder_button.clicked.connect(self.load_dicom_folder)

        self.load_button = QPushButton("Load DICOM File", self)
        self.load_button.clicked.connect(self.load_dicom)

        self.prefix_input = QLineEdit(self)
        self.prefix_input.setPlaceholderText("Enter anonymization prefix")

        self.search_input = QLineEdit(self)  # Search input field
        self.search_input.setPlaceholderText("Search tag keyword...")

        self.search_button = QPushButton("Search Tags", self)  # Search button
        self.search_button.clicked.connect(self.search_tags)

        self.anonymize_button = QPushButton("Anonymize File", self)
        self.anonymize_button.clicked.connect(self.anonymize_dicom)

        self.patient_button = QPushButton("Patient Info", self)
        self.patient_button.clicked.connect(self.display_patient_info)

        self.study_button = QPushButton("Study Info", self)
        self.study_button.clicked.connect(self.display_study_info)

        self.modality_button = QPushButton("Modality Info", self)
        self.modality_button.clicked.connect(self.display_modality_info)

        self.physician_button = QPushButton("Physician Info", self)
        self.physician_button.clicked.connect(self.display_physician_info)

        self.image_button = QPushButton("Image Info", self)
        self.image_button.clicked.connect(self.display_image_info)

        self.all_tags_button = QPushButton("Show All Tags", self)
        self.all_tags_button.clicked.connect(self.display_all_tags)

        self.play_button = QPushButton("Play Video", self)
        self.play_button.clicked.connect(self.play_video)

        self.stop_button = QPushButton("Stop Video", self)
        self.stop_button.clicked.connect(self.stop_video)

        self.dicom_info_text = QTextEdit(self)
        self.dicom_info_text.setReadOnly(True)

        # Navigation buttons for folder view
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.clicked.connect(self.show_previous_page)
        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.show_next_page)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)

        # Layout for buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.load_folder_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.prefix_input)
        button_layout.addWidget(self.search_input)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.anonymize_button)
        button_layout.addWidget(self.patient_button)
        button_layout.addWidget(self.study_button)
        button_layout.addWidget(self.modality_button)
        button_layout.addWidget(self.physician_button)
        button_layout.addWidget(self.image_button)
        button_layout.addWidget(self.all_tags_button)
        button_layout.addWidget(self.current_slice_label)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addLayout(nav_layout)

        self.slice_slider = QSlider(Qt.Horizontal, self)
        self.slice_slider.setMinimum(0)
        self.slice_slider.valueChanged.connect(self.update_displayed_grid)
        self.slice_slider.setVisible(False)
        button_layout.addWidget(self.slice_slider)

        # Layout for DICOM info and image display
        display_layout = QHBoxLayout()
        display_layout.addWidget(self.dicom_info_text)
        display_layout.addLayout(self.image_grid)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addLayout(display_layout)
        self.setLayout(main_layout)

        # Initialize navigation buttons state
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Update the state of navigation buttons based on current view"""
        has_files = len(self.dicom_files) > 0 if self.is_folder_view else False
        self.prev_button.setEnabled(has_files and self.current_file_index > 0)
        self.next_button.setEnabled(
            has_files and self.current_file_index + self.slices_per_grid < len(self.dicom_files))

    def clear_all_data(self):
        """Clear all loaded data and reset the viewer state"""
        try:
            # Stop any ongoing timers
            if self.image_timer.isActive():
                self.image_timer.stop()

            # Clear the image grid first
            self.clear_image_display()

            # Reset all data
            self.dicom_data = None
            self.dicom_files.clear()
            self.current_file_index = 0
            self.image_data_3d = None

            # Clear UI elements
            self.dicom_info_text.clear()
            self.current_slice_label.setText("Slice Range Start: -")

            if self.slice_slider:
                self.slice_slider.setVisible(False)
                self.slice_slider.setValue(0)

            self.is_folder_view = False

            # Update navigation buttons
            self.update_navigation_buttons()

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def clear_image_display(self):
        """Safely clear the image grid"""
        try:
            while self.image_grid.count():
                item = self.image_grid.takeAt(0)
                widget = item.widget()
                if widget is not None:  # Check if widget exists
                    widget.setParent(None)
                    widget.deleteLater()

        except Exception as e:
            print(f"Error clearing image display: {e}")

    def display_all_tags(self):
        if not self.dicom_data:
            print("No DICOM file loaded.")
            return

        all_tags = ""
        for elem in self.dicom_data:
            if elem.keyword == "PixelData":
                continue
            if elem.keyword and elem.value:
                all_tags += f"{elem.tag} - {elem.name}: {elem.value}\n"


        self.dicom_info_text.setText(all_tags)

    def load_dicom_folder(self):
        try:
            # Clear existing data first
            self.clear_all_data()

            folder_path = QFileDialog.getExistingDirectory(self, "Select DICOM Folder")
            if folder_path:
                # Load all DICOM files from the folder
                for filename in os.listdir(folder_path):
                    if filename.endswith('.dcm'):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            dicom_data = pydicom.dcmread(file_path)
                            self.dicom_files.append(dicom_data)
                        except Exception as e:
                            print(f"Error loading {filename}: {e}")

                if self.dicom_files:
                    self.is_folder_view = True
                    self.display_folder_images()
                    print(f"Loaded {len(self.dicom_files)} DICOM files")
                else:
                    print("No DICOM files found in the selected folder")

                self.update_navigation_buttons()
        except Exception as e:
            print(f"Error loading folder: {e}")

    def show_previous_page(self):
        if self.dicom_files:
            self.current_file_index = max(0, self.current_file_index - self.slices_per_grid)
            self.display_folder_images()

    def show_next_page(self):
        if self.dicom_files:
            max_index = len(self.dicom_files) - self.slices_per_grid
            self.current_file_index = min(max_index, self.current_file_index + self.slices_per_grid)
            self.display_folder_images()

    def display_folder_images(self):
        if not self.dicom_files:
            return

        self.clear_image_display()
        rows = cols = int(np.sqrt(self.slices_per_grid))

        for i in range(self.slices_per_grid):
            file_index = self.current_file_index + i
            if file_index < len(self.dicom_files):
                dicom_data = self.dicom_files[file_index]
                if 'PixelData' in dicom_data:
                    image_data = dicom_data.pixel_array

                    # Handle different image types
                    if len(image_data.shape) > 2:
                        if len(image_data.shape) == 3 and image_data.shape[2] <= 4:
                            image_data = image_data[:, :, 0]
                        else:
                            image_data = image_data[0] if len(image_data.shape) > 2 else image_data

                    # Normalize and convert to uint8
                    if image_data.dtype != np.uint8:
                        image_data = ((image_data - image_data.min()) /
                                      (image_data.max() - image_data.min()) * 255).astype(np.uint8)

                    # Create QImage and display
                    qimage = QImage(image_data.data, image_data.shape[1], image_data.shape[0],
                                    image_data.shape[1], QImage.Format_Grayscale8)
                    label = QLabel(self)
                    pixmap = QPixmap.fromImage(qimage)
                    label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
                    self.image_grid.addWidget(label, i // cols, i % cols)

        # Update navigation buttons
        self.prev_button.setEnabled(self.current_file_index > 0)
        self.next_button.setEnabled(self.current_file_index + self.slices_per_grid < len(self.dicom_files))

    def load_dicom(self):
        try:
            # Clear existing data first
            self.clear_all_data()

            dicom_file, _ = QFileDialog.getOpenFileName(self, "Open DICOM File", "", "DICOM Files (*.dcm)")
            if dicom_file:
                self.dicom_data = pydicom.dcmread(dicom_file)
                self.display_patient_info()
                self.display_image()
                self.update_navigation_buttons()
        except Exception as e:
            print(f"Error loading file: {e}")

    def display_patient_info(self):
        if not self.dicom_data:
            return

        # Extract patient-related info
        patient_info = ""
        if 'PatientName' in self.dicom_data:
            patient_info += f"Patient Name: {self.dicom_data.PatientName}\n"
        if 'PatientID' in self.dicom_data:
            patient_info += f"Patient ID: {self.dicom_data.PatientID}\n"
        if 'PatientBirthDate' in self.dicom_data:
            patient_info += f"Patient Birth Date: {self.dicom_data.PatientBirthDate}\n"
        if 'PatientSex' in self.dicom_data:
            patient_info += f"Patient Sex: {self.dicom_data.PatientSex}\n"

        self.dicom_info_text.setText(patient_info)

    def display_study_info(self):
        if not self.dicom_data:
            return

        # Extract study-related info
        study_info = ""
        if 'StudyInstanceUID' in self.dicom_data:
            study_info += f"Study Instance UID: {self.dicom_data.StudyInstanceUID}\n"
        if 'StudyDate' in self.dicom_data:
            study_info += f"Study Date: {self.dicom_data.StudyDate}\n"
        if 'StudyTime' in self.dicom_data:
            study_info += f"Study Time: {self.dicom_data.StudyTime}\n"
        if 'AccessionNumber' in self.dicom_data:
            study_info += f"Accession Number: {self.dicom_data.AccessionNumber}\n"

        self.dicom_info_text.setText(study_info)

    def display_modality_info(self):
        if not self.dicom_data:
            return

        # Extract modality-related info
        modality_info = ""
        if 'Modality' in self.dicom_data:
            modality_info += f"Modality: {self.dicom_data.Modality}\n"
        if 'Manufacturer' in self.dicom_data:
            modality_info += f"Manufacturer: {self.dicom_data.Manufacturer}\n"
        if 'InstitutionName' in self.dicom_data:
            modality_info += f"Institution Name: {self.dicom_data.InstitutionName}\n"

        self.dicom_info_text.setText(modality_info)

    def display_physician_info(self):
        if not self.dicom_data:
            return

        # Extract physician-related info
        physician_info = ""
        if 'ReferringPhysicianName' in self.dicom_data:
            physician_info += f"Referring Physician: {self.dicom_data.ReferringPhysicianName}\n"
        if 'PhysicianOfRecord' in self.dicom_data:
            physician_info += f"Physician of Record: {self.dicom_data.PhysicianOfRecord}\n"

        self.dicom_info_text.setText(physician_info)

    def display_image_info(self):
        if not self.dicom_data or 'PixelData' not in self.dicom_data:
            print("No image data found in this DICOM file.")
            return

        # Extract image-related info
        image_info = ""
        if 'Rows' in self.dicom_data:
            image_info += f"Rows: {self.dicom_data.Rows}\n"
        if 'Columns' in self.dicom_data:
            image_info += f"Columns: {self.dicom_data.Columns}\n"
        if 'BitsAllocated' in self.dicom_data:
            image_info += f"Bits Allocated: {self.dicom_data.BitsAllocated}\n"
        if 'PhotometricInterpretation' in self.dicom_data:
            image_info += f"Photometric Interpretation: {self.dicom_data.PhotometricInterpretation}\n"

        self.dicom_info_text.setText(image_info)

    def display_image(self):
        if not self.dicom_data or 'PixelData' not in self.dicom_data:
            return

        image_data = self.dicom_data.pixel_array

        if len(image_data.shape) == 4:  # Multi-frame (time series) with potential color data
            self.image_data_3d = image_data[:, :, :, 0] if image_data.shape[3] <= 4 else image_data[:, :, :, 0]
            self.play_video(self.image_data_3d)
        elif len(image_data.shape) == 3:
            if image_data.shape[2] <= 4:  # 3D Color image
                self.display_single_image(image_data[:, :, 0])
            else:  # Multi-frame grayscale
                self.image_data_3d = image_data
                self.display_tiles(image_data)
        else:  # 2D grayscale
            self.display_single_image(image_data)

    def display_single_image(self, image_data):
        if image_data.dtype != np.uint8:
            image_data = ((image_data - image_data.min()) /
                          (image_data.max() - image_data.min()) * 255).astype(np.uint8)

        height, width = image_data.shape
        qimage = QImage(image_data.data, width, height, width, QImage.Format_Grayscale8)

        label = QLabel(self)
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))

        self.clear_image_display()
        self.image_grid.addWidget(label, 0, 0)

    def display_tiles(self, image_data):
        if len(image_data.shape) != 3:
            return

        num_slices = image_data.shape[0]
        self.image_data_3d = image_data

        max_start_index = max(0, num_slices - self.slices_per_grid)
        self.slice_slider.setMaximum(max_start_index)
        self.slice_slider.setSingleStep(1)
        self.slice_slider.setValue(0)
        self.slice_slider.setVisible(num_slices > 1)

        self.update_displayed_grid(0)

    def update_displayed_grid(self, start_slice_idx):
        if self.image_data_3d is None:
            return

        image_data = self.image_data_3d
        num_slices = image_data.shape[0]
        rows = 2
        cols = 2 if num_slices > 1 else 1
        self.slices_per_grid = rows * cols

        self.clear_image_display()

        end_slice_idx = min(start_slice_idx + self.slices_per_grid, num_slices)
        self.current_slice_label.setText(f"Slice Range: {start_slice_idx} to {end_slice_idx - 1}")

        slice_idx = start_slice_idx
        for r in range(rows):
            for c in range(cols):
                if slice_idx < end_slice_idx:
                    slice_data = image_data[slice_idx]
                    if slice_data.dtype != np.uint8:
                        slice_data = ((slice_data - slice_data.min()) /
                                      (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)

                    qimage = QImage(slice_data.data, slice_data.shape[1], slice_data.shape[0],
                                    slice_data.shape[1], QImage.Format_Grayscale8)

                    label = QLabel(self)
                    pixmap = QPixmap.fromImage(qimage)
                    label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
                    self.image_grid.addWidget(label, r, c)
                    slice_idx += 1

    def play_video(self, _=None):
        """Starts playing video from the 3D array of frames."""
        if self.image_data_3d is None or len(self.image_data_3d.shape) != 3:
            print("No valid video frames loaded.")
            return

        # Reset current frame if playing again
        self.current_video_frame = 0

        # Stop timer if it is already running
        if self.image_timer.isActive():
            self.image_timer.stop()

        # Normalize pixel values for consistent display
        video_frames = self.image_data_3d
        if video_frames.dtype != np.uint8:
            video_frames = ((video_frames - video_frames.min()) /
                            (video_frames.max() - video_frames.min()) * 255).astype(np.uint8)

        self.image_data_3d = video_frames  # Update data for playback
        self.image_timer.start(100)  # Set frame rate (milliseconds)

    def stop_video(self):
        """Stop the video playback."""
        if self.image_timer.isActive():
            self.image_timer.stop()

    def update_video_frame(self):
        """Update the video frame for playback."""
        if self.image_data_3d is None:
            return

        num_frames = self.image_data_3d.shape[0]

        # Check if all frames have been displayed
        if self.current_video_frame >= num_frames:
            self.stop_video()  # Stop the video once all frames are shown
            return

        frame_data = self.image_data_3d[self.current_video_frame]

        if frame_data.dtype != np.uint8:
            frame_data = ((frame_data - frame_data.min()) /
                          (frame_data.max() - frame_data.min()) * 255).astype(np.uint8)

        qimage = QImage(frame_data.data, frame_data.shape[1], frame_data.shape[0],
                        frame_data.shape[1], QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)

        # Clear current grid and display the frame
        self.clear_image_display()
        label = QLabel(self)
        label.setPixmap(pixmap.scaled(800, 800, Qt.KeepAspectRatio))
        self.image_grid.addWidget(label, 0, 0)

        # Increment frame counter
        self.current_video_frame = (self.current_video_frame + 1) % num_frames

    def anonymize_dicom(self):
        if not self.dicom_data:
            print("No DICOM file loaded.")
            return

        prefix = self.prefix_input.text()
        if not prefix:
            print("Please enter a prefix for anonymization.")
            return

        # Anonymize critical tags
        for tag in ['PatientName', 'PatientID', 'PhysicianName']:
            if tag in self.dicom_data:
                self.dicom_data.data_element(tag).value = anonymize_tag(self.dicom_data.data_element(tag).value, prefix)

        # Update the displayed tags after anonymization
        self.display_patient_info()

        # Save the anonymized file
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Anonymized DICOM File", "", "DICOM Files (*.dcm)")
        if save_path:
            try:
                self.dicom_data.save_as(save_path)
                print(f"Anonymized DICOM file saved to: {save_path}")
            except Exception as e:
                print(f"Error saving anonymized file: {e}")

    def search_tags(self):
        """Search for tags containing the entered keyword."""
        if not self.dicom_data:
            print("No DICOM file loaded.")
            return

        keyword = self.search_input.text().strip().lower()
        if not keyword:
            self.dicom_info_text.setText("Please enter a keyword to search.")
            return

        matching_tags = ""
        for elem in self.dicom_data:
            if elem.keyword and keyword in elem.keyword.lower():
                matching_tags += f"{elem.tag} - {elem.name}: {elem.value}\n"

        if matching_tags:
            self.dicom_info_text.setText(matching_tags)
        else:
            self.dicom_info_text.setText("No matching tags found.")

if __name__ == "__main__":
    app = QApplication([])
    viewer = DICOMViewer()
    viewer.show()
    app.exec_()
