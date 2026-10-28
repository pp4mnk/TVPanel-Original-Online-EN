
[quote]**[b]TVPanel 1.9.4 EN — Improvements over 1.9.3[/b]**

Version 1.9.4 adds **M3U channel previews before adding them to the panel**.


- **[b]New Watch button[/b]:** load an M3U/M3U8 playlist, tick a channel and click **Watch** to play it with mpv without saving it.
- **[b]Keep browsing after previewing[/b]:** the playlist window reopens with your checked selections retained, allowing you to test more channels.
- **Choose what to save:[b]** use **Add selected** or **Add all**[/b] when ready. Watching alone does not change your saved channel list.
- **Preview existing channels:** channels already on your panel remain available for testing, while duplicate stream URLs are skipped when adding.

If several channels are checked, **[b]Watch plays the first checked channel in playlist order[/b]**.

[b]The + catalogue preview and selection features from 1.9.3 remain available[/b]. Installation is unchanged: extract the archive and run `sh install.sh`. Existing saved channels and logos are preserved.

[b]by pp4mnk[/b].[/quote]


-----------------------------------------------------------------------------------------------------------------------
#TVPANEL_M3U-1.9.3-EN.tar


A **TVPanel M3U 1.9.3 EN — Tested and working**

Good news! Version **1.9.3 EN** has now been tested and is working. You can add channels to the panel both through the **+ button** and by importing **M3U/M3U8 playlists**.

This release is **not a PET package**. It is a compressed archive containing the program and an installer.

**Installation on EasyOS**

1. Download the `TVPanel_M3U-1.9.3-EN.tar.gz` archive.
2. Move it to the `/root` folder in EasyOS.
3. Extract the archive.
4. Open the extracted folder and open a terminal there.
5. Run:

```bash
sh install.sh
```

6. Close any previous TVPanel window and reopen the program. The title should show **TVPanel 1.9.3 EN M3U**.

**What you can do**

- Use the **+ button** to search the online IPTV-org catalogue by channel name or country.
- Tick one or more channels and click **Add to panel**.
- Use **Watch** to test the first selected channel before adding it.
- Import channels from a local **M3U/M3U8 file** or a playlist URL.
- Select individual channels from a playlist or add all available new entries.
- Navigate between pages, remove channels and play streams using **mpv**.
- See the channel name beneath each button, even when no logo is available.

Your existing saved channels and downloaded logos are retained when updating.

**For the technically curious**

The issue in the previous release was in the catalogue selection window. When **Add to panel** was clicked, YAD was not returning the selected entries to the Python program, so it reported that no channel had been selected.

In version 1.9.3, the catalogue uses a YAD checklist with `--always-print-result`, allowing the selected channel IDs to be returned when the **Add to panel** button is used. The Python code then checks those IDs, skips streams already present in the panel and saves the new entries.

The channel list is stored in:

```text
~/.config/tvpanel-original/channels.json
```

A backup of the previous list is made when changes are saved. Downloaded PNG/JPEG logos are kept in the configuration folder, and generated icons and catalogue data are cached separately. Channel names remain visible if a logo is unavailable.

The installer checks for **Python 3, YAD, mpv and gtkdialog**, updates the launcher and creates a menu entry. YouTube streams may also require a working **yt-dlp** installation. As always, whether an individual stream plays depends on its source and any geographical or other restrictions.

The original TVPanel is ETP’s work; this version adds the online catalogue, M3U import and user-configurable channel selection. Modifications by **pp4mnk**.
