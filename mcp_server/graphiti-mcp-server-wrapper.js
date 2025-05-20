#!/usr/bin/env node

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Check if we're running from the installed package or from source
let scriptPath;
if (fs.existsSync(path.join(__dirname, 'graphiti_mcp_server.py'))) {
  // Running from source directory
  scriptPath = path.join(__dirname, 'graphiti_mcp_server.py');
} else {
  // Running from installed package, use the global script
  const binPath = execSync('which graphiti-mcp-server', { encoding: 'utf8' }).trim();
  if (binPath) {
    // Use the shell script directly
    console.log(`Using Graphiti MCP Server from: ${binPath}`);
    const childProcess = spawn(binPath, process.argv.slice(2), {
      stdio: 'inherit'
    });
    childProcess.on('exit', (code) => process.exit(code));
    return;
  } else {
    console.error('Error: graphiti-mcp-server not found in PATH');
    process.exit(1);
  }
}

// Environment variables for SurrealDB
process.env.DATABASE_TYPE = 'surrealdb';
process.env.DATABASE_URI = 'ws://localhost:8001/rpc';
process.env.DATABASE_USER = 'root';
process.env.DATABASE_PASSWORD = 'root';
process.env.DATABASE_NAMESPACE = 'graphiti';
process.env.DATABASE_DB = 'graphiti';

// Install required Python packages if needed
try {
  execSync('python3 -c "import openai"', { stdio: 'ignore' });
} catch (e) {
  console.log('Installing required Python packages...');
  try {
    execSync('pip install openai surrealdb fastapi uvicorn', { stdio: 'inherit' });
  } catch (err) {
    console.error('Failed to install required packages:', err.message);
    process.exit(1);
  }
}

// Run the Python script with the same arguments passed to this script
const pythonProcess = spawn('python3', [scriptPath, ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: process.env
});

// Handle process exit
pythonProcess.on('exit', (code) => {
  process.exit(code);
});
