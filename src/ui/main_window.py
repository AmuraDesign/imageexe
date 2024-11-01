from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QFileDialog, QMessageBox, 
                           QInputDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from .workspace import WorkspacePanel
from .queue_panel import QueuePanel
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
        
        # Rechte Seite (Queue)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Queue
        self.queue = QueuePanel()
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
    
    def add_images_to_queue(self, image_paths):
        for path in image_paths:
            self.queue.add_image(path)
    
    def process_images(self):
        if self.queue.queue_list.count() == 0:
            return
            
        # Ausgabeordner wählen
        output_dir = QFileDialog.getExistingDirectory(
            self, "Ausgabeordner wählen")
        if not output_dir:
            return
            
        # Dateinamen-Template
        filename_template, ok = QInputDialog.getText(
            self, 
            "Dateinamen-Format",
            "Gib ein Dateinamen-Template ein (z.B. optimized_{filename}):\n"
            "{filename} wird durch den originalen Dateinamen ersetzt",
            text="optimized_{filename}"
        )
        if not ok:
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
            
            input_path = self.queue.queue_list.item(i).text()
            options = self.queue.image_options[input_path]
            
            # Ausgabedateiname erstellen
            original_filename = os.path.basename(input_path)
            name, _ = os.path.splitext(original_filename)
            new_filename = filename_template.replace('{filename}', name)
            output_path = os.path.join(
                output_dir,
                f"{new_filename}.{options['format'].lower()}"
            )
            
            # Bild verarbeiten
            success, error = ImageProcessor.optimize_image(
                input_path,
                output_path,
                options
            )
            
            if not success:
                failed_images.append((original_filename, error))
            
            progress.setValue(i + 1)
        
        progress.close()
        
        # Ergebnisbericht
        if failed_images:
            error_msg = "Folgende Bilder konnten nicht verarbeitet werden:\n\n"
            for filename, error in failed_images:
                error_msg += f"• {filename}: {error}\n"
            QMessageBox.warning(self, "Fehler bei der Verarbeitung", error_msg)
        else:
            QMessageBox.information(
                self,
                "Erfolg",
                f"Alle Bilder wurden erfolgreich verarbeitet und in\n{output_dir}\ngespeichert!"
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