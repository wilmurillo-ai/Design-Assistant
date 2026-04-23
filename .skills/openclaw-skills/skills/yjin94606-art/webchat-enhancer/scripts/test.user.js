// ==UserScript==
// @name         WebChat Enhancer Test
// @namespace    https://clawhub.ai/skills/webchat-enhancer
// @version      1.0.0-test
// @description  Test version
// @author       Boss
// @match        http://127.0.0.1:18789/*
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';
    
    console.log('🧪 WebChat Enhancer Test: Script loaded');
    
    // Simple test
    document.body.insertAdjacentHTML('beforeend', '<div id="test-panel" style="position:fixed;top:10px;right:10px;background:red;color:white;padding:10px;border-radius:8px;z-index:99999;font-size:14px;">🧪 Test Panel Loaded!</div>');
    
    setTimeout(function() {
        var panel = document.getElementById('test-panel');
        if (panel) {
            panel.textContent = '✅ Script is working!';
            panel.style.background = '#4ade80';
        }
    }, 2000);
    
})();
