from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSlider, QPushButton, QFormLayout, QComboBox, 
                            QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import os
import json

class EditPanel(QWidget):
    adjustments_changed = pyqtSignal(dict)
    rotation_changed = pyqtSignal(int)
    flip_changed = pyqtSignal(str)
    format_changed = pyqtSignal(str)
    size_changed = pyqtSignal(dict)
    compression_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_rotation = 0
        self.is_flipped_h = False
        self.is_flipped_v = False
        self.updating = False
        self.original_width = 0
        self.original_height = 0
        self.aspect_ratio = 1.0
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Format & Größe
        format_title = QLabel("Format & Größe")
        format_title.setProperty("cssClass", "section-title")
        layout.addWidget(format_title)

        format_panel = QWidget()
        format_panel.setProperty("cssClass", "section-panel")
        format_layout = QFormLayout(format_panel)
        
        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["WEBP", "JPEG", "PNG", "ICO"])
        self.format_combo.currentTextChanged.connect(self.format_changed.emit)
        format_layout.addRow("Format:", self.format_combo)
        
        # Größe Container
        size_container = QWidget()
        size_layout = QVBoxLayout(size_container)
        size_layout.setContentsMargins(0, 0, 0, 0)

        # Einheit
        unit_container = QWidget()
        unit_layout = QHBoxLayout(unit_container)
        unit_layout.setContentsMargins(0, 0, 0, 0)
        
        self.size_unit = QComboBox()
        self.size_unit.addItems(["Pixel", "%"])
        unit_layout.addWidget(QLabel("Einheit:"))
        unit_layout.addWidget(self.size_unit)
        unit_layout.addStretch()
        
        self.keep_aspect = QCheckBox("Seitenverhältnis beibehalten")
        unit_layout.addWidget(self.keep_aspect)
        
        size_layout.addWidget(unit_container)

        # Breite & Höhe
        dimensions_container = QWidget()
        dimensions_layout = QFormLayout(dimensions_container)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, 10000)
        self.width_spin.setSpecialValueText("Original")
        dimensions_layout.addRow("Breite:", self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, 10000)
        self.height_spin.setSpecialValueText("Original")
        dimensions_layout.addRow("Höhe:", self.height_spin)
        
        size_layout.addWidget(dimensions_container)
        format_layout.addRow("Größe:", size_container)

        # Kompression
        compression_container = QWidget()
        compression_layout = QHBoxLayout(compression_container)
        compression_layout.setContentsMargins(0, 0, 0, 0)
        
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(0, 100)
        self.compression_slider.setValue(85)
        self.compression_slider.setObjectName("compression_slider")
        
        self.compression_label = QLabel("85%")
        compression_layout.addWidget(self.compression_slider)
        compression_layout.addWidget(self.compression_label)
        
        format_layout.addRow("Kompression:", compression_container)
        layout.addWidget(format_panel)

        # Bildanpassungen
        adjustments_title = QLabel("Bildanpassungen")
        adjustments_title.setProperty("cssClass", "section-title")
        layout.addWidget(adjustments_title)

        adjustments_panel = QWidget()
        adjustments_panel.setProperty("cssClass", "section-panel")
        adjustments_layout = QFormLayout(adjustments_panel)
        
        # Helligkeit
        brightness_container = QWidget()
        brightness_layout = QHBoxLayout(brightness_container)
        brightness_layout.setContentsMargins(0, 0, 0, 0)
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_value = QLabel("0")
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value)
        
        adjustments_layout.addRow("Helligkeit:", brightness_container)

        # Kontrast
        contrast_container = QWidget()
        contrast_layout = QHBoxLayout(contrast_container)
        contrast_layout.setContentsMargins(0, 0, 0, 0)
        
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_value = QLabel("0")
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_value)
        
        adjustments_layout.addRow("Kontrast:", contrast_container)

        # Sättigung
        saturation_container = QWidget()
        saturation_layout = QHBoxLayout(saturation_container)
        saturation_layout.setContentsMargins(0, 0, 0, 0)
        
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_value = QLabel("0")
        saturation_layout.addWidget(self.saturation_slider)
        saturation_layout.addWidget(self.saturation_value)
        
        adjustments_layout.addRow("Sättigung:", saturation_container)
        
        layout.addWidget(adjustments_panel)

        # Transformation
        transform_title = QLabel("Transformation")
        transform_title.setProperty("cssClass", "section-title")
        layout.addWidget(transform_title)

        transform_panel = QWidget()
        transform_panel.setProperty("cssClass", "section-panel")
        transform_layout = QHBoxLayout(transform_panel)
        
        self.rotate_left_btn = QPushButton("↺ 90°")
        self.rotate_right_btn = QPushButton("↻ 90°")
        self.flip_h_btn = QPushButton("↔")
        self.flip_v_btn = QPushButton("↕")
        
        transform_layout.addWidget(self.rotate_left_btn)
        transform_layout.addWidget(self.rotate_right_btn)
        transform_layout.addWidget(self.flip_h_btn)
        transform_layout.addWidget(self.flip_v_btn)
        
        layout.addWidget(transform_panel)

        # Template Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        self.save_template_btn = QPushButton("Aktuelle Einstellungen als Vorlage speichern")
        self.save_template_btn.setProperty("cssClass", "accent")
        self.save_template_btn.clicked.connect(self.save_template)
        
        self.load_template_btn = QPushButton("Vorlage laden")
        self.load_template_btn.setProperty("cssClass", "accent")
        self.load_template_btn.clicked.connect(self.load_template)
        
        button_layout.addWidget(self.save_template_btn)
        button_layout.addWidget(self.load_template_btn)
        
        layout.addWidget(button_container)

        # Reset Button
        self.reset_btn = QPushButton("Alle Einstellungen zurücksetzen")
        self.reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(self.reset_btn)

        # Connect signals
        self.setup_connections()

    def setup_connections(self):
        # Kompression
        self.compression_slider.valueChanged.connect(
            lambda v: (
                self.compression_label.setText(f"{v}%"),
                self.compression_changed.emit(v)
            )
        )

        # Bildanpassungen mit korrigierten Wertebereichen
        self.brightness_slider.valueChanged.connect(
            lambda v: (
                self.brightness_value.setText(str(v)),
                self.emit_adjustments()
            )
        )
        
        # Setze die korrekten Wertebereiche für die Slider
        self.brightness_slider.setRange(-100, 100)
        self.contrast_slider.setRange(-100, 100)
        self.saturation_slider.setRange(-100, 100)

        self.contrast_slider.valueChanged.connect(
            lambda v: (
                self.contrast_value.setText(str(v)),
                self.emit_adjustments()
            )
        )
        
        self.saturation_slider.valueChanged.connect(
            lambda v: (
                self.saturation_value.setText(str(v)),
                self.emit_adjustments()
            )
        )

        # Größenänderungen
        self.width_spin.valueChanged.connect(self.on_size_changed)
        self.height_spin.valueChanged.connect(self.on_size_changed)
        self.size_unit.currentTextChanged.connect(self.on_unit_changed)
        self.keep_aspect.stateChanged.connect(self.on_size_changed)

        # Transformation
        self.rotate_left_btn.clicked.connect(lambda: self.rotate(-90))
        self.rotate_right_btn.clicked.connect(lambda: self.rotate(90))
        self.flip_h_btn.clicked.connect(lambda: self.flip('h'))
        self.flip_v_btn.clicked.connect(lambda: self.flip('v'))

    def emit_adjustments(self):
        """Sendet die normalisierten Bildanpassungswerte"""
        if not self.updating:
            adjustments = {
                'brightness': self.normalize_brightness(self.brightness_slider.value()),
                'contrast': self.normalize_contrast(self.contrast_slider.value()),
                'saturation': self.normalize_saturation(self.saturation_slider.value())
            }
            self.adjustments_changed.emit(adjustments)

    def normalize_brightness(self, value):
        """Normalisiert den Helligkeitswert für PIL"""
        # Konvertiert -100 bis 100 zu einem Faktor von 0.0 bis 2.0
        return 1.0 + (value / 100.0)

    def normalize_contrast(self, value):
        """Normalisiert den Kontrastwert für PIL"""
        # Konvertiert -100 bis 100 zu einem Faktor von 0.0 bis 2.0
        return 1.0 + (value / 100.0)

    def normalize_saturation(self, value):
        """Normalisiert den Sättigungswert für PIL"""
        # Konvertiert -100 bis 100 zu einem Faktor von 0.0 bis 2.0
        return 1.0 + (value / 100.0)

    def rotate(self, angle):
        """Rotiert das Bild um den angegebenen Winkel"""
        self.current_rotation = (self.current_rotation + angle) % 360
        self.rotation_changed.emit(angle)

    def flip(self, direction):
        """Spiegelt das Bild horizontal oder vertikal"""
        if direction == 'h':
            self.is_flipped_h = not self.is_flipped_h
        else:
            self.is_flipped_v = not self.is_flipped_v
        self.flip_changed.emit(direction)

    def on_size_changed(self):
        """Behandelt Änderungen der Bildgröße"""
        if self.updating:
            return
        
        width = self.width_spin.value()
        height = self.height_spin.value()
        unit = self.size_unit.currentText()
        keep_aspect = self.keep_aspect.isChecked()
        
        size_info = {
            'width': width,
            'height': height,
            'unit': unit,
            'keep_aspect': keep_aspect
        }
        self.size_changed.emit(size_info)

    def on_unit_changed(self):
        """Aktualisiert die Größenfelder basierend auf der gewählten Einheit"""
        self.updating = True
        if self.size_unit.currentText() == "Pixel":
            self.width_spin.setRange(0, 10000)
            self.height_spin.setRange(0, 10000)
            self.width_spin.setSuffix("")
            self.height_spin.setSuffix("")
        else:
            self.width_spin.setRange(0, 1000)
            self.height_spin.setRange(0, 1000)
            self.width_spin.setSuffix("%")
            self.height_spin.setSuffix("%")
        self.updating = False

    def save_template(self):
        # ... Implementation ...
        pass

    def load_template(self):
        # ... Implementation ...
        pass

    def reset_all(self):
        # ... Implementation ...
        pass
