# Skrippl.py

A Skribbl.io clone in Python, using sockets and tkinter.

This is very much a work in progress, as everything is not working yet.
So far, (after you start the server script) you can do these things:

* Request a new random word from the server, which puts you in "paint mode"
* Paint. Only in black as of yet, but other clients will see what you paint. You can also clear the canvas.
* Guess what others are painting, and get recognized with "Username NAILED IT", but no points.
* Chat. If you start your message with "//", it will not be treated as a guess.
* Change username with SN//NewName
* (Cheat) - Seems to freeze the game now, not sure what's wrong. But before this, if you sent the chat message "//Ooooooh! I can see it now!", you got the right word and the addition "(cheater)" to your username.
