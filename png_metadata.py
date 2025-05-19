from PIL import Image
import piexif
import os

def show_image_metadata(image_path):
    try:
        # Abrir la imagen
        img = Image.open(image_path)
        
        # Extraer los metadatos EXIF
        exif_dict = piexif.load(img.filename)
        
        # Mostrar los campos más comunes
        print("\nMetadatos de la imagen:")
        print("-" * 50)
        
        # Mostrar los campos 0th (basicos)
        print("\nMetadatos Básicos:")
        print("Artista:", exif_dict["0th"].get(piexif.ImageIFD.Artist, "No especificado"))
        print("Fecha/Hora:", exif_dict["0th"].get(piexif.ImageIFD.DateTime, "No especificado"))
        print("Copyright:", exif_dict["0th"].get(piexif.ImageIFD.Copyright, "No especificado"))
        print("Descripción:", exif_dict["0th"].get(piexif.ImageIFD.ImageDescription, "No especificado"))
        print("Software:", exif_dict["0th"].get(piexif.ImageIFD.Software, "No especificado"))
        
        # Mostrar los campos Exif (camara)
        print("\nMetadatos de Cámara:")
        print("Marca:", exif_dict["Exif"].get(piexif.ExifIFD.Make, "No especificado"))
        print("Modelo:", exif_dict["Exif"].get(piexif.ExifIFD.Model, "No especificado"))
        
        return exif_dict
    except Exception as e:
        print(f"Error al leer los metadatos: {str(e)}")
        return None

def update_image_metadata(image_path, new_metadata):
    try:
        # Abrir la imagen
        img = Image.open(image_path)
        
        # Cargar los metadatos existentes
        exif_dict = piexif.load(img.filename)
        
        # Actualizar los campos especificados
        if "Artist" in new_metadata:
            exif_dict["0th"][piexif.ImageIFD.Artist] = new_metadata["Artist"].encode('utf-8')
        if "DateTime" in new_metadata:
            exif_dict["0th"][piexif.ImageIFD.DateTime] = new_metadata["DateTime"].encode('utf-8')
        if "Copyright" in new_metadata:
            exif_dict["0th"][piexif.ImageIFD.Copyright] = new_metadata["Copyright"].encode('utf-8')
        if "ImageDescription" in new_metadata:
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = new_metadata["ImageDescription"].encode('utf-8')
        if "Software" in new_metadata:
            exif_dict["0th"][piexif.ImageIFD.Software] = new_metadata["Software"].encode('utf-8')
        if "Make" in new_metadata:
            exif_dict["Exif"][piexif.ExifIFD.Make] = new_metadata["Make"].encode('utf-8')
        if "Model" in new_metadata:
            exif_dict["Exif"][piexif.ExifIFD.Model] = new_metadata["Model"].encode('utf-8')
        
        # Crear el nombre del archivo de salida
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_edited.png"
        
        # Guardar la imagen con los nuevos metadatos
        piexif.insert(piexif.dump(exif_dict), image_path, output_path)
        
        print(f"\nNueva imagen guardada en: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error al actualizar los metadatos: {str(e)}")
        return None

if __name__ == "__main__":
    print("Bienvenido al Inspector de Metadatos PNG!")
    print("-" * 50)
    
    # Pedir la ruta de la imagen
    image_path = input("\nPor favor, ingrese la ruta de la imagen PNG: ")
    
    # Mostrar los metadatos actuales
    exif_dict = show_image_metadata(image_path)
    
    if exif_dict:
        # Pedir los nuevos metadatos
        print("\nIngrese los nuevos valores para los metadatos (deje vacío para mantener el valor actual):")
        new_metadata = {}
        
        # Pedir cada campo
        new_metadata["Artist"] = input("Artista: ")
        new_metadata["DateTime"] = input("Fecha/Hora: ")
        new_metadata["Copyright"] = input("Copyright: ")
        new_metadata["ImageDescription"] = input("Descripción: ")
        new_metadata["Software"] = input("Software: ")
        new_metadata["Make"] = input("Marca de Cámara: ")
        new_metadata["Model"] = input("Modelo de Cámara: ")
        
        # Actualizar la imagen
        update_image_metadata(image_path, new_metadata)
