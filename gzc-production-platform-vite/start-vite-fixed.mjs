import { createServer } from 'vite';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

async function startViteServer() {
  try {
    console.log('Starting Vite server with Node.js', process.version);
    
    const server = await createServer({
      configFile: false,
      root: process.cwd(),
      server: {
        port: 3300,
        host: '0.0.0.0', // Bind to all interfaces
        strictPort: false,
        open: false,
        fs: {
          strict: false
        }
      },
      // Load the existing config but override server settings
      ...require('./vite.config.ts')
    });
    
    await server.listen();
    
    const info = server.config.server;
    console.log('\n✅ Vite dev server is running!');
    console.log(`   Local:   http://localhost:${info.port}/`);
    console.log(`   Network: http://${require('os').networkInterfaces()['en0']?.[1]?.address || 'localhost'}:${info.port}/\n`);
    
    // Verify the server is actually listening
    const net = require('net');
    const testConnection = () => {
      const socket = new net.Socket();
      socket.on('connect', () => {
        console.log('✅ Server is accepting connections on port', info.port);
        socket.destroy();
      });
      socket.on('error', (err) => {
        console.log('❌ Server is not accepting connections:', err.message);
      });
      socket.connect(info.port, 'localhost');
    };
    
    setTimeout(testConnection, 1000);
    
    // Keep process alive
    process.on('SIGINT', async () => {
      console.log('\nShutting down Vite server...');
      await server.close();
      process.exit(0);
    });
    
  } catch (error) {
    console.error('❌ Failed to start Vite server:', error);
    console.error('\nTroubleshooting tips:');
    console.error('1. Try using Node.js LTS version (v20 or v22)');
    console.error('2. Clear node_modules and reinstall: rm -rf node_modules && npm install');
    console.error('3. Check if port 3300 is already in use: lsof -i :3300');
    process.exit(1);
  }
}

startViteServer();