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

    tab_list = [
        "default",
        ]
    live_tabs = {}

    def __init__(self, person, active_tab=None):
        self.tabs = []
        for tab in self.tab_list:
            tab_dict = getattr(self, tab)(person)

            if tab_dict:
                if active_tab == tab_dict["address"]:
                    tab_dict["active"] = True
                    self.meta_dict = tab_dict["meta_description_content"]
                self.tabs.append(tab_dict)
                self.live_tabs[tab_dict["address"]] = tab_dict

    def default(self, person):
        return {
            "tab": "contact",
            "title": "Contact information",
            "address": "",
            "meta_description_content": ""
        }
