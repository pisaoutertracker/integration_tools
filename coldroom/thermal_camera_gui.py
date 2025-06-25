from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
import logging
import json
import os
import numpy as np
import yaml
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ThermalCameraTab(QtWidgets.QWidget):
    def __init__(self, system):
        super(ThermalCameraTab, self).__init__()
        self.system = system

        # Load the UI file into a QMainWindow
        self.widget = QtWidgets.QMainWindow()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "thermal_camera.ui"), self.widget)
        self.ui = self.widget  # Assign the loaded UI to self.ui

        # Initialize camera positions from config file
        self.config_file = os.path.join(os.path.dirname(__file__), "camera_config.yaml")
        self.camera_positions = self.load_camera_config()
        self.camera_fov = 20  # Field of view in degrees for each camera

        # Create layout for this widget and add the UI
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.widget)

        # Initialize matplotlib figures
        self.setup_camera_views()

        # Connect signals
        self.connect_signals()
        self.update_camera_displays()
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second

        # Disable controls until thermal camera is started
        self.enable_controls(False)
        self.mounted_modules = None

        logger.info("Thermal camera tab initialized")

    def get_camera_modules_map(self):
        if self.mounted_modules is None:
            print("Mounted modules not set, returning default camera modules map")
            return {
                "camera1": "Unknown",
                "camera2": "Unknown",
                "camera3": "Unknown",
                "camera4": "Unknown",
            }
        # For each module and camera position, get the closest module within 20 degrees
        camera_modules = {}
        absolute_position = self.get_current_system_position()
        for module_name, module_info in self.mounted_modules.items():
            module_position = module_info["angular_position"]
            module_side = module_info["side"]
            if module_side == "13":
                module_side = "Front"
            elif module_side == "24":
                module_side = "Back"
            close_camera = False
            for camera_name, camera_offset in self.camera_positions.items():
                camera_position = (absolute_position + camera_offset["position"]) % 360
                module_slot = str(module_info.get("mounted_on", "-").split(";")[1])
                if abs(module_position - camera_position) <= 20:
                    camera_modules[camera_name] = f"{module_slot};{module_name}"
                    close_camera = True
                    break
            if not close_camera:
                # Use Unknown if no close camera found
                for camera_name in self.camera_positions.keys():
                    if camera_name not in camera_modules:
                        camera_modules[camera_name] = "Unknown"
        return camera_modules

    def load_camera_config(self):
        """Load camera positions from YAML config file"""
        default_config = {
            "camera1": {"position": 0, "side": "Front"},
            "camera2": {"position": 0, "side": "Back"},
            "camera3": {"position": 180, "side": "Front"},
            "camera4": {"position": 180, "side": "Back"},
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = yaml.safe_load(f)

                # Validate the config structure
                if self.validate_camera_config(config):
                    logger.info(f"Camera config loaded from {self.config_file}")
                    return config
                else:
                    logger.warning("Invalid camera config structure, using defaults")
                    # Save default config to file
                    self.save_camera_config(default_config)
                    return default_config
            else:
                logger.info(f"Config file not found at {self.config_file}, creating with defaults")
                # Save default config to file
                self.save_camera_config(default_config)
                return default_config

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config file: {e}")
            # Save default config to file
            self.save_camera_config(default_config)
            return default_config
        except Exception as e:
            logger.error(f"Error loading camera config: {e}")
            # Save default config to file
            self.save_camera_config(default_config)
            return default_config

    def validate_camera_config(self, config):
        """Validate the camera config structure"""
        try:
            if not isinstance(config, dict):
                return False

            required_cameras = ["camera1", "camera2", "camera3", "camera4"]
            for camera in required_cameras:
                if camera not in config:
                    return False
                if not isinstance(config[camera], dict):
                    return False
                if "position" not in config[camera] or "side" not in config[camera]:
                    return False
                if not isinstance(config[camera]["position"], (int, float)):
                    return False
                if not isinstance(config[camera]["side"], str):
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False

    def save_camera_config(self, config=None):
        """Save camera positions to YAML config file"""
        try:
            if config is None:
                config = self.camera_positions

            with open(self.config_file, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False, indent=2)

            logger.info(f"Camera config saved to {self.config_file}")

        except Exception as e:
            logger.error(f"Error saving camera config: {e}")

    def setup_camera_views(self):
        """Setup matplotlib figures for camera views"""
        try:
            # Create scene and canvas for individual cameras view
            scene1 = QtWidgets.QGraphicsScene()
            self.ui.graphicsView.setScene(scene1)

            # Create matplotlib figure for individual cameras with adjusted size
            self.cameras_fig = Figure(figsize=(8, 5), dpi=100)  # Increased width
            self.cameras_canvas = FigureCanvas(self.cameras_fig)
            scene1.addWidget(self.cameras_canvas)

            # Create 2x2 grid for cameras with minimal spacing
            self.cameras_axes = self.cameras_fig.subplots(2, 2, gridspec_kw={"hspace": 0.15, "wspace": 0.1})
            self.camera_images = []

            # Initialize camera images with proper sizing
            camera_index = 0  # Add counter for sequential numbering
            for i in range(2):
                for j in range(2):
                    ax = self.cameras_axes[i, j]
                    img = ax.imshow(np.zeros((24, 32)), cmap="plasma", aspect="equal", interpolation="nearest")
                    self.camera_images.append(img)
                    camera_index += 1  # Increment for each camera
                    ax.set_title(f"Camera {camera_index}")
                    ax.set_xticks([])
                    ax.set_yticks([])

                    # Add colorbar with proper sizing
                    cbar = self.cameras_fig.colorbar(img, ax=ax, fraction=0.046, pad=0.04)
                    cbar.ax.tick_params(labelsize=8)

            # Adjust subplot parameters to remove excess whitespace
            self.cameras_fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

            # Create stitched view for each camera
            self.stitched_figs = []
            self.stitched_canvases = []
            self.stitched_images = []
            self.stitched_axes = []

            # Get the tab widget from the UI
            self.stitched_tab_widget = self.ui.findChild(QtWidgets.QTabWidget, "tabWidget")

            for graphics_view in [self.ui.graphics_1, self.ui.graphics_2, self.ui.graphics_3, self.ui.graphics_4]:
                scene = QtWidgets.QGraphicsScene()
                graphics_view.setScene(scene)

                # Create figure and canvas with proper aspect ratio for 360-degree view
                fig = Figure(figsize=(12, 3), dpi=100)
                canvas = FigureCanvas(fig)
                scene.addWidget(canvas)

                # Create axes and image
                ax = fig.add_subplot(111)
                # Initialize with a 360-degree wide array
                img = ax.imshow(
                    np.zeros((24, 360)),  # Full 360-degree width
                    cmap="plasma",
                    aspect="auto",  # Use 'auto' to fill the space
                    interpolation="nearest",
                    extent=[0, 360, 0, 24],  # Set the extent to match degrees
                )

                # Set up the axes for degrees
                # ax.set_xlabel("Angle (degrees)") ! Do not set xlabel
                ax.set_xticks(np.linspace(0, 360, 9))  # Ticks every 45 degrees
                ax.set_yticks([])

                # Add colorbar
                cbar = fig.colorbar(img, fraction=0.046, pad=0.04)
                cbar.ax.tick_params(labelsize=8)

                # Adjust subplot parameters to maximize image space
                fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)

                # Store references
                self.stitched_figs.append(fig)
                self.stitched_canvases.append(canvas)
                self.stitched_images.append(img)
                self.stitched_axes.append(ax)

            # Setup temperature plot tab
            self.setup_temperature_plot()

            logger.info("Camera views initialized")

        except Exception as e:
            logger.error(f"Error setting up camera views: {e}")

    def setup_temperature_plot(self):
        """Setup temperature plotting tab"""
        try:
            # Get the existing tab widget
            tab_widget = self.ui.findChild(QtWidgets.QTabWidget, "tabWidget")

            if tab_widget is None:
                logger.warning("Tab widget not found in UI")
                return

            # Create a new tab for temperature plot
            temp_tab = QtWidgets.QWidget()
            temp_layout = QtWidgets.QVBoxLayout(temp_tab)

            # Create graphics view for temperature plot
            temp_graphics_view = QtWidgets.QGraphicsView()
            temp_layout.addWidget(temp_graphics_view)

            # Add the new tab to the tab widget
            tab_widget.addTab(temp_tab, "Temperature Plot")

            # Create scene and canvas for temperature plot
            temp_scene = QtWidgets.QGraphicsScene()
            temp_graphics_view.setScene(temp_scene)

            # Create matplotlib figure for temperature plot
            self.temp_fig = Figure(figsize=(12, 3), dpi=100)
            self.temp_canvas = FigureCanvas(self.temp_fig)
            temp_scene.addWidget(self.temp_canvas)

            # Create axes for temperature plot
            self.temp_ax = self.temp_fig.add_subplot(111)
            self.temp_ax.set_xlabel("Angle (degrees)")
            self.temp_ax.set_ylabel("Temperature (°C)")
            self.temp_ax.set_title("Camera Temperature Readings vs Position")
            self.temp_ax.grid(True, alpha=0.3)
            self.temp_ax.set_xlim(0, 360)

            # Initialize empty line plots for each camera (max and min)
            self.temp_lines = {}
            colors = ["red", "blue", "green", "orange"]

            for i in range(4):
                camera_name = f"camera{i+1}"
                color = colors[i]

                # Create lines for max and min temperatures
                (max_line,) = self.temp_ax.plot([], [], "o-", color=color, label=f"{camera_name} Max", markersize=3)
                (min_line,) = self.temp_ax.plot(
                    [], [], "s--", color=color, label=f"{camera_name} Min", markersize=3, alpha=0.7
                )

                self.temp_lines[f"{camera_name}_max"] = max_line
                self.temp_lines[f"{camera_name}_min"] = min_line

            # Add legend
            self.temp_ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

            # Adjust layout to make room for legend
            self.temp_fig.subplots_adjust(right=0.85)

            logger.info("Temperature plot tab added successfully")

        except Exception as e:
            logger.error(f"Error setting up temperature plot: {e}")

    def update_temperature_plot(self):
        """Update the temperature plot with current data"""
        try:
            if not hasattr(self, "temp_ax"):
                return

            # Get temperature data from thermal camera
            if hasattr(self.system._thermalcamera, "_stitching_max_temperature") and hasattr(
                self.system._thermalcamera, "_stitching_min_temperature"
            ):

                for i in range(4):
                    camera_name = f"camera{i}"  # This matches the thermal_camera.py naming
                    camera_display_name = f"camera{i+1}"  # This matches the GUI naming

                    if (
                        camera_name in self.system._thermalcamera._stitching_max_temperature
                        and camera_name in self.system._thermalcamera._stitching_min_temperature
                    ):

                        max_temp_data = self.system._thermalcamera._stitching_max_temperature[camera_name]
                        min_temp_data = self.system._thermalcamera._stitching_min_temperature[camera_name]

                        if max_temp_data and min_temp_data:
                            # Extract positions and temperatures
                            positions = []
                            max_temps = []
                            min_temps = []

                            # Get all positions that have both max and min data
                            common_positions = set(max_temp_data.keys()) & set(min_temp_data.keys())

                            for pos in sorted(common_positions, key=float):
                                # Apply camera position offset to get effective position
                                effective_position = (
                                    float(pos) + self.camera_positions[camera_display_name]["position"]
                                ) % 360

                                positions.append(effective_position)
                                max_temps.append(max_temp_data[pos])
                                min_temps.append(min_temp_data[pos])

                            if positions:
                                # Update the plot lines
                                self.temp_lines[f"{camera_display_name}_max"].set_data(positions, max_temps)
                                self.temp_lines[f"{camera_display_name}_min"].set_data(positions, min_temps)

                # Auto-scale the y-axis based on all temperature data
                all_temps = []
                for line in self.temp_lines.values():
                    y_data = line.get_ydata()
                    if len(y_data) > 0:
                        all_temps.extend(y_data)

                if all_temps:
                    temp_min = min(all_temps)
                    temp_max = max(all_temps)
                    temp_range = temp_max - temp_min
                    margin = temp_range * 0.1 if temp_range > 0 else 1.0

                    self.temp_ax.set_ylim(temp_min - margin, temp_max + margin)

                # Redraw the canvas
                self.temp_canvas.draw()

        except Exception as e:
            logger.error(f"Error updating temperature plot: {e}")

    def enable_controls(self, enabled=True):
        """Enable or disable all controls except Start Thermal Camera button"""
        controls = [
            self.ui.rotate_PB,
            self.ui.go_to_PB,
            self.ui.calibrate_PB,
            self.ui.set_abs_pos_PB,
            self.ui.export_abs_pos_PB,
            self.ui.get_frms_PB,
            self.ui.relse_mtr_PB,
            self.ui.run_PB,
            self.ui.stop_PB,
            self.ui.ip_DAngle_LE,
            self.ui.ip_angle_LE,
            self.ui.ip_angle_LE_2,  # This is the 90-degree angle input
            self.ui.ip_abs_pos_LE,
            self.ui.direction_combo,  # Direction combobox
        ]
        for control in controls:
            control.setEnabled(enabled)

    def connect_signals(self):
        """Connect UI signals to their handlers"""
        try:
            # Connect buttons to their respective functions
            self.ui.relse_mtr_PB_2.clicked.connect(self.start_thermal_camera)
            self.ui.rotate_PB.clicked.connect(self.rotate)
            self.ui.go_to_PB.clicked.connect(self.go_to)
            self.ui.calibrate_PB.clicked.connect(self.calibrate)
            self.ui.set_abs_pos_PB.clicked.connect(self.set_absolute_position)
            self.ui.export_abs_pos_PB.clicked.connect(self.export_absolute_position)
            self.ui.get_frms_PB.clicked.connect(self.get_frames)
            self.ui.relse_mtr_PB.clicked.connect(self.release_motor)
            self.ui.run_PB.clicked.connect(self.run)
            self.ui.stop_PB.clicked.connect(self.stop)
            self.ui.reset_figures_PB.clicked.connect(self.setup_camera_views)

            # Connect camera coordinate setting buttons
            self.ui.camera_set_pos_button_1.clicked.connect(lambda: self.set_camera_position(1))
            self.ui.camera_set_pos_button_2.clicked.connect(lambda: self.set_camera_position(2))
            self.ui.camera_set_pos_button_3.clicked.connect(lambda: self.set_camera_position(3))
            self.ui.camera_set_pos_button_4.clicked.connect(lambda: self.set_camera_position(4))

            logger.info("Thermal camera signals connected")
        except Exception as e:
            logger.error(f"Error connecting signals: {e}")

    def set_camera_position(self, camera_id):
        """Set the position for a specific camera"""
        try:
            # Get the line edit widget for this camera
            pos_le = getattr(self.ui, f"camera_pos_le_{camera_id}")

            # Parse the new position
            try:
                new_position = float(pos_le.text())
            except ValueError:
                logger.error(f"Invalid position value for camera {camera_id}: {pos_le.text()}")
                return

            # Validate position range (0-360 degrees)
            if not (0 <= new_position <= 360):
                logger.error(f"Position out of range for camera {camera_id}: {new_position}. Must be 0-360°")
                return

            # Update camera position offset in our data structure
            camera_name = f"camera{camera_id}"
            if camera_name in self.camera_positions:
                old_offset = self.camera_positions[camera_name]["position"]
                self.camera_positions[camera_name]["position"] = new_position

                # Save the updated config to file
                self.save_camera_config()

                # Update the display labels immediately to reflect the new offset
                self.update_camera_displays()

                logger.info(
                    f"Camera {camera_id} offset updated from {old_offset}° to {new_position}° and saved to config"
                )

        except Exception as e:
            logger.error(f"Error setting position for camera {camera_id}: {e}")

    def update_camera_displays(self):
        """Update the camera position and side display labels"""
        try:
            # Get current system position (either from status or from our tracking)
            current_system_pos = self.get_current_system_position()
            camera_modules_map = self.get_camera_modules_map()
            print(f"Camera modules map: {camera_modules_map}")

            for i, (camera_name, camera_info) in enumerate(self.camera_positions.items(), 1):
                # Calculate effective position based on current system position and camera offset
                camera_offset = camera_info["position"]
                effective_position = (current_system_pos + camera_offset) % 360

                # Update position label with effective position
                pos_label = getattr(self.ui, f"camera_pos_label_{i}")
                pos_label.setText(f"{effective_position:.1f}°")

                # Update side label
                side_label = getattr(self.ui, f"camera_side_label_{i}")
                side_label.setText(camera_info["side"])

                module_label = getattr(self.ui, f"camera_module_label_{i}")
                module_label.setText(camera_modules_map.get(camera_name, "Unknown"))

        except Exception as e:
            logger.error(f"Error updating camera displays: {e}")

    def move_camera(self, camera_id, target_angle):
        """Move a specific camera to a target angular position using go_to function"""
        try:
            camera_name = f"camera{camera_id}"
            if camera_name not in self.camera_positions:
                logger.error(f"Invalid camera ID: {camera_id}")
                return False

            # Get the current camera position offset
            camera_offset = self.camera_positions[camera_name]["position"]

            # Calculate the absolute position needed for the system
            # Since camera1 has the same absolute position as the system,
            # other cameras need to account for their offset
            if camera_id == 1:
                # Camera 1: target angle = absolute position
                absolute_position = target_angle
            else:
                # Other cameras: need to calculate based on their offset from camera1
                # The system needs to move to (target_angle - camera_offset)
                # so that this camera ends up at target_angle
                absolute_position = target_angle - camera_offset

            # Normalize to 0-360 range
            absolute_position = absolute_position % 360

            logger.info(f"Moving camera {camera_id} to target {target_angle}°")
            logger.info(f"Camera offset: {camera_offset}°, calculated absolute position: {absolute_position}°")

            # Use the go_to function to move to the calculated absolute position
            if self.system._thermalcamera:
                self.system._thermalcamera.go_to({"position": absolute_position})

                # After movement, calculate and display actual positions for all cameras
                # Wait a moment for the system to update (you might want to make this more robust)
                self._update_all_camera_positions_after_move(absolute_position)

                logger.info(f"Camera {camera_id} moved to target position {target_angle}°")
                return True
            else:
                logger.error("Thermal camera system not available")
                return False

        except ValueError as e:
            logger.error(f"Invalid target angle for camera {camera_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error moving camera {camera_id} to {target_angle}°: {e}")
            return False

    def _update_all_camera_positions_after_move(self, new_system_position):
        """Update all camera position displays after a system movement"""
        try:
            # Calculate actual effective positions for all cameras based on new system position
            for camera_name, camera_info in self.camera_positions.items():
                camera_offset = camera_info["position"]
                # Calculate the actual effective position of this camera
                effective_position = (new_system_position + camera_offset) % 360

                # Log the calculated position for verification
                camera_id = camera_name.replace("camera", "")
                logger.debug(
                    f"Camera {camera_id}: system_pos={new_system_position}°, offset={camera_offset}°, effective={effective_position}°"
                )

            # Update the display with calculated positions
            self.update_camera_displays()

        except Exception as e:
            logger.error(f"Error updating camera positions after move: {e}")

    def get_current_system_position(self):
        """Get the current absolute position of the thermal camera system"""
        try:
            if self.system and hasattr(self.system, "status"):
                status = self.system.status.get("thermal_camera", {})
                return status.get("position", 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error getting current system position: {e}")
            return 0.0

    def get_camera_effective_position(self, camera_id):
        """Get the effective angular position of a specific camera"""
        try:
            system_position = self.get_current_system_position()
            camera_name = f"camera{camera_id}"

            if camera_name in self.camera_positions:
                camera_offset = self.camera_positions[camera_name]["position"]
                effective_position = (system_position + camera_offset) % 360
                return effective_position
            else:
                logger.error(f"Invalid camera ID: {camera_id}")
                return None
        except Exception as e:
            logger.error(f"Error calculating effective position for camera {camera_id}: {e}")
            return None

    def stitch_multiple_images(self, images, positions, temp_min, temp_max, full_coverage=360):
        """Stitch multiple images from different positions into a panorama"""
        # Get dimensions of a single image
        h, w = images[0].shape

        # Calculate total width based on full coverage and FOV
        total_width = int(w * full_coverage / self.camera_fov)

        # Create canvas and count arrays for tracking overlaps
        panorama = np.zeros((h, total_width), dtype=np.float32)
        overlap_count = np.zeros((h, total_width), dtype=np.float32)

        # Place images on canvas based on absolute position within the full range
        for img, angle in zip(images, positions):
            # Calculate x offset based on absolute angle position in the full range
            # Normalize angle to 0-360 range if needed
            norm_angle = angle % full_coverage
            x_offset = int(norm_angle * w / self.camera_fov)

            # Make sure offset is within bounds
            if x_offset + w <= total_width:
                # Add image to panorama (accumulate values)
                panorama[:, x_offset : x_offset + w] += img
                # Increment counter for overlapping pixels
                overlap_count[:, x_offset : x_offset + w] += 1
            else:
                # Handle case where image would wrap around
                wrap_width = total_width - x_offset
                # Add first part
                panorama[:, x_offset:] += img[:, :wrap_width]
                overlap_count[:, x_offset:] += 1
                # Add second part (wrap around)
                panorama[:, : w - wrap_width] += img[:, wrap_width:]
                overlap_count[:, : w - wrap_width] += 1

        # Compute mean for overlapping regions (avoid division by zero)
        mask = overlap_count > 0
        panorama[mask] = panorama[mask] / overlap_count[mask]

        # Convert to uint8 for display - use actual temperature range
        if np.isclose(temp_min, temp_max):
            temp_max = temp_min + 1.0  # Add a small difference to avoid division by zero

        # Create normalized array with proper handling of NaN values
        panorama_norm = np.zeros_like(panorama)
        valid_mask = ~np.isnan(panorama)
        panorama_norm[valid_mask] = 255 * (panorama[valid_mask] - temp_min) / (temp_max - temp_min)

        # Areas without data will be black (0)
        panorama_norm = np.nan_to_num(panorama_norm, nan=0.0)  # Convert NaNs to 0
        panorama_norm = np.clip(panorama_norm, 0, 255)  # Ensure values are in valid range
        panorama_norm = panorama_norm.astype(np.uint8)

        return panorama_norm, panorama

    def update_status(self):
        """Update UI with current thermal camera status"""
        try:
            if not self.system or not hasattr(self.system, "status"):
                return

            status = self.system.status.get("thermal_camera", {})
            if not status:
                return

            # Update position display
            if "position" in status:
                self.ui.ip_limiting_angle_lbl_2.setText(f"{status['position']:.2f}")

            streaming = status.get("streaming", False)
            self.ui.streamin_image_flag.setStyleSheet(
                "background-color: green;" if streaming else "background-color: red;"
            )
            running = status.get("running", False)
            self.ui.run_stat_flg.setStyleSheet("background-color: green;" if running else "background-color: red;")

            switch_state = status.get("switch_state", False)
            self.ui.switch_state_flag.setStyleSheet(
                "background-color: green;" if switch_state else "background-color: red;"
            )

            # Update camera images with proper scaling
            if hasattr(self.system._thermalcamera, "_images"):
                # First update individual camera views
                for i, (camera_name, image_data) in enumerate(self.system._thermalcamera._images.items()):
                    if isinstance(image_data, np.ndarray):
                        # Convert to float if needed
                        if image_data.dtype != np.float64:
                            try:
                                image_data = image_data.astype(np.float64)
                            except (ValueError, TypeError) as e:
                                logger.error(f"Failed to convert image data to float: {e}")
                                continue

                        # Update individual camera view
                        self.camera_images[i].set_array(image_data)

                        # Calculate temperature range for consistent scaling
                        vmin = np.nanmin(image_data)
                        vmax = np.nanmax(image_data)
                        self.camera_images[i].set_clim(vmin, vmax)

                        # Update colorbar ticks for camera view
                        cbar = self.camera_images[i].colorbar
                        if cbar is not None:
                            cbar.set_ticks(np.linspace(vmin, vmax, 5))
                            cbar.set_ticklabels([f"{temp:.1f}°C" for temp in np.linspace(vmin, vmax, 5)])

                # Draw camera canvas
                self.cameras_canvas.draw()

                # Create stitched images using the accumulated data
                try:
                    # Get stitching data from thermal camera
                    if hasattr(self.system._thermalcamera, "_stitching_data"):
                        for i, (camera_name, camera_data) in enumerate(
                            self.system._thermalcamera._stitching_data.items()
                        ):
                            # add +1 to the camera name to match the UI naming
                            camera_index = int(camera_name[-1]) + 1
                            camera_name = f"camera{camera_index}"
                            if camera_data:  # If we have data for this camera
                                # Get all images and positions
                                images = []
                                positions = []
                                temp_min = float("inf")
                                temp_max = float("-inf")

                                # Collect all images and positions
                                for pos, pos_images in camera_data.items():
                                    if pos_images:  # If we have images at this position
                                        # Keep only the last image at this position
                                        last_img = pos_images[-1]
                                        images.append(last_img)
                                        # positions.append(float(pos))
                                        positions.append(float(pos) + self.camera_positions[camera_name]["position"])

                                        # Update temperature range
                                        temp_min = min(temp_min, last_img.min())
                                        temp_max = max(temp_max, last_img.max())

                                if images:  # If we have any images to stitch
                                    # Create stitched panorama
                                    panorama_norm, panorama = self.stitch_multiple_images(
                                        images, positions, temp_min, temp_max, full_coverage=360
                                    )

                                    # Ensure the panorama is properly sized for 360 degrees
                                    if panorama.shape[1] != 360:
                                        # Resize to 360 degrees if needed
                                        from scipy.ndimage import zoom

                                        zoom_factor = (1, 360 / panorama.shape[1])
                                        panorama = zoom(panorama, zoom_factor, order=1)

                                    # Update the stitched view
                                    self.stitched_images[camera_index - 1].set_array(panorama)
                                    self.stitched_images[camera_index - 1].set_clim(temp_min, temp_max)

                                    # Update colorbar
                                    cbar = self.stitched_images[camera_index - 1].colorbar
                                    if cbar is not None:
                                        cbar.set_ticks(np.linspace(temp_min, temp_max, 5))
                                        cbar.set_ticklabels(
                                            [f"{temp:.1f}°C" for temp in np.linspace(temp_min, temp_max, 5)]
                                        )

                                    # Draw canvas
                                    self.stitched_canvases[camera_index - 1].draw()

                    # Update temperature plot
                    self.update_temperature_plot()

                except Exception as e:
                    logger.error(f"Error creating stitched images: {e}")
                    logger.error(f"Error details: {str(e)}", exc_info=True)

        except Exception as e:
            logger.error(f"Error updating status: {e}")
            logger.error(f"Error details: {str(e)}", exc_info=True)

    def rotate(self):
        """Rotate the thermal camera by the specified angle"""
        try:
            angle = float(self.ui.ip_DAngle_LE.text())
            if self.system._thermalcamera:
                direction = "bw" if self.ui.direction_combo.currentText() == "Clockwise" else "fw"
                self.system._thermalcamera.rotate({"angle": angle, "direction": direction})
                logger.info(f"Rotating camera by {angle} degrees")
        except ValueError:
            logger.error("Invalid angle value")
        except Exception as e:
            logger.error(f"Error rotating camera: {e}")

    def go_to(self):
        """Go to the specified angle"""
        try:
            angle = float(self.ui.ip_angle_LE.text())
            if self.system._thermalcamera:
                self.system._thermalcamera.go_to({"position": angle})
                logger.info(f"Moving camera to {angle} degrees")
                self.update_camera_displays()
        except ValueError:
            logger.error("Invalid angle value")
        except Exception as e:
            logger.error(f"Error moving camera: {e}")

    def calibrate(self):
        """Calibrate the thermal camera"""
        try:
            # Use ip_angle_LE_2 which contains the 90-degree angle input
            limit = float(self.ui.ip_angle_LE_2.text())
            if self.system._thermalcamera:
                direction = "bw" if self.ui.direction_combo.currentText() == "Clockwise" else "fw"
                self.system._thermalcamera.calibrate({"prudence": limit, "direction": direction})
                logger.info(f"Calibrating camera with limit {limit} degrees")
                self.update_camera_displays()
        except ValueError:
            logger.error("Invalid angle limit value")
        except Exception as e:
            logger.error(f"Error calibrating camera: {e}")

    def set_absolute_position(self):
        """Set the absolute position"""
        try:
            position = float(self.ui.ip_abs_pos_LE.text())
            if self.system._thermalcamera:
                self.system._thermalcamera.set_absolute_position({"value": position})
                logger.info(f"Setting absolute position to {position}")
                self.update_camera_displays()
        except ValueError:
            logger.error("Invalid position value")
        except Exception as e:
            logger.error(f"Error setting absolute position: {e}")

    def export_absolute_position(self):
        """Export the absolute position"""
        try:
            if self.system._thermalcamera:
                self.system._thermalcamera.export_absolute_position({})
                logger.info("Exporting absolute position")
        except Exception as e:
            logger.error(f"Error exporting absolute position: {e}")

    def get_frames(self):
        """Get frames from all cameras"""
        try:
            if self.system._thermalcamera:
                self.system._thermalcamera.get_frames({})
                logger.info("Getting frames from all cameras")
        except Exception as e:
            logger.error(f"Error getting frames: {e}")

    def release_motor(self):
        """Release the stepper motor"""
        try:
            if self.system._thermalcamera:
                self.system._thermalcamera.release({})
                logger.info("Releasing stepper motor")
        except Exception as e:
            logger.error(f"Error releasing motor: {e}")

    def run(self):
        """Start the thermal camera process"""
        try:
            if self.system._thermalcamera:
                self.system._thermalcamera.run({})
                logger.info("Starting thermal camera process")
        except Exception as e:
            logger.error(f"Error starting process: {e}")

    def stop(self):
        """Stop the thermal camera process"""
        try:
            if self.system._thermalcamera:
                self.system._thermalcamera.stop({})
                logger.info("Stopping thermal camera process")
                self.update_camera_displays()
        except Exception as e:
            logger.error(f"Error stopping process: {e}")

    def start_thermal_camera(self):
        """Initialize and start the thermal camera"""
        try:
            if self.system._thermalcamera:
                # Add logging to check available methods
                logger.info("Starting thermal camera")

                # Try using init method instead of initialize
                self.system._thermalcamera.init({})
                self.enable_controls(True)
                # self.ui.relse_mtr_PB_2.setEnabled(False)  # Disable start button
                logger.info("Thermal camera initialized")
                self.update_camera_displays()
        except Exception as e:
            logger.error(f"Error using alternative init method: {e}")
            self.enable_controls(False)
            self.ui.relse_mtr_PB_2.setEnabled(True)  # Re-enable start button

    def closeEvent(self, event):
        """Handle widget close event"""
        try:
            self.update_timer.stop()
            event.accept()
        except Exception as e:
            logger.error(f"Error in close event: {e}")
            event.accept()
