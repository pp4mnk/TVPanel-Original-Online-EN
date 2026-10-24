# TVPanel-Original-Online-EN

TVPanel Original Online — English edition 1.4 — 96px icons

Original-style gtkdialog TV panel with an Internet channel catalogue.
Six columns and five rows, up to 30 channels per page. Channel buttons
show icons only, scaled to 96 x 96 pixels, with equal 104 x 104 button
areas. Names appear as tooltips when hovering. Existing logos
are copied from /root/noob/files/128 when available. Missing logos use a
plain television symbol with no letters.

INSTALL / UPDATE (EasyOS, root):
Extract the archive, open a terminal inside TVPanel-Original-Online-EN:
sh install.sh
Requirements: python3, yad, mpv, gtkdialog or gtkdialog3.
YouTube playback also requires a compatible yt-dlp installation.
The installer checks dependencies; it does not download them.

This updates the Spanish Online edition in place. Your saved channels
and catalogue cache are retained. No uninstall is necessary.
User-provided channel names and existing metadata are kept as saved.
YAD's built-in system controls may follow your desktop language.

Installed program: /usr/local/lib/tvpanel-online/
Command: /usr/local/bin/tvpanel-online
Menu: Multimedia > TVPanel
The installer updates noob128_front_end under /root/noob and keeps the
first original backup as noob128_front_end.before-online. Existing
shortcuts to that launcher use the updated version.
The older TVPanel Personal application is separate.

USE:
Click the + icon (Add channels). Search by name and/or country, or leave
both fields empty to show all. ES/Spain filters Spain; GB/UK/Scotland/
Edinburgh filters the United Kingdom, not a specific city or region.
Select a stream and click Watch to play it without saving it.
Add to panel creates a permanent button. Previous/Next switch pages.
Remove channel asks for confirmation before removing a saved button.

CATALOGUE:
https://github.com/iptv-org/api
https://iptv-org.github.io/api/
Combines channels.json, streams.json, logos.json and countries.json.
Only mapped HTTP/HTTPS streams are shown; closed channels and channels
marked as adult by the source are excluded. Multiple quality options may
exist for one channel. Availability and geographical restrictions vary.
The panel does not bypass DRM or subscriptions.

Downloaded catalogue data is cached for 24 hours. Refresh catalogue
requests new data. A previously saved cache is used if a download fails;
the first download requires Internet access. PNG/JPEG channel logos are
downloaded when possible when a channel is added.

DATA / TROUBLESHOOTING:
~/.config/tvpanel-original/channels.json (saved channels)
~/.config/tvpanel-original/channels.json.bak (previous list)
~/.cache/tvpanel-original/ (catalogue and logos)
~/.config/tvpanel-original/mpv.log (latest player log)
Screenshots: /files/media/images/TV_panel_screenshots (mpv key: s).
Save your EasyOS session if running without automatic persistence.

RESTORE ORIGINAL PANEL:
Close TVPanel. Use your file manager to copy the .before-online backup
over its matching noob128_front_end file. Keep the backup until tested.

CREDITS:
The supplied original panel credits Lobster, ETP and Barry Kauler.
This edition recreates its gtkdialog layout and adds a Python catalogue
manager. The online catalogue is supplied by IPTV-org.

VALIDATION:
English labels and installer syntax checked. Saved-channel compatibility
and generated gtkdialog structure checked. GUI playback has not been
retested on EasyOS in this environment.

MINI VERSION:
The window title must show TVPanel 1.4. All panel controls use icons
with hover tooltips. Logos use fixed 96px SVG canvases with aspect ratio
preserved. Words inside an original station logo remain part of its image;
no channel name labels or generated initials are added.
Close any previous panel before installing. To open this exact version:
/usr/local/bin/tvpanel-online
