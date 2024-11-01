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
