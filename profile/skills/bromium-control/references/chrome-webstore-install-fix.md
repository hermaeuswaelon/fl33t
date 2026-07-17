# Chrome Web Store Extension Install — Full Fix Reference

## Problem

Clicking "Add to Chrome" on Chrome Web Store opens an external OS Chromium window instead of installing the extension into Bromium.

## Root Cause

CEF's extension manager intercepts `clients2.google.com/service/update2/crx` URLs at the CEF network layer — **below** all browser events (OnBeforePopup, OnBeforeBrowse, etc.). Any navigation or network request to this URL is intercepted by CEF's internal extension install machinery before our Pascal handlers can act.

## Architecture of the Fix

### Files touched
- `dual_citizen_v2.lpr` — Added `ChromeWebStoreInstall` to `--disable-features`
- `ucontrollerbrowser.pas` — `DoLoadEnd` JS injection, `Timer1Timer` download+install, `install_crx` IPC, `FPendingExtId`/`FPendingCrxPath` fields, `InstallCRX()` function
- `~/.local/bin/bromium-crx-install.py` — Python CRX3 unpacker

### Key fields on TControllerForm
```pascal
FPendingExtId: string;    // Extension ID being downloaded
FPendingCrxPath: string;  // Path where curl is writing the CRX
```

### JS Hook Code (in `DoLoadEnd`)
```pascal
if (Pos('chromewebstore.google.com', LowerCase(frame.Url)) > 0) or
   (Pos('chrome.google.com/webstore', LowerCase(frame.Url)) > 0) then
begin
  browser.MainFrame.ExecuteJavaScript(
    '(function(){'+
    'function bromiumHookButton(){'+
    'var btns=document.querySelectorAll('+QuotedStr('button')+');'+
    'for(var i=0;i<btns.length;i++){'+
    'var b=btns[i];'+
    'if(b.textContent.trim()==='+QuotedStr('Add to Chrome')+'&&!b.dataset.bromiumHooked){'+
    'b.dataset.bromiumHooked="1";'+
    'b.addEventListener("click",function(e){'+
    'e.preventDefault();e.stopPropagation();'+
    'var id=window.location.pathname.split("/").pop().split("?")[0];'+
    'document.title="BROMIUM_CRX:"+id;'+
    '},true);'+
    '}'+
    '}'+
    '}'+
    'bromiumHookButton();'+
    'setInterval(bromiumHookButton,500);'+
    '})();',
    '', 0
  );
end;
```

### Timer Detection + Download Code (in `Timer1Timer`)
```pascal
// Check for pending download completion
if (FPendingCrxPath <> '') and (FPendingExtId <> '') then
begin
  if FileExists(FPendingCrxPath) then
  begin
    if (FindFirst(FPendingCrxPath, faAnyFile, sr) = 0) then
    begin
      if sr.Size > 100 then
      begin
        FindClose(sr);
        if InstallCRX(FPendingCrxPath) <> '' then
        begin
          LoadExtensions;
          FPendingExtId := '';
          FPendingCrxPath := '';
        end;
      end
      else FindClose(sr);
    end;
  end;
  Exit; // Wait for download
end;

// Check for BROMIUM_CRX: signal
for i := 0 to FTabCount - 1 do
begin
  title := FTabs[i].LastTitle;
  if Copy(title, 1, 12) = 'BROMIUM_CRX:' then
  begin
    extId := Copy(title, 13, Length(title) - 12);
    FTabs[i].LastTitle := 'BROMIUM_DOWNLOADING';
    crxUrl := '...&prodversion=131.0.6778.265&acceptformat=crx3&...';
    crxPath := EXT_STAGING + extId + '.crx';
    FPendingExtId := extId;
    FPendingCrxPath := crxPath;
    ExecuteProcess('/usr/bin/curl',
      Format('-s -L --compressed -o "%s" "%s"', [crxPath, crxUrl]));
    Break;
  end;
end;
```

### CRX Download URL (exact format)
```
https://clients2.google.com/service/update2/crx
  ?response=redirect
  &prod=chromiumcrx
  &prodversion=131.0.6778.265       ← REQUIRED (without: HTTP 204)
  &acceptformat=crx3                ← REQUIRED (without: HTTP 204)
  &x=id%3D<ext_id>%26v%3D%26installsource%3Dondemand%26uc
```

### CRX3 Binary Format
```
[0-3]   Magic    "Cr24"            — 4 bytes
[4-7]   Version  3 (LE uint32)     — 4 bytes
[8-11]  HdrLen   header length (LE) — 4 bytes
[12+]   Header   signed header data — HdrLen bytes
After   ZIP data                   — rest of file
```

## Failed Approaches (in order attempted)

1. **CEF flags only** (`--disable-extensions-dialogs`, `--disable-features=ExtensionInstallDialog`) — OS window still created
2. **OnBeforePopup interception** — Routes popups to new tabs, but extension manager bypasses this event
3. **OnOpenUrlFromTab interception** — Same: extension manager uses a different code path
4. **OnBeforeBrowse interception** — Catches CRX URL but extension manager already created the window at network level. Using `browser.Host.StartDownload(url)` works for regular URLs but CRX URLs are intercepted by extension manager internally
5. **JavaScript injection with `window.location.href = crx_url`** — The subsequent navigation triggers OnBeforeBrowse, but the extension manager intercepts at network level during the navigation, creating an OS window
6. **`<a download=".crx">` click from JS** — Cross-origin download restrictions prevent this from working for `clients2.google.com` URLs
7. **`fetch()` + blob download** — CORS: `clients2.google.com` doesn't include `Access-Control-Allow-Origin` headers
8. **CDP port 9224 injection** — `--remote-debugging-port` doesn't bind in this CEF4Delphi build (port not listening)
9. **Background `curl ... &` via `ExecuteProcess('/bin/sh', ...)`** — Shell quoting breaks with Pascal Format strings. The single-quote escaping inside Pascal string literals produces invalid shell commands. `ExecuteProcess` calls `fpSystem` which concatenates path + ' ' + command line and runs through `/bin/sh -c`, creating a double-indirection problem
10. **Direct synchronous `curl`** — Works! Blocks timer 2-5s but is reliable

## Pitfalls

- **Button selector is English-only**: `textContent === 'Add to Chrome'` won't match localized Chrome Web Store pages
- **ExecuteProcess quoting**: Never use `ExecuteProcess('/bin/sh', '-c ''cmd &''')` for backgrounding — the Pascal string quoting produces invalid sh syntax. Use `ExecuteProcess('/usr/bin/cmd', 'args')` directly
- **Timer blocks during download**: Synchronous `ExecuteProcess` blocks the main thread. IPC commands queue up and get processed on the next tick. Acceptable for 2-5s download
- **Restart required**: CEF only loads `--load-extension` at startup. The extension is installed to disk but not active until restart
- **No progress feedback**: No UI indicator during download. User sees nothing happen for 2-5s then title changes to `BROMIUM_DOWNLOADING`
- **Staging files accumulate**: `/tmp/bromium-crx-staging/` keeps the CRX file after install. Clean up periodically
