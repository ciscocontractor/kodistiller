#!/bin/sh

#Set file path for your environment
MEDIA_PATH='/media/television'
CONFIG_PATH='/usr/local/share/kometa/config/metadata/tvdb/'

cd "$CONFIG_PATH"


find "$MEDIA_PATH" -name '*{tvdb-*' | awk '{ \
  if (match($0, /tvdb-[[:digit:]]+/)) {  printf  "%s ", substr($0, RSTART + 5, RLENGTH - 5) } \
  if (match($0, /tvdborder-[[:alpha:]]+/)) { print substr($0, RSTART + 10, RLENGTH - 10) } else { print "default" } \
}' | sort -u | tee serieslist.log | xargs -n 2 python buildtvdbyaml.py  | tee run.log


exit


: << 'ENDCOMMENT'

This should automate building a kometa metadata yaml file for each tv series from the TVDB API.
It requires an API key, which you should be able to get as in independent developer.

Requires a small addition to your config file:
TV Shows:
  metadata_files:
    - folder: config/metadata/folder_set_above

In your library, add tags to each series folder to control it, {tvdb-:digits:} and OPTIONALLY {tvdborder-:alphas:}
options are the api strings for relevant orders, EX:  "default" (Aired Order), "official", "dvd", "absolute", "alternate" (Streaming)
If you don't set an order tag, it uses "default", which works fine for many shows.

Example:  /media/television/Firefly (2002) {tvdb-78874} {tvdborder-dvd}

If you don't want to do folder naming, you can run manually as:
        python buildtvdbyaml.py 78874 dvd

Note, Kometa cannot change the order flag in Plex for the library or series, that's a manual step.

I tried to make it POSIX and not require GNU extensions, YMMV.
Yes, I had AI help with a lot of the python, as I'd never interacted with TVDB API directly.
there is at least one package you'll need to install, see first line of that code.

It currently pulls series and episode titles, summary, and first air date, but NOT for season because it made the looping harder,
series content rating, and episode thumbnails. No series and season thumbs because it returns an array of all available art.
This is probably an area where personal preference makes manually picking artwork preferred anyway.

If you change the language variable in the python script, it will prefer localized series title and summary, but not episodes yet.

It will add a label like "tvdb-dvd" to make it easy to find which shows have non-plex-managed metadata from inside the Plex UI.

As I'm not certain how Plex will handle TVDB IDs in the future, the import data will match a series on the IMDB ID,
if it exists, and fallback to match on the TVDB ID otherwise. I don't believe Kometa has support TMDB IDs for television.

'ENDCOMMENT'

