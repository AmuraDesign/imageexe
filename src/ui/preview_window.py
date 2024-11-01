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
