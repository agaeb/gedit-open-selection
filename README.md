gedit-open-selection
====================

Open Selection plugin for gedit.

Opens the currently selected path in a new tab.
Considers the currently selected text to be the name of a (local) file
which is opened in a new tab by pressing Ctrl-Shift-O or the corresponding
menu entry. Globs like * are expanded, possibly to multiple files in
multiple new tabs. Tilde (~) is expanded as well.

Tested with gedit 3.4 on Ubuntu 12.04 and gedit 3.10 on Ubuntu 14.04.
To use with gedit 3.10 change Loader=python to Loader=python3 in openselection.plugin.



