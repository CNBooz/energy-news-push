#!/usr/bin/env node
/**
 * IMA Knowledge Base File Upload Script
 * Uploads energy_news.html to IMA knowledge base
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CLIENT_ID = process.env.IMA_CLIENT_ID || 'dd4962571a67592aa50ec9146343419a';
const API_KEY = process.env.IMA_API_KEY || 'g8WnLUpeen54d0yrZO+zBN9LwoPndZIL+OnXjibRJB08G+19erJY+dJdIIJbQQsie+r93Gg2nA==';
const KB_ID = process.env.IMA_KB_ID || 'E9owuqdzTE2LcRB0A5ub04_cxrGGpMzCmFQEahJ8te0=';

const HTML_FILE = path.join(__dirname, 'energy_news.html');

function uploadToIMA() {
  return new Promise((resolve, reject) => {
    // Read HTML file
    if (!fs.existsSync(HTML_FILE)) {
      console.log(`[IMA] File not found: ${HTML_FILE}`);
      resolve(false);
      return;
    }

    const htmlContent = fs.readFileSync(HTML_FILE, 'utf-8');
    console.log(`[IMA] Read HTML file: ${htmlContent.length} bytes`);

    // Step 1: Upload to COS (simplified - use direct API if possible)
    // For now, we'll try to use the IMA OpenAPI to upload directly
    
    // Step 2: Call IMA API to add file to knowledge base
    const postData = JSON.stringify({
      knowledge_base_id: KB_ID,
      file_name: 'energy_news.html',
      file_content: Buffer.from(htmlContent).toString('base64'),
      file_type: 'text/html'
    });

    const options = {
      hostname: 'ima.qq.com',
      path: '/openapi/wiki/v1/knowledge/doc/upload',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
        'ima-openapi-clientid': CLIENT_ID,
        'ima-openapi-key': API_KEY
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        console.log(`[IMA] Response: ${res.statusCode} - ${data}`);
        if (res.statusCode === 200) {
          console.log('[IMA] Upload success!');
          resolve(true);
        } else {
          console.log(`[IMA] Upload failed: ${data}`);
          resolve(false);
        }
      });
    });

    req.on('error', (e) => {
      console.log(`[IMA] Error: ${e.message}`);
      resolve(false);
    });

    req.write(postData);
    req.end();
  });
}

// Main
(async () => {
  console.log('[IMA] Starting upload to knowledge base...');
  console.log(`[IMA] KB ID: ${KB_ID}`);
  console.log(`[IMA] File: ${HTML_FILE}`);
  
  const success = await uploadToIMA();
  
  if (success) {
    console.log('[IMA] Done!');
    process.exit(0);
  } else {
    console.log('[IMA] Failed!');
    process.exit(1);
  }
})();
