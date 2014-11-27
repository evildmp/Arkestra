from urlparse import urlparse
from urllib import urlopen

from django import forms
from django.contrib import messages

from links.models import ExternalLink, LinkType


def check_urls(url, allowed_schemes=None):
    """
    Checks and reports on a URL that might end up in the database.
    Returns a list of message dicts
    """
    message_list = []

    allowed_schemes = allowed_schemes or [kind.scheme for kind in LinkType.objects.all()]

    # parse the url and get some attributes
    purl = urlparse(url)
    scheme = purl.scheme

    # make sure it's a kind we allow before anything else
    if not scheme in allowed_schemes:
        permitted_schemes = (", ".join(allowed_schemes[:-1]) + " and " + allowed_schemes[-1]) if len(allowed_schemes) > 1 else allowed_schemes[0]
        if scheme:
            message = "Sorry, link type %s is not permitted. Permitted types are %s." % (scheme, permitted_schemes)
        else:
            message = 'Please provide a complete URL, such as "http://example.com/" or "mailto:example@example.com". Permitted schemes are %s.' % permitted_schemes

        raise forms.ValidationError(message)

    # for hypertext types only
    if str(scheme) == "http" or scheme == "https":
        # can we reach the domain?
        try:
            url_test = urlopen(url)
        except IOError:
            message = "Hostname " + purl.netloc + " not found. Please check that it is correct."
            raise forms.ValidationError(message)

        # check for a 404 (needs python 2.6)
        try:
            code = url_test.getcode()
        except AttributeError:
            message_list.append({
                "message": "Warning: I couldn't check your link %s. Please check that it works." % url,
                "level": messages.WARNING
                })
        else:
            if code == 404:
                message_list.append({
                    "message": "Warning: the link %s appears not to work. Please check that it is correct." % url,
                    "level": messages.WARNING
                    })

        # check for a redirect
        if url_test.geturl() != url:
            message_list.append({
                "message": "Warning: your URL " + url + " doesn't match the site's, which is: " + url_test.geturl(),
                "level": messages.WARNING
                })

    # for mailto types only
    elif str(scheme) == "mailto":
        message_list.append({
            "message": """
                Warning: this email address hasn't been checked. I hope it's correct.
                """,
            "level": messages.WARNING
            })

    return message_list


def get_or_create_external_link(
    request, input_url, external_url, title, description=""
    ):
    """
    When provided with candidate attributes for an ExternalLink object, will:
    * return the URL of an ExternalLink that matches
    * create an ExternalLink if there's no match, then return its URL
    """
    message_list = []

    if input_url or external_url:
        # run checks - doesn't return anything
        message_list.extend(
            check_urls(input_url or external_url.url, ["https", "http"])
            )

    if external_url:
        message_list.append({
            "message": "This is an external item: %s." % external_url.url,
            "level": messages.INFO
            })

        if input_url:
            message_list.append({
                "message": """
                    You can't have both External URL and Input URL fields, so I
                    have ignored your Input URL.
                    """,
                "level": messages.WARNING
                })

    elif input_url:
        if not title:
            ExternalLink.objects.get(url=input_url)

        # get or create the external_link based on the url
        external_url, created = ExternalLink.objects.get_or_create(
            url=input_url, defaults = {
                "url": input_url,
                "title": title,
                "description": description,
        })

        if created:
            message_list.append({
                "message": """
                    A link for this item has been added to the External Links
                    database: %s.
                    """
                % external_url.url,
                "level": messages.INFO
                })

        else:
            message_list.append({
                "message": "Using existing External Link: %s." \
                    % external_url.url,
                "level": messages.INFO
                })

    for message in message_list:
        messages.add_message(
            request,
            message["level"],
            message["message"]
            )

    return external_url
