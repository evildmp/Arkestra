News and Events for Django CMS

<http://github.com/evildmp/Apps-for-Django-CMS/>

This application will manage and publish news articles and events for an institution.

It requires the Contacts and People application, <http://github.com/evildmp/Contacts-and-people/>.

A News item or Event can be can be attached to one or more Entities of an institution, by setting its Publishing destinations. This way the author of an item can control its distribution across a website.

For example, consider an institution with the following hierarchy of entities:

University of Rummidge
    Faculty of Humanities
        Department of English
        Department of Philosophy
        [...]
    [...]
    Academic Exchange Office
    [...]

A minor item in the Philosophy Department should be published at the level of the Philosophy department (on its home page or its news/events page, perhaps) but it shouldn't appear outside that. (No-one else is very interested in minor items in the Philosophy department.)

However, if the Department of English is involved in a high-profile academic exchange with Professor Morris Zapp from Euphoria State University, this should certainly go to the Department of English *and* the Academic Exchange Office, and if it's important enough, the Faculty of Humanities too.

A simple templatetag on the home page for each entity can display recent news headlines and event titles; a news/events page for each entity can hold an archive of news/events for that entity.

It is also possible to add metadata to items describing which pages, people and other items they are related to. Uses for this would include:

*   links on items directing readers to people mentioned or involved
*   links on news items referring to previous stories on the subject/related events
*   on a person's profile page, lists of news stories/events referring to them

There are many ways in which this application can (and needs to) be
developed. However it is ready to use and includes templates and
templatetags demonstrating some useful functionality.

Its output can be explored (when the server is up) by starting at:

<http://w128.medcn.uwcm.ac.uk:8001/news/item/nixon-resigns/>