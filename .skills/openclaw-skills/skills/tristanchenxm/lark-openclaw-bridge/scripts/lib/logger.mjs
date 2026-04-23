function log(...args) {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 23);
  console.log(`[${timestamp}]`, ...args);
}

function logError(...args) {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 23);
  console.error(`[${timestamp}]`, ...args);
}

export { log, logError };
