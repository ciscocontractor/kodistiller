#!/usr/bin/env python

### Ver 2026-11-23

### Be sure to install tvdb-v4 python Package
#python -m pip install tvdb_v4_official

import tvdb_v4_official
import yaml
import sys

# Configuration  You want to customize this section
# Got tired of stripping my key every time I updated git, so you can do manually below or put it in ./api.key
try:
    with open("api.key", "r", encoding="utf-8") as f:
        TVDB_API_KEY = str(f.read()).strip() or "YOUR_TVDB_V4_API_KEY"  # falls back if file empty/missing
except OSError:
    TVDB_API_KEY = "YOUR_TVDB_V4_API_KEY"
TVDB_PIN = None  # Set to your subscriber PIN string if required by your project

SERIES_ID = sys.argv[1] if len(sys.argv) > 1 else "121361"  # Example: Game of Thrones
SEASON_TYPE = sys.argv[2] if len(sys.argv) > 2 else "default"
#Some order options: "default" (Aired), "official", "dvd", "absolute", "alternate" (Streaming), "regional", and "altdvd"
LANGUAGE = "eng"  # 3-letter ISO 639-2 code (e.g., "eng", "spa", "fra", "jpn")
COUNTRY = "usa"  # 3-letter ISO code, for finding content ratings
OUTPUT_FILE = f"tvdb_{SERIES_ID}_metadata.yml"


