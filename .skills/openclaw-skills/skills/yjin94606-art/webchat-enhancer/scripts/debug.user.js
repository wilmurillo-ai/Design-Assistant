// ==UserScript==
// @name         WebChat Debug
// @namespace    https://clawhub.ai/skills/webchat-enhancer
// @version      1.0.4
// @description  Debug script
// @author       Boss
// @match        http://127.0.0.1:18789/*
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';
    
    function debug() {
        var container = document.querySelector('.chat-split-container');
        if (!container) {
            console.log('[DEBUG] No chat-split-container');
            return;
        }
        
        console.log('[DEBUG] Found chat-split-container');
        console.log('[DEBUG] Container children:', container.children.length);
        
        for (var i = 0; i < container.children.length; i++) {
            var child = container.children[i];
            console.log('[DEBUG] Child', i, ':', child.tagName, 'class:', child.className);
        }
        
        // Find chat-group-messages
        var chatGroup = document.querySelector('.chat-group-messages');
        if (chatGroup) {
            console.log('[DEBUG] Found chat-group-messages');
            console.log('[DEBUG] ChatGroup children:', chatGroup.children.length);
            
            for (var j = 0; j < chatGroup.children.length; j++) {
                var msg = chatGroup.children[j];
                console.log('[DEBUG] Msg', j, ':', msg.tagName, 'class:', msg.className, 'text:', msg.textContent.substring(0, 60));
            }
        }
        
        // Alternative: find all message groups
        var groups = document.querySelectorAll('[class*="message-group"], [class*="chat-group"]');
        console.log('[DEBUG] Message groups found:', groups.length);
        groups.forEach(function(g, i) {
            console.log('[DEBUG] Group', i, ':', g.className, 'children:', g.children.length);
        });
    }
    
    setTimeout(debug, 3000);
})();
