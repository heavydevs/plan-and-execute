#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function clean(directory) {
  if (!fs.existsSync(directory)) return;
  let entries;
  try {
    entries = fs.readdirSync(directory, { withFileTypes: true });
  } catch (error) {
    if (['EACCES', 'EPERM', 'ENOENT'].includes(error.code)) return;
    throw error;
  }
  for (const entry of entries) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === '__pycache__') {
        try {
          fs.rmSync(absolute, { recursive: true, force: true });
        } catch (error) {
          if (!['EACCES', 'EPERM', 'ENOENT'].includes(error.code)) throw error;
        }
      } else if (!['.git', '.ai-work', 'node_modules'].includes(entry.name)) {
        clean(absolute);
      }
    } else if (entry.isFile() && entry.name.endsWith('.pyc')) {
      try {
        fs.rmSync(absolute, { force: true });
      } catch (error) {
        if (!['EACCES', 'EPERM', 'ENOENT'].includes(error.code)) throw error;
      }
    }
  }
}

clean(process.cwd());
