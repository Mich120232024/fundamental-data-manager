import { createServer } from 'vite';

async function startViteServer() {
  const server = await createServer({
    // Use existing config
    configFile: './vite.config.ts',
    server: {
      port: 3300,
      host: '127.0.0.1'
    }
  });
  
  await server.listen();
  
  console.log('✅ Vite is running at http://localhost:3300/');
  server.printUrls();
}

startViteServer().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});