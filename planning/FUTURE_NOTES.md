# List of things to implement in the future:

## 1. Creating a head ✅

- Need to actually make a head to implement the features that I want in the future, setting stuff via commands initially is ok because there aren't that many but in the future when I need a bunch of interaction I'll need a head.
- Should allow users to validate config and run the app from the head as well and probably view the output within the head too.

## 2. Add seen articles to database ✅

- Instead of adding every single article into the database instead what im going to do is just create a simple method of storage (probably just a JSON) that stores urls to articles that the user has marked as seen, then at runtime we can check against this storage and remove articles.
- What this won't do is put every article from the digest from the previous days into this storage, this makes no sense as the likelihood of a user accessing all 30 articles from the digest from that day is basically 0, just give the user the option to mark off articles they don't want to reappear the next day because they've already read them

## 3. Built in HTML reading ✅

- Instead of generating a PDF in a file for users to access I think instead we will opt to generate html every time and then use a PyQT6 + QTWebEngineWidgets to embed a chromium instance into the head and then use that to view html generated outputs within the head of the app.

## 4. Expanding sources and use archive? 

- Need to expand to more sources and could perhaps use archive as a way to bypass paywalled content, need to look into how I could get from a website to archive to an rss feed? Seems relatively difficult but a possible stretch goal for fun.

## 5. Re-use PDF generation content ✅

- Since I got rid of PDF generation in favour of an HTML to chromium widget presentation, the PDF generator content is currently not in use, whilst I can just get rid of it it seems a waste so going to rework it just into a button beside the digest chooser that allows people to export it as a PDF. 
- Now that I think about it it might also be wise to include a widget beside the digest that allows people to change their output directory like they can in the CLI.