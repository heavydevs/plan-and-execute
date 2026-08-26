#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function clean(directory) {
  if (!fs.existsSync(directory)) return;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === '__pycache__') {
        fs.rmSync(absolute, { recursive: true, force: true });
      } else if (!['.git', 'node_modules'].includes(entry.name)) {
        clean(absolute);
      }
    } else if (entry.isFile() && entry.name.endsWith('.pyc')) {
      fs.rmSync(absolute, { force: true });
    }
  }
}

clean(process.cwd());
