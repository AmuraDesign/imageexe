# imageexe Resource Summary

Start of file:
Directory of every file in the project
- File: .ignorethese (not included in output)
- File: image_processing.log (not included in output)
- File: main.py
- File: requirements.txt
- Directory: src
- Directory: src\assets (not included in output)
- Directory: src\assets\icons (not included in output)
- File: src\assets\icons\add-image.png (not included in output)
- File: src\assets\icons\remove-image.png (not included in output)
- File: src\assets\icons\right-arrow.png (not included in output)
- File: src\assets\icons\start.png (not included in output)
- Directory: src\ui
- File: src\ui\edit_panel.py
- File: src\ui\main_window.py
- File: src\ui\preview_window.py
- File: src\ui\queue_panel.py
- File: src\ui\workspace.py
- Directory: src\ui\__pycache__ (not included in output)
- File: src\ui\__pycache__\edit_panel.cpython-312.pyc (not included in output)
- File: src\ui\__pycache__\main_window.cpython-312.pyc (not included in output)
- File: src\ui\__pycache__\preview_window.cpython-312.pyc (not included in output)
- File: src\ui\__pycache__\queue_panel.cpython-312.pyc (not included in output)
- File: src\ui\__pycache__\workspace.cpython-312.pyc (not included in output)
- Directory: src\utils
- File: src\utils\image_processor.py
- Directory: src\utils\__pycache__ (not included in output)
- File: src\utils\__pycache__\image_processor.cpython-312.pyc (not included in output)
End of directory part

Start of file output part

### File: main.py
```
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

def main():
    # Enable High DPI display with PyQt6
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

```

### File: requirements.txt
```
Pillow
PyQt6
pillow-heif

```

### File: src\ui\edit_panel.py
```
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

```

### File: src\ui\main_window.py
```
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QFileDialog, QMessageBox, 
                           QInputDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from .workspace import WorkspacePanel
from .queue_panel import QueuePanel
from .edit_panel import EditPanel
from ..utils.image_processor import ImageProcessor
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bildoptimierung")
        self.setMinimumSize(1200, 700)
        
        # Allgemeines Styling für das Hauptfenster
        self.setStyleSheet("""
            QMainWindow {
                background-color: palette(window);
                color: palette(text);
            }
            QWidget {
                background-color: palette(window);
                color: palette(text);
            }
            QPushButton {
                color: palette(text);
            }
            QLabel {
                color: palette(text);
            }
        """)
        
        # Hauptwidget und Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content Container
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Linke Seite (Workspace)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Workspace
        self.workspace = WorkspacePanel()
        left_layout.addWidget(self.workspace)
        
        # Rechte Seite (Queue und Edit Panel)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Queue und Edit Panel erstellen
        self.queue = QueuePanel()
        self.edit_panel = EditPanel()
        
        # Edit Panel und Queue zum rechten Layout hinzufügen
        right_layout.addWidget(self.edit_panel)
        right_layout.addWidget(self.queue)
        
        # Mittlerer Bereich für den "Zur Queue" Button
        middle_container = QWidget()
        middle_container.setFixedWidth(50)
        middle_layout = QVBoxLayout(middle_container)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        
        # Spacer oben
        middle_layout.addStretch()
        
        # "Zur Queue" Button mit Icon
        add_to_queue_btn = QPushButton()
        add_to_queue_btn.setFixedSize(40, 40)
        add_to_queue_btn.setIcon(QIcon("src/assets/icons/right-arrow.png"))
        add_to_queue_btn.setIconSize(QSize(24, 24))
        add_to_queue_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(button);
                border: 1px solid palette(mid);
                border-radius: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: palette(midlight);
            }
        """)
        add_to_queue_btn.clicked.connect(self.add_selected_to_queue)
        middle_layout.addWidget(add_to_queue_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Spacer unten
        middle_layout.addStretch()
        
        # Layout zusammensetzen
        content_layout.addWidget(left_container, stretch=2)  # Workspace größer
        content_layout.addWidget(middle_container)
        content_layout.addWidget(right_container, stretch=1)  # Queue kleiner
        
        main_layout.addWidget(content_container)
        
        # Verbindungen
        self.workspace.images_added.connect(self.add_images_to_queue)
        self.queue.process_started.connect(self.process_images)
        self.edit_panel.adjustments_changed.connect(self.queue.apply_adjustments)
        self.edit_panel.rotation_changed.connect(self.queue.apply_rotation)
        self.edit_panel.flip_changed.connect(self.queue.apply_flip)
        self.edit_panel.format_changed.connect(lambda fmt: self.queue.update_format(fmt))
        self.edit_panel.size_changed.connect(lambda size: self.queue.update_size(size))
        self.edit_panel.compression_changed.connect(lambda v: self.queue.update_compression(v))
        
    def add_images_to_queue(self, image_paths):
        for path in image_paths:
            self.queue.add_image(path)
    
    def process_images(self):
        """Verarbeitet die Bilder in der Queue"""
        if self.queue.queue_list.count() == 0:
            QMessageBox.warning(self, "Warnung", "Die Queue ist leer.")
            return

        # Output-Verzeichnis wählen
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Ausgabeverzeichnis wählen",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not output_dir:
            return

        # Progress Dialog
        progress = QProgressDialog(
            "Verarbeite Bilder...", 
            "Abbrechen", 
            0, 
            self.queue.queue_list.count(),
            self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        
        failed_images = []
        
        for i in range(self.queue.queue_list.count()):
            if progress.wasCanceled():
                break
            
            # Hole das aktuelle Item und Widget
            item = self.queue.queue_list.item(i)
            widget = self.queue.queue_list.itemWidget(item)
            
            if not widget or not widget.filepath:
                continue
            
            input_path = widget.filepath
            
            if input_path not in self.queue.image_options:
                print(f"Keine Optionen gefunden für: {input_path}")
                continue
            
            options = self.queue.image_options[input_path]
            
            # Ausgabedateiname erstellen
            original_filename = os.path.basename(input_path)
            name, _ = os.path.splitext(original_filename)
            new_filename = f"AD-{name}.{options['format'].lower()}"
            output_path = os.path.join(output_dir, new_filename)
            
            # Bild verarbeiten
            success, error, _ = ImageProcessor.optimize_image(
                input_path,
                output_path,
                options
            )
            
            if not success:
                failed_images.append((original_filename, error))
            
            progress.setValue(i + 1)
        
        progress.close()
        
        # Zeige Ergebnisse
        if failed_images:
            error_message = "Folgende Bilder konnten nicht verarbeitet werden:\n\n"
            for filename, error in failed_images:
                error_message += f"- {filename}: {error}\n"
            QMessageBox.warning(self, "Fehler bei der Verarbeitung", error_message)
        else:
            QMessageBox.information(
                self, 
                "Verarbeitung abgeschlossen",
                "Alle Bilder wurden erfolgreich verarbeitet."
            )

    def add_selected_to_queue(self):
        selected_images = self.workspace.get_selected_images()
        if not selected_images:
            QMessageBox.warning(
                self,
                "Keine Auswahl",
                "Bitte wähle zuerst Bilder aus."
            )
            return

        added_count = 0
        already_in_queue = 0
        
        for image in selected_images:
            if self.queue.add_image(image):
                added_count += 1
            else:
                already_in_queue += 1

        if already_in_queue > 0:
            QMessageBox.information(
                self,
                "Hinweis",
                f"{added_count} Bilder zur Queue hinzugefügt.\n"
                f"{already_in_queue} Bilder waren bereits in der Queue."
            )

    def update_image_options(self, adjustments):
        """Aktualisiert die Bildoptionen für ausgewählte Bilder in der Queue"""
        for i in range(self.queue.queue_list.count()):
            item = self.queue.queue_list.item(i)
            if item.isSelected():
                path = item.text()
                if path in self.queue.image_options:
                    self.queue.image_options[path]['adjustments'] = adjustments
```

### File: src\ui\preview_window.py
```
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSlider, QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PIL import Image
from io import BytesIO
import os

class ImageComparisonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_pixmap = None
        self.processed_pixmap = None
        self.slider_position = 50
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Container für die Bildvorschau
        self.image_container = QFrame()
        self.image_container.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
        """)
        self.image_container.setMinimumSize(400, 300)
        self.image_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        # Überschreibe paintEvent des Containers
        self.image_container.paintEvent = self.container_paint_event
        
        # Info-Labels
        info_layout = QHBoxLayout()
        self.original_info = QLabel("Original: --")
        self.processed_info = QLabel("Optimiert: --")
        info_layout.addWidget(self.original_info)
        info_layout.addStretch()
        info_layout.addWidget(self.processed_info)
        
        # Schieberegler mit angepasstem Style
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.update_comparison)
        self.slider.setStyleSheet("""
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
        
        # Label für Slider-Position
        self.slider_label = QLabel("50%")
        self.slider.valueChanged.connect(
            lambda v: self.slider_label.setText(f"{v}%")
        )
        
        # Slider-Layout mit Label
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.slider_label)
        
        # Layout zusammensetzen
        main_layout.addWidget(self.image_container, stretch=1)
        main_layout.addLayout(info_layout)
        main_layout.addLayout(slider_layout)

    def container_paint_event(self, event):
        """Paint-Event für den Container"""
        if not self.original_pixmap or not self.processed_pixmap:
            return
            
        painter = QPainter(self.image_container)
        container_rect = self.image_container.rect()
        
        # Bilder auf Container-Größe skalieren
        scaled_original = self.original_pixmap.scaled(
            container_rect.width(),
            container_rect.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        scaled_processed = self.processed_pixmap.scaled(
            container_rect.width(),
            container_rect.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Berechne zentrierte Position
        x_offset = (container_rect.width() - scaled_original.width()) // 2
        y_offset = (container_rect.height() - scaled_original.height()) // 2
        
        # Berechne Split-Position
        split_pos = int(scaled_original.width() * (self.slider_position / 100))
        
        # Zeichne Original (links)
        painter.drawPixmap(
            QRect(x_offset, y_offset, split_pos, scaled_original.height()),
            scaled_original,
            QRect(0, 0, split_pos, scaled_original.height())
        )
        
        # Zeichne verarbeitetes Bild (rechts)
        painter.drawPixmap(
            QRect(x_offset + split_pos, y_offset, 
                 scaled_processed.width() - split_pos, scaled_processed.height()),
            scaled_processed,
            QRect(split_pos, 0, scaled_processed.width() - split_pos, scaled_processed.height())
        )
        
        # Zeichne Trennlinie
        pen = painter.pen()
        pen.setColor(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(
            x_offset + split_pos, y_offset,
            x_offset + split_pos, y_offset + scaled_original.height()
        )

    def update_comparison(self):
        """Aktualisiert die Vorschau basierend auf Schieberposition"""
        self.slider_position = self.slider.value()
        self.image_container.update()  # Nur Container neu zeichnen

    def set_images(self, original_path, processed_pixmap, processed_size):
        """Lädt Original- und verarbeitetes Bild"""
        self.original_pixmap = QPixmap(original_path)
        self.processed_pixmap = processed_pixmap
        
        # Größeninformationen aktualisieren
        original_size = os.path.getsize(original_path) / 1024  # KB
        reduction = ((original_size - processed_size) / original_size) * 100
        
        self.original_info.setText(f"Original: {original_size:.1f} KB")
        self.processed_info.setText(
            f"Optimiert: {processed_size:.1f} KB (-{reduction:.1f}%)")
        
        self.image_container.update()

```

### File: src\ui\queue_panel.py
```
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QListWidget, QLabel, QDialog, QComboBox, 
                            QSpinBox, QFormLayout, QMessageBox, QMenu,
                            QCheckBox, QSlider, QSizePolicy, QListWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap
from .preview_window import ImageComparisonWidget
from io import BytesIO
from ..utils.image_processor import ImageProcessor
from datetime import datetime, timedelta
import os

class GlobalOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Globale Bildoptionen")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        
        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["WEBP", "JPEG", "PNG", "ICO"])
        layout.addRow("Format:", self.format_combo)
        
        # Breite
        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, 10000)
        self.width_spin.setSpecialValueText("Original")
        layout.addRow("Breite:", self.width_spin)
        
        # Höhe
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, 10000)
        self.height_spin.setSpecialValueText("Original")
        layout.addRow("Höhe:", self.height_spin)
        
        # Kompression (0-100)
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(0, 100)
        self.compression_slider.setValue(85)  # Standard-Wert
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
        
        # Label für Kompressionswert
        self.compression_label = QLabel("85%")
        self.compression_slider.valueChanged.connect(
            lambda v: self.compression_label.setText(f"{v}%"))
        
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(self.compression_slider)
        compression_layout.addWidget(self.compression_label)
        layout.addRow("Kompression:", compression_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Abbrechen")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addRow(buttons_layout)

class ProcessingStats(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Statistik-Labels
        self.current_file = QLabel("Aktuelle Datei: -")
        self.progress = QLabel("Fortschritt: 0/0")
        self.time_elapsed = QLabel("Vergangene Zeit: 00:00:00")
        self.time_remaining = QLabel("Geschätzte Restzeit: --:--:--")
        self.total_saved = QLabel("Gespeicherte Größe: 0 KB")
        
        for label in [self.current_file, self.progress, self.time_elapsed,
                     self.time_remaining, self.total_saved]:
            layout.addWidget(label)
    
    def update_stats(self, current_file, processed, total, start_time, saved_size):
        self.current_file.setText(f"Aktuelle Datei: {os.path.basename(current_file)}")
        self.progress.setText(f"Fortschritt: {processed}/{total}")
        
        elapsed = datetime.now() - start_time
        self.time_elapsed.setText(f"Vergangene Zeit: {str(elapsed).split('.')[0]}")
        
        if processed > 0:
            avg_time_per_file = elapsed.total_seconds() / processed
            remaining_files = total - processed
            estimated_remaining = timedelta(seconds=avg_time_per_file * remaining_files)
            self.time_remaining.setText(f"Geschätzte Restzeit: {str(estimated_remaining).split('.')[0]}")
        
        self.total_saved.setText(f"Gespeicherte Größe: {saved_size/1024/1024:.1f} MB")

class QueueListItem(QWidget):
    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 8, 8, 8)
        layout.setSpacing(10)
        
        self.checkbox = QCheckBox()
        self.label = QLabel(os.path.basename(filepath))
        self.filepath = filepath
        
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 4px;
            }
            QLabel {
                color: palette(text);
                padding: 4px;
            }
            QCheckBox {
                padding: 4px;
            }
        """)
        
        self.label.setToolTip(filepath)
        
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label, 1)
        
        self.setMinimumHeight(40)

class QueuePanel(QWidget):
    process_started = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.image_options = {}
        self.current_preview_path = None
        self.current_settings = {
            'format': 'WEBP',
            'width': 0,
            'height': 0,
            'compression': 85,
            'adjustments': {
                'brightness': 1.0,
                'contrast': 1.0,
                'saturation': 1.0
            },
            'rotation': 0,
            'flip': None
        }
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header section with title only (removed options button)
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        title = QLabel("Warteschlange")
        title.setStyleSheet("""
            QLabel {
                color: palette(text);
                font-size: 16px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title)
        layout.addWidget(header)
        
        # Toolbar über der Liste
        queue_toolbar = QHBoxLayout()
        self.select_all_btn = QPushButton("Alle auswählen")
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        self.apply_to_selected_btn = QPushButton("Auf Ausgewählte anwenden")
        self.apply_to_selected_btn.clicked.connect(self.apply_settings_to_selected)
        
        queue_toolbar.addWidget(self.select_all_btn)
        queue_toolbar.addWidget(self.apply_to_selected_btn)
        queue_toolbar.addStretch()
        layout.addLayout(queue_toolbar)
        
        # Queue List mit Styling für mehr Abstand
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("""
            QListWidget {
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(base);
                padding: 2px;
            }
            QListWidget::item {
                border-bottom: 1px solid palette(mid);
                padding: 1px 4px;
                margin: 2px 2px;
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: palette(midlight);
            }
        """)
        self.queue_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.queue_list.customContextMenuRequested.connect(self.show_context_menu)
        self.queue_list.currentItemChanged.connect(self.update_preview)
        layout.addWidget(self.queue_list)
        
        # Vorschau-Widget
        self.preview = ImageComparisonWidget()
        self.preview.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.preview.setMinimumHeight(300)
        layout.addWidget(self.preview)
        
        # Bottom toolbar with action buttons
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Remove button
        self.remove_btn = QPushButton()
        self.remove_btn.setIcon(QIcon("src/assets/icons/remove-image.png"))
        self.remove_btn.setIconSize(QSize(24, 24))
        self.remove_btn.setFixedSize(40, 40)
        self.remove_btn.setToolTip("Ausgewählte Bilder entfernen")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(button);
                border: 1px solid palette(mid);
                border-radius: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: palette(midlight);
            }
        """)
        
        # Start button
        self.start_btn = QPushButton()
        self.start_btn.setIcon(QIcon("src/assets/icons/start.png"))
        self.start_btn.setIconSize(QSize(24, 24))
        self.start_btn.setFixedSize(40, 40)
        self.start_btn.setToolTip("Verarbeitung starten")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(button);
                border: 1px solid palette(mid);
                border-radius: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: palette(midlight);
            }
        """)
        
        toolbar_layout.addWidget(self.remove_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.start_btn)
        
        layout.addWidget(toolbar)
        
        # Connect signals
        self.remove_btn.clicked.connect(self.remove_selected)
        self.start_btn.clicked.connect(self.start_processing)
    
    def show_context_menu(self, position):
        menu = QMenu()
        remove_action = QAction("Entfernen", self)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_action)
        
        clear_action = QAction("Queue leeren", self)
        clear_action.triggered.connect(self.clear_queue)
        menu.addAction(clear_action)
        
        menu.exec(self.queue_list.mapToGlobal(position))
    
    def add_image(self, filepath):
        """Fügt ein Bild zur Queue hinzu"""
        if filepath not in [self.queue_list.itemWidget(self.queue_list.item(i)).filepath 
                          for i in range(self.queue_list.count())]:
            item = QListWidgetItem(self.queue_list)
            widget = QueueListItem(filepath)
            item.setSizeHint(widget.sizeHint())
            self.queue_list.addItem(item)
            self.queue_list.setItemWidget(item, widget)
            
            # Kopiere die aktuellen Einstellungen für dieses Bild
            self.image_options[filepath] = self.get_current_settings()
            return True
        return False

    def toggle_select_all(self):
        """Wählt alle Bilder aus oder ab"""
        select_all = self.select_all_btn.text() == "Alle auswählen"
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            widget = self.queue_list.itemWidget(item)
            widget.checkbox.setChecked(select_all)
        self.select_all_btn.setText("Alle abwählen" if select_all else "Alle auswählen")

    def get_selected_files(self):
        """Gibt eine Liste aller ausgewählten Dateien zurück"""
        selected = []
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            widget = self.queue_list.itemWidget(item)
            if widget and widget.filepath and widget.checkbox.isChecked():
                selected.append(widget.filepath)
        return selected

    def get_current_settings(self):
        """Gibt die aktuellen Einstellungen zurück"""
        return self.current_settings.copy()

    def update_current_settings(self, settings_type, value):
        """Aktualisiert die aktuellen Einstellungen"""
        if isinstance(settings_type, dict):
            self.current_settings.update(settings_type)
        else:
            if '.' in settings_type:
                # Für verschachtelte Einstellungen wie 'adjustments.brightness'
                main_key, sub_key = settings_type.split('.')
                if main_key not in self.current_settings:
                    self.current_settings[main_key] = {}
                self.current_settings[main_key][sub_key] = value
            else:
                self.current_settings[settings_type] = value

    def apply_settings_to_selected(self):
        """Wendet die aktuellen Einstellungen auf alle ausgewählten Bilder an"""
        selected_files = self.get_selected_files()
        if not selected_files:
            QMessageBox.warning(self, "Warnung", 
                              "Bitte wähle mindestens ein Bild aus.")
            return
            
        current_settings = self.get_current_settings()
        
        # Auf alle ausgewählten Bilder anwenden
        for filepath in selected_files:
            self.image_options[filepath].update(current_settings)
            
        # Aktualisiere die Vorschau des aktuell ausgewählten Bildes
        current_item = self.queue_list.currentItem()
        if current_item:
            self.update_preview(current_item, None)
            
        QMessageBox.information(self, "Erfolg", 
                              f"Einstellungen auf {len(selected_files)} Bilder angewendet.")

    def start_processing(self):
        if self.queue_list.count() == 0:
            QMessageBox.warning(self, "Warnung", 
                              "Die Queue ist leer. Bitte füge zuerst Bilder hinzu.")
            return
        self.process_started.emit()
    
    def clear_queue(self):
        self.queue_list.clear()
        self.image_options.clear()
    
    def update_preview(self, current, previous):
        """Wird aufgerufen, wenn ein neues Bild in der Queue ausgewählt wird"""
        if not current:
            self.preview.setVisible(False)
            self.current_preview_path = None
            return
            
        widget = self.queue_list.itemWidget(current)
        if not widget:
            return

        input_path = widget.filepath
        self.current_preview_path = input_path
        print(f"Versuche Bild zu laden: {input_path}")
        
        # Lade die spezifischen Einstellungen für dieses Bild
        if input_path in self.image_options:
            # Verwende die gespeicherten Einstellungen für dieses Bild
            self.update_preview_with_options(self.image_options[input_path])
        else:
            # Verwende die Standard-Einstellungen
            self.image_options[input_path] = self.get_current_settings()
            self.update_preview_with_options()

    def update_preview_with_options(self, options=None):
        """Aktualisiert die Vorschau mit den gegebenen Optionen"""
        if not self.current_preview_path:
            return
            
        current_item = self.queue_list.currentItem()
        if not current_item:
            return

        widget = self.queue_list.itemWidget(current_item)
        if not widget:
            return

        input_path = widget.filepath
        self.current_preview_path = input_path
        
        # Wenn keine Optionen übergeben wurden, aktuelle Optionen verwenden
        if options is None:
            options = self.get_current_settings()
        else:
            # Optionen mit den bestehenden Optionen zusammenführen
            current_options = self.get_current_settings()
            current_options.update(options)
            options = current_options

        # Temporäres verarbeitetes Bild erstellen
        temp_output = BytesIO()
        
        success, error, stats = ImageProcessor.optimize_image(
            input_path,
            temp_output,
            options
        )
        
        if success:
            temp_output.seek(0)
            processed_size = len(temp_output.getvalue()) / 1024  # KB
            
            temp_pixmap = QPixmap()
            success = temp_pixmap.loadFromData(temp_output.getvalue())
            
            if not temp_pixmap.isNull():
                self.preview.set_images(input_path, temp_pixmap, processed_size)
                self.preview.setVisible(True)
            else:
                self.preview.setVisible(False)
        else:
            print(f"Vorschau-Aktualisierung fehlgeschlagen: {error}")
            self.preview.setVisible(False)

    def apply_adjustments(self, adjustments):
        """Wendet neue Bildanpassungen auf die Vorschau an"""
        self.update_current_settings('adjustments', adjustments)
        self.update_preview_with_options({'adjustments': adjustments})

    def apply_rotation(self, angle):
        """Wendet neue Rotation auf die Vorschau an"""
        self.update_current_settings('rotation', angle)
        self.update_preview_with_options({'rotation': angle})

    def apply_flip(self, flip_type):
        """Wendet neue Spiegelung auf die Vorschau an"""
        self.update_current_settings('flip', flip_type)
        self.update_preview_with_options({'flip': flip_type})

    def update_format(self, format):
        """Aktualisiert das Format"""
        self.update_current_settings('format', format)
        self.update_preview_with_options({'format': format})

    def update_size(self, size):
        """Aktualisiert die Größeneinstellungen"""
        self.update_current_settings('width', size.get('width', 0))
        self.update_current_settings('height', size.get('height', 0))
        self.update_preview_with_options(size)

    def update_compression(self, value):
        """Aktualisiert die Kompressionseinstellung"""
        self.update_current_settings('compression', value)
        self.update_preview_with_options({'compression': value})

    def process_images(self):
        """Verarbeitet alle Bilder in der Queue"""
        # Entweder alle oder nur ausgewählte Bilder verarbeiten
        files_to_process = self.get_selected_files()
        if not files_to_process:  # Wenn keine ausgewählt, alle verarbeiten
            files_to_process = [self.queue_list.itemWidget(
                self.queue_list.item(i)).filepath 
                for i in range(self.queue_list.count())]
        
        if not files_to_process:
            QMessageBox.warning(self, "Warnung", "Die Queue ist leer.")
            return
            
        # ... (Rest des Verarbeitungscodes) ...

    def remove_selected(self):
        """Entfernt ausgewählte Bilder aus der Queue"""
        selected_files = self.get_selected_files()
        if not selected_files:
            QMessageBox.warning(self, "Warnung", 
                              "Bitte wähle mindestens ein Bild aus.")
            return

        # Bilder aus der Queue und den Optionen entfernen
        items_to_remove = []
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            widget = self.queue_list.itemWidget(item)
            if widget and widget.filepath in selected_files:
                items_to_remove.append(item)
                if widget.filepath in self.image_options:
                    del self.image_options[widget.filepath]

        # Items aus der Liste entfernen
        for item in items_to_remove:
            self.queue_list.takeItem(self.queue_list.row(item))

        # Vorschau aktualisieren falls nötig
        if self.queue_list.count() == 0:
            self.preview.setVisible(False)
        elif not self.queue_list.currentItem():
            self.queue_list.setCurrentRow(0)

```

### File: src\ui\workspace.py
```
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMenu, QApplication, QFrame,
                            QScrollArea, QToolBar, QSizePolicy, QLayout,
                            QRubberBand, QInputDialog, QMessageBox,
                            QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRect, QPoint
from PyQt6.QtGui import (QDropEvent, QDragEnterEvent, QPixmap, QColor,
                        QPainter, QIcon, QAction, QCursor, QPen)
import os
from PIL import Image
from io import BytesIO

class ImageTile(QFrame):
    clicked = pyqtSignal(object, QPoint)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.selected = False
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Container für Thumbnail
        self.thumbnail_container = QFrame()
        self.thumbnail_container.setFixedSize(180, 180)
        self.thumbnail_container.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }
        """)
        
        # Thumbnail
        self.thumbnail = QLabel(self.thumbnail_container)
        try:
            if self.image_path.lower().endswith(('.heic', '.heif')):
                heic_img = Image.open(self.image_path)
                heic_img = heic_img.convert('RGB')
                buffer = BytesIO()
                heic_img.save(buffer, format='PNG')
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
            else:
                pixmap = QPixmap(self.image_path)
                
            scaled_pixmap = pixmap.scaled(
                160, 160,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.thumbnail.setPixmap(scaled_pixmap)
        except Exception as e:
            self.thumbnail.setText("Keine Vorschau\nverfügbar")
            self.thumbnail.setStyleSheet("QLabel { color: palette(text); }")
            
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail.setFixedSize(180, 180)
        
        # Dateiname
        filename = os.path.basename(self.image_path)
        if len(filename) > 20:
            filename = filename[:17] + "..."
        self.name_label = QLabel(filename)
        self.name_label.setStyleSheet("QLabel { color: palette(text); }")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.thumbnail_container)
        layout.addWidget(self.name_label)
        
        self.setFixedSize(200, 230)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: palette(alternate-base);
            }
        """)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Roter Rahmen
            painter.setPen(QPen(QColor("#ff4444"), 2))  # Kräftiges Rot
            painter.drawRect(1, 1, self.width()-2, self.height()-2)
            
            # Roter Hintergrund mit Transparenz
            painter.fillRect(self.rect(), QColor(255, 68, 68, 30))  # Rot mit 30% Opacity
            
            # Auswahlindikator (Checkbox) in der oberen linken Ecke
            checkbox_rect = QRect(8, 8, 20, 20)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#ff4444"))  # Gleiche Rotfarbe
            painter.drawEllipse(checkbox_rect)
            
            # Weißes Häkchen
            painter.setPen(QPen(QColor("white"), 2))
            painter.drawText(checkbox_rect, Qt.AlignmentFlag.AlignCenter, "✓")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self, event.globalPosition().toPoint())
            
    def enterEvent(self, event):
        if not self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 68, 68, 0.1);
                    border-radius: 8px;
                }
            """)
    
    def leaveEvent(self, event):
        if not self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border-radius: 8px;
                }
            """)

    def setSelected(self, selected):
        self.selected = selected
        if selected:
            self.setProperty("selected", True)
            self.setStyleSheet("""
                QFrame[selected="true"] {
                    background-color: palette(highlight);
                }
                QFrame QLabel {
                    color: palette(text);
                }
            """)
        else:
            self.setProperty("selected", False)
            self.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                }
                QFrame:hover {
                    background-color: palette(alternate-base);
                }
                QFrame QLabel {
                    color: palette(text);
                }
            """)
        
        self.style().unpolish(self)
        self.style().polish(self)

class DottedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dot_spacing = 20  # Abstand zwischen den Punkten
        self.dot_size = 2      # Größe der Punkte
        self.dot_color = QColor(200, 200, 200)  # Hellgrau für die Punkte
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Stift für die Punkte konfigurieren
        pen = QPen(self.dot_color)
        pen.setWidth(self.dot_size)
        painter.setPen(pen)
        
        # Zeichenbereich bestimmen
        width = self.width()
        height = self.height()
        
        # Punkte zeichnen
        for x in range(0, width, self.dot_spacing):
            for y in range(0, height, self.dot_spacing):
                painter.drawPoint(x, y)

class WorkspacePanel(QWidget):
    images_added = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.tiles = {}
        self.selected_tiles = set()
        self.rubberband = None
        self.origin = None
        self.last_selected = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container für Empty State mit gepunktetem Hintergrund
        self.empty_container = DottedBackground()
        empty_layout = QVBoxLayout(self.empty_container)
        
        # Empty State Icon
        self.empty_state = QLabel()
        empty_icon = QIcon("src/assets/icons/add-image.png")
        pixmap = empty_icon.pixmap(QSize(128, 128))
        self.empty_state.setPixmap(pixmap)
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Zentrieren des Empty States
        empty_layout.addStretch()
        empty_layout.addWidget(self.empty_state, alignment=Qt.AlignmentFlag.AlignCenter)
        empty_layout.addStretch()
        
        # Content Widget mit gepunktetem Hintergrund
        self.content = DottedBackground()
        self.flow_layout = FlowLayout(self.content)
        self.flow_layout.setSpacing(16)
        self.flow_layout.setContentsMargins(16, 16, 16, 16)
        
        # Scroll-Bereich
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.content)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Stack für Empty State und Content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.empty_container)
        self.stack.addWidget(self.scroll)
        layout.addWidget(self.stack)
        
        self.setAcceptDrops(True)
    
    def update_empty_state(self):
        """Aktualisiert die Anzeige des Empty States basierend auf vorhandenen Bildern"""
        if len(self.tiles) == 0:
            self.stack.setCurrentWidget(self.empty_container)
        else:
            self.stack.setCurrentWidget(self.scroll)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.ico', '.heic', '.heif'}
        
        new_images = []
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions and file not in self.tiles:
                tile = ImageTile(file)
                tile.clicked.connect(self.on_tile_clicked)
                self.flow_layout.addWidget(tile)
                self.tiles[file] = tile
                new_images.append(file)
        
        # Empty State aktualisieren
        self.update_empty_state()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubberband = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self.rubberband.setGeometry(QRect(self.origin, QSize()))
            self.rubberband.show()
            
            # Clear selection if no modifier keys
            if not (QApplication.keyboardModifiers() & 
                   (Qt.KeyboardModifier.ControlModifier | 
                    Qt.KeyboardModifier.ShiftModifier)):
                self.clear_selection()
    
    def mouseMoveEvent(self, event):
        if self.rubberband:
            selection_rect = QRect(self.origin, event.pos()).normalized()
            self.rubberband.setGeometry(selection_rect)
            
            # Select tiles within rubber band
            for tile in self.tiles.values():
                tile_rect = QRect(tile.mapTo(self, QPoint(0, 0)), tile.size())
                if selection_rect.intersects(tile_rect):
                    if tile not in self.selected_tiles:
                        self.selected_tiles.add(tile)
                        tile.selected = True
                        tile.update()
                elif tile in self.selected_tiles and not (
                    QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier):
                    self.selected_tiles.remove(tile)
                    tile.selected = False
                    tile.update()
    
    def mouseReleaseEvent(self, event):
        if self.rubberband:
            self.rubberband.hide()
            self.rubberband = None
    
    def on_tile_clicked(self, tile, pos):
        modifiers = QApplication.keyboardModifiers()
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Toggle selection
            if tile in self.selected_tiles:
                self.selected_tiles.remove(tile)
                tile.selected = False
            else:
                self.selected_tiles.add(tile)
                tile.selected = True
                self.last_selected = tile
        
        elif modifiers & Qt.KeyboardModifier.ShiftModifier and self.last_selected:
            # Range selection
            start_idx = list(self.tiles.values()).index(self.last_selected)
            end_idx = list(self.tiles.values()).index(tile)
            tiles_list = list(self.tiles.values())
            
            for idx in range(min(start_idx, end_idx), max(start_idx, end_idx) + 1):
                current_tile = tiles_list[idx]
                self.selected_tiles.add(current_tile)
                current_tile.selected = True
        
        else:
            # Single selection
            self.clear_selection()
            self.selected_tiles.add(tile)
            tile.selected = True
            self.last_selected = tile
        
        tile.update()
        
        # Show context menu on right click
        if QApplication.mouseButtons() & Qt.MouseButton.RightButton:
            self.show_context_menu(pos)
    
    def clear_selection(self):
        for tile in self.selected_tiles:
            tile.selected = False
            tile.update()
        self.selected_tiles.clear()
        self.last_selected = None
    
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        add_to_queue = menu.addAction("Zur Queue hinzufügen")
        add_to_queue.triggered.connect(self.add_selected_to_queue)
        
        if len(self.selected_tiles) > 0:
            menu.addSeparator()
            
            rename_action = menu.addAction("Umbenennen")
            rename_action.triggered.connect(self.rename_selected_files)
            
            select_all = menu.addAction("Alle auswählen")
            select_all.triggered.connect(self.select_all)
            
            clear_selection = menu.addAction("Auswahl aufheben")
            clear_selection.triggered.connect(self.clear_selection)
        
        menu.exec(pos)
    
    def select_all(self):
        for tile in self.tiles.values():
            self.selected_tiles.add(tile)
            tile.selected = True
            tile.update()
        self.last_selected = list(self.tiles.values())[-1] if self.tiles else None
    
    def add_selected_to_queue(self):
        selected_paths = [tile.image_path for tile in self.selected_tiles]
        if selected_paths:
            self.images_added.emit(selected_paths)
    
    def rename_selected_files(self):
        if not self.selected_tiles:
            return
            
        new_name, ok = QInputDialog.getText(
            self,
            "Dateien umbenennen",
            "Neuer Dateiname (bei mehreren Dateien wird automatisch nummeriert):"
        )
        
        if not ok or not new_name:
            return
            
        # Sortiere die ausgewhlten Tiles nach Dateinamen
        selected_tiles = sorted(list(self.selected_tiles), 
                              key=lambda t: t.image_path)
        
        for i, tile in enumerate(selected_tiles, 1):
            old_path = tile.image_path
            dir_path = os.path.dirname(old_path)
            ext = os.path.splitext(old_path)[1]
            
            # Generiere neuen Dateinamen
            if len(selected_tiles) > 1:
                new_filename = f"{new_name}-{i}{ext}"
            else:
                new_filename = f"{new_name}{ext}"
                
            new_path = os.path.join(dir_path, new_filename)
            
            try:
                # Umbenennen der Datei
                os.rename(old_path, new_path)
                
                # Update Tile
                tile.image_path = new_path
                tile.name_label.setText(
                    new_filename if len(new_filename) <= 20 
                    else new_filename[:17] + "..."
                )
                
                # Update tiles dict
                self.tiles.pop(old_path)
                self.tiles[new_path] = tile
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Fehler",
                    f"Fehler beim Umbenennen von {os.path.basename(old_path)}: {str(e)}"
                )

    # Neue Methode zum Abrufen der ausgewählten Bilder
    def get_selected_images(self):
        """Gibt eine Liste der Pfade der ausgewählten Bilder zurück"""
        return [tile.image_path for tile in self.tiles.values() if tile.selected]

class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.spacing_x = 10
        self.spacing_y = 10
    
    def addItem(self, item):
        self.items.append(item)
    
    def count(self):
        return len(self.items)
    
    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
        return size
    
    def doLayout(self, rect, test_only=False):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.items:
            next_x = x + item.sizeHint().width() + spacing
            
            if next_x - spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                next_x = x + item.sizeHint().width() + spacing
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()

```

### File: src\utils\image_processor.py
```
from PIL import Image, ImageEnhance
import os
import piexif
from io import BytesIO
import pillow_heif
import time
import logging

# Logger Setup
logging.basicConfig(
    filename='image_processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# HEIF-Registrierung
pillow_heif.register_heif_opener()

class ImageProcessor:
    @staticmethod
    def adjust_image(image, brightness=1.0, contrast=1.0, saturation=1.0):
        """Passt Helligkeit, Kontrast und Sättigung des Bildes an"""
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        return image

    @staticmethod
    def rotate_image(image, angle):
        """Rotiert das Bild um den angegebenen Winkel"""
        return image.rotate(angle, expand=True)

    @staticmethod
    def flip_image(image, horizontal=True):
        """Spiegelt das Bild horizontal oder vertikal"""
        if horizontal:
            return image.transpose(Image.FLIP_LEFT_RIGHT)
        return image.transpose(Image.FLIP_TOP_BOTTOM)

    @staticmethod
    def crop_image(image, box):
        """Schneidet einen Bereich aus dem Bild aus"""
        return image.crop(box)

    @staticmethod
    def optimize_image(image_path, output_path, options):
        start_time = time.time()
        original_size = os.path.getsize(image_path)
        
        try:
            logging.info(f"Starte Verarbeitung von: {image_path}")
            img = Image.open(image_path)
            
            # HEIC nach RGB konvertieren wenn nötig
            if img.format == 'HEIF':
                img = img.convert('RGB')
            
            # Bildanpassungen anwenden
            if 'adjustments' in options:
                adj = options['adjustments']
                img = ImageProcessor.adjust_image(
                    img,
                    brightness=adj.get('brightness', 1.0),
                    contrast=adj.get('contrast', 1.0),
                    saturation=adj.get('saturation', 1.0)
                )
            
            # Rotation anwenden
            if 'rotation' in options and options['rotation']:
                img = img.rotate(options['rotation'], expand=True)
            
            # Spiegelung anwenden
            if 'flip' in options and options['flip']:
                if options['flip'] == 'horizontal':
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif options['flip'] == 'vertical':
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Größe anpassen wenn nötig
            if options.get('width') or options.get('height'):
                img = ImageProcessor._resize_image(
                    img, 
                    options.get('width', 0), 
                    options.get('height', 0),
                    options.get('width_unit', 'Pixel'),
                    options.get('height_unit', 'Pixel')
                )

            # Format bestimmen
            output_format = options['format'].upper()
            compression = options.get('compression', 85)
            quality = 100 - compression
            
            # Wenn gleiches Format wie Original, dann Format aus Originaldatei verwenden
            if output_format == img.format:
                output_format = img.format
            # Sonst Format aus den Optionen verwenden und normalisieren
            elif output_format in ['JPEG', 'JPG']:
                output_format = 'JPEG'
            elif output_format == 'WEBP':
                output_format = 'WEBP'
            elif output_format == 'PNG':
                output_format = 'PNG'
            elif output_format == 'ICO':
                output_format = 'ICO'
            else:
                # Fallback auf JPEG wenn Format unbekannt
                output_format = 'JPEG'
            
            # Speichern mit entsprechendem Format
            if output_format in ['JPEG', 'JPG']:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                img.save(
                    output_path,
                    format=output_format,
                    quality=quality,
                    optimize=True
                )
            
            elif output_format == 'WEBP':
                img.save(
                    output_path,
                    format='WEBP',
                    quality=quality,
                    method=6,
                    lossless=False,
                    exact=False
                )
            
            elif output_format == 'PNG':
                png_compression = int(compression / 11)
                img.save(
                    output_path,
                    format='PNG',
                    optimize=True,
                    compression_level=png_compression
                )
            
            elif output_format == 'ICO':
                sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                img.save(
                    output_path,
                    format='ICO',
                    sizes=sizes
                )
            
            # Statistiken berechnen
            end_time = time.time()
            processing_time = end_time - start_time
            final_size = os.path.getsize(output_path) if isinstance(output_path, str) else len(output_path.getvalue())
            size_reduction = ((original_size - final_size) / original_size) * 100

            stats = {
                'processing_time': processing_time,
                'original_size': original_size,
                'final_size': final_size,
                'size_reduction': size_reduction
            }

            logging.info(f"""
                Verarbeitung abgeschlossen:
                - Datei: {image_path}
                - Verarbeitungszeit: {processing_time:.2f}s
                - Größenreduzierung: {size_reduction:.1f}%
                - Finale Größe: {final_size/1024:.1f}KB
            """)

            return True, None, stats

        except Exception as e:
            logging.error(f"Fehler bei der Verarbeitung von {image_path}: {str(e)}")
            return False, str(e), None
    
    @staticmethod
    def _resize_image(img, width, height, unit="Pixel", keep_aspect=True):
        """
        Passt die Bildgröße unter Beibehaltung des Seitenverhältnisses an.
        """
        original_width, original_height = img.size
        
        # Konvertiere Prozentangaben in Pixel
        if unit == "%" and width > 0:
            width = int(original_width * (width / 100))
            height = int(original_height * (height / 100))
        
        # Wenn eine Dimension 0 ist oder Seitenverhältnis beibehalten werden soll
        if width and not height:
            ratio = width / original_width
            height = int(original_height * ratio)
        elif height and not width:
            ratio = height / original_height
            width = int(original_width * ratio)
        elif not width and not height:
            return img  # Originalgröße beibehalten
        elif keep_aspect:
            # Behalte das Seitenverhältnis bei, verwende die kleinere Dimension
            ratio_w = width / original_width
            ratio_h = height / original_height
            ratio = min(ratio_w, ratio_h)
            width = int(original_width * ratio)
            height = int(original_height * ratio)
        
        # Hochwertige Größenanpassung
        return img.resize(
            (width, height),
            Image.Resampling.LANCZOS
        )
    
    @staticmethod
    def estimate_quality(image_path):
        """
        Schätzt die aktuelle Qualität/Komprimierung eines Bildes.
        """
        img = Image.open(image_path)
        temp_buffer = BytesIO()
        
        # Speichern mit höchster Qualität
        img.save(temp_buffer, format=img.format, quality=100)
        max_size = len(temp_buffer.getvalue())
        
        # Speichern mit aktueller Qualität
        temp_buffer.seek(0)
        temp_buffer.truncate()
        img.save(temp_buffer, format=img.format)
        current_size = len(temp_buffer.getvalue())
        
        # Qualität schätzen
        quality_ratio = current_size / max_size
        
        if quality_ratio > 0.9:
            return "Niedrig"
        elif quality_ratio > 0.7:
            return "Mittel"
        else:
            return "Hoch"

```

End of file
