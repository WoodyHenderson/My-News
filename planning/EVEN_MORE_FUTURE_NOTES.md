# List of things to implement for even more the future.

## 1. Create a repository of credentials and searches for news and categories

I want to allow users to have categories they can dynamically select/deselect at a certain point in order to allow them to have the maximum amount of control, we may be headed towards a kind of web-hosted service so it'd be nice to allow people to use it as a guest (dont want an account system) and simply select the categories and providers they want to see from and then hit go. Probably need to institute a minimum number of providers at once.
It'd be ideal to create preset weights as well, e.g. a user can create priorities like low/medium/high that they can select that have preselected weights for their individually generated config. Need to think about handling individual sessions, shouldn't be super hard as since we are storing the entire ranking process in memory.

## 2. Create a GUI that allows people to select from news providers

Can provide a brief description of the news websites, might do a ground news type deal where we talk about what way they typically lean but people will probably know that themselves, not really going to use any niche news providers for now anyways.

## 3. Look at hosting and session handling

Again like in pt1 since we said we don't want to do account handling will just do individual sessions, some cookie business. Look at web hosting so I can use it on my phone but that does mean making it mobile compatible sadge.