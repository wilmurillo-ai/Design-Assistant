// Chrome Use - Popup Script

const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const hostInput = document.getElementById('host');
const portInput = document.getElementById('port');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');

// Update status display
function updateStatus(text, color) {
  statusDot.className = 'status-dot ' + color;
  statusText.textContent = text;
}

// Get current status from background
function checkStatus() {
  chrome.runtime.sendMessage({ type: 'get_status' }, (response) => {
    if (response) {
      if (response.connected) {
        updateStatus('Connected', 'connected');
        hostInput.value = response.host;
        portInput.value = response.port;
      } else {
        updateStatus('Disconnected', 'disconnected');
      }
    }
  });
}

// Connect button
connectBtn.addEventListener('click', () => {
  const host = hostInput.value || 'localhost';
  const port = parseInt(portInput.value) || 9224;

  updateStatus('Connecting...', 'connecting');

  chrome.runtime.sendMessage({
    type: 'connect',
    host: host,
    port: port
  }, (response) => {
    if (response && response.status === 'connecting') {
      // Background will update status on actual connection
    }
  });
});

// Disconnect button
disconnectBtn.addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'disconnect' }, (response) => {
    if (response && response.status === 'disconnected') {
      updateStatus('Disconnected', 'disconnected');
    }
  });
});

// Listen for status updates from background
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'status') {
    updateStatus(message.text, message.color);
  }
});

// Initial status check
checkStatus();
