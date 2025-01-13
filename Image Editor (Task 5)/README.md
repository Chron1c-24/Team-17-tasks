# Image Quality Viewer

## Overview

Image Quality Viewer is a Python-based GUI application designed for visualizing and enhancing images, as well as measuring image quality metrics like Signal-to-Noise Ratio (SNR) and Contrast-to-Noise Ratio (CNR). Built using PyQt5 and OpenCV, this application offers various features for image manipulation, quality assessment, and transformation.

## Features

- **Image Viewing**:
  - Load and display images in input and output viewports.
  - View histograms for image intensity distributions.
- **Image Quality Measurement**:
  - Measure Signal-to-Noise Ratio (SNR) and Contrast-to-Noise Ratio (CNR) via user-selected regions of interest (ROIs).
- **Image Manipulation**:
  - Apply noise types (Gaussian Noise, Salt & Pepper, Speckle Noise).
  - Use various denoising filters (Gaussian Filter, Median Filter, Bilateral Filter).
  - Enhance contrast with Histogram Equalization, CLAHE, and Gamma Correction.
  - Adjust brightness and contrast.
  - Apply high-pass and low-pass filters.
- **Image Transformation**:
  - Zoom in and out using predefined scales and interpolation methods (Nearest Neighbor, Linear, Bilinear, Cubic).

## Requirements

- Python 3.x
- Required Python libraries:
  - PyQt5
  - OpenCV
  - Matplotlib
  - NumPy

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies:
   ```bash
   pip install PyQt5 opencv-python matplotlib numpy
   ```
3. Run the application:
   ```bash
   python <script_name>.py
   ```

## How to Use

1. **Load an Image**:
   - Click on "Load Image" and select an image file.
2. **Choose an Active Viewport**:
   - Use the dropdown under "Active Viewport" to select the target viewport (Input, Output 1, or Output 2).
3. **View Histograms**:
   - Click "Show Histogram" under the respective viewport to view the image intensity distribution.
4. **Measure SNR and CNR**:
   - Select the "Measure SNR/CNR" button and follow the prompts to draw ROIs for measurement.
5. **Apply Noise and Filters**:
   - Select noise or denoising methods from the "SNR" group and apply them.
6. **Enhance Contrast and Adjust Settings**:
   - Use contrast enhancement options or sliders for brightness and contrast in the "CNR" group.
7. **Zoom and Transform**:
   - Choose a zoom factor and interpolation method under "Resolution", and apply them to the image.

## Code Architecture

- **`ImageViewer`**** class**: Implements the main application logic using PyQt5.
- **Modules**:
  - `cv2`: For image processing.
  - `PyQt5.QtWidgets`: For building the graphical interface.
  - `PyQt5.QtGui` and `PyQt5.QtCore`: For handling image rendering and application logic.
  - `matplotlib.pyplot`: For histogram visualization.
  - `numpy`: For numerical operations like adding noise.
- **Main Functions**:
  - `load_image`: Loads and displays an image.
  - `show_histogram`: Displays histograms for grayscale intensity.
  - `select_roi`: Measures SNR and CNR via user-selected ROIs.
  - `apply_noise`: Adds noise to the image.
  - `apply_denoising`: Applies selected filters to denoise the image.
  - `enhance_contrast`: Enhances image contrast with specified methods.
  - `adjust_brightness_contrast`: Dynamically adjusts brightness and contrast.
  - `apply_zoom`: Applies zoom transformations using interpolation.

## Example Images

Add screenshots or descriptions of typical image transformations and results for better understanding.

## License

This project is released under the MIT License.

## Acknowledgments

This application utilizes libraries such as OpenCV, PyQt5, NumPy, and Matplotlib to offer a seamless and interactive image processing experience.
