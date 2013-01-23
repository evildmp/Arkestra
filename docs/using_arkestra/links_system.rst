################
The links system
################

The links system is one of the most complex parts of Arkestra.

**************************
The ExternalLinks database
**************************

What happens when saving an ExternalLink in Admin
=================================================

ExternalLinkForm.clean() checks that the link is in order.

If the URL (which must be unique) already exists in the database, an error is raised; if the title already exists, a warning is raised (a duplicate title could be confusing but is not fatal).


`links.utils.get_or_create_external_link()`
-------------------------------------------

When an object that can have an External URL is saved, the ModelAdmin.clean() of that object must call `links.admin.get_or_create_external_link()`, passing it various items of information:

* self.cleaned_data.get("input_url", None), # a manually entered url
* self.cleaned_data.get("external_url", None), # a url chosen with autocomplete
* self.cleaned_data.get("title"), # link title
* self.cleaned_data.get("summary"), # link description

`links.admin.get_or_create_external_link()` checks that information against the database:

* is the URL scheme of input_url or external_url permitted by `links.utils.check_urls()`?
* has input_url been provided?
	* get_or_create an `ExternalLink` based on it