# Holo GPS 03

Holo GPS 03 is a static GPS tracking web app built for iPhone usage and GitHub Pages deployment.

All profile, trip, and history data is saved in browser storage. No backend is required.

## Features Implemented

- User profiles (create, rename, delete)
- Deleting a profile also deletes its ride history and mileage records
- Total mileage and trip mileage tracking per profile
- Ride history saved in browser storage
- Delete individual history entries
- Save and delete trails
- Compass heading with degree + cardinal text (example: NE 45 deg)
- North indicator always visible on map
- Map rotation mode toggle:
	- North Up
	- Follow Heading
- Recenter button that also resets map orientation to North Up
- Oahu offline map tile pack download and clear controls (standard zoom 11 to 14, high detail zoom 15 to 16)
- Full local backup and restore (profiles, rides, trails, mileage) using JSON export/import

## Offline Oahu Map

The app includes an offline tile workflow for Oahu:

- Open the app while online.
- In the right panel, open Display Options.
- Use Offline Oahu Map -> Download Standard z11-z14 or Download High Detail z15-z16.
- Keep the app open until caching completes.
- After download, Oahu map tiles for the selected preset are available offline in this browser.

Notes:

- Offline tiles are cached in the browser cache storage.
- Standard pack size is about 1390 tiles; high detail is about 19182 tiles and takes much longer.
- Use Clear Cache in the same section to remove cached tile packs.
- Offline availability is per-browser and per-origin.

## Backup And Restore (#2)

In Device Status:

- Export Data downloads a JSON backup.
- Import Data restores profiles, rides, trails, and mileage from a backup JSON file.
- This is useful for migration between devices or browsers.

## iPhone 15 Pro GPS And Sensor Notes

This app uses browser APIs, which means it uses Safari/WebKit access to iPhone sensors:

- Location: `navigator.geolocation.watchPosition`
	- Uses iPhone fused positioning (GNSS + Wi-Fi/cell assistance)
	- Reports latitude, longitude, accuracy, speed, and sometimes course/heading
- Direction/Compass: `DeviceOrientationEvent`
	- Uses device orientation sensors for heading when available
	- On iOS, compass permission must be requested from a user gesture

Practical behavior on iPhone:

- Heading is best outdoors and away from magnetic interference
- If orientation permission is denied, map stays in North Up mode
- GPS drift filtering is enabled to reduce bad jumps in recorded mileage

## Run Locally

Prerequisite: Node.js 20+

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Native iPhone App

This project can be wrapped as a native iPhone app with Capacitor.

```bash
npm install
npm run build
npm run cap:sync
npm run cap:open:ios
```

Then open the generated Xcode project, select your iPhone or simulator, and run.

Notes:

- The first time you open the project, Xcode may ask you to trust signing settings.
- The app still uses your bundled Vite build, so update the web app with `npm run build` and `npm run cap:sync` before reinstalling.

## GitHub Pages Deployment

This project is configured with:

- Vite base path: `/Holo-gps-03/`

Deploy to:

- `https://<your-github-username>.github.io/Holo-gps-03/`

## iPhone Install As App

1. Open the deployed URL in Safari.
2. Tap Share.
3. Tap Add to Home Screen.
4. Launch from Home Screen and grant:
	 - Location access
	 - Motion and orientation access (when prompted)

## Storage Notes

- Data is local to the same browser + origin
- Clearing site data removes profiles/history
- Storage keys are namespaced for this app to avoid collision with your other GPS projects

## Python 3.12 Helper (#file:3.12)

A helper script is included at scripts/oahu_tile_manifest.py.

It can be run with your attached Python 3.12 runtime, for example:

```bash
/Users/bagonoy/Desktop/Python_Project/CodeX_7_2026/Python312_runtime/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
	scripts/oahu_tile_manifest.py --min-zoom 11 --max-zoom 14 --output tile-manifest/oahu-z11-z14.json
```

This generates a manifest of Oahu tile URLs for offline planning/inspection workflows.

## Key Files

- Main app: [src/App.tsx](src/App.tsx)
- Map component: [src/components/Map.tsx](src/components/Map.tsx)
- Local data store: [src/lib/localData.ts](src/lib/localData.ts)
- Service worker offline cache: [public/sw.js](public/sw.js)
- Python tile manifest helper: [scripts/oahu_tile_manifest.py](scripts/oahu_tile_manifest.py)
- Build config: [vite.config.ts](vite.config.ts)
