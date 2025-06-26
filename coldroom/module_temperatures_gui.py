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


class ModuleTemperaturesTAB(QtWidgets.QMainWindow):
    def __init__(self, system_obj):
        super(ModuleTemperaturesTAB, self).__init__()
        self.system = system_obj
        # Load UI from file
        ui_file = os.path.join(os.path.dirname(__file__), "module_temperatures.ui")
        uic.loadUi(ui_file, self)

        # Initialize stitching-related attributes
        self.camera_fov = 20  # Field of view in degrees for each camera
        self.config_file = os.path.join(os.path.dirname(__file__), "camera_config.yaml")
        self.camera_positions = self.load_camera_config()
        self.mounted_modules = None
        self.number_of_modules = None

        # Setup UI components
        self.setup_stitched_views()
        self.reset_figures_PB.clicked.connect(self.reset_camera_views)

        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(1000)  # Update every second

        logger.info("Module temperatures tab initialized")

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
                if self.validate_camera_config(config):
                    return config
                else:
                    logger.warning("Invalid camera config, using defaults")
                    self.save_camera_config(default_config)
                    return default_config
            else:
                logger.info("Camera config file not found, creating with defaults")
                self.save_camera_config(default_config)
                return default_config

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config file: {e}")
            self.save_camera_config(default_config)
            return default_config
        except Exception as e:
            logger.error(f"Error loading camera config: {e}")
            self.save_camera_config(default_config)
            return default_config

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

            return True
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False

    def setup_stitched_views(self):
        """Setup matplotlib figures for stitched camera views"""
        try:
            # Create stitched view for each camera
            self.stitched_figs = []
            self.stitched_canvases = []
            self.stitched_images = []
            self.stitched_axes = []

            # Get the tab widget from the UI
            self.stitched_tab_widget = self.findChild(QtWidgets.QTabWidget, "tabWidget")

            for graphics_view in [self.graphics_1, self.graphics_2, self.graphics_3, self.graphics_4]:
                scene = QtWidgets.QGraphicsScene()
                graphics_view.setScene(scene)

                # Create figure and canvas with proper aspect ratio for 360-degree view
                fig = Figure(figsize=(12, 3.5), dpi=100, tight_layout=True)
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

            self.setup_temperature_plot()

            logger.info("Stitched views initialized")

        except Exception as e:
            logger.error(f"Error setting up stitched views: {e}")

    def setup_temperature_plot(self):
        """Setup temperature plotting tab"""
        try:
            # Get the existing tab widget
            tab_widget = self.findChild(QtWidgets.QTabWidget, "tabWidget")

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
            self.temp_fig = Figure(figsize=(12, 3.5), dpi=100, tight_layout=True)
            self.temp_canvas = FigureCanvas(self.temp_fig)
            temp_scene.addWidget(self.temp_canvas)

            # Create axes for temperature plot
            self.temp_ax = self.temp_fig.add_subplot(111)
            self.temp_ax.set_ylabel("T (°C)")
            self.temp_ax.grid(True, alpha=0.3, which="both")
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
            self.temp_ax.legend(bbox_to_anchor=(1.0, 1), loc="upper left", fontsize=8, frameon=False)

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

                            if positions and max_temps:
                                # Filter spikes from max temperatures using simple method
                                filtered_max_temps = self.simple_spike_filter(max_temps)

                                # Update the plot lines
                                self.temp_lines[f"{camera_display_name}_max"].set_data(positions, filtered_max_temps)
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

    def simple_spike_filter(self, temps, max_change=5.0):
        """Simple spike filter - replaces values that change too much from neighbors"""
        if len(temps) < 3:
            return temps

        filtered = temps.copy()

        for i in range(1, len(temps) - 1):
            prev_temp = filtered[i - 1]
            curr_temp = temps[i]
            next_temp = temps[i + 1]

            # Check if current value is very different from both neighbors
            if abs(curr_temp - prev_temp) > max_change and abs(curr_temp - next_temp) > max_change:
                # Replace with average of neighbors
                filtered[i] = (prev_temp + next_temp) / 2

        return filtered

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

            # Center the FOV around the camera position by subtracting half FOV
            # This makes the camera position the center of the image rather than the left edge
            centered_angle = (norm_angle - self.camera_fov / 2) % full_coverage
            x_offset = int(centered_angle * w / self.camera_fov)

            # Make sure offset is within bounds
            if x_offset >= 0 and x_offset + w <= total_width:
                # Add image to panorama (accumulate values)
                panorama[:, x_offset : x_offset + w] += img
                # Increment counter for overlapping pixels
                overlap_count[:, x_offset : x_offset + w] += 1
            else:
                # Handle case where image would wrap around
                if x_offset < 0:
                    # Image starts before 0, wrap around to the end
                    wrap_width = abs(x_offset)
                    # Add wrapped part at the end
                    panorama[:, total_width - wrap_width :] += img[:, :wrap_width]
                    overlap_count[:, total_width - wrap_width :] += 1
                    # Add remaining part at the beginning
                    panorama[:, : w - wrap_width] += img[:, wrap_width:]
                    overlap_count[:, : w - wrap_width] += 1
                elif x_offset + w > total_width:
                    # Image extends beyond total_width, wrap around to the beginning
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

    def simple_spike_filter(self, temps, max_change=5.0):
        """Simple spike filter - replaces values that change too much from neighbors"""
        if len(temps) < 3:
            return temps

        filtered = temps.copy()

        for i in range(1, len(temps) - 1):
            prev_temp = filtered[i - 1]
            curr_temp = temps[i]
            next_temp = temps[i + 1]

            # Check if current temp is a spike
            if abs(curr_temp - prev_temp) > max_change and abs(curr_temp - next_temp) > max_change:
                # Replace with average of neighbors
                filtered[i] = (prev_temp + next_temp) / 2

        return filtered

    def update_temperature_plot(self):
        """Update the temperature plot with current data"""
        try:
            if not hasattr(self, "temp_ax"):
                return

            # Get temperature data from thermal camera
            if hasattr(self.system._thermalcamera, "_stitching_max_temperature") and hasattr(
                self.system._thermalcamera, "_stitching_min_temperature"
            ):

                max_temps = self.system._thermalcamera._stitching_max_temperature
                min_temps = self.system._thermalcamera._stitching_min_temperature

                # Update lines for each camera
                for camera_name in ["camera1", "camera2", "camera3", "camera4"]:
                    if camera_name in max_temps and camera_name in min_temps:
                        angles = sorted(max_temps[camera_name].keys())
                        max_values = [max_temps[camera_name][angle] for angle in angles]
                        min_values = [min_temps[camera_name][angle] for angle in angles]

                        # Apply spike filter
                        max_values_filtered = self.simple_spike_filter(max_values)
                        min_values_filtered = self.simple_spike_filter(min_values)

                        # Update line data
                        if f"{camera_name}_max" in self.temp_lines:
                            self.temp_lines[f"{camera_name}_max"].set_data(angles, max_values_filtered)
                        if f"{camera_name}_min" in self.temp_lines:
                            self.temp_lines[f"{camera_name}_min"].set_data(angles, min_values_filtered)

                # Auto-scale y-axis
                self.temp_ax.relim()
                self.temp_ax.autoscale_view()

                # Redraw canvas
                self.temp_canvas.draw()

        except Exception as e:
            logger.error(f"Error updating temperature plot: {e}")

    def reset_camera_views(self):
        """Reset camera views to initial state"""
        try:
            # Clear stitched images
            for ax in self.stitched_axes:
                ax.clear()
            for img in self.stitched_images:
                img.set_array(np.zeros((24, 360)))

            # Redraw canvases
            for canvas in self.stitched_canvases:
                canvas.draw()

            logger.info("Camera views reset successfully")

            self.system._thermalcamera._stitching_data = {}  # Clear stitching data
            self.system._thermalcamera._stitching_max_temperature = {}
            self.system._thermalcamera._stitching_min_temperature = {}

            # Remove the temperature plot tab if it exists
            tab_widget = self.findChild(QtWidgets.QTabWidget, "tabWidget")
            if tab_widget is not None:
                # Find the Temperature Plot tab by iterating through tabs
                for i in range(tab_widget.count()):
                    if tab_widget.tabText(i) == "Temperature Plot":
                        tab_widget.removeTab(i)
                        logger.info("Removed existing Temperature Plot tab")
                        break

            self.setup_stitched_views()

        except Exception as e:
            logger.error(f"Error resetting camera views: {e}")

    def update_displays(self):
        """Update all displays with current data"""
        # Create stitched images using the accumulated data
        try:
            # Get stitching data from thermal camera
            if hasattr(self.system._thermalcamera, "_stitching_data"):
                for i, (camera_name, camera_data) in enumerate(self.system._thermalcamera._stitching_data.items()):
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

                            # Clear previous annotations and add module names
                            ax = self.stitched_axes[camera_index - 1]
                            # Remove previous text annotations and lines (but keep camera position lines)
                            for txt in ax.texts[:]:
                                if hasattr(txt, "_module_annotation"):
                                    txt.remove()

                            # Remove previous annotation lines (both module and camera position)
                            for line in ax.lines[:]:
                                if hasattr(line, "_module_annotation") or hasattr(line, "_camera_position"):
                                    line.remove()

                            # Add camera position line (red dashed line showing current camera position)
                            current_camera_pos = self.get_camera_effective_position(camera_index)
                            if current_camera_pos is not None:
                                camera_line = ax.axvline(
                                    x=current_camera_pos,
                                    color="red",
                                    linestyle="--",
                                    alpha=0.8,
                                    linewidth=2,
                                    label=f"Camera {camera_index} Position",
                                )
                                # Mark as camera position line for easy removal
                                camera_line._camera_position = True

                            # Add module annotations if we have mounted modules
                            if self.mounted_modules is not None:
                                self.add_module_annotations_to_stitched_image(ax, camera_name)
                            else:
                                logger.debug(f"No mounted modules available for {camera_name}")

                            # Update colorbar
                            cbar = self.stitched_images[camera_index - 1].colorbar
                            if cbar is not None:
                                cbar.set_ticks(np.linspace(temp_min, temp_max, 5))
                                cbar.set_ticklabels([f"{temp:.1f}°C" for temp in np.linspace(temp_min, temp_max, 5)])

                            # Draw canvas
                            self.stitched_canvases[camera_index - 1].draw()

            # Update temperature plot
            self.update_temperature_plot()

        except Exception as e:
            logger.error(f"Error creating stitched images: {e}")
            logger.error(f"Error details: {str(e)}", exc_info=True)

    def update_stitched_images(self):
        """Update stitched images for all cameras"""
        try:
            if not hasattr(self.system._thermalcamera, "_stitching_data"):
                return

            stitching_data = self.system._thermalcamera._stitching_data

            for i, camera_name in enumerate(["camera1", "camera2", "camera3", "camera4"]):
                if (
                    camera_name in stitching_data
                    and len(stitching_data[camera_name]) > 0
                    and i < len(self.stitched_axes)
                ):

                    # Get images and positions for this camera
                    camera_data = stitching_data[camera_name]
                    positions = list(camera_data.keys())
                    images = [camera_data[pos]["image"] for pos in positions]

                    if len(images) > 0:
                        # Get temperature range for this camera
                        max_temps = self.system._thermalcamera._stitching_max_temperature.get(camera_name, {})
                        min_temps = self.system._thermalcamera._stitching_min_temperature.get(camera_name, {})

                        if max_temps and min_temps:
                            temp_max = max(max_temps.values())
                            temp_min = min(min_temps.values())

                            # Stitch images
                            stitched_image, _ = self.stitch_multiple_images(images, positions, temp_min, temp_max)

                            # Update display
                            if i < len(self.stitched_images):
                                self.stitched_images[i].set_data(stitched_image)
                                self.stitched_images[i].set_clim(0, 255)
                                self.stitched_canvases[i].draw()

        except Exception as e:
            logger.error(f"Error updating stitched images: {e}")

    def add_module_annotations_to_stitched_image(self, ax, camera_name):
        """Add module name annotations to the stitched image"""
        try:
            if self.mounted_modules is None:
                logger.debug(f"No mounted modules available for {camera_name}")
                return

            # Get camera side for filtering
            camera_side = self.camera_positions[camera_name]["side"]

            # Convert side format for comparison
            if camera_side == "Front":
                target_side = "13"
            elif camera_side == "Back":
                target_side = "24"
            else:
                target_side = camera_side

            logger.debug(f"Camera {camera_name} side: {camera_side}, target_side: {target_side}")

            # Clear previous annotations
            # Remove previous text annotations and lines
            for txt in ax.texts[:]:
                if hasattr(txt, "_module_annotation"):
                    txt.remove()

            # Remove previous module annotation lines
            for line in ax.lines[:]:
                if hasattr(line, "_module_annotation"):
                    line.remove()

            # Add annotations for modules on the same side as this camera
            annotation_count = 0
            for module_name, module_info in self.mounted_modules.items():
                module_side = module_info["side"]
                module_position = module_info["angular_position"]

                logger.debug(f"Module {module_name}: side={module_side}, position={module_position}")

                # Only show modules on the same side as the camera
                if module_side == target_side:
                    # Calculate the module's position relative to the camera's view
                    # The stitched image shows 360 degrees with 0 at the left edge
                    module_x_pos = module_position

                    # Get module slot information if available
                    if "mounted_on" in module_info and ";" in str(module_info["mounted_on"]):
                        module_slot = str(module_info["mounted_on"]).split(";")[1]
                    else:
                        module_slot = "-"

                    # Create annotation text
                    annotation_text = f"{module_slot}:{module_name}"

                    logger.debug(f"Adding annotation '{annotation_text}' at x={module_x_pos}")

                    # Add text annotation on the top x-axis with 45-degree rotation
                    text_obj = ax.text(
                        module_x_pos,
                        ax.get_ylim()[1],  # Position at the top of the plot
                        annotation_text,
                        fontsize=6,
                        color="black",
                        ha="left",  # Right-align for better readability with rotation
                        va="bottom",
                        rotation=45,
                        # weight='bold',
                        clip_on=False,  # Allow text to extend beyond plot area
                    )

                    # Mark as module annotation for easy removal
                    text_obj._module_annotation = True

                    # Add a dashed vertical line to mark the exact position
                    line_obj = ax.axvline(x=module_x_pos, color="black", linestyle="--", alpha=0.7, linewidth=1.5)

                    # Mark as module annotation for easy removal
                    line_obj._module_annotation = True

                    annotation_count += 1
                    logger.debug(f"Added annotation {annotation_count}: {annotation_text} at position {module_x_pos}")

            logger.info(f"Added {annotation_count} module annotations for {camera_name} on side {camera_side}")

            # Adjust the top margin to make room for the angled text
            # Get current subplot parameters
            current_top = ax.figure.subplotpars.top
            if current_top > 0.85:  # Only adjust if not already adjusted
                ax.figure.subplots_adjust(top=0.85)

            # Force redraw
            ax.figure.canvas.draw_idle()

        except Exception as e:
            logger.error(f"Error adding module annotations: {e}")
            
