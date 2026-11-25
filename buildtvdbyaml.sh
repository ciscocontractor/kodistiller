#!/bin/sh

### Ver 2026-11-25

MEDIA_PATH='/media/television'
CONFIG_PATH='/usr/local/share/kometa/config/metadata/Television/'

cd "$CONFIG_PATH"


#had to rework passing arguments with xargs because the number is now variable as two or three.
find "$MEDIA_PATH" -type d -name '*{tvdb-*' | awk '{ \
  if (match($0, /tvdb-[[:digit:]]+/)) {  printf  "%s ", substr($0, RSTART + 5, RLENGTH - 5) } \
  if (match($0, /tvdborder-[[:alnum:] ]+/)) { print substr($0, RSTART + 10, RLENGTH - 10) } else { print "default" } \
}' | sort -u | tee serieslist.log | tr '\n' '\0' | xargs -0 -n 1 sh -c 'python buildtvdbyaml.py $1' _ | tee run.log



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

It currently pulls series, season and episode titles, summary, and first air date,
series content rating, and episode thumbnails. No series and season images because it returns an array of all available art.
This is probably an area where personal preference makes manually picking artwork preferred anyway.

If you change the language variable in the python script, it will prefer localized title and summary.

It will add a label like "tvdb-dvd" to make it easy to find which shows have non-plex-managed metadata from inside the Plex UI.

KNOWN ISSUE:

Applies metadata to all episodes of all editions or split series.
Ex: Pokemon (Aired in JP) and Pokemon (US Dub)

Even if both have different {tvdborder-XX} tags, it processes only one, applied to both.
Workaround (ver 2026-11-24 ++) requires using editions, sorry, I don't see any other way.

To apply ONLY to Pokemon series with an edition tag, you must also specify the API order plus the edition tag, example using directory name:
Pokemon (1997) {tvdb-76703} {tvdborder-regional Japanese} {edition-Japanese}

To apply ONLY to the default edition without a tag, use special keyword "none" as:
Pokemon (1997) {tvdb-76703} {tvdborder-official none}

To Apply to ALL editions, use only one or no ordering tag as before:
Pokemon (1997) {tvdb-76703} {tvdborder-official}
Pokemon (1997) {tvdb-76703}

Run from command line directly, it requires three arguments:
python buildtvdbyaml.py 76703 regional Japanese
python buildtvdbyaml.py 76703 official none

Otherwise with two or one command line arguments, it still applies to all editions or split versions:
python buildtvdbyaml.py 76703 official
python buildtvdbyaml.py 76703

'ENDCOMMENT'
