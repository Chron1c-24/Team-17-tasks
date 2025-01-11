import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QHBoxLayout, \
    QComboBox, QLabel, QMessageBox, QSizePolicy, QSlider
from PyQt5.QtCore import QTimer, Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import vtkmodules.util.numpy_support as numpy_support


class MultiPlanarViewer(QMainWindow):
    def __init__(self, image):

        super().__init__()

        # Convert VTK image to numpy array
        vtk_array = image.GetPointData().GetScalars()
        self.image = numpy_support.vtk_to_numpy(vtk_array)

        # Reshape the numpy array to match the image dimensions (z, y, x)
        dims = image.GetDimensions()
        self.image = self.image.reshape(dims[2], dims[1], dims[0])
        self.image_shape = self.image.shape

        # Initialize slice indices
        self.axial_slice = self.image_shape[0] // 2
        self.coronal_slice = self.image_shape[1] // 2
        self.sagittal_slice = self.image_shape[2] // 2

        # Initialize panning
        self.panning = False
        self.pan_start = None
        self.pan_axes = {'axial': [0, 0], 'coronal': [0, 0], 'sagittal': [0, 0]}

        # Set up the UI
        self.setWindowTitle('Multi-Planar Viewer with 3D Visualization')
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        # Create top panel for axial and sagittal slices
        self.top_panel = QWidget()
        self.top_layout = QHBoxLayout(self.top_panel)

        # Create bottom panel for 3D view and coronal slice
        self.bottom_panel = QWidget()
        self.bottom_layout = QHBoxLayout(self.bottom_panel)

        # Create the figure and canvas for the 2D views
        self.fig = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.fig)

        # Create the control buttons (Zoom Reset, Play, Pause, Stop)
        self.zoom_reset_button = QPushButton("Reset Zoom/panning")
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop/Reset")

        # Combo box for selecting the view for cine playback
        self.cine_view_combo = QComboBox()
        self.cine_view_combo.addItems(["Axial", "Coronal", "Sagittal"])
        self.cine_view_combo.setCurrentText("Axial")  # Default selection

        # Connect buttons to their respective functions
        self.zoom_reset_button.clicked.connect(self.reset_zoom)
        self.play_button.clicked.connect(self.start_cine)
        self.pause_button.clicked.connect(self.pause_cine)
        self.stop_button.clicked.connect(self.stop_cine)

        # Add controls to a layout
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Cine View: "))
        control_layout.addWidget(self.cine_view_combo)
        control_layout.addWidget(self.zoom_reset_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)

        self.layout.addLayout(control_layout)

        # Create VTK widget for 3D visualization
        self.vtk_widget = QVTKRenderWindowInteractor(self.bottom_panel)

        # Add widgets to layouts
        self.top_layout.addWidget(self.canvas)

        # Create a container for the 3D view
        self.vtk_container = QWidget()
        self.vtk_container_layout = QVBoxLayout(self.vtk_container)
        self.vtk_container_layout.addWidget(self.vtk_widget)

        # Add 3D view container and coronal slice to bottom layout
        self.bottom_layout.addWidget(self.vtk_container)
        self.bottom_layout.addWidget(self.canvas)

        # Set size policies
        self.vtk_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add panels to main layout
        self.layout.addWidget(self.top_panel)
        self.layout.addWidget(self.bottom_panel)

        # Set main widget layout
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        #full screenwindowed
        self.showMaximized()

        # Initialize cine playback state
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cine_step)

        # Connect events for 2D views
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # Initialize contrast, brightness, and zoom adjustment
        self.adjusting = False
        self.adjust_start = None
        self.contrast = 0.1
        self.brightness = 0.0
        self.zoom_factor = {'axial': 1, 'coronal': 1, 'sagittal': 1}

        # Create contrast slider
        self.contrast_slider = QSlider()
        self.contrast_slider.setOrientation(Qt.Horizontal)
        self.contrast_slider.setRange(1, 500)  # Adjust the range as needed
        self.contrast_slider.setValue(int(self.contrast * 100))
        self.contrast_slider.valueChanged.connect(self.update_contrast)
        self.contrast_slider.setFixedWidth(200)

        # Create brightness slider
        self.brightness_slider = QSlider()
        self.brightness_slider.setOrientation(Qt.Horizontal)
        self.brightness_slider.setRange(-500, 100)  # Adjust the range as needed
        self.brightness_slider.setValue(int(self.brightness * 1000))
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        self.brightness_slider.setFixedWidth(200)

        # Add labels for the sliders
        self.contrast_label = QLabel(f"Contrast: {self.contrast:.2f}")
        self.brightness_label = QLabel(f"Brightness: {self.brightness:.2f}")

        # Add sliders to layout
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(QLabel("Contrast"))
        slider_layout.addWidget(self.contrast_slider)
        slider_layout.addWidget(self.contrast_label)

        slider_layout.addWidget(QLabel("Brightness"))
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(self.brightness_label)

        # Add sliders layout to main layout
        self.layout.addLayout(slider_layout)

        # Show description popup on startup without blocking the viewer
        self.show_description_popup()

    def update_contrast(self, value):
        """Update the contrast based on slider value."""
        self.contrast = value / 100.0
        self.contrast_label.setText(f"Contrast: {self.contrast:.2f}")
        self.plot_images()  # Re-draw the images with updated contrast

    def update_brightness(self, value):
        """Update the brightness based on slider value."""
        self.brightness = value / 100.0
        self.brightness_label.setText(f"Brightness: {self.brightness:.2f}")
        self.plot_images()  # Re-draw the images with updated brightness

    def show_description_popup(self):
        """Show a non-blocking pop-up with description information."""
        description_text = ("This is a multi-planar viewer. You can view Axial, Coronal, and Sagittal slices "
                            "of the loaded medical image.\n\n"
                            "Instructions:\n"
                            "- Adjust brightness/contrast by moving the sliders to the write and to the left.\n"
                            "- Zoom in/out by moving the mouse vertically while holding mouse right click.\n"
                            "- Panning by moving the mouse while holding the mousewheel button.\n"
                            "- Scroll through slices with mouse wheel.")

        # Create a non-modal message box to show alongside the viewer
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Viewer Instructions")
        message_box.setText(description_text)
        message_box.setStandardButtons(QMessageBox.Ok)

        # Display the message box
        message_box.show()

        # Initial plot
        self.plot_images()

        # Set up 3D visualization
        self.setup_3d_visualization()

    def setup_3d_visualization(self):
        # Normalize the image data to 0-255 range
        image_normalized = ((self.image - self.image.min()) / (self.image.max() - self.image.min()) * 255).astype(
            np.uint8)

        # Create VTK data from the image
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(self.image_shape[::-1])  # VTK uses x,y,z order
        vtk_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

        # Copy data to VTK image
        vtk_array = vtk_image.GetPointData().GetScalars()
        vtk_array.SetNumberOfTuples(image_normalized.size)
        vtk_array.SetVoidArray(image_normalized.ravel(), image_normalized.size, 1)

        # Create volume mapper
        volume_mapper = vtk.vtkSmartVolumeMapper()
        volume_mapper.SetInputData(vtk_image)

        # Create volume property
        volume_property = vtk.vtkVolumeProperty()
        volume_property.SetInterpolationTypeToLinear()

        # Set up opacity function
        opacity_function = vtk.vtkPiecewiseFunction()
        opacity_function.AddPoint(0, 0.0)
        opacity_function.AddPoint(128, 0.5)
        opacity_function.AddPoint(255, 1.0)
        volume_property.SetScalarOpacity(opacity_function)

        # Set up color function
        color_function = vtk.vtkColorTransferFunction()
        color_function.AddRGBPoint(0, 0.0, 0.0, 0.0)
        color_function.AddRGBPoint(128, 0.5, 0.5, 0.5)
        color_function.AddRGBPoint(255, 1.0, 1.0, 1.0)
        volume_property.SetColor(color_function)

        # Create volume
        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)

        # Adjust the 3D view to fit in the bottom-left corner
        self.vtk_widget.GetRenderWindow().SetSize(400, 400)  # Adjust size as needed
        self.vtk_container.setMaximumSize(400, 400)  # Adjust size as needed

        # Set up renderer and render window
        renderer = vtk.vtkRenderer()
        renderer.AddVolume(volume)
        renderer.ResetCamera()

        self.vtk_widget.GetRenderWindow().AddRenderer(renderer)
        self.vtk_widget.GetRenderWindow().Render()

        # Set up interactor
        self.vtk_interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.vtk_interactor.Initialize()
        self.vtk_interactor.Start()

    def reset_zoom(self):
        """Resets the zoom factor/panning for all views."""
        self.zoom_factor = {'axial': 1, 'coronal': 1, 'sagittal': 1}
        self.pan_axes = {'axial': [0, 0], 'coronal': [0, 0], 'sagittal': [0, 0]}
        self.plot_images()

    def start_cine(self):
        """Start cine playback."""
        self.timer.start(100)  # Play at a speed of 10 frames per second

    def pause_cine(self):
        """Pause cine playback."""
        self.timer.stop()

    def stop_cine(self):
        """Stop cine playback and reset to the middle slice."""
        self.timer.stop()
        self.axial_slice = self.image_shape[0] // 2
        self.coronal_slice = self.image_shape[1] // 2
        self.sagittal_slice = self.image_shape[2] // 2
        self.plot_images()

    def cine_step(self):
        """Advance the cine playback by one slice based on the selected view."""
        selected_view = self.cine_view_combo.currentText()

        if selected_view == "Axial":
            self.axial_slice = (self.axial_slice + 1) % self.image_shape[0]  # Loop through axial slices
        elif selected_view == "Coronal":
            self.coronal_slice = (self.coronal_slice + 1) % self.image_shape[1]  # Loop through coronal slices
        elif selected_view == "Sagittal":
            self.sagittal_slice = (self.sagittal_slice + 1) % self.image_shape[2]  # Loop through sagittal slices

        self.plot_images()

    def on_mouse_press(self, event):
        if event.button == 3:  # Right mouse button
            self.adjusting = True
            self.adjust_start = (event.x, event.y)
        elif event.button == 1 and event.inaxes:  # Left mouse button
            self.update_crosshair(event)
        elif event.button == 2:  # mousewheel button
            self.panning = True
            self.pan_start = (event.x, event.y)

    def on_mouse_release(self, event):
        if event.button == 3:  # Right mouse button
            self.adjusting = False
        elif event.button == 2:  # mousewheel mouse button
            self.panning = False

    def on_mouse_move(self, event):
        if self.adjusting and event.inaxes:
            # Calculate changes based on mouse movement
            dx = event.x - self.adjust_start[0]
            dy = event.y - self.adjust_start[1]

            # Adjust zoom (vertical movement)
            zoom_speed = 0.01
            zoom_change = 1 + dy * zoom_speed

            if event.inaxes == self.axial_ax:
                self.zoom_factor['axial'] *= zoom_change
            elif event.inaxes == self.coronal_ax:
                self.zoom_factor['coronal'] *= zoom_change
            elif event.inaxes == self.sagittal_ax:
                self.zoom_factor['sagittal'] *= zoom_change

            # Update the adjustment start position
            self.adjust_start = (event.x, event.y)
            self.plot_images()

        elif self.panning and event.inaxes:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]

            if event.inaxes == self.axial_ax:
                self.pan_axes['axial'][0] -= dx / self.zoom_factor['axial']
                self.pan_axes['axial'][1] += dy / self.zoom_factor['axial']
            elif event.inaxes == self.coronal_ax:
                self.pan_axes['coronal'][0] -= dx / self.zoom_factor['coronal']
                self.pan_axes['coronal'][1] += dy / self.zoom_factor['coronal']
            elif event.inaxes == self.sagittal_ax:
                self.pan_axes['sagittal'][0] -= dx / self.zoom_factor['sagittal']
                self.pan_axes['sagittal'][1] += dy / self.zoom_factor['sagittal']

            self.pan_start = (event.x, event.y)
            self.plot_images()

        elif event.inaxes and event.button == 1:  # Left mouse button
            self.update_crosshair(event)

    def update_crosshair(self, event):
        if event.inaxes == self.axial_ax:
            self.coronal_slice = self.image_shape[1] - int(event.ydata)
            self.sagittal_slice = self.image_shape[2] - int(event.xdata)
        elif event.inaxes == self.coronal_ax:
            self.axial_slice = self.image_shape[0] - int(event.ydata)
            self.sagittal_slice = self.image_shape[2] - int(event.xdata)
        elif event.inaxes == self.sagittal_ax:
            self.axial_slice = self.image_shape[0] - int(event.ydata)
            self.coronal_slice = self.image_shape[1] - int(event.xdata)

        # Ensure slice indices are within bounds
        self.axial_slice = np.clip(self.axial_slice, 0, self.image_shape[0] - 1)
        self.coronal_slice = np.clip(self.coronal_slice, 0, self.image_shape[1] - 1)
        self.sagittal_slice = np.clip(self.sagittal_slice, 0, self.image_shape[2] - 1)

        self.plot_images()

    def on_scroll(self, event):
        if event.inaxes:
            if event.inaxes == self.axial_ax:
                self.axial_slice = np.clip(self.axial_slice + (1 if event.button == 'up' else -1), 0,
                                           self.image_shape[0] - 1)
            elif event.inaxes == self.coronal_ax:
                self.coronal_slice = np.clip(self.coronal_slice + (1 if event.button == 'up' else -1), 0,
                                             self.image_shape[1] - 1)
            elif event.inaxes == self.sagittal_ax:
                self.sagittal_slice = np.clip(self.sagittal_slice + (1 if event.button == 'up' else -1), 0,
                                              self.image_shape[2] - 1)
            self.plot_images()

    def apply_contrast_brightness(self, image):
        """Apply contrast and brightness adjustments to the image."""
        return np.clip((image - image.min()) * self.contrast + self.brightness, 0, 255).astype(np.uint8)

    def plot_images(self):
        self.fig.clear()

        # Apply contrast and brightness to the images
        axial_image = self.apply_contrast_brightness(np.rot90(self.image[self.axial_slice, :, :], 2))
        coronal_image = self.apply_contrast_brightness(np.rot90(self.image[:, self.coronal_slice, :], 2))
        sagittal_image = self.apply_contrast_brightness(np.rot90(self.image[:, :, self.sagittal_slice], 2))

        # Define custom layout
        self.axial_ax = self.fig.add_subplot(221)  # Top left
        self.sagittal_ax = self.fig.add_subplot(222)  # Top right
        self.coronal_ax = self.fig.add_subplot(224)  # Bottom right

        # Set background color to black
        self.axial_ax.set_facecolor('black')
        self.sagittal_ax.set_facecolor('black')
        self.coronal_ax.set_facecolor('black')

        # Plot axial slice
        self.axial_ax.imshow(axial_image, cmap='gray', extent=[0, axial_image.shape[1], axial_image.shape[0], 0])
        center_x = axial_image.shape[1] / 2 + self.pan_axes['axial'][0]
        center_y = axial_image.shape[0] / 2 + self.pan_axes['axial'][1]
        self.axial_ax.set_xlim(center_x - axial_image.shape[1] / (2 * self.zoom_factor['axial']),
                               center_x + axial_image.shape[1] / (2 * self.zoom_factor['axial']))
        self.axial_ax.set_ylim(center_y + axial_image.shape[0] / (2 * self.zoom_factor['axial']),
                               center_y - axial_image.shape[0] / (2 * self.zoom_factor['axial']))
        self.axial_ax.axhline(axial_image.shape[0] - self.coronal_slice, color='b', linestyle='--')
        self.axial_ax.axvline(axial_image.shape[1] - self.sagittal_slice, color='b', linestyle='--')
        self.axial_ax.set_title(f'Axial Slice {self.axial_slice}')
        self.axial_ax.set_xticks([])
        self.axial_ax.set_yticks([])

        # Plot sagittal slice (similar changes as axial)
        self.sagittal_ax.imshow(sagittal_image, cmap='gray',
                                extent=[0, sagittal_image.shape[1], sagittal_image.shape[0], 0])
        center_x = sagittal_image.shape[1] / 2 + self.pan_axes['sagittal'][0]
        center_y = sagittal_image.shape[0] / 2 + self.pan_axes['sagittal'][1]
        self.sagittal_ax.set_xlim(center_x - sagittal_image.shape[1] / (2 * self.zoom_factor['sagittal']),
                                  center_x + sagittal_image.shape[1] / (2 * self.zoom_factor['sagittal']))
        self.sagittal_ax.set_ylim(center_y + sagittal_image.shape[0] / (2 * self.zoom_factor['sagittal']),
                                  center_y - sagittal_image.shape[0] / (2 * self.zoom_factor['sagittal']))
        self.sagittal_ax.axhline(sagittal_image.shape[0] - self.axial_slice, color='b', linestyle='--')
        self.sagittal_ax.axvline(sagittal_image.shape[1] - self.coronal_slice, color='b', linestyle='--')
        self.sagittal_ax.set_title(f'Sagittal Slice {self.sagittal_slice}')
        self.sagittal_ax.set_xticks([])
        self.sagittal_ax.set_yticks([])

        # Plot coronal slice (similar changes as axial)
        self.coronal_ax.imshow(coronal_image, cmap='gray',
                               extent=[0, coronal_image.shape[1], coronal_image.shape[0], 0])
        center_x = coronal_image.shape[1] / 2 + self.pan_axes['coronal'][0]
        center_y = coronal_image.shape[0] / 2 + self.pan_axes['coronal'][1]
        self.coronal_ax.set_xlim(center_x - coronal_image.shape[1] / (2 * self.zoom_factor['coronal']),
                                 center_x + coronal_image.shape[1] / (2 * self.zoom_factor['coronal']))
        self.coronal_ax.set_ylim(center_y + coronal_image.shape[0] / (2 * self.zoom_factor['coronal']),
                                 center_y - coronal_image.shape[0] / (2 * self.zoom_factor['coronal']))
        self.coronal_ax.axhline(coronal_image.shape[0] - self.axial_slice, color='b', linestyle='--')
        self.coronal_ax.axvline(coronal_image.shape[1] - self.sagittal_slice, color='b', linestyle='--')
        self.coronal_ax.set_title(f'Coronal Slice {self.coronal_slice}')
        self.coronal_ax.set_xticks([])
        self.coronal_ax.set_yticks([])

        # Update the canvas
        self.fig.tight_layout()
        self.canvas.draw()


def load_image():
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Select NIfTI File", "",
                                               "NIfTI Files (*.nii *.nii.gz);;All Files ()",
                                               options=options)
    if file_path:
        try:
            reader = vtk.vtkNIFTIImageReader()
            reader.SetFileName(file_path)
            reader.Update()  # Reads the image
            return reader.GetOutput()
        except Exception as e:
            QMessageBox.critical(None, "Error",
                                 f"Failed to load image: {str(e)} \nMake sure to select a NIfTI file format.")
            return None
    else:
        return None


def main():
    app = QApplication(sys.argv)
    image = load_image()
    if image is not None:
        try:
            viewer = MultiPlanarViewer(image)
            viewer.show()
            sys.exit(app.exec_())
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to initialize viewer: {str(e)}")
    else:
        print("No file selected or failed to load image, exiting...")


if __name__ == "__main__":
    main()