import cv2
import numpy as np
from ultralytics import YOLO
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading


class PlayerTracker:
    def __init__(self, video_path):
        # Initialize YOLO model
        self.model = YOLO('yolov8n-seg.pt')

        # Video capture
        self.cap = cv2.VideoCapture(video_path)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0

        # Player tracking data
        self.player_positions = defaultdict(list)
        self.cumulative_positions = defaultdict(list)  # Maintain cumulative positions
        self.next_player_id = 0
        self.player_tracks = {}

        # Processing control
        self.processing = True
        self.paused = False

        # Create football pitch background
        self.pitch_background = self.create_pitch_background()

    def create_pitch_background(self):
        """Create a football pitch background image"""
        pitch = np.ones((self.frame_height, self.frame_width, 3)) * np.array([34, 139, 34]) / 255

        line_color = (1, 1, 1)
        line_thickness = 2

        cv2.rectangle(pitch, (50, 50), (self.frame_width - 50, self.frame_height - 50), line_color, line_thickness)
        cv2.line(pitch,
                 (self.frame_width // 2, 50),
                 (self.frame_width // 2, self.frame_height - 50),
                 line_color,
                 line_thickness)
        cv2.circle(pitch,
                   (self.frame_width // 2, self.frame_height // 2),
                   70,
                   line_color,
                   line_thickness)

        pen_width = 160
        pen_height = 320
        cv2.rectangle(pitch,
                      (50, (self.frame_height - pen_height) // 2),
                      (50 + pen_width, (self.frame_height + pen_height) // 2),
                      line_color,
                      line_thickness)
        cv2.rectangle(pitch,
                      (self.frame_width - 50 - pen_width, (self.frame_height - pen_height) // 2),
                      (self.frame_width - 50, (self.frame_height + pen_height) // 2),
                      line_color,
                      line_thickness)

        goal_width = 60
        goal_height = 160
        cv2.rectangle(pitch,
                      (50, (self.frame_height - goal_height) // 2),
                      (50 + goal_width, (self.frame_height + goal_height) // 2),
                      line_color,
                      line_thickness)
        cv2.rectangle(pitch,
                      (self.frame_width - 50 - goal_width, (self.frame_height - goal_height) // 2),
                      (self.frame_width - 50, (self.frame_height + goal_height) // 2),
                      line_color,
                      line_thickness)

        return pitch

    def seek_to_frame(self, frame_number):
        """Seek to a specific frame in the video"""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame = frame_number

    def process_frame(self, frame):
        """Process a single frame and track players"""
        results = self.model(frame, classes=0)
        processed_frame = frame.copy()
        current_positions = []

        if len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                boxes = result.boxes.cpu().numpy()
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    current_positions.append((center_x, center_y))
                    player_id = self.assign_player_id(center_x, center_y)
                    self.player_positions[player_id].append((center_x, center_y))
                    self.cumulative_positions[player_id].append((center_x, center_y))  # Store cumulative position

                    cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(processed_frame, f"Player {player_id}",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 2)

        self.update_tracks(current_positions)
        return processed_frame, list(self.player_positions.keys())

    def assign_player_id(self, x, y, max_distance=100):
        """Assign player ID based on proximity to existing tracks"""
        min_dist = float('inf')
        closest_id = None

        for player_id, positions in self.player_tracks.items():
            if positions:
                last_x, last_y = positions[-1]
                dist = np.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
                if dist < min_dist and dist < max_distance:
                    min_dist = dist
                    closest_id = player_id

        if closest_id is None:
            closest_id = self.next_player_id
            self.next_player_id += 1
            self.player_tracks[closest_id] = []

        self.player_tracks[closest_id].append((x, y))
        return closest_id

    def update_tracks(self, current_positions):
        """Update active tracks"""
        for player_id in list(self.player_tracks.keys()):
            if len(self.player_tracks[player_id]) > 30:
                self.player_tracks[player_id] = self.player_tracks[player_id][-30:]


class TrackerGUI:
    def __init__(self, video_path=None):
        self.root = tk.Tk()
        self.root.title("Football Player Tracking")

        # Initialize tracker with default or provided video path
        self.video_path = video_path
        self.tracker = None

        # Processing control
        self.is_playing = False

        # Setup GUI
        self.setup_gui()

        # If video path provided, start processing
        if video_path:
            self.load_video(video_path)

    def setup_gui(self):
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # File selection button
        file_frame = ttk.Frame(container)
        file_frame.pack(fill='x', pady=5)

        ttk.Button(file_frame, text="Open Video File", command=self.choose_file).pack(side='left', padx=5)

        # Video frame
        video_frame = ttk.Frame(container)
        video_frame.pack(side='left', padx=5)

        self.video_label = ttk.Label(video_frame)
        self.video_label.pack()

        # Video controls
        control_frame = ttk.Frame(video_frame)
        control_frame.pack(pady=5, fill='x')

        # Play/Pause button
        self.play_pause_btn = ttk.Button(control_frame, text="Play", command=self.toggle_play_pause)
        self.play_pause_btn.pack(side='left', padx=5)

        # Frame slider
        self.frame_slider = ttk.Scale(
            control_frame,
            from_=0,
            to=100,  # Will be updated when video is loaded
            orient='horizontal',
            command=self.slider_changed
        )
        self.frame_slider.pack(side='left', fill='x', expand=True, padx=5)

        # Frame counter label
        self.frame_label = ttk.Label(control_frame, text="Frame: 0/0")
        self.frame_label.pack(side='left', padx=5)

        # Player selection
        player_control_frame = ttk.Frame(video_frame)
        player_control_frame.pack(pady=5)

        ttk.Label(player_control_frame, text="Select Player:").pack(side='left', padx=5)
        self.player_var = tk.StringVar()
        self.player_var.trace('w', self.update_heatmap)
        self.player_dropdown = ttk.Combobox(
            player_control_frame,
            textvariable=self.player_var,
            state='readonly',
            width=15
        )
        self.player_dropdown.pack(side='left', padx=5)

        # Heatmap
        heatmap_frame = ttk.Frame(container)
        heatmap_frame.pack(side='right', padx=5)

        self.fig = Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=heatmap_frame)
        self.canvas.get_tk_widget().pack()

    def choose_file(self):
        """Open file dialog to choose video file"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mkv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_video(file_path)

    def load_video(self, video_path):
        """Load a new video file"""
        # Stop current processing if any
        if self.tracker:
            self.tracker.processing = False
            if hasattr(self, 'processing_thread'):
                self.processing_thread.join()

        # Initialize new tracker
        self.tracker = PlayerTracker(video_path)

        # Update slider range
        self.frame_slider.configure(to=self.tracker.total_frames - 1)

        # Reset play state
        self.is_playing = False
        self.play_pause_btn.configure(text="Play")

        # Start processing
        self.start_processing()

    def toggle_play_pause(self):
        """Toggle between play and pause states"""
        self.is_playing = not self.is_playing
        self.play_pause_btn.configure(text="Pause" if self.is_playing else "Play")
        if self.is_playing:
            self.tracker.paused = False
        else:
            self.tracker.paused = True

    def slider_changed(self, value):
        """Handle slider value change"""
        if self.tracker:
            frame_number = int(float(value))
            self.tracker.seek_to_frame(frame_number)
            self.frame_label.configure(text=f"Frame: {frame_number}/{self.tracker.total_frames - 1}")
            self.update_heatmap()  # Update heatmap when changing frames

    def update_video(self, frame):
        """Update video display"""
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (800, 600))
            image = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image=image)
            self.video_label.configure(image=photo)
            self.video_label.image = photo

    def update_player_list(self, player_ids):
        """Update player dropdown list"""
        current_values = self.player_dropdown['values']
        new_values = [f"Player {pid}" for pid in sorted(player_ids)]
        if new_values != current_values:
            self.player_dropdown['values'] = new_values
            if not self.player_var.get() and new_values:
                self.player_dropdown.set(new_values[0])

    def update_heatmap(self, *args):
        """Update heatmap for selected player"""
        try:
            self.fig.clear()
            self.ax = self.fig.add_subplot(111)

            player_str = self.player_var.get()
            if not player_str:
                return

            player_id = int(player_str.split()[-1])
            positions = self.tracker.cumulative_positions[player_id]  # Get cumulative positions

            if not positions:
                return

            self.ax.imshow(self.tracker.pitch_background)

            x_pos = [p[0] for p in positions]
            y_pos = [p[1] for p in positions]

            # Create a histogram for the heatmap
            heatmap, xedges, yedges = np.histogram2d(
                x_pos,
                y_pos,
                bins=50,
                range=[[0, self.tracker.frame_width], [0, self.tracker.frame_height]]
            )

            # No smoothing applied, just use the raw histogram
            extent = [0, self.tracker.frame_width, self.tracker.frame_height, 0]
            self.ax.imshow(heatmap.T, extent=extent, alpha=0.6, cmap='hot')

            self.ax.set_title(f'Player {player_id} Movement Heatmap')
            self.ax.set_xlabel('X Position')
            self.ax.set_ylabel('Y Position')

            self.fig.colorbar(self.ax.images[-1], label='Density')

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"Error updating heatmap: {e}")

    def process_video(self):
        """Process video frames"""
        while self.tracker.processing:
            if not self.tracker.paused and self.is_playing:
                ret, frame = self.tracker.cap.read()
                if not ret:
                    self.is_playing = False
                    self.play_pause_btn.configure(text="Play")
                    break

                processed_frame, player_ids = self.tracker.process_frame(frame)

                # Update frame slider
                self.tracker.current_frame += 1
                self.frame_slider.set(self.tracker.current_frame)
                self.frame_label.configure(text=f"Frame: {self.tracker.current_frame}/{self.tracker.total_frames - 1}")

                # Update GUI
                self.root.after(0, self.update_video, processed_frame)
                self.root.after(0, self.update_player_list, player_ids)

            self.root.update()  # Allow GUI to remain responsive
            self.root.after(10)  # Small delay to prevent excessive CPU usage

        self.tracker.cap.release()

    def start_processing(self):
        """Start video processing in separate thread"""
        self.processing_thread = threading.Thread(target=self.process_video)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    app = TrackerGUI()
    app.run()


if __name__ == "__main__":
    main()