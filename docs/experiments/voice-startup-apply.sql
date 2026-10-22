-- AU8000 T-KSU2EAKUC-2301.1 only. Run using sqlite3 -bail.
-- Save original rows first; these guards require the observed original state.
BEGIN IMMEDIATE;
CREATE TEMP TABLE voice_startup_guard (matched INTEGER CHECK (matched = 2));
INSERT INTO voice_startup_guard
SELECT count(*) FROM package_app_info
WHERE app_id IN ('com.samsung.tv.ondevice-voice', 'com.samsung.tv.bixby-prov')
  AND app_disable = 'false' AND app_onboot = 'true' AND app_autorestart = 'true';
UPDATE package_app_info SET app_onboot = 'false', app_autorestart = 'false'
WHERE app_id IN ('com.samsung.tv.ondevice-voice', 'com.samsung.tv.bixby-prov');
COMMIT;
