# kodistiller
Extract TVDB television series data for Kometa for import to Plex.

In December 2026, Plex is ending data access contracts with The TVDB for television series metadata. 
It isn't relevant why, but the impact is many series have incomplete or inaccurate data from other sources. 
This is my first attempt at a workaround to import data via the TVDB API into Plex by building yaml files for Kometa. 

I am no expert on Kometa or the TVDB, and I don't really want to support this code long term,
so I am offering it without any license or terms into the public domain, with sole hope that it helps 
those who will face a metadata crisis, or that someone is inspired to build a better tool.
No warranty is expressed or implied, as to usability or fitness.

Some customization of each file will be required to fit your environment.
Don't publicly share your API keys.

AI Disclosure, some AI generated code is included.
-

This should automate building a kometa metadata yaml file for each tv series from the TVDB API.
It requires an API key, which you should be able to get as in independent developer.

Requires a small addition to your Kometa config file:
TV Shows:
  metadata_files:
    - folder: config/metadata/folder_you_will_set_in_shell_script

In your library, add tags to each series folder to control it, {tvdb-:digits:} and OPTIONALLY {tvdborder-:alphas:}.
options are the API strings for relevant orders, EX:  "default" (Aired Order), "official", "dvd", "absolute", "alternate" (Streaming)
If you don't set an order tag, it uses "default", which works fine for many shows.

Example:  `/media/television/Firefly (2002) {tvdb-78874} {tvdborder-dvd}`

If you don't want to do folder naming, you can run manually as:
- python buildtvdbyaml.py 78874 dvd

Note, Kometa cannot change the order flag in Plex for the library or series, that's a manual step.

I tried to make the shell script POSIX and not require GNU extensions, YMMV.
Yes, I had AI help with a lot of the python, as I'd never interacted with TVDB API directly.
there is at least one package you'll need to install, see first line of that code.

It currently pulls series, season, and episode titles, summary, and first air date, ~~but NOT for season because it made the looping harder,~~*
series content rating, and episode thumbnails. No series and season thumbs because it returns an array of all available art.
This is probably an area where personal preference makes manually picking artwork preferred anyway, and a one time task.
*Adding: Figured out how to update the season titles and summary.

If you change the language variable in the python script, it will prefer localized series title and summary, but not episodes yet.

It will add a Plex label like "tvdb-dvd" to make it easy to find which shows have non-plex-managed metadata from inside the Plex UI.

As I'm not certain how Plex will handle TVDB IDs in the future, the import data will match a series on it's IMDB ID
if it exists, and fallback to match on the TVDB ID otherwise. I don't believe Kometa has support TMDB IDs for television.
