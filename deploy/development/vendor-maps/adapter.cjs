'use strict';
// Experimental only: never imported by the application or official controller.
const fs = require('node:fs');
const path = require('node:path');
const {createHash} = require('node:crypto');
const {createRequire} = require('node:module');
const fingerprints = Object.freeze({
  'next/dist/compiled/webpack/bundle5.js': '4f227eeae1d56f062ad42143e1e4c7b9520fae7aa359fdc1e25ee8d0d3445b2c',
  'next/dist/compiled/next-server/app-page.runtime.dev.js': 'f5642afec1b380029730444582c0af19300709dcb586f91c96cb002fc8bffddb',
  'next/dist/build/webpack/plugins/eval-source-map-dev-tool-plugin.js': 'bdb7813990c37584a2fb02c0439bf4dc899edd60085bab78f0dfce3c392eca2d',
  'next/dist/build/webpack/config/blocks/base.js': '50549f6840d622bf655efdd1d63e04d3fd827f67647e525db536ef63d56e216a',
  'next/dist/compiled/webpack/webpack.js': '13649aa1a17e743f377e062cbebfd430b6e2498ecacdf40145a3d0722a650f4d',
});
const vendor = /(?:^|[\\/])node_modules[\\/]/;
function refuse(condition, message) { if (!condition) throw Error('VENDOR_MAP_REFUSED: '+message); }
function adapt(config, context, env = process.env) {
  if (env.NADI_FIX06_VENDOR_MAPS === undefined || env.NADI_FIX06_VENDOR_MAPS === '0') return config;
  refuse(env.NADI_FIX06_VENDOR_MAPS === '1', 'explicit flag');
  const root = fs.realpathSync(process.cwd());
  refuse(env.NODE_ENV === 'development' && context.dev === true, 'development only');
  refuse(root.startsWith('/tmp/nadi-fix06-private/') && root.endsWith('/runs/frontend/reliability-cockpit/web'), 'disposable root');
  refuse(env.NADI_FIX06_DISPOSABLE_ROOT === root && !env.NEXT_RSPACK && !env.TURBOPACK, 'disposable acknowledgment');
  const requireAt = createRequire(path.join(root, 'package.json'));
  for (const [pkg, version] of [['next','15.5.9'],['react','19.2.8'],['react-dom','19.2.8']])
    refuse(requireAt(pkg+'/package.json').version === version, 'package '+pkg);
  refuse(requireAt('next/dist/compiled/react').version === '19.2.0-canary-0bdb9206-20250818', 'bundled React version');
  refuse(process.versions.node === '22.23.1', 'Node version');
  for (const [file, hash] of Object.entries(fingerprints))
    refuse(createHash('sha256').update(fs.readFileSync(requireAt.resolve(file))).digest('hex') === hash, 'fingerprint '+file);
  const bundled = requireAt('next/dist/compiled/webpack/webpack'); bundled.init();
  refuse(bundled.webpack.version === '5.98.0' && context.webpack === bundled.webpack, 'Webpack identity');
  const Plugin = requireAt('next/dist/build/webpack/plugins/eval-source-map-dev-tool-plugin').default;
  refuse(config.mode === 'development' && config.devtool === false && config.cache === false &&
    ['client','server','edge-server'].includes(config.name) && Array.isArray(config.plugins), 'config shape');
  const matches = config.plugins.filter(p => /(?:Eval)?SourceMapDevToolPlugin/.test(p?.constructor?.name ?? ''));
  refuse(matches.length === 1 && Object.getPrototypeOf(matches[0]) === Plugin.prototype, 'unique exact plugin');
  const plugin = matches[0], options = plugin.options;
  refuse(Object.keys(plugin).sort().join(',') === 'moduleFilenameTemplate,namespace,options,shouldIgnorePath,sourceMapComment', 'plugin properties');
  refuse(Object.getPrototypeOf(options) === Object.prototype && Object.keys(options).sort().join(',') === 'moduleFilenameTemplate,shouldIgnorePath', 'options shape');
  refuse(options.moduleFilenameTemplate === config.output.devtoolModuleFilenameTemplate &&
    typeof options.shouldIgnorePath === 'function' && plugin.shouldIgnorePath === options.shouldIgnorePath &&
    plugin.sourceMapComment === '//# sourceURL=[module]\n//# sourceMappingURL=[url]' && plugin.namespace === '', 'option values');
  // Documented exclude option. The fork returns original vendor module source;
  // application eval/maps and all other options remain unchanged.
  plugin.options = {...options, exclude: vendor};
  return config;
}
module.exports = {adapt, vendor, fingerprints};
