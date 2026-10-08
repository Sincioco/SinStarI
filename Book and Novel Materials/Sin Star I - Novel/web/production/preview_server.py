"""Loopback-only reader preview with byte ranges; launched outside task lifetime."""
import argparse, functools, http.server, json, os, re, time
from pathlib import Path
from urllib.parse import urlsplit

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
parser.add_argument('--port',type=int,default=8897)
args=parser.parse_args()
root=args.root.resolve()
assert (root/'book.json').is_file() and (root/'audio/01.mp3').is_file(), 'Reader root is incomplete'
started=time.time()

class Preview(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control','no-cache')
        super().end_headers()

    def do_GET(self):
        if urlsplit(self.path).path=='/__preview_health':
            body=json.dumps({'service':'Sin Star Book One preview','pid':os.getpid(),'root':str(root),'port':args.port,'uptime_seconds':round(time.time()-started,1)}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            return
        super().do_GET()

    def send_head(self):
        self.range_remaining=None
        path=Path(self.translate_path(self.path))
        if not path.resolve().is_relative_to(root):
            self.send_error(403);return None
        if path.is_file() and path.suffix.lower()=='.mp3':
            size=path.stat().st_size;start=0;end=size-1
            requested=self.headers.get('Range')
            if requested:
                match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested)
                if match and (match[1] or match[2]):
                    if match[1]:start=int(match[1]);end=min(int(match[2]),end) if match[2] else end
                    else:start=max(0,size-int(match[2]))
                else:start=size
                if start>=size or start>end:
                    self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return None
            stream=path.open('rb');stream.seek(start);self.range_remaining=end-start+1
            self.send_response(206 if requested else 200)
            self.send_header('Content-Type','audio/mpeg');self.send_header('Accept-Ranges','bytes')
            self.send_header('Content-Length',str(self.range_remaining))
            if requested:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers();return stream
        return super().send_head()

    def copyfile(self,source,outputfile):
        if self.range_remaining is None:return super().copyfile(source,outputfile)
        remaining=self.range_remaining
        while remaining:
            data=source.read(min(65536,remaining))
            if not data:break
            outputfile.write(data);remaining-=len(data)

    def log_message(self,format,*values):
        # pythonw has no console. Keep logging bounded to the local preview log.
        with (Path(os.environ['TEMP'])/f'sinstar-preview-{args.port}.log').open('a',encoding='utf-8') as log:
            log.write(f'{self.log_date_time_string()} {format % values}\n')

server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),functools.partial(Preview,directory=str(root)))
server.serve_forever()
