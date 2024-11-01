from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QListWidget, QLabel, QDialog, QComboBox, 
                            QSpinBox, QFormLayout, QMessageBox, QMenu,
                            QCheckBox, QSlider, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap
from .preview_window import ImageComparisonWidget
from io import BytesIO
from ..utils.image_processor import ImageProcessor
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

class QueuePanel(QWidget):
    process_started = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.image_options = {}
        self.global_options = {
            'format': 'WEBP',
            'width': 0,
            'height': 0,
            'compression': 85
        }
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header section with title and options
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
        
        # Options Button
        self.options_btn = QPushButton("Globale Optionen")
        self.options_btn.setStyleSheet("""
            QPushButton {
                color: palette(text);
                background-color: palette(button);
                padding: 6px 12px;
                border: 1px solid palette(mid);
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: palette(midlight);
            }
        """)
        header_layout.addWidget(self.options_btn)
        layout.addWidget(header)
        
        # Queue List
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("""
            QListWidget {
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(base);
                color: palette(text);
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid palette(mid);
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QListWidget::item:hover {
                background-color: palette(midlight);
            }
        """)
        self.queue_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.queue_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.queue_list)
        
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
        self.options_btn.clicked.connect(self.show_global_options)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.start_btn.clicked.connect(self.start_processing)
        
        # Vorschau-Widget hinzufügen
        self.preview = ImageComparisonWidget()
        self.preview.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.preview.setMinimumHeight(300)  # Minimale Höhe setzen
        layout.addWidget(self.preview)
        
        # Queue-Liste Auswahl verbinden
        self.queue_list.currentItemChanged.connect(self.update_preview)
    
    def show_context_menu(self, position):
        menu = QMenu()
        remove_action = QAction("Entfernen", self)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_action)
        
        clear_action = QAction("Queue leeren", self)
        clear_action.triggered.connect(self.clear_queue)
        menu.addAction(clear_action)
        
        menu.exec(self.queue_list.mapToGlobal(position))
    
    def add_image(self, image_path):
        # Prüfen ob das Bild bereits in der Queue ist
        for i in range(self.queue_list.count()):
            if self.queue_list.item(i).text() == image_path:
                return False  # Bild bereits in der Queue
        
        self.queue_list.addItem(image_path)
        self.image_options[image_path] = self.global_options.copy()
        return True
    
    def remove_selected(self):
        for item in self.queue_list.selectedItems():
            path = item.text()
            if path in self.image_options:
                self.image_options.pop(path)
            self.queue_list.takeItem(self.queue_list.row(item))
    
    def show_global_options(self):
        dialog = GlobalOptionsDialog(self)
        
        # Aktuelle globale Optionen laden
        dialog.format_combo.setCurrentText(self.global_options['format'])
        dialog.width_spin.setValue(self.global_options['width'])
        dialog.height_spin.setValue(self.global_options['height'])
        dialog.compression_slider.setValue(self.global_options['compression'])
        
        # Verbinde Slider mit Live-Vorschau
        dialog.compression_slider.valueChanged.connect(self.update_preview_compression)
        
        if dialog.exec():
            new_options = {
                'format': dialog.format_combo.currentText(),
                'width': dialog.width_spin.value(),
                'height': dialog.height_spin.value(),
                'compression': dialog.compression_slider.value()
            }
            
            self.global_options = new_options
            
            # Auf alle Bilder in der Queue anwenden
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                self.image_options[item.text()] = new_options.copy()
            
            # Aktualisiere die Vorschau mit den neuen Optionen
            current_item = self.queue_list.currentItem()
            if current_item:
                self.update_preview(current_item, None)
    
    def update_preview_compression(self, value):
        """Aktualisiert die Vorschau wenn sich die Kompression ändert"""
        current_item = self.queue_list.currentItem()
        if current_item:
            # Temporär die Kompressionseinstellung ändern
            temp_options = self.image_options[current_item.text()].copy()
            temp_options['compression'] = value
            
            # Vorschau mit temporären Optionen aktualisieren
            input_path = current_item.text()
            temp_output = BytesIO()
            
            success, _ = ImageProcessor.optimize_image(
                input_path,
                temp_output,
                temp_options
            )
            
            if success:
                temp_output.seek(0)
                processed_size = len(temp_output.getvalue()) / 1024
                
                temp_pixmap = QPixmap()
                temp_pixmap.loadFromData(temp_output.getvalue())
                
                self.preview.set_images(input_path, temp_pixmap, processed_size)
    
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
        """Aktualisiert die Vorschau wenn ein Bild in der Queue ausgewählt wird"""
        if not current:
            self.preview.setVisible(False)
            return
            
        input_path = current.text()
        print(f"Versuche Bild zu laden: {input_path}")  # Debug
        
        # Temporäres verarbeitetes Bild erstellen
        temp_output = BytesIO()
        options = self.image_options[input_path]
        
        success, error = ImageProcessor.optimize_image(
            input_path,
            temp_output,
            options
        )
        
        if success:
            print("Bildoptimierung erfolgreich")  # Debug
            # BytesIO in QPixmap konvertieren
            temp_output.seek(0)
            processed_size = len(temp_output.getvalue()) / 1024  # KB
            
            temp_pixmap = QPixmap()
            success = temp_pixmap.loadFromData(temp_output.getvalue())
            print(f"Pixmap geladen: {success}")  # Debug
            
            if not temp_pixmap.isNull():
                print(f"Pixmap Größe: {temp_pixmap.width()}x{temp_pixmap.height()}")  # Debug
                self.preview.set_images(input_path, temp_pixmap, processed_size)
                self.preview.setVisible(True)
            else:
                print("Fehler: Pixmap ist null")  # Debug
                self.preview.setVisible(False)
        else:
            print(f"Bildoptimierung fehlgeschlagen: {error}")  # Debug
            self.preview.setVisible(False)
