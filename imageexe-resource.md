# imageexe Resource Summary

Start of file:
Directory of every file in the project
- File: .ignorethese (not included in output)
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
- File: src\ui\main_window.py
- File: src\ui\queue_panel.py
- File: src\ui\workspace.py
- Directory: src\ui\__pycache__ (not included in output)
- File: src\ui\__pycache__\main_window.cpython-312.pyc (not included in output)
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

### File: src\ui\main_window.py
```
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
```

### File: src\ui\queue_panel.py
```
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QListWidget, QLabel, QDialog, QComboBox, 
                            QSpinBox, QFormLayout, QMessageBox, QMenu,
                            QCheckBox, QSlider)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QAction, QIcon

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
        
        if dialog.exec():
            new_options = {
                'format': dialog.format_combo.currentText(),
                'width': dialog.width_spin.value(),
                'height': dialog.height_spin.value(),
                'compression': dialog.compression_slider.value()  # Numerischer Wert
            }
            
            self.global_options = new_options
            
            # Auf alle Bilder in der Queue anwenden
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                self.image_options[item.text()] = new_options.copy()
    
    def start_processing(self):
        if self.queue_list.count() == 0:
            QMessageBox.warning(self, "Warnung", 
                              "Die Queue ist leer. Bitte füge zuerst Bilder hinzu.")
            return
        self.process_started.emit()
    
    def clear_queue(self):
        self.queue_list.clear()
        self.image_options.clear()

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
                ImageTile {
                    background-color: rgba(255, 68, 68, 0.1);  # Leichtes Rot beim Hover
                    border-radius: 8px;
                }
            """)
    
    def leaveEvent(self, event):
        if not self.selected:
            self.setStyleSheet("""
                ImageTile {
                    background-color: transparent;
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
from PIL import Image
import os
import piexif
from io import BytesIO
import pillow_heif

# HEIF-Registrierung
pillow_heif.register_heif_opener()

class ImageProcessor:
    @staticmethod
    def optimize_image(image_path, output_path, options):
        """
        Optimiert ein Bild mit den gegebenen Optionen.
        """
        try:
            # Bild öffnen
            img = Image.open(image_path)
            
            # HEIC nach RGB konvertieren wenn nötig
            if img.format == 'HEIF':
                img = img.convert('RGB')
            
            # Größe anpassen wenn nötig
            if options['width'] or options['height']:
                img = ImageProcessor._resize_image(
                    img, 
                    options['width'], 
                    options['height']
                )
            
            # Format konvertieren und speichern
            output_format = options['format'].upper()
            compression = options.get('compression', 85)
            quality = 100 - compression
            
            if output_format == 'JPEG':
                # Für JPEG: RGB-Modus erzwingen
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                img.save(
                    output_path,
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
                # PNG verwendet 0-9 Skala, 9 = maximale Kompression
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
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _resize_image(img, width, height):
        """
        Passt die Bildgröße unter Beibehaltung des Seitenverhältnisses an.
        """
        original_width, original_height = img.size
        
        if width and not height:
            ratio = width / original_width
            height = int(original_height * ratio)
        elif height and not width:
            ratio = height / original_height
            width = int(original_width * ratio)
        
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
