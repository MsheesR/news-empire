#!/usr/bin/env python3
"""
CDP-Level Anti-Detection Stealth Patches for Playwright
========================================================
Injects anti-detection JavaScript at the Chrome DevTools Protocol level
before ANY page script runs. This is the lowest-level defense against
browser automation detection.

Detection vectors neutralized (15 total):
1.  navigator.webdriver = true
2.  navigator.plugins.length = 0
3.  navigator.mimeTypes.length = 0
4.  chrome.runtime (automation extension detection)
5.  permissions.query (automation permission)
6.  window.outerWidth/outerHeight = 0 (headless detection)
7.  navigator.languages (automation language)
8.  WebGL vendor/renderer (headless uses SwiftShader)
9.  Canvas fingerprinting (adds per-session noise)
10. AudioContext fingerprinting (adds per-session noise)
11. Service Worker / Shared Worker detection
12. Notification.permission
13. Battery API
14. Media devices enumeration
15. Hardware concurrency / device memory (spoofed per session)

Architecture:
- STEALTH_SCRIPT_BASE: Core navigator/API overrides (runs before page JS)
- CANVAS_NOISE_SCRIPT: Canvas/WebGL/Audio fingerprint noise (per-session seed)
- PLATFORM_ENTROPY_SCRIPT: Additional entropy for realistic platform diversity
- StealthPatcher: Applies patches to Playwright contexts and pages

Usage:
    from stealth_patches import StealthPatcher
    
    # On context creation (covers all pages)
    await StealthPatcher.patch_context(context, fingerprint)
    
    # On individual page (additional CDP-level injection)
    await StealthPatcher.patch_page(page, fingerprint)
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger('stealth')

# ============================ CORE STEALTH SCRIPT ============================
# This runs via Page.addScriptToEvaluateOnNewDocument BEFORE any page JS.
# All placeholder tokens (___XXX___) are replaced per session by fingerprint_manager.

STEALTH_SCRIPT_BASE = r"""
(function() {
    'use strict';
    
    var fp = window.__fp__ || {};
    
    // ================================================================
    // 1. CRITICAL: Remove webdriver flag
    // ================================================================
    Object.defineProperty(navigator, 'webdriver', {
        get: function() { return false; },
        configurable: true
    });
    
    // ================================================================
    // 2. Fake plugins array (real Chrome has 3-5 plugins)
    // ================================================================
    var fakePlugins = [
        {
            name: 'Chrome PDF Plugin',
            filename: 'internal-pdf-viewer',
            description: 'Portable Document Format',
            length: 1,
            item: function(i) { return i === 0 ? this : null; },
            namedItem: function(name) { return name === 'Chrome PDF Plugin' ? this : null; }
        },
        {
            name: 'Chrome PDF Viewer',
            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
            description: '',
            length: 1,
            item: function(i) { return i === 0 ? this : null; },
            namedItem: function(name) { return name === 'Chrome PDF Viewer' ? this : null; }
        },
        {
            name: 'Native Client',
            filename: 'internal-nacl-plugin',
            description: '',
            length: 1,
            item: function(i) { return i === 0 ? this : null; },
            namedItem: function(name) { return name === 'Native Client' ? this : null; }
        }
    ];
    
    var pluginArrayProto = Object.create({
        item: function(i) { return this[i] || null; },
        namedItem: function(name) {
            for (var i = 0; i < this.length; i++) {
                if (this[i].name === name) return this[i];
            }
            return null;
        },
        refresh: function() {}
    });
    
    Object.defineProperty(navigator, 'plugins', {
        get: function() {
            var arr = Array.prototype.slice.call(fakePlugins);
            arr.length = fakePlugins.length;
            Object.setPrototypeOf(arr, pluginArrayProto);
            return arr;
        },
        configurable: true
    });
    
    // ================================================================
    // 3. Fake MIME types
    // ================================================================
    var fakeMimeTypes = [
        { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format' },
        { type: 'text/pdf', suffixes: 'pdf', description: 'PDF Document' }
    ];
    
    Object.defineProperty(navigator, 'mimeTypes', {
        get: function() {
            var arr = Array.prototype.slice.call(fakeMimeTypes);
            arr.length = fakeMimeTypes.length;
            arr.item = function(i) { return this[i] || null; };
            arr.namedItem = function(name) {
                for (var i = 0; i < this.length; i++) {
                    if (this[i].type === name) return this[i];
                }
                return null;
            };
            return arr;
        },
        configurable: true
    });
    
    // ================================================================
    // 4. Override chrome.runtime (detects automation extensions)
    // ================================================================
    if (typeof chrome === 'undefined') {
        window.chrome = {};
    }
    if (!chrome.runtime) {
        chrome.runtime = {
            connect: function() {
                return {
                    onMessage: { addListener: function() {} },
                    onDisconnect: { addListener: function() {} },
                    postMessage: function() {},
                    disconnect: function() {}
                };
            },
            sendMessage: function(msg, cb) { if (cb) cb(); },
            onMessage: { addListener: function() {} },
            onConnect: { addListener: function() {} },
            lastError: undefined
        };
    } else {
        var origConnect = chrome.runtime.connect;
        chrome.runtime.connect = function() {
            var args = Array.prototype.slice.call(arguments);
            if (args[0] && args[0].name === 'automation') {
                throw new Error('No matching bindings found');
            }
            return origConnect.apply(this, args);
        };
    }
    chrome.loadTimes = function() { return {}; };
    chrome.csi = function() { return {}; };
    chrome.app = {};
    
    // ================================================================
    // 5. Fix permissions API (automation detection)
    // ================================================================
    var origQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = function(parameters) {
        if (parameters.name === 'notifications') {
            return Promise.resolve({
                state: Notification.permission || 'denied',
                onchange: null
            });
        }
        return origQuery.call(this, parameters).then(function(result) {
            return result;
        }).catch(function() {
            return { state: 'prompt', onchange: null };
        });
    };
    
    // ================================================================
    // 6. Fix window dimensions (headless returns 0 or wrong values)
    // ================================================================
    var screenW = fp.screenWidth || screen.width || 1920;
    var screenH = fp.screenHeight || screen.height || 1080;
    var availW = fp.availWidth || screen.availWidth || screenW;
    var availH = fp.availHeight || screen.availHeight || (screenH - 40);
    
    Object.defineProperty(screen, 'width', { get: function() { return screenW; }, configurable: true });
    Object.defineProperty(screen, 'height', { get: function() { return screenH; }, configurable: true });
    Object.defineProperty(screen, 'availWidth', { get: function() { return availW; }, configurable: true });
    Object.defineProperty(screen, 'availHeight', { get: function() { return availH; }, configurable: true });
    Object.defineProperty(screen, 'colorDepth', {
        get: function() { return fp.colorDepth || 24; },
        configurable: true
    });
    Object.defineProperty(screen, 'pixelDepth', {
        get: function() { return fp.colorDepth || 24; },
        configurable: true
    });
    
    // Fix outer dimensions
    Object.defineProperty(window, 'outerWidth', {
        get: function() { return screenW; },
        configurable: true
    });
    Object.defineProperty(window, 'outerHeight', {
        get: function() { return screenH - 40; },
        configurable: true
    });
    Object.defineProperty(window, 'innerWidth', {
        get: function() { return screenW; },
        configurable: true
    });
    Object.defineProperty(window, 'innerHeight', {
        get: function() { return screenH - 80; },
        configurable: true
    });
    
    // ================================================================
    // 7. Override languages (real browsers have en-US first)
    // ================================================================
    var languages = fp.languages || ['en-US', 'en'];
    Object.defineProperty(navigator, 'languages', {
        get: function() { return languages.slice(); },
        configurable: true
    });
    Object.defineProperty(navigator, 'language', {
        get: function() { return languages[0]; },
        configurable: true
    });
    
    // ================================================================
    // 8. Platform consistency
    // ================================================================
    Object.defineProperty(navigator, 'platform', {
        get: function() { return fp.platform || 'Win32'; },
        configurable: true
    });
    
    // ================================================================
    // 9. Hardware concurrency (spoofed per session)
    // ================================================================
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: function() { return fp.hardwareConcurrency || 8; },
        configurable: true
    });
    
    // ================================================================
    // 10. Device memory (spoofed per session)
    // ================================================================
    Object.defineProperty(navigator, 'deviceMemory', {
        get: function() { return fp.deviceMemory || 8; },
        configurable: true
    });
    
    // ================================================================
    // 11. User agent override
    // ================================================================
    if (fp.userAgent) {
        Object.defineProperty(navigator, 'userAgent', {
            get: function() { return fp.userAgent; },
            configurable: true
        });
        Object.defineProperty(navigator, 'appVersion', {
            get: function() { return fp.userAgent.replace('Mozilla/', ''); },
            configurable: true
        });
    }
    
    // ================================================================
    // 12. Override getBattery (often used for fingerprinting)
    // ================================================================
    if (navigator.getBattery) {
        navigator.getBattery = function() {
            // Realistic battery diversity: 10-100%, sometimes charging, sometimes not
            var batteryLevel = 0.10 + Math.random() * 0.90;  // 10% to 100%
            var isCharging = Math.random() < 0.65;  // 65% of devices are plugged in
            var dischargeTime = isCharging ? Infinity : Math.floor(Math.random() * 14400) + 600;  // 10min to 4hr
            return Promise.resolve({
                charging: isCharging,
                chargingTime: isCharging ? Math.floor(Math.random() * 3600) : 0,
                dischargingTime: dischargeTime,
                level: batteryLevel,
                onchargingchange: null,
                onchargingtimechange: null,
                ondischargingtimechange: null,
                onlevelchange: null,
                addEventListener: function() {}
            });
        };
    }
    
    // ================================================================
    // 13. Notification permission
    // ================================================================
    if (typeof Notification !== 'undefined') {
        Object.defineProperty(Notification, 'permission', {
            get: function() { return 'default'; },
            configurable: true
        });
    }
    
    // ================================================================
    // 14. Override media devices enumeration
    // ================================================================
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        var origEnumerate = navigator.mediaDevices.enumerateDevices;
        navigator.mediaDevices.enumerateDevices = function() {
            return origEnumerate.call(this).then(function(devices) {
                var hasAudio = devices.some(function(d) { return d.kind === 'audioinput'; });
                var hasVideo = devices.some(function(d) { return d.kind === 'videoinput'; });
                if (!hasAudio) {
                    devices.push({
                        deviceId: 'default',
                        kind: 'audioinput',
                        label: '',
                        groupId: 'default'
                    });
                }
                if (!hasVideo) {
                    devices.push({
                        deviceId: 'default',
                        kind: 'videoinput',
                        label: '',
                        groupId: 'default'
                    });
                }
                return devices;
            });
        };
    }
    
    // ================================================================
    // 15. Override navigator.productSub (some detection scripts use this)
    // ================================================================
    Object.defineProperty(navigator, 'productSub', {
        get: function() { return '20030107'; },
        configurable: true
    });
    Object.defineProperty(navigator, 'vendor', {
        get: function() { return 'Google Inc.'; },
        configurable: true
    });
    Object.defineProperty(navigator, 'vendorSub', {
        get: function() { return ''; },
        configurable: true
    });
    
    // ================================================================
    // 16. Remove "HeadlessChrome" traces from appVersion
    // ================================================================
    if (navigator.appVersion && navigator.appVersion.indexOf('HeadlessChrome') !== -1) {
        var fixedVersion = navigator.appVersion.replace(/HeadlessChrome/g, 'Chrome');
        Object.defineProperty(navigator, 'appVersion', {
            get: function() { return fixedVersion; },
            configurable: true
        });
    }
    
    // ================================================================
    // 17. Service Worker detection protection
    // ================================================================
    if (typeof ServiceWorkerContainer !== 'undefined') {
        var origRegister = ServiceWorkerContainer.prototype.register;
        if (origRegister) {
            ServiceWorkerContainer.prototype.register = function() {
                return origRegister.apply(this, arguments).catch(function() {
                    return Promise.resolve({
                        installing: null,
                        waiting: null,
                        active: null,
                        addEventListener: function() {},
                        update: function() { return Promise.resolve(); },
                        unregister: function() { return Promise.resolve(true); }
                    });
                });
            };
        }
    }
    
    // ================================================================
    // 18. WebRTC leak protection — prevent REAL IP leak
    // ================================================================
    if (typeof RTCPeerConnection !== 'undefined') {
        var origRTCPeerConnection = RTCPeerConnection;
        window.RTCPeerConnection = function(config, constraints) {
            // Force WebRTC to only use the proxy IP (public interface only)
            if (config && config.iceServers) {
                config.iceServers = [{ urls: 'stun:stun.l.google.com:19302' }];
            }
            return new origRTCPeerConnection(config, constraints);
        };
        window.RTCPeerConnection.prototype = origRTCPeerConnection.prototype;
        
        // Also patch webkitRTCPeerConnection
        if (typeof webkitRTCPeerConnection !== 'undefined') {
            var origWebkitRTCPeerConnection = webkitRTCPeerConnection;
            window.webkitRTCPeerConnection = function(config, constraints) {
                if (config && config.iceServers) {
                    config.iceServers = [{ urls: 'stun:stun.l.google.com:19302' }];
                }
                return new origWebkitRTCPeerConnection(config, constraints);
            };
            window.webkitRTCPeerConnection.prototype = origWebkitRTCPeerConnection.prototype;
        }
    }
    
    // ================================================================
    // 19. navigator.userAgentData spoofing (Chrome 90+ detection)
    // ================================================================
    if (navigator.userAgentData) {
        var origGetHighEntropyValues = navigator.userAgentData.getHighEntropyValues;
        navigator.userAgentData.getHighEntropyValues = function(hints) {
            return Promise.resolve({
                platform: fp.platform || 'Windows',
                platformVersion: '10.0.0',
                architecture: 'x86',
                model: '',
                uaFullVersion: fp.chromeVersion || '126.0.6478.122',
                fullVersionList: [
                    { brand: 'Google Chrome', version: fp.chromeVersion || '126.0.6478.122' },
                    { brand: 'Chromium', version: fp.chromeVersion || '126.0.6478.122' },
                    { brand: 'Not=A?Brand', version: '24.0.0.0' }
                ]
            });
        };
        
        Object.defineProperty(navigator.userAgentData, 'mobile', {
            get: function() { return fp.deviceType === 'mobile'; },
            configurable: true
        });
        Object.defineProperty(navigator.userAgentData, 'brands', {
            get: function() {
                return [
                    { brand: 'Google Chrome', version: fp.chromeVersion || '126' },
                    { brand: 'Chromium', version: fp.chromeVersion || '126' },
                    { brand: 'Not=A?Brand', version: '24' }
                ];
            },
            configurable: true
        });
    }
    
    // ================================================================
    // 20. Override isTrusted for touch events (defeats #14 detection)
    // ================================================================
    if (typeof TouchEvent !== 'undefined') {
        var origTouchEvent = TouchEvent;
        // Override the isTrusted property for touch events
        Object.defineProperty(TouchEvent.prototype, 'isTrusted', {
            get: function() { return true; },
            configurable: true
        });
    }
    if (typeof MouseEvent !== 'undefined') {
        Object.defineProperty(MouseEvent.prototype, 'isTrusted', {
            get: function() { return true; },
            configurable: true
        });
    }
    if (typeof KeyboardEvent !== 'undefined') {
        Object.defineProperty(KeyboardEvent.prototype, 'isTrusted', {
            get: function() { return true; },
            configurable: true
        });
    }
    
    console.debug('[Stealth] Core patches applied');
})();
"""

# ============================ CANVAS / WEBGL / AUDIO NOISE SCRIPT ============================
# Runs in a separate isolated world to add fingerprint noise
# Uses session-specific seeds from fingerprint_manager

CANVAS_NOISE_SCRIPT = r"""
(function() {
    'use strict';
    
    var fp = window.__fp__ || {};
    var canvasSeed = fp.canvasSeed || Math.floor(Math.random() * 1000000);
    var audioSeed = fp.audioSeed || Math.floor(Math.random() * 1000000);
    var webglVendor = fp.webglVendor || 'Google Inc. (NVIDIA)';
    var webglRenderer = fp.webglRenderer || 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)';
    
    // === Seeded PRNG for consistent per-session noise ===
    function SeededRandom(seed) {
        this.seed = seed;
    }
    SeededRandom.prototype.next = function() {
        this.seed = (this.seed * 16807 + 0) % 2147483647;
        return (this.seed - 1) / 2147483646;
    };
    
    var canvasRng = new SeededRandom(canvasSeed);
    
    // === Canvas Fingerprint Noise ===
    // Subtle per-pixel noise added to getImageData and toDataURL
    if (typeof HTMLCanvasElement !== 'undefined') {
        var origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {
            var ctx = this.getContext('2d');
            if (ctx) {
                try {
                    var imageData = ctx.getImageData(0, 0, 
                        Math.min(this.width, 50), Math.min(this.height, 50));
                    var data = imageData.data;
                    for (var i = 0; i < data.length; i += 4) {
                        var noise = Math.round(canvasRng.next() * 2 - 1);
                        data[i] = Math.min(255, Math.max(0, data[i] + noise));
                        data[i+1] = Math.min(255, Math.max(0, data[i+1] + noise));
                        data[i+2] = Math.min(255, Math.max(0, data[i+2] + noise));
                    }
                    ctx.putImageData(imageData, 0, 0);
                } catch(e) {}
            }
            return origToDataURL.apply(this, arguments);
        };
        
        var origToBlob = HTMLCanvasElement.prototype.toBlob;
        HTMLCanvasElement.prototype.toBlob = function(callback) {
            var args = arguments;
            // Same noise as toDataURL
            var ctx = this.getContext('2d');
            if (ctx) {
                try {
                    var imageData = ctx.getImageData(0, 0,
                        Math.min(this.width, 50), Math.min(this.height, 50));
                    var data = imageData.data;
                    for (var i = 0; i < data.length; i += 4) {
                        var noise = Math.round(canvasRng.next() * 2 - 1);
                        data[i] = Math.min(255, Math.max(0, data[i] + noise));
                        data[i+1] = Math.min(255, Math.max(0, data[i+1] + noise));
                        data[i+2] = Math.min(255, Math.max(0, data[i+2] + noise));
                    }
                    ctx.putImageData(imageData, 0, 0);
                } catch(e) {}
            }
            return origToBlob.apply(this, args);
        };
    }
    
    // === WebGL Fingerprint Override ===
    if (typeof WebGLRenderingContext !== 'undefined') {
        var origGetParam = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // UNMASKED_VENDOR_WEBGL = 37445
            if (parameter === 37445) {
                return webglVendor;
            }
            // UNMASKED_RENDERER_WEBGL = 37446
            if (parameter === 37446) {
                return webglRenderer;
            }
            // MAX_TEXTURE_SIZE - add subtle variation
            if (parameter === 3379) {
                var result = origGetParam.call(this, parameter);
                return Math.max(4096, result - Math.floor(canvasRng.next() * 1024));
            }
            return origGetParam.call(this, parameter);
        };
        
        // Also patch WebGL2RenderingContext
        if (typeof WebGL2RenderingContext !== 'undefined') {
            var origGetParam2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return webglVendor;
                if (parameter === 37446) return webglRenderer;
                return origGetParam2.call(this, parameter);
            };
        }
    }
    
    // === AudioContext Fingerprint Noise ===
    var audioRng = new SeededRandom(audioSeed);
    
    if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
        var AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
            var origCreateAnalyser = AudioCtx.prototype.createAnalyser;
            AudioCtx.prototype.createAnalyser = function() {
                var analyser = origCreateAnalyser.apply(this, arguments);
                var origGetFloatFrequencyData = analyser.getFloatFrequencyData;
                analyser.getFloatFrequencyData = function(array) {
                    origGetFloatFrequencyData.call(this, array);
                    // Add imperceptible noise to frequency data
                    for (var i = 0; i < array.length; i++) {
                        array[i] += (audioRng.next() * 0.000001);
                    }
                };
                return analyser;
            };
        }
    }
    
    // === Font Enumeration Protection ===
    // Some detection scripts enumerate available fonts
    // Add slight delay to font loading to appear natural
    if (document.fonts && document.fonts.ready) {
        var origReady = Object.getOwnPropertyDescriptor(Document.prototype, 'fonts');
        // Do nothing invasive, just ensure fonts.ready resolves normally
    }
    
    console.debug('[Stealth] Canvas/WebGL/Audio noise applied');
})();
"""

# ============================ PLATFORM ENTROPY SCRIPT ============================
# Additional entropy sources to make fingerprints more realistic

PLATFORM_ENTROPY_SCRIPT = r"""
(function() {
    'use strict';
    
    var fp = window.__fp__ || {};
    
    // === Randomize connection info (RTT, downlink, etc.) ===
    if (navigator.connection) {
        var conn = navigator.connection;
        Object.defineProperty(conn, 'rtt', {
            get: function() { return fp.rtt || 50 + Math.floor(Math.random() * 100); },
            configurable: true
        });
        Object.defineProperty(conn, 'downlink', {
            get: function() { return fp.downlink || 10 + Math.random() * 50; },
            configurable: true
        });
        Object.defineProperty(conn, 'effectiveType', {
            get: function() { return fp.effectiveType || '4g'; },
            configurable: true
        });
        Object.defineProperty(conn, 'saveData', {
            get: function() { return false; },
            configurable: true
        });
    }
    
    // === Hide automation frame count ===
    // Chrome in automation mode has frameCount === 0 on about:blank
    // Some detection scripts check this
    if (window.length === 0 && window.self === window.top) {
        try {
            var iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = 'about:blank';
            document.body.appendChild(iframe);
            setTimeout(function() {
                try { document.body.removeChild(iframe); } catch(e) {}
            }, 100);
        } catch(e) {}
    }
    
    // === Touch support entropy ===
    // Match device type: desktop = no touch, mobile = touch
    if (fp.deviceType === 'desktop') {
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: function() { return 0; },
            configurable: true
        });
        delete window.ontouchstart;
    } else if (fp.deviceType === 'mobile') {
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: function() { return 5; },
            configurable: true
        });
    }
    
    // === Clipboard API ===
    // Real browsers have clipboard API
    if (!navigator.clipboard) {
        navigator.clipboard = {
            readText: function() { return Promise.resolve(''); },
            writeText: function() { return Promise.resolve(); },
            read: function() { return Promise.resolve([]); },
            write: function() { return Promise.resolve(); }
        };
    }
    
    // === Credentials Management API ===
    if (!navigator.credentials && typeof PasswordCredential !== 'undefined') {
        navigator.credentials = {
            get: function() { return Promise.resolve(null); },
            store: function() { return Promise.resolve(); },
            preventSilentAccess: function() { return Promise.resolve(); }
        };
    }
    
    console.debug('[Stealth] Platform entropy applied');
})();
"""

# ============================ WEB WORKER PROTECTION ============================
# Injects into Web Workers to ensure consistent navigator spoofing

WORKER_INJECTION_SCRIPT = r"""
// This script is injected into Web Workers to maintain fingerprint consistency
(function() {
    'use strict';
    
    if (typeof navigator !== 'undefined') {
        Object.defineProperty(navigator, 'webdriver', {
            get: function() { return false; },
            configurable: true
        });
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: function() { return self.__worker_hw_concurrency__ || 8; },
            configurable: true
        });
        Object.defineProperty(navigator, 'deviceMemory', {
            get: function() { return self.__worker_device_memory__ || 8; },
            configurable: true
        });
        Object.defineProperty(navigator, 'platform', {
            get: function() { return self.__worker_platform__ || 'Win32'; },
            configurable: true
        });
        Object.defineProperty(navigator, 'languages', {
            get: function() { return (self.__worker_languages__ || ['en-US', 'en']).slice(); },
            configurable: true
        });
        Object.defineProperty(navigator, 'language', {
            get: function() { 
                var langs = self.__worker_languages__ || ['en-US', 'en'];
                return langs[0];
            },
            configurable: true
        });
    }
})();
"""


# ============================ STEALTH PATCHER CLASS ============================

class StealthPatcher:
    """
    Applies anti-detection patches to Playwright browser contexts and pages.
    
    Must be called BEFORE any page navigation to ensure stealth scripts
    execute before any site JavaScript.
    
    Two levels of patching:
    1. Context-level: patch_context() - applies to all pages in a browser context
    2. Page-level:   patch_page()   - additional CDP-level injection
    
    Usage:
        context = await browser.new_context()
        await StealthPatcher.patch_context(context, fingerprint)
        
        page = await context.new_page()
        await StealthPatcher.patch_page(page, fingerprint)
        await page.goto('https://target.com')
    """
    
    @staticmethod
    def _build_fp_object(fingerprint: Optional[Dict] = None) -> str:
        """Build the __fp__ JavaScript object from fingerprint dict."""
        if not fingerprint:
            fingerprint = {}
        
        fp_lines = []
        fp_lines.append(f'window.__fp__ = {{')
        fp_lines.append(f'    hardwareConcurrency: {fingerprint.get("hardware_concurrency", 8)},')
        fp_lines.append(f'    deviceMemory: {fingerprint.get("device_memory", 8)},')
        fp_lines.append(f'    platform: "{fingerprint.get("platform", "Win32")}",')
        fp_lines.append(f'    screenWidth: {fingerprint.get("screen_width", 1920)},')
        fp_lines.append(f'    screenHeight: {fingerprint.get("screen_height", 1080)},')
        fp_lines.append(f'    availWidth: {fingerprint.get("avail_width", 1920)},')
        fp_lines.append(f'    availHeight: {fingerprint.get("avail_height", 1040)},')
        fp_lines.append(f'    colorDepth: {fingerprint.get("color_depth", 24)},')
        fp_lines.append(f'    userAgent: "{fingerprint.get("user_agent", "")}",')
        fp_lines.append(f'    languages: {fingerprint.get("languages", ["en-US", "en"])},')
        fp_lines.append(f'    canvasSeed: {fingerprint.get("canvas_seed", 0)},')
        fp_lines.append(f'    audioSeed: {fingerprint.get("audio_seed", 0)},')
        fp_lines.append(f'    webglVendor: "{fingerprint.get("webgl_vendor", "Google Inc. (NVIDIA)")}",')
        fp_lines.append(f'    webglRenderer: "{fingerprint.get("webgl_renderer", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)")}",')
        fp_lines.append(f'    deviceType: "{fingerprint.get("device_type", "desktop")}",')
        fp_lines.append(f'    rtt: {fingerprint.get("rtt", 50)},')
        fp_lines.append(f'    downlink: {fingerprint.get("downlink", 10)},')
        fp_lines.append(f'    effectiveType: "{fingerprint.get("effective_type", "4g")}",')
        fp_lines.append(f'    timezone: "{fingerprint.get("timezone", "America/New_York")}",')
        fp_lines.append(f'    locale: "{fingerprint.get("locale", "en-US")}",')
        fp_lines.append('};')
        
        return '\n'.join(fp_lines)
    
    @staticmethod
    async def patch_context(context, fingerprint: Optional[Dict] = None):
        """
        Apply CDP-level stealth patches to a browser context.
        All new pages in this context will inherit these patches.
        
        Args:
            context: Playwright BrowserContext
            fingerprint: Optional fingerprint dict from FingerprintFactory
        """
        # Build fingerprint object for JS
        fp_script = StealthPatcher._build_fp_object(fingerprint)
        
        # Inject fingerprint object first (so it's available to patches)
        await context.add_init_script(fp_script)
        
        # Inject core stealth patches
        await context.add_init_script(STEALTH_SCRIPT_BASE)
        
        # Inject canvas/WebGL/audio noise
        await context.add_init_script(CANVAS_NOISE_SCRIPT)
        
        # Inject platform entropy
        await context.add_init_script(PLATFORM_ENTROPY_SCRIPT)
        
        logger.debug(f"StealthPatcher: Context patched (fp_seed={fingerprint.get('canvas_seed', 'none') if fingerprint else 'none'})")
    
    @staticmethod
    async def patch_page(page, fingerprint: Optional[Dict] = None):
        """
        Apply additional CDP-level patches to a specific page.
        Use this for extra protection on high-value pages.
        
        Args:
            page: Playwright Page
            fingerprint: Optional fingerprint dict
        """
        try:
            cdp = await page.context.new_cdp_session(page)
            
            # Inject fingerprint object via CDP
            fp_script = StealthPatcher._build_fp_object(fingerprint)
            await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
                'source': fp_script,
                'worldName': 'stealth-fp'
            })
            
            # Inject core stealth via CDP (runs in main world before page JS)
            await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
                'source': STEALTH_SCRIPT_BASE,
                'worldName': 'stealth-core'
            })
            
            # Inject canvas/Audio noise in isolated world
            await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
                'source': CANVAS_NOISE_SCRIPT,
                'worldName': 'stealth-canvas'
            })
            
            # Inject platform entropy
            await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
                'source': PLATFORM_ENTROPY_SCRIPT,
                'worldName': 'stealth-platform'
            })
            
            # Inject worker protection
            worker_script = WORKER_INJECTION_SCRIPT
            if fingerprint:
                worker_script = worker_script.replace(
                    'self.__worker_hw_concurrency__ || 8',
                    f'self.__worker_hw_concurrency__ || {fingerprint.get("hardware_concurrency", 8)}'
                ).replace(
                    'self.__worker_device_memory__ || 8',
                    f'self.__worker_device_memory__ || {fingerprint.get("device_memory", 8)}'
                ).replace(
                    'self.__worker_platform__ || \'Win32\'',
                    f'self.__worker_platform__ || \'{fingerprint.get("platform", "Win32")}\''
                ).replace(
                    'self.__worker_languages__ || [\'en-US\', \'en\']',
                    f'self.__worker_languages__ || {fingerprint.get("languages", ["en-US", "en"])}'
                )
            
            await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
                'source': worker_script,
                'worldName': 'stealth-worker'
            })
            
            await cdp.detach()
            logger.debug(f"StealthPatcher: Page patched via CDP")
            
        except Exception as e:
            logger.warning(f"StealthPatcher: CDP page patching failed: {e}")
    
    @staticmethod
    async def verify_stealth(page) -> Dict:
        """
        Verify that stealth patches are active.
        Returns dict of detection test results.
        Intended for testing/debugging.
        """
        results = {}
        
        tests = {
            'webdriver': 'navigator.webdriver',
            'plugins': 'navigator.plugins.length',
            'mimeTypes': 'navigator.mimeTypes.length',
            'languages': 'navigator.languages',
            'platform': 'navigator.platform',
            'hardwareConcurrency': 'navigator.hardwareConcurrency',
            'deviceMemory': 'navigator.deviceMemory',
            'chrome': 'typeof window.chrome !== "undefined"',
            'outerWidth': 'window.outerWidth > 0',
            'outerHeight': 'window.outerHeight > 0',
            'screenWidth': 'screen.width > 0',
            'screenHeight': 'screen.height > 0',
        }
        
        for name, js in tests.items():
            try:
                result = await page.evaluate(f'(() => {{ try {{ return {js}; }} catch(e) {{ return "ERROR: " + e.message; }} }})()')
                results[name] = result
            except Exception as e:
                results[name] = f'EVAL_ERROR: {e}'
        
        return results


# ============================ STANDALONE TEST ============================
if __name__ == '__main__':
    import asyncio
    from playwright.async_api import async_playwright
    
    async def test_stealth():
        print("=" * 60)
        print("  STEALTH PATCHER TEST")
        print("=" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Test 1: Without stealth (should show webdriver=true)
            print("\n[Test 1] Without stealth patches:")
            context1 = await browser.new_context()
            page1 = await context1.new_page()
            await page1.goto('about:blank')
            webdriver1 = await page1.evaluate('navigator.webdriver')
            print(f"  navigator.webdriver = {webdriver1}")
            
            # Test 2: With stealth patches
            print("\n[Test 2] With stealth patches:")
            context2 = await browser.new_context()
            
            test_fp = {
                'hardware_concurrency': 12,
                'device_memory': 32,
                'platform': 'Win32',
                'screen_width': 1920,
                'screen_height': 1080,
                'avail_width': 1920,
                'avail_height': 1040,
                'color_depth': 24,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'canvas_seed': 123456,
                'audio_seed': 789012,
                'webgl_vendor': 'Google Inc. (NVIDIA)',
                'webgl_renderer': 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)',
                'device_type': 'desktop',
            }
            
            await StealthPatcher.patch_context(context2, test_fp)
            
            page2 = await context2.new_page()
            await page2.goto('about:blank')
            
            # Run all checks
            results = await StealthPatcher.verify_stealth(page2)
            print(f"  navigator.webdriver = {results['webdriver']}")
            print(f"  navigator.plugins.length = {results['plugins']}")
            print(f"  navigator.hardwareConcurrency = {results['hardwareConcurrency']}")
            print(f"  navigator.deviceMemory = {results['deviceMemory']}")
            print(f"  navigator.platform = {results['platform']}")
            print(f"  navigator.languages = {results['languages']}")
            print(f"  screen.width = {results['screenWidth']}")
            print(f"  chrome available = {results['chrome']}")
            
            # Test 3: Navigate to a real site that checks fingerprints
            print("\n[Test 3] Navigating to fingerprint test site...")
            try:
                await page2.goto('https://bot.sannysoft.com', wait_until='networkidle', timeout=15000)
                title = await page2.title()
                print(f"  Page title: {title}")
                
                # Check if any "FAIL" indicators
                page_text = await page2.evaluate('document.body.innerText')
                fail_count = page_text.count('❌') if '❌' in page_text else 0
                print(f"  Detection indicators found: {fail_count}")
            except Exception as e:
                print(f"  Test site error (expected if offline): {e}")
            
            await browser.close()
        
        print("\n" + "=" * 60)
        print("  TEST COMPLETE")
        print("=" * 60)
    
    asyncio.run(test_stealth())