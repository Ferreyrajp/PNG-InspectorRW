import http.server
import io
import json
import socketserver
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import multipart


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def _read_form(self):
        from multipart import parse_options_header, MultipartParser

        content_type = self.headers.get('Content-Type', '')
        length = int(self.headers.get('Content-Length', 0))
        _, params = parse_options_header(content_type)
        parser = MultipartParser(io.BytesIO(self.rfile.read(length)), params.get('boundary', ''))
        fields = {}
        for part in parser:
            if part.filename:
                fields[part.name] = part.file.read()
            else:
                value = part.value
                fields[part.name] = value.decode('utf-8') if isinstance(value, bytes) else str(value)
        return fields

    def _json(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            form = self._read_form()
            if 'image' not in form:
                self._json(400, {'error': 'No se recibió una imagen.'})
                return

            image_data = form['image']
            with Image.open(io.BytesIO(image_data)) as source:
                image = source.copy()
                if form.get('action', 'inspect') == 'inspect':
                    metadata = {key: value for key, value in source.info.items()
                                if isinstance(value, str)}
                    self._json(200, {'metadata': metadata})
                    return

            if form.get('action') != 'save':
                self._json(400, {'error': 'Acción no válida.'})
                return

            remove_all = form.get('remove_all', 'false').lower() == 'true'
            metadata = json.loads(form.get('metadata', '{}'))
            if not isinstance(metadata, dict):
                self._json(400, {'error': 'Los metadatos deben ser un objeto JSON.'})
                return

            pnginfo = PngInfo()
            if not remove_all:
                for key, value in metadata.items():
                    if isinstance(key, str) and isinstance(value, str):
                        pnginfo.add_text(key, value)

            output = io.BytesIO()
            options = {'format': 'PNG'}
            if not remove_all and metadata:
                options['pnginfo'] = pnginfo
            image.save(output, **options)
            data = output.getvalue()
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Disposition', 'attachment; filename="png_metadata_updated.png"')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (ValueError, json.JSONDecodeError) as error:
            self._json(400, {'error': f'Datos no válidos: {error}'})
        except Exception as error:
            self._json(500, {'error': f'Error al procesar la imagen: {error}'})


if __name__ == '__main__':
    import webbrowser
    PORT = 8081
    url = f'http://localhost:{PORT}'
    with socketserver.TCPServer(('', PORT), MyHandler) as httpd:
        print(f'Servidor iniciado en {url}')
        webbrowser.open(url)
        httpd.serve_forever()
