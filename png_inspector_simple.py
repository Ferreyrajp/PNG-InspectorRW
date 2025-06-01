import http.server
import socketserver
import os
import json
from PIL import Image
from PIL.PngImagePlugin import PngInfo
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
                    
                    # Crear el nombre del archivo de salida
                    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_image_with_metadata.png')
                    
                    # Guardar la imagen con los metadatos exactamente como vienen
                    print(f"Metadatos originales: {metadata}")
                    
                    # Limpiar los metadatos si vienen en formato {"parameters": ...}
                    if metadata and isinstance(metadata, str) and metadata.strip():
                        if metadata.strip().startswith('{"parameters":'):
                            try:
                                # Extraer solo el contenido después de "parameters":
                                metadata = metadata.split('"parameters":', 1)[1].strip()
                                # Eliminar llaves al inicio/final si existen
                                metadata = metadata.strip('{}').strip()
                                # Eliminar comillas al inicio/final si existen
                                if (metadata.startswith('"') and metadata.endswith('"')) or \
                                   (metadata.startswith("'") and metadata.endswith("'")):
                                    metadata = metadata[1:-1]
                                print(f"Metadatos limpios: {metadata}")
                            except Exception as e:
                                print(f"Error limpiando metadatos: {e}")
                    
                    pnginfo = PngInfo()
                    pnginfo.add_text("Modificados", metadata)
                    if metadata and isinstance(metadata, str) and metadata.strip():
                        img.save(output_path, format='PNG', pnginfo=pnginfo)
                    else:
                        img.save(output_path, format='PNG')
                    
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
                    
                    # Crear la respuesta con el formato que el frontend espera
                    response_data = {
                        "metadata": {
                            "metadatos": str(img.info),
                            "metadatos_crudos": str(img.info),
                            "image_path": image_path
                        }
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
    import webbrowser
    PORT = 8081
    url = f"http://localhost:{PORT}"
    Handler = MyHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Servidor iniciado en el puerto {PORT}")
        print(f"Abre tu navegador en: {url}")
        print("O haz clic aquí: ", end='')
        print(f"\033]8;;{url}\033\\{url}\033]8;;\033\\")
        webbrowser.open(url)
        httpd.serve_forever()
