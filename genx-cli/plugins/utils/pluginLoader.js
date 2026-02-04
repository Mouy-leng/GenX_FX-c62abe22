import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function loadPlugins(config) {
  const pluginDir = path.join(__dirname, '..');
  const pluginNames = config.plugins || [];
  const plugins = [];

  for (const name of pluginNames) {
    try {
      if (name.endsWith('.py')) {
        plugins.push({ name });
      } else {
        const pluginPath = path.join(pluginDir, `${name}.js`);
        const plugin = await import(pathToFileURL(pluginPath).href);
        plugins.push({ name, ...plugin });
      }
    } catch (error) {
      console.error(`Error loading plugin "${name}":`, error);
    }
  }

  return plugins;
}
