-- Restore the two startup fields captured before this specific trial.
-- Run using sqlite3 -bail. Refuse to overwrite subsequent conflicting edits.
BEGIN IMMEDIATE;
CREATE TEMP TABLE voice_startup_guard (matched INTEGER CHECK (matched = 2));
INSERT INTO voice_startup_guard
SELECT count(*) FROM package_app_info
WHERE app_id IN ('com.samsung.tv.ondevice-voice', 'com.samsung.tv.bixby-prov')
  AND app_disable = 'false' AND app_onboot = 'false' AND app_autorestart = 'false';
UPDATE package_app_info SET app_onboot = 'true', app_autorestart = 'true'
WHERE app_id IN ('com.samsung.tv.ondevice-voice', 'com.samsung.tv.bixby-prov');
COMMIT;
