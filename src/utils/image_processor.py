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
