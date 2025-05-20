import http.server
import socketserver
import os
import json
from PIL import Image
import cgi

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        try:
            # Leer los datos del formulario
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Verificar si es una solicitud de guardar metadatos
            if 'metadata' in form and 'image' in form:
                # Obtener los metadatos del formulario
                metadata = form.getvalue('metadata')
                image_item = form['image']
                
                if not metadata or not hasattr(image_item, 'file') or not image_item.file:
                    self.send_error(400, "Datos incompletos en la solicitud")
                    return

                try:
                    # Guardar la imagen temporalmente
                    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_image.png')
                    with open(image_path, 'wb') as f:
                        f.write(image_item.file.read())
                    
                    # Abrir la imagen original
                    img = Image.open(image_path)
                    
                    # Crear un diccionario de metadatos
                    metadata_dict = {}
                    try:
                        for line in metadata.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                key = key.strip()
                                value = value.strip()
                                if key and value:  # Solo agregar si ambos no están vacíos
                                    metadata_dict[key] = value
                    except Exception as e:
                        self.send_error(400, f"Error al procesar los metadatos: {str(e)}")
                        return

                    # Crear una copia de la imagen
                    img_copy = img.copy()
                    
                    # Procesar los metadatos del formulario
                    if metadata and isinstance(metadata, str) and metadata.strip():
                        metadata = metadata.strip()
                        try:
                            # Intentar cargar como JSON
                            if metadata.startswith('{') and metadata.endswith('}'):
                                try:
                                    metadata_dict = json.loads(metadata)
                                    if isinstance(metadata_dict, dict):
                                        # Actualizar los metadatos
                                        for k, v in metadata_dict.items():
                                            if v is not None:
                                                # Convertir a string si no es str o bytes
                                                img_copy.info[str(k)] = str(v) if not isinstance(v, (str, bytes)) else v
                                    else:
                                        # Si no es un diccionario, guardar como parámetro
                                        img_copy.info['parameters'] = metadata
                                except json.JSONDecodeError as je:
                                    # Si no es un JSON válido, guardar como parámetro
                                    print(f"Error decodificando JSON: {str(je)}")
                                    img_copy.info['parameters'] = metadata
                            else:
                                # Si no es un JSON, guardar como parámetro
                                img_copy.info['parameters'] = metadata
                        except Exception as e:
                            print(f"Error procesando metadatos: {str(e)}")
                            img_copy.info['parameters'] = metadata
                    
                    # Guardar la imagen con los metadatos
                    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_image_with_metadata.png')
                    img_copy.save(output_path, format='PNG')
                    
                    # Enviar la imagen de vuelta al cliente
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-stream')
                    self.send_header('Content-Disposition', 'attachment; filename="image_with_metadata.png"')
                    self.end_headers()
                    
                    # Leer y enviar la imagen
                    with open(output_path, 'rb') as f:
                        self.wfile.write(f.read())
                    
                    # Limpiar archivos temporales
                    os.remove(output_path)
                    os.remove(image_path)
                    return
                    
                except Exception as e:
                    self.send_error(500, f"Error al procesar la imagen: {str(e)}")
                    return

            # Si no es guardar metadatos, asumimos que es cargar imagen
            elif "image" in form:
                image_item = form['image']
                if not image_item.file:
                    self.send_error(400, "Archivo no válido")
                    return

                image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_image.png')
                with open(image_path, 'wb') as f:
                    f.write(image_item.file.read())

                try:
                    img = Image.open(image_path)
                    metadatos = img.info
                    metadatos_texto = ""
                    for clave, valor in metadatos.items():
                        try:
                            if isinstance(valor, bytes):
                                valor = valor.decode('utf-8')
                            metadatos_texto += f"{clave}: {valor}\n"
                        except:
                            metadatos_texto += f"{clave}: (valor no decodificable)\n"

                    metadatos_texto += "\nInformación Técnica:\n"
                    metadatos_texto += f"Dimensiones: {img.width}x{img.height}\n"
                    metadatos_texto += f"Modo de Color: {img.mode}\n"
                    metadatos_texto += f"Formato: {img.format}\n"
                    metadatos_texto += f"Tamaño: {img.size[0]}x{img.size[1]}\n"

                    metadata = {
                        "metadatos": metadatos_texto,
                        "image_path": image_path,
                        "metadatos_crudos": str(img.info)
                    }
                    response_data = {
                        "metadata": metadata
                    }

                except Exception as e:
                    metadata = {
                        "metadatos": f"Error procesando imagen: {str(e)}",
                        "image_path": "",
                        "metadatos_crudos": str(e)
                    }
                    response_data = {
                        "metadata": metadata
                    }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
                return

            else:
                self.send_error(400, "Solicitud no válida")
                return

        except Exception as e:
            self.send_error(500, f"Error interno del servidor: {str(e)}")
            return

if __name__ == '__main__':
    PORT = 8081
    Handler = MyHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Servidor iniciado en el puerto {PORT}")
        httpd.serve_forever()
