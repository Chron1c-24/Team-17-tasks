# Multi-Planar Viewer with 3D Visualization

The **Multi-Planar Viewer** is a Python-based medical imaging application that provides interactive visualization of medical image data in axial, sagittal, and coronal slices, along with a 3D volumetric view. Users can interact with the viewer to adjust brightness/contrast, zoom/pan, perform cine playback, and much more.

## Features

- **2D Slices Viewer:**
  - Display of axial, sagittal, and coronal views of the loaded medical image.
  - Adjustable contrast and brightness with sliders.
  - Zoom and pan functionality with mouse interactions.
  - Crosshair synchronization for multi-slice navigation.
  - Cine playback for sequential slice viewing.
- **3D Volume Visualization:**
  - Real-time rendering of volumetric data using VTK.
  - Adjustable opacity and color transfer functions.
- **User-Friendly Interface:**
  - PyQt5-powered GUI for ease of interaction.
  - Full-screen display for a comprehensive visualization experience.
- **Instructions Popup:**
  - Displays usage instructions on startup for first-time users.

## Prerequisites

Ensure the following Python libraries are installed before running the application:

- PyQt5
- vtk
- numpy
- matplotlib

You can install the dependencies using pip:
```bash
pip install PyQt5 vtk numpy matplotlib
```

## Installation

1. Clone or download the repository containing this script.
2. Navigate to the directory of the script.
3. Run the script:
```bash
python multiplanar_viewer.py
```

## Usage

1. Load a VTK image file (e.g., `.vtk`, `.vtp`) to initialize the viewer.
2. Interact with the 2D slices using the following controls:
   - **Mouse Scroll:** Navigate through slices.
   - **Right Mouse Button Drag:** Adjust zoom by dragging vertically.
   - **Middle Mouse Button Drag:** Pan across the image.
   - **Sliders:** Adjust contrast and brightness.
   - **Playback Buttons:**
     - **Play:** Start cine playback.
     - **Pause:** Pause cine playback.
     - **Stop/Reset:** Stop playback and reset to the middle slice.
   - **Zoom Reset:** Reset zoom and panning to default.
3. View 3D data on the volumetric visualization panel in the bottom-left corner.

## GUI Components

### Controls Panel
- **Zoom Reset Button:** Resets zoom and pan for all views.
- **Playback Controls:** Play, Pause, and Stop/Reset buttons for cine playback.
- **Cine View Selection:** Dropdown to select the view for cine playback.
- **Brightness/Contrast Sliders:** Allows dynamic adjustment of brightness and contrast.

### Display Panels
- **Top Panel:** Displays axial and sagittal slices.
- **Bottom Panel:** Displays the coronal slice and 3D view.

## Interactive Instructions

An informational popup appears on startup, detailing the interaction methods:

- **Mouse Controls:**
  - Zoom and pan using mouse buttons.
  - Crosshair navigation for synchronized slice updates.
- **Sliders:** Use the contrast and brightness sliders to optimize visualization.

## Acknowledgments

This viewer leverages the powerful combination of PyQt5, Matplotlib, and VTK to deliver an efficient visualization solution for medical imaging data. Special thanks to the communities behind these libraries for their continuous development and support.

## Future Enhancements

- Support for additional image formats (e.g., DICOM).
- Enhanced 3D rendering capabilities with advanced segmentation options.
- Inclusion of measurement tools for clinical applications.

## License

This project is open-source and freely available for non-commercial use under the MIT license.

---
Enjoy exploring and visualizing your medical image data with the Multi-Planar Viewer!
