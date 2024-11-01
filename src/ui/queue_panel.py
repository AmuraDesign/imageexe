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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Modernes Styling
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                padding: 8px;
            }
            QListWidget::item {
                border-bottom: 1px solid #f0f0f0;
                padding: 8px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #e5f3ff;
                color: #000000;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1484d7;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)

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
        # Füge die Einheit zu den Einstellungen hinzu
        self.update_current_settings('width_unit', size.get('unit', 'Pixel'))
        self.update_current_settings('height_unit', size.get('unit', 'Pixel'))
        self.update_preview_with_options({
            'width': size.get('width', 0),
            'height': size.get('height', 0),
            'width_unit': size.get('unit', 'Pixel'),
            'height_unit': size.get('unit', 'Pixel'),
            'keep_aspect': size.get('keep_aspect', True)
        })

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
