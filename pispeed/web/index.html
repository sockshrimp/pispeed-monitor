diff --git a/pispeed/web/index.html b/pispeed/web/index.html
index b850ab4b31e0fbd750939195a7379989e9481337..5d08cecdf001a5b82f6a585dc5731208e5c7ecfa 100644
--- a/pispeed/web/index.html
+++ b/pispeed/web/index.html
@@ -55,52 +55,53 @@
   /* Header */
   header {
     display: flex;
     align-items: center;
     justify-content: space-between;
     padding: 28px 0 32px;
     border-bottom: 1px solid var(--border);
     margin-bottom: 32px;
   }
 
   .logo {
     display: flex;
     align-items: center;
     gap: 14px;
   }
 
   .logo-icon {
     width: 44px; height: 44px;
     background: linear-gradient(135deg, var(--accent), var(--accent3));
     border-radius: 10px;
     display: flex; align-items: center; justify-content: center;
     font-size: 22px;
   }
 
   .logo h1 {
+    font-family: var(--font);
     font-size: 22px;
-    font-weight: 800;
+    font-weight: 700;
     letter-spacing: -0.5px;
     color: var(--text);
   }
 
   .logo span {
     font-size: 12px;
     color: var(--text3);
     font-family: var(--mono);
     display: block;
     margin-top: 2px;
   }
 
   nav {
     display: flex;
     gap: 4px;
     background: var(--surface);
     padding: 4px;
     border-radius: var(--radius);
     border: 1px solid var(--border);
   }
 
   nav button {
     background: none;
     border: none;
     color: var(--text2);
@@ -1266,51 +1267,51 @@ function loadSettings() {
     document.getElementById('cfgInterval').value = cfg.interval_minutes || '';
     document.getElementById('cfgBackend').value = cfg.backend || 'auto';
     document.getElementById('cfgPort').value = cfg.port || '';
     document.getElementById('cfgName').value = cfg.display_name || '';
   }).catch(() => showToast('Could not load settings'));
 }
 
 async function saveSettings() {
   const newCfg = {
     isp_download: parseFloat(document.getElementById('cfgIspDown').value),
     isp_upload: parseFloat(document.getElementById('cfgIspUp').value),
     threshold_percent: parseFloat(document.getElementById('cfgThreshold').value),
     interval_minutes: parseInt(document.getElementById('cfgInterval').value),
     backend: document.getElementById('cfgBackend').value,
     port: parseInt(document.getElementById('cfgPort').value),
     display_name: document.getElementById('cfgName').value,
   };
 
   try {
     const r = await fetch('/api/config', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify(newCfg)
     });
     const data = await r.json();
-    if (resp.ok) {
+    if (r.ok) {
       config = data.config;
       showToast('✅ Settings saved!');
       renderDashboard();
       renderViolations();
       loadSettings();
     } else {
       showToast('❌ Error: ' + data.message);
     }
   } catch(e) {
     showToast('❌ Failed to save settings');
   }
 }
 
 // ─── Actions ──────────────────────────────────────────────────
 async function triggerTest() {
   const btn = document.getElementById('runBtn');
   btn.disabled = true;
   try {
     const r = await fetch('/api/trigger', { method: 'POST' });
     const d = await r.json();
     if (d.status === 'started') {
       showToast('🚀 Speedtest started!');
       document.getElementById('runningBadge').classList.add('visible', 'was-running');
     } else {
       showToast('⏳ ' + d.message);
