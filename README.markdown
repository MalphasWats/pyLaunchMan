#Python Launchpad Manager - pyLaunchMan

I wrote a *very* simple application that enables you to manage your OS X Launchpad.

With pyLaunchMan you can:

- Delete individual apps
- Delete folders
- Rename apps (Adobe Creative Site Photoshop 5.5 Ultimate Super Edition anyone?)

These changes only affect icons in Launchpad, icons in your Applications folder stay where they are, named what they are.

Things you can't do (yet):

- Add apps - I can't work out how OS X generates the `bookmark` field in the `apps` table.
- Move apps around or into and out of folders - you're *much* better off doing this by dragging and dropping them

I'd really like to be able to do the first one - I thought about keeping a separate database that stores all of the apps and use that to restore back into the Launchpad database, but I'd much rather work out how to generate them myself. **Fork it** if you work it out!

##Licensing

You may use pyLaunchMan with the following conditions:

- I am not responsible for killing your Launchpad database. If it all goes wrong, navigate to `~/Library/Application Support/Dock` and delete the `.db` file in there, then type `killall Dock` at the command prompt, OS X will regenerate a new database for you.
- No laughing at my awful try/except/finally blocks, I really haven't got the hang of these yet.
- Ditto all the `global` declarations, I can't think of a way to store application state without them!

##Dependencies

Other than only working on Mac OS X 10.7.x (duh!), everything else should be standard library. I wanted to learn `curses` which is why it's written using that, terminal apps are cute.

##Bugs

There are probably some in there, tell me and I'll try and fix them.