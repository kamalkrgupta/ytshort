# Published Shorts

This folder contains independent copies of Shorts verified as **public and processed** on the TECH AT 60 YouTube channel. Scheduled, private and incomplete uploads are excluded. Production originals stay in their existing locations so the publishing workflow remains intact.

- `published.csv`: spreadsheet-friendly register of lesson numbers, titles, video IDs, YouTube links, YouTube-reported publication timestamps, IST timestamps, planned release times, last verification, current visibility and filenames.
- `published.md`: readable list of published Shorts and links.
- `published.json`: machine-readable publication history.
- `records/<video ID>/`: publication record, upload receipt and metadata snapshots.
- `archive-status.json`: last synchronization and any errors.

Copies and checksums are retained even if a previously published video later becomes private or unavailable; its current visibility is updated in the register. Archive files are not removed automatically. Copies do not share file contents with the production originals.

The local upload routine archives newly confirmed public Shorts. The existing hourly publishing worker and daily readiness check also synchronize this folder, catching videos that become public through YouTube scheduling. This local folder can synchronize only while the Mac is running and online. No paid service is used.

Manual refresh: `.youtube-venv/bin/python tools/archive_published_shorts.py` from the workspace root.
