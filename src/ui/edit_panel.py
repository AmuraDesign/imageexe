from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSlider, QPushButton, QGroupBox, QComboBox, 
                            QSpinBox, QFormLayout, QInputDialog, QMessageBox, 
                            QCheckBox)
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
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Format und Größe
        format_group = QGroupBox("Format & Größe")
        format_layout = QFormLayout()
        
        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["WEBP", "JPEG", "PNG", "ICO"])
        self.format_combo.currentTextChanged.connect(self.format_changed.emit)
        format_layout.addRow("Format:", self.format_combo)
        
        # Größeneinstellungen Container
        size_container = QWidget()
        size_layout = QVBoxLayout(size_container)
        size_layout.setContentsMargins(0, 0, 0, 0)

        # Einheitenauswahl
        unit_layout = QHBoxLayout()
        self.size_unit = QComboBox()
        self.size_unit.addItems(["Pixel", "%"])
        self.size_unit.currentTextChanged.connect(self.on_unit_changed)
        unit_layout.addWidget(QLabel("Einheit:"))
        unit_layout.addWidget(self.size_unit)
        unit_layout.addStretch()

        # Checkbox für Seitenverhältnis
        self.keep_aspect = QCheckBox("Seitenverhältnis beibehalten")
        self.keep_aspect.setChecked(True)
        unit_layout.addWidget(self.keep_aspect)

        size_layout.addLayout(unit_layout)

        # Breite
        width_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, 10000)
        self.width_spin.setSpecialValueText("Original")
        self.width_spin.valueChanged.connect(self.on_width_changed)
        width_layout.addWidget(QLabel("Breite:"))
        width_layout.addWidget(self.width_spin)
        size_layout.addLayout(width_layout)

        # Höhe
        height_layout = QHBoxLayout()
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, 10000)
        self.height_spin.setSpecialValueText("Original")
        self.height_spin.valueChanged.connect(self.on_height_changed)
        height_layout.addWidget(QLabel("Höhe:"))
        height_layout.addWidget(self.height_spin)
        size_layout.addLayout(height_layout)

        format_layout.addRow("Größe:", size_container)

        # Kompression mit angepasstem Stil
        compression_layout = QHBoxLayout()
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(0, 100)
        self.compression_slider.setValue(85)
        self.compression_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4444, stop:1 #44ff44);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #999999;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        self.compression_label = QLabel("85%")
        self.compression_slider.valueChanged.connect(
            lambda v: (
                self.compression_label.setText(f"{v}%"),
                self.compression_changed.emit(v)
            )
        )
        compression_layout.addWidget(QLabel("Kompression:"))
        compression_layout.addWidget(self.compression_slider)
        compression_layout.addWidget(self.compression_label)
        format_layout.addRow("", compression_layout)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Bildanpassungen
        adjust_group = QGroupBox("Bildanpassungen")
        adjust_layout = QVBoxLayout()
        
        # Helligkeit
        brightness_layout = QHBoxLayout()
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.on_adjustment_changed)
        self.brightness_label = QLabel("0")
        brightness_layout.addWidget(QLabel("Helligkeit:"))
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_label)
        adjust_layout.addLayout(brightness_layout)
        
        # Kontrast
        contrast_layout = QHBoxLayout()
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.on_adjustment_changed)
        self.contrast_label = QLabel("0")
        contrast_layout.addWidget(QLabel("Kontrast:"))
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_label)
        adjust_layout.addLayout(contrast_layout)
        
        # Sättigung
        saturation_layout = QHBoxLayout()
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.valueChanged.connect(self.on_adjustment_changed)
        self.saturation_label = QLabel("0")
        saturation_layout.addWidget(QLabel("Sättigung:"))
        saturation_layout.addWidget(self.saturation_slider)
        saturation_layout.addWidget(self.saturation_label)
        adjust_layout.addLayout(saturation_layout)
        
        adjust_group.setLayout(adjust_layout)
        layout.addWidget(adjust_group)
        
        # Transformation
        transform_group = QGroupBox("Transformation")
        transform_layout = QHBoxLayout()
        
        self.rotate_left_btn = QPushButton("↺ 90°")
        self.rotate_right_btn = QPushButton("↻ 90°")
        self.flip_h_btn = QPushButton("↔")
        self.flip_v_btn = QPushButton("↕")
        
        self.rotate_left_btn.clicked.connect(lambda: self.rotate(-90))
        self.rotate_right_btn.clicked.connect(lambda: self.rotate(90))
        self.flip_h_btn.clicked.connect(lambda: self.flip('horizontal'))
        self.flip_v_btn.clicked.connect(lambda: self.flip('vertical'))
        
        transform_layout.addWidget(self.rotate_left_btn)
        transform_layout.addWidget(self.rotate_right_btn)
        transform_layout.addWidget(self.flip_h_btn)
        transform_layout.addWidget(self.flip_v_btn)
        
        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)
        
        # Vorlagen-Buttons
        template_layout = QHBoxLayout()
        save_template_btn = QPushButton("Aktuelle Einstellungen als Vorlage speichern")
        load_template_btn = QPushButton("Vorlage laden")
        
        save_template_btn.clicked.connect(self.save_template)
        load_template_btn.clicked.connect(self.load_template)
        
        template_layout.addWidget(save_template_btn)
        template_layout.addWidget(load_template_btn)
        layout.addLayout(template_layout)
        
        # Zurücksetzen Button
        reset_btn = QPushButton("Alle Einstellungen zurücksetzen")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn)
        
        layout.addStretch()

    def rotate(self, angle):
        """Rotiert das Bild um den angegebenen Winkel"""
        self.current_rotation = (self.current_rotation + angle) % 360
        self.rotation_changed.emit(self.current_rotation)

    def flip(self, direction):
        """Spiegelt das Bild in der angegebenen Richtung"""
        if direction == 'horizontal':
            self.is_flipped_h = not self.is_flipped_h
            if self.is_flipped_h:
                self.flip_h_btn.setStyleSheet("background-color: palette(highlight);")
            else:
                self.flip_h_btn.setStyleSheet("")
        else:  # vertical
            self.is_flipped_v = not self.is_flipped_v
            if self.is_flipped_v:
                self.flip_v_btn.setStyleSheet("background-color: palette(highlight);")
            else:
                self.flip_v_btn.setStyleSheet("")
        
        self.flip_changed.emit(direction)

    def on_adjustment_changed(self):
        """Wird aufgerufen, wenn sich ein Slider-Wert ändert"""
        # Aktualisiere Labels
        self.brightness_label.setText(str(self.brightness_slider.value()))
        self.contrast_label.setText(str(self.contrast_slider.value()))
        self.saturation_label.setText(str(self.saturation_slider.value()))
        
        adjustments = {
            'brightness': 1.0 + (self.brightness_slider.value() / 100),
            'contrast': 1.0 + (self.contrast_slider.value() / 100),
            'saturation': 1.0 + (self.saturation_slider.value() / 100)
        }
        self.adjustments_changed.emit(adjustments)

    def on_size_changed(self):
        """Wird aufgerufen, wenn sich die Größeneinstellungen ändern"""
        if self.updating:
            return
            
        size = {
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
            'unit': self.size_unit.currentText(),
            'keep_aspect': self.keep_aspect.isChecked()
        }
        self.size_changed.emit(size)

    def reset_all(self):
        """Setzt alle Einstellungen zurück"""
        # Format und Größe
        self.format_combo.setCurrentText("WEBP")
        self.width_spin.setValue(0)
        self.height_spin.setValue(0)
        self.size_unit.setCurrentText("Pixel")
        self.keep_aspect.setChecked(True)
        self.compression_slider.setValue(85)
        
        # Bildanpassungen
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        
        # Transformation
        self.current_rotation = 0
        self.is_flipped_h = False
        self.is_flipped_v = False
        self.flip_h_btn.setStyleSheet("")
        self.flip_v_btn.setStyleSheet("")
        
        # Signale senden
        self.on_adjustment_changed()
        self.on_size_changed()
        self.rotation_changed.emit(0)
        self.format_changed.emit("WEBP")
        self.compression_changed.emit(85)

    def save_template(self):
        """Speichert die aktuellen Einstellungen als Vorlage"""
        name, ok = QInputDialog.getText(
            self, 'Vorlage speichern', 
            'Name der Vorlage:'
        )
        if ok and name:
            template = {
                'format': self.format_combo.currentText(),
                'width': self.width_spin.value(),
                'height': self.height_spin.value(),
                'compression': self.compression_slider.value(),
                'adjustments': {
                    'brightness': self.brightness_slider.value(),
                    'contrast': self.contrast_slider.value(),
                    'saturation': self.saturation_slider.value()
                },
                'rotation': self.current_rotation,
                'flip_h': self.is_flipped_h,
                'flip_v': self.is_flipped_v
            }
            
            try:
                # Erstelle templates Ordner, falls nicht vorhanden
                templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
                os.makedirs(templates_dir, exist_ok=True)
                
                # Speichere Template als JSON
                import json
                template_path = os.path.join(templates_dir, f"{name}.json")
                with open(template_path, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=4)
                
                QMessageBox.information(
                    self,
                    "Erfolg",
                    f"Vorlage '{name}' wurde erfolgreich gespeichert."
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Fehler",
                    f"Fehler beim Speichern der Vorlage: {str(e)}"
                )

    def load_template(self):
        """Lädt eine gespeicherte Vorlage"""
        try:
            # Template-Verzeichnis
            templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
            if not os.path.exists(templates_dir):
                QMessageBox.warning(
                    self,
                    "Keine Vorlagen",
                    "Es wurden keine gespeicherten Vorlagen gefunden."
                )
                return

            # Liste verfügbarer Templates
            templates = [f for f in os.listdir(templates_dir) if f.endswith('.json')]
            if not templates:
                QMessageBox.warning(
                    self,
                    "Keine Vorlagen",
                    "Es wurden keine gespeicherten Vorlagen gefunden."
                )
                return

            # Template auswählen
            template_name, ok = QInputDialog.getItem(
                self,
                "Vorlage laden",
                "Wähle eine Vorlage:",
                [os.path.splitext(t)[0] for t in templates],
                0,
                False
            )

            if ok and template_name:
                # Template laden und anwenden
                import json
                template_path = os.path.join(templates_dir, f"{template_name}.json")
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)

                # Einstellungen anwenden
                self.format_combo.setCurrentText(template['format'])
                self.width_spin.setValue(template['width'])
                self.height_spin.setValue(template['height'])
                self.compression_slider.setValue(template['compression'])
                
                # Bildanpassungen
                self.brightness_slider.setValue(template['adjustments']['brightness'])
                self.contrast_slider.setValue(template['adjustments']['contrast'])
                self.saturation_slider.setValue(template['adjustments']['saturation'])
                
                # Transformation
                self.current_rotation = template['rotation']
                self.is_flipped_h = template['flip_h']
                self.is_flipped_v = template['flip_v']
                
                # UI aktualisieren
                self.on_adjustment_changed()
                self.on_size_changed()
                self.rotation_changed.emit(self.current_rotation)
                self.format_changed.emit(template['format'])
                self.compression_changed.emit(template['compression'])
                
                # Flip-Button-Styles aktualisieren
                self.flip_h_btn.setStyleSheet(
                    "background-color: palette(highlight);" if self.is_flipped_h else ""
                )
                self.flip_v_btn.setStyleSheet(
                    "background-color: palette(highlight);" if self.is_flipped_v else ""
                )

                QMessageBox.information(
                    self,
                    "Erfolg",
                    f"Vorlage '{template_name}' wurde erfolgreich geladen."
                )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Fehler beim Laden der Vorlage: {str(e)}"
            )

    def update_spin_ranges(self):
        """Aktualisiert die erlaubten Bereiche der Spinboxen basierend auf der gewählten Einheit"""
        # Breite
        if self.size_unit.currentText() == "%":
            self.width_spin.setRange(0, 200)  # 0-200%
            if self.width_spin.value() > 200:
                self.width_spin.setValue(100)
        else:
            self.width_spin.setRange(0, 10000)  # 0-10000px
        
        # Höhe
        if self.size_unit.currentText() == "%":
            self.height_spin.setRange(0, 200)  # 0-200%
            if self.height_spin.value() > 200:
                self.height_spin.setValue(100)
        else:
            self.height_spin.setRange(0, 10000)  # 0-10000px

    def on_unit_changed(self):
        """Wird aufgerufen, wenn sich die Einheit ändert"""
        if self.updating:
            return
            
        self.updating = True
        current_unit = self.size_unit.currentText()
        
        if current_unit == "Pixel":
            self.width_spin.setRange(0, 10000)
            self.height_spin.setRange(0, 10000)
            if self.width_spin.value() > 0:
                self.width_spin.setValue(int(self.width_spin.value() * self.original_width / 100))
            if self.height_spin.value() > 0:
                self.height_spin.setValue(int(self.height_spin.value() * self.original_height / 100))
        else:  # Prozent
            self.width_spin.setRange(0, 200)
            self.height_spin.setRange(0, 200)
            if self.width_spin.value() > 0:
                self.width_spin.setValue(int(self.width_spin.value() * 100 / self.original_width))
            if self.height_spin.value() > 0:
                self.height_spin.setValue(int(self.height_spin.value() * 100 / self.original_height))
        
        self.updating = False
        self.on_size_changed()

    def on_width_changed(self):
        """Wird aufgerufen, wenn sich die Breite ändert"""
        if self.updating:
            return
            
        self.updating = True
        if self.keep_aspect.isChecked() and self.width_spin.value() > 0:
            if self.size_unit.currentText() == "Pixel":
                self.height_spin.setValue(int(self.width_spin.value() / self.aspect_ratio))
            else:
                self.height_spin.setValue(self.width_spin.value())
        self.updating = False
        self.on_size_changed()

    def on_height_changed(self):
        """Wird aufgerufen, wenn sich die Höhe ändert"""
        if self.updating:
            return
            
        self.updating = True
        if self.keep_aspect.isChecked() and self.height_spin.value() > 0:
            if self.size_unit.currentText() == "Pixel":
                self.width_spin.setValue(int(self.height_spin.value() * self.aspect_ratio))
            else:
                self.width_spin.setValue(self.height_spin.value())
        self.updating = False
        self.on_size_changed()

    def set_original_size(self, width, height):
        """Setzt die Originalgröße des Bildes"""
        self.original_width = width
        self.original_height = height
        self.aspect_ratio = width / height if height else 1.0
        
        # Aktualisiere die Ranges basierend auf der aktuellen Einheit
        self.on_unit_changed()
