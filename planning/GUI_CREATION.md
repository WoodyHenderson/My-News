# Creating a GUI with PyQt6

## 1. Create a barebones GUI

Create a GUI that has the buttons necessary and get the styling down first, we want View, Run and a drop down that allows us to search in the output folder for the .html files we have generated and once they are selected to spin up a chromium viewer to read them. We dont want to worry about the actual chromium implementation in this phase though we are just getting down the basic styling of the GUI

## 2. Create the Chromium HTML viewer

Once a user has selected an output from the dropdown they can hit a button that then spins up a chromium instance in the GUI using QtWebEngineTweaks and translates the html into a navigatble webpage.

## 3. Link up 

Lastly we want to link up our buttons to their respective commands in the rest of the app, luckily I actually made the codebase modular enough for this to be a fairly easy implementation with no (or little?) refactoring needed, so this shouldn't take long.