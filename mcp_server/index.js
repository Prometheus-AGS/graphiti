#!/usr/bin/env node

console.log('Starting Graphiti MCP Server...');

// Execute the shell script directly
require('child_process').spawn('/Users/gqadonis/bin/graphiti-mcp-server', process.argv.slice(2), {
  stdio: 'inherit'
}).on('exit', (code) => process.exit(code));
