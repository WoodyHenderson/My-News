# List of things to implement for even more the future.

## 1. Create a repository of providers, categories and searches

I want to allow users to have categories they can dynamically select/deselect at a certain point in order to allow them to have the maximum amount of control, we may be headed towards a kind of web-hosted service so it'd be nice to allow people to use it as a guest (dont want an account system) and simply select the categories and providers they want to see from and then hit go. Probably need to institute a minimum number of providers at once, although we should probably count distinct news organisations rather than individual feeds so that someone cannot select five BBC feeds and technically meet the minimum.
It'd be ideal to create preset weights as well, e.g. a user can select priorities like low/medium/high that have preselected multipliers for their individually generated config. This would be better than having separate keyword sets for every priority, since the category can have a base weight and the priority can just multiply it. Need to think about handling individual sessions, shouldn't be super hard as the user selections are fairly small and can probably be stored in a short-lived signed cookie at first.

How we might potentially do this is there's a top level folder at the same level as src for example config_catalog then it has a config_base.yaml that contains the basics that every generated config would contain, then two sub directories being news_aggregators/ and categories/. The news_aggregators directory would contain the reusable metadata and feed definitions for each individual news website, while categories would contain each individual category and the keywords related to that category. Some news aggregators have multiple feeds, so these should probably be treated as separate feeds under one provider rather than as completely separate providers. By separating this out it allows us to scale horizontally so we can just add more news aggregators by adding their own individual yaml file.

The user's selections should probably not create a new yaml file every time. Instead, we can load the catalog files, combine the selected providers, feeds, categories and priority into one runtime config in memory, validate that config, and then pass it through the existing fetch and ranking process. This also means the catalog is separate from the user's session and we do not have to maintain a large number of temporary config files. We may need to refactor the ranking process eventually so it can accept the validated config directly rather than reading it from a path, but that can happen when this becomes a web-hosted service.

## 2. Create a GUI that allows people to select from news providers

Can provide a brief description of the news websites, might do a ground news type deal where we talk about what way they typically lean but people will probably know that themselves, not really going to use any niche news providers for now anyways.

## 3. Look at hosting and session handling

Again like in pt1 since we said we don't want to do account handling will just do individual sessions, some cookie business. Look at web hosting so I can use it on my phone but that does mean making it mobile compatible sadge.