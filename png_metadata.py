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
        
        # Obtener los metadatos existentes de la imagen
        info = img.info.copy()
        
        # Cargar los metadatos EXIF existentes o crear un nuevo diccionario si no hay
        exif_dict = {}
        if 'exif' in info:
            exif_dict = piexif.load(info['exif'])
        else:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        # Asegurarse de que los diccionarios internos existan
        if "0th" not in exif_dict:
            exif_dict["0th"] = {}
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        
        # Actualizar los campos EXIF estándar
        if "Artist" in new_metadata and new_metadata["Artist"]:
            exif_dict["0th"][piexif.ImageIFD.Artist] = new_metadata["Artist"].encode('utf-8')
        if "DateTime" in new_metadata and new_metadata["DateTime"]:
            exif_dict["0th"][piexif.ImageIFD.DateTime] = new_metadata["DateTime"].encode('utf-8')
        if "Copyright" in new_metadata and new_metadata["Copyright"]:
            exif_dict["0th"][piexif.ImageIFD.Copyright] = new_metadata["Copyright"].encode('utf-8')
        if "ImageDescription" in new_metadata and new_metadata["ImageDescription"]:
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = new_metadata["ImageDescription"].encode('utf-8')
        if "Software" in new_metadata and new_metadata["Software"]:
            exif_dict["0th"][piexif.ImageIFD.Software] = new_metadata["Software"].encode('utf-8')
        if "Make" in new_metadata and new_metadata["Make"]:
            exif_dict["Exif"][piexif.ExifIFD.Make] = new_metadata["Make"].encode('utf-8')
        if "Model" in new_metadata and new_metadata["Model"]:
            exif_dict["Exif"][piexif.ExifIFD.Model] = new_metadata["Model"].encode('utf-8')
        
        # Manejar el campo 'parameters' de manera especial
        parameters_text = None
        
        # Verificar si hay un campo 'parameters' en los nuevos metadatos
        if 'parameters' in new_metadata and new_metadata['parameters']:
            parameters_text = new_metadata['parameters']
        # Si no está en los nuevos metadatos, mantener el existente si lo hay
        elif 'parameters' in info:
            parameters_text = info['parameters']
        
        # Si hay un texto de parámetros, asegurarse de que se guarde correctamente
        if parameters_text is not None:
            info['parameters'] = parameters_text
        
        # Actualizar otros metadatos específicos de PNG
        for key, value in new_metadata.items():
            # Ignorar campos EXIF estándar y 'parameters' que ya manejamos
            if key not in ["Artist", "DateTime", "Copyright", "ImageDescription", 
                          "Software", "Make", "Model", "parameters"]:
                info[key] = value
        
        # Crear el nombre del archivo de salida
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_edited.png"
        
        # Guardar la imagen con los metadatos EXIF y PNG
        exif_bytes = piexif.dump(exif_dict)
        
        # Preparar los parámetros para guardar
        save_params = {'format': 'PNG', 'exif': exif_bytes}
        
        # Añadir los metadatos PNG al diccionario de parámetros
        for key, value in info.items():
            if key != 'exif':  # Ya manejamos EXIF por separado
                save_params[key] = value
        
        # Guardar la imagen con todos los metadatos
        img.save(output_path, **save_params)
        
        print(f"\nNueva imagen guardada en: {output_path}")
        if parameters_text:
            print("Se conservó el campo 'parameters' con la configuración de generación de la imagen")
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
