import { createServer } from 'vite';

async function startServer() {
  try {
    const server = await createServer({
      configFile: './vite.config.ts',
      server: {
        port: 5173,
        host: 'localhost'
      }
    });
    
    await server.listen();
    
    console.log('Vite server info:', {
      port: server.config.server.port,
      host: server.config.server.host,
      url: server.resolvedUrls?.local[0]
    });
    
    // Keep the process alive
    process.on('SIGTERM', () => {
      server.close();
    });
    
  } catch (err) {
    console.error('Failed to start Vite:', err);
    process.exit(1);
  }
}

startServer();