def fetch_series_data(tvdb, series_id, output_path, season_type="default", lang="eng"):
    # Fetch base series info and translation if requested
    series = tvdb.get_series_extended(series_id)
    show_title = series.get("name", "")
    show_summary = series.get("overview", "")
    show_available = series.get("firstAired", "")
    show_rating = ""
    show_ratings = series.get("contentRatings", "")
    for rating in show_ratings:
        show_rating = rating.get('name') if rating.get('country') == COUNTRY else ""
    show_language = series.get("originalLanguage", lang)

    print(f"TVDB ID: {series_id}")  # DEBUG
    remote_ids = series.get("remoteIds", [])
    tmdb_id = next(
        (item["id"] for item in remote_ids if item.get("sourceName") == "TheMovieDB.com"),
        None
    )
    print(f"TMDB ID: {tmdb_id}")  # DEBUG
    imdb_id = next(
        (item["id"] for item in remote_ids if item.get("sourceName") == "IMDB"),
        None
    )
    print(f"IMDB ID: {imdb_id}")  # DEBUG

    # if the native language of the series is not ours, look for translations
    if show_language != lang:
        try:
            trans = tvdb.get_series_translation(series_id, lang)
            show_title = trans.get("name") or show_title
            show_summary = trans.get("overview") or show_summary
        except Exception:
            pass  # Fallback to default language if translation is missing

    ########

    # build season specific data, loop by season ID, map to season numbering
    # episodes have a default season which they belong to, but there is no default season per se
    serseason_type = "official" if season_type == "default" else season_type
    seasons_dict={}

    # strip only single prefered order
    series_seasons = [
        s for s in series["seasons"]
        if s["type"]["type"] == serseason_type
    ]

    # find translated title and description
    for season in series_seasons:
        season_id = season["id"]
        s_num = season["number"]
        seasons_dict[s_num] = {"episodes": {}}

        # Base season name (often None if not set at the root level)
        title = overview = ""
        title = season.get("name")

        # Fetch language-specific title and overview
        try:
            translation = tvdb.get_season_translation(season_id, lang)
            title = translation.get("name")
            overview = translation.get("overview")
        except Exception:
            # Fallback if no translation exists for the requested language
            title = title

        if title == f"Season {s_num}":
            title = ''

        seasons_dict[s_num]["title"] = title
        seasons_dict[s_num]["summary"] = overview

        #print(f"TT: {title}")  #DEBUG
        #print(f"TS: {overview}")  #DEBUG
        #print(f"TN: {s_num}")  #DEBUG

    ########

    # now loop the episode tree, which is ordered by episode ID, including season markers as a child item,
    # because an episode item will belown to different seasons based on the season_type
    # unsure if we need to force season_type official instead of default. are there cases where default!=official?
    episodes = []
    page = 0
    while True:
        ep_data = tvdb.get_series_episodes(
            series_id, season_type=season_type, page=page, lang=lang
        )
        batch = ep_data.get("episodes", [])
        if not batch:
            break
        episodes.extend(batch)
        page += 1

    # Organize episodes by season -> episode number
    for ep in episodes:
        s_num = ep.get("seasonNumber")
        e_num = ep.get("number")
        if s_num is None or e_num is None:
            continue

        #print(f"EN: {s_num}")  #DEBUG
        if s_num not in seasons_dict:
            seasons_dict[s_num] = {"episodes": {}}
        if not seasons_dict[s_num].get("episodes"):
            seasons_dict[s_num]["episodes"] = {}

        # build array of episode data
        ep_entry = {}
        if ep.get("name"):
            ep_entry["title"] = ep["name"]
        if ep.get("overview"):
            ep_entry["summary"] = ep["overview"]
        if ep.get("aired"):
            ep_entry["originally_available"] = ep["aired"]
        if ep.get("image"):
            ep_entry["url_poster"] = "https://artworks.thetvdb.com" + ep["image"]

        if ep_entry:
            seasons_dict[s_num]["episodes"][e_num] = ep_entry


    # Sort seasons and episodes numerically
    sorted_seasons = {}
    for s_num in sorted(seasons_dict.keys()):
        sorted_eps = dict(sorted(seasons_dict[s_num]["episodes"].items()))
        sorted_seasons[s_num] = {}
        if seasons_dict[s_num].get("title"):
            sorted_seasons[s_num]["title"] = seasons_dict[s_num]["title"]
            #print(f"ST: {seasons_dict[s_num]["title"]}")  #DEBUG
        if seasons_dict[s_num].get("summary"):
            sorted_seasons[s_num]["summary"] = seasons_dict[s_num]["summary"]
            #print(f"SS: {seasons_dict[s_num]["summary"]}")  #DEBUG
        sorted_seasons[s_num]["episodes"] = sorted_eps

    ########


    # Build top-level Kometa metadata structure
    show_block = {}
    # Build show-level Kometa metadata structure
    if show_title:
        show_block["title"] = show_title
    if show_summary:
        show_block["summary"] = show_summary
    if show_available:
        show_block["originally_available"] = show_available
    if show_rating:
        show_block["content_rating"] = show_rating
    #if season_type!="default":
    if season_type:
        show_block["label"] = "tvdb-" + season_type

    # Now build the episide tree
    show_block["seasons"] = sorted_seasons

    # If IMDB is available, use that to match, in case Plex deprecates TVDB linking. Doing one or the other only
    # has proved problematic where Plex series link to each ID is inconsistent, so we add BOTH as separate match blocks
    # The yaml.dump is smart enough to not dupicate the entire season data and use a pointer.

    # double importing using IMDB ID probably isn't required, now that we know it works, let's disable until needed
    imdb_id = ""
    #imdb_id = imdb_id if imdb_id != "None" else ""

    tvdb_block = {"tvdb_"+str(int(series_id)): { "match": {"mapping_id": int(series_id)}, } | show_block}
    imdb_block = {"imdb_"+imdb_id: { "match": {"mapping_id": imdb_id}, } | show_block} if imdb_id else {}

    kometa_data = {"metadata": tvdb_block | imdb_block}

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            kometa_data,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        )

    return show_title

if __name__ == "__main__":
    client = (
        tvdb_v4_official.TVDB(TVDB_API_KEY, pin=TVDB_PIN)
        if TVDB_PIN
        else tvdb_v4_official.TVDB(TVDB_API_KEY)
    )
    show_title = fetch_series_data(
        client, SERIES_ID, OUTPUT_FILE, season_type=SEASON_TYPE, lang=LANGUAGE
    )

    print(f"Successfully generated {OUTPUT_FILE} for '{show_title}'.")

