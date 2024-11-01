from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QFileDialog, QMessageBox, 
                           QInputDialog, QProgressDialog, QApplication)
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
        
        # Modernes Windows 11 Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f8f8;
            }
            QWidget {
                font-family: 'Segoe UI', sans-serif;
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
            QLabel {
                color: #000000;
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
        add_to_queue_btn.setObjectName("primaryButton")
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
        
        # Theme detection
        self.update_theme()
        
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

    def update_theme(self):
        """Updates the application theme based on system settings"""
        app = QApplication.instance()
        
        if app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #202020;
                    color: #ffffff;
                    font-family: 'Segoe UI', sans-serif;
                }
                
                QWidget[cssClass="section-panel"] {
                    background-color: #2d2d2d;
                    border-radius: 8px;
                }
                
                QComboBox, QSpinBox {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #ffffff;
                }
                
                QComboBox:hover, QSpinBox:hover {
                    background-color: #363636;
                    border-color: #60cdff;
                }
                
                QPushButton {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: #ffffff;
                }
                
                QPushButton:hover {
                    background-color: #363636;
                    border-color: #60cdff;
                }
                
                QPushButton[cssClass="accent"] {
                    background-color: #0078d4;
                    border: none;
                    color: #ffffff;
                }
                
                QPushButton[cssClass="accent"]:hover {
                    background-color: #1484d7;
                }
                
                QLabel[cssClass="section-title"] {
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: 500;
                }
                
                QCheckBox {
                    color: #ffffff;
                }
                
                QSlider::groove:horizontal {
                    background: #404040;
                    height: 4px;
                    border-radius: 2px;
                }
                
                QSlider::handle:horizontal {
                    background: #60cdff;
                    border: 2px solid #60cdff;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #202020;
                    font-family: 'Segoe UI', sans-serif;
                }
                
                QWidget[cssClass="section-panel"] {
                    background-color: #ffffff;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }
                
                QComboBox, QSpinBox {
                    background-color: #ffffff;
                    border: 1px solid #d1d1d1;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #202020;
                }
                
                QComboBox:hover, QSpinBox:hover {
                    background-color: #f5f5f5;
                    border-color: #0078d4;
                }
                
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #d1d1d1;
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: #202020;
                }
                
                QPushButton:hover {
                    background-color: #f5f5f5;
                    border-color: #0078d4;
                }
                
                QPushButton[cssClass="accent"] {
                    background-color: #0078d4;
                    border: none;
                    color: #ffffff;
                }
                
                QPushButton[cssClass="accent"]:hover {
                    background-color: #1484d7;
                }
                
                QLabel[cssClass="section-title"] {
                    color: #202020;
                    font-size: 14px;
                    font-weight: 500;
                }
                
                QCheckBox {
                    color: #202020;
                }
                
                QSlider::groove:horizontal {
                    background: #e0e0e0;
                    height: 4px;
                    border-radius: 2px;
                }
                
                QSlider::handle:horizontal {
                    background: #0078d4;
                    border: 2px solid #0078d4;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }
            """)