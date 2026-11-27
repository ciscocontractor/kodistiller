# kodistiller

**Extract TVDB television series data into Kometa metadata YAML files for import into Plex.**

In December 2026, Plex is ending data access contracts with The TVDB for television series metadata. Rather than cluttering your filesystem with per-episode NFO/JPG sidecar files or modifying embedded media tags, `kodistiller` pulls metadata directly from The TVDB v4 API and formats it for Kometa to import into your Plex database.

> **Disclaimer & Public Domain:** I am no expert on Kometa or The TVDB, and I do not intend to maintain this long term. This project is released into the **public domain** without warranty, expressed or implied, in hopes that it helps those affected or inspires a better tool.  
> **AI Content Disclosure:** Portions of the Python code and documentation were created with AI assistance.

---

## Goals
* Aquire Television series metadata directly from the TVDB and import to Plex.
* Prevent clutter of the media library filesystems or require write access to them.
* Make it fully automatic. Once installed and scheduled, it should update without manual tasks.
* Provide flexibility to use different episode ordering on a per-series basis. 

---

## What It Does (and Doesn't Do)

* **Imports:** Series, season, and episode titles, summaries, and first air dates; series content ratings; episode thumbnails; and a Plex label (e.g., `tvdb-dvd`) so you can easily filter TVDB-managed shows in the Plex UI.
* **Supports Localization:** Set the `LANGUAGE` variable in `buildtvdbyaml.py` (e.g., `eng`, `spa`, `fra`, `jpn`) to prefer translated titles and summaries when available.
* **Does Not Import:** Genres, actors, studios, collections, episode ratings, or series/season posters and banners. **Recommended workflow:** Match new shows against TMDB first to populate credits, genres, and artwork, then apply `kodistiller` where episode ordering or text metadata needs TVDB data.
* **Manual Plex Step:** Kometa cannot change the episode ordering setting inside Plex for a library or series. You must still set that preference manually in the Plex UI.

---

## Quick Start

### 1. Prerequisites
* A Unix-like OS (FreeBSD, Linux, macOS; Windows is untested, though Cygwin may work) with POSIX utilities (`sh`, `awk`, `find`, `sort`, `tr`, `xargs`).
* Python 3 with the TVDB v4 client and PyYAML:
  ```sh
  python -m pip install tvdb_v4_official PyYAML
  ```
* A working [Kometa](https://kometa.wiki) installation and a personal [TVDB v4 API key](https://thetvdb.com). **Never commit or publicly share your API key.**

### 2. Configure the Scripts
1. **`buildtvdbyaml.sh`:** Update `MEDIA_PATH` (your TV root folder) and `CONFIG_PATH` (your Kometa metadata output folder).
2. **`buildtvdbyaml.py`:** Place your API key in an `api.key` file inside `CONFIG_PATH` (or set `TVDB_API_KEY` directly in the script). Optionally adjust `LANGUAGE` and `COUNTRY`.
3. **Kometa `config.yml`:** Point your TV library to the output directory:
   ```yaml
   TV Shows:
     metadata_files:
       - folder: config/metadata/Television
   ```

### 3. Tag Your Folders & Run
Add `{tvdb-<id>}` and an optional `{tvdborder-<order>}` tag (e.g., `official`, `dvd`, `absolute`, `alternate`) to your series directories:

```text
/media/television/Firefly (2002) {tvdb-78874} {tvdborder-dvd}
```

Run the batch wrapper to scan your library and generate `tvdb_<id>_metadata.yml` files:

```sh
./buildtvdbyaml.sh
```

Or generate a single series manually from the command line:

```sh
python buildtvdbyaml.py 78874 dvd
```

### 4. Optional full automation
Schedule to run the buildtvdbyaml.sh weekly by cron or your scheduling agent.
Schedule kometa to run daily, after the Plex scheduled maintenance window.

Series data could be updated more frequently, but I don't want to get people banned from overusing the TVDB API on a developer key. Any new episodes found during Plex scheduled library scans will get updated by kometa during its run, using the previously fetched data.

---

## Known Issues

* **Multiple Editions or Split Series:** By default, generated YAML files apply to all versions or editions of a show sharing the same TVDB ID (for example, *Pokemon (Aired in JP)* and *Pokemon (US Dub)*). As of version `2026-11-24`, you can isolate specific editions using Plex `{edition-...}` tags paired with a third argument or space-separated order tag (e.g., `{tvdborder-regional Japanese}` or `none` for untagged default editions). You may also specify `zero` like an edition tag to collect data only for Season Zero "Specials", while leaving data of other seasons managed by Plex providers.
* **IMDB Dual-ID Matching:** Code to match on both IMDB and TVDB IDs is included in `buildtvdbyaml.py` as a hedge against future Plex changes, though it is currently disabled by default.

---

## Full Documentation

For complete CLI syntax, all supported TVDB ordering strings, edition-filtering rules, log files, and configuration variables, see the included manual page:

```sh
man ./kodistiller.1
cat examples.txt
```

*(Or view `examples.txt` / `kodistiller.txt` / `kodistiller.1.html` in this repository.)*

2026-11-27
