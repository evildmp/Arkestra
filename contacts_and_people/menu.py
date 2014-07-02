menu_dict = {
    "application": "contacts_and_people",
    "auto_page_attribute": "auto_contacts_page",
    "cms_plugin_model_name": None,
    "title_attribute": "contacts_page_menu_title",
    "url_attribute": "contact-entity",
    "sub_menus": ()
    }


class PersonTabs(object):
    # information for each kind of person tab

    tab_list = ["default"]

    def __init__(self, person, active_tab=None):
        self.tabs = []
        self.live_tabs = {}

        # each tab in tab_list represents a method we want to call
        for tab in self.tab_list:

            # call the method for that tab
            tab_dict = getattr(self, tab)(person)

            # the method will return a tab_dict if the person should have
            # the appropriate tab
            if tab_dict:
                # is this tab the active (i.e. currently selected) tab?
                if active_tab == tab_dict["address"]:

                    # mark it so we can highlight it in the template
                    tab_dict["active"] = True

                    # and set self.description based
                    self.description = tab_dict["meta_description_content"]

                # add this tab to the list of nodes in the tabbed menu
                self.tabs.append(tab_dict)

                # make the entire tab_dict available as a value in live_tabs
                # using the key 'address'
                self.live_tabs[tab_dict["address"]] = tab_dict

    def default(self, person):
        return {
            "tab": "contact",
            "title": "Contact information",
            "address": "",
            "meta_description_content": ""
        }
