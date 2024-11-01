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
