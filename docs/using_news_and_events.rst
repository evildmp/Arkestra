###################
Using news & events
###################

******
Events
******

The hierarchy of events
=======================

Events in Arkestra are maintained in a hierarchy, because that's what they are in real life. The stages of each year's Tour de France are the `children` of that year's race:

* Tour de France 1969
	* Stage 1
	* Stage 2
	* Stage 3
	* Stage 4
	* [... and so on]
* Tour de France 1970
	* Stage 1
	* Stage 2
	* Stage 3
	* Stage 4
	* [... and so on]

If we wanted, we could identify different events within each stage too - the Départ Fictif, the Départ Réel, the award ceremony - and Arkestra would happily deal with that too.

(Another typical example of a hierarchy would be the sessions in a conference.)

Actual events and series of events
==================================

This year's Tour de France is an `actual` event, as was last year's and as will be next's. It starts and ends.

But the Tour de France itself is a `series` of `actual` events. The `series` is the `parent` of each annual event. 

* Tour de France
	* Tour de France 1969
		* Stage 1
		* Stage 2
		* Stage 3
		* Stage 4
		* [... and so on]
	* Tour de France 1970
		* [...]
	* Tour de France 1971
		* [...]
	* Tour de France 1972
		* [...]

We can't store a start or end date for the `series`, but there are still lots of other useful items of information that we might want to record about the series as a whole, or that apply to the `actual` events that are its children.

So Arkestra can record an event as being a `series`. Any event that doesn't have at least a start date is assumed to be a series (what else could it be?).

What gets shown in Events lists?
================================

In a list of events, such as on a News & Events page, which items will be listed?

* actual events (not series events) that do not have an actual event parent

So, Tour de France 1969 will show up in the list, but not all its children. If someone wants to see details of all the children, they can visit the Tour de France 1969 page.

Similarly, we would want to show a conference, but not all of its sessions.

Each item in the list has this basic structure:

[title of series, link to series]
[title of event, link to event]
[summary of event]
[date]
[venue]

or:

Public Health lecture series [links to the page for the series]
"The health benefits & risks of milk" [links to the page for this particular item]
A debate between two leading researchers
12th January, 19:00
UHW Main Building

We don't always need to show all of these. [title of series, link to series] can't be shown if the item isn't part of a series, for example.

For our Tour de France example, this would look silly though:

Tour de France [links to the page for the series]
Tour de France 1969 [links to the page for this particular item]
The 1969 edition of the Tour opens with [...]
June 28th to July 20th, 1969

don't link to children [children contain little extra information]

For events in this series:
* series name, child name, child summary
* series name, child summary
* series name, series summary
* child name


So, for the series we could choose the option:
