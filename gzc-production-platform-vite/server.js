import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const server = http.createServer((req, res) => {
  console.log(`Request for: ${req.url}`);
  
  if (req.url === '/') {
    fs.readFile(path.join(__dirname, 'index.html'), (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end(data);
    });
  } else {
    res.writeHead(200);
    res.end('Vite project server running on port 3300');
  }
});

server.listen(3300, () => {
  console.log('Server is running on http://localhost:3300');
  console.log('Server actually listening on all interfaces');
});

server.on('error', (err) => {
  console.error('Server error:', err);
});