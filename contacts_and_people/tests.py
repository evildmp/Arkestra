from datetime import datetime

from django.test import TestCase

from contacts_and_people.models import Site, Person, Building, Entity, Membership

class ContactsAndPeopleTests(TestCase):

    def test_person_memberships(self):
        cardiff = Site(
            site_name="Main site",
            post_town="Cardiff",
            country="UK",
            )
        cardiff.save()

        main_building = Building(
            name="Main Building",
            street="St Mary's Street",
            site=cardiff,
            )
        main_building.save()
        
        heart_testing_centre = Building(
            name="Heart Testing Centre",
            street="Queen Street",
            site=cardiff,
            )
        heart_testing_centre.save()        

        # create some entities in a hierarchy
        # School of Medicine
        #   Departments (an abstract entity)
        #       Department of Cardiology
        #           Section of Heart Research
        #           Department of Cardiology Student Centre
        #           Heart Testing Centre
        
        school = Entity(
            name="School of Medicine", 
            building=main_building,
            slug="medicine",
            )
        school.save()

        departments = Entity(
            name="departments", 
            parent=school,
            slug="departments",
            abstract_entity=True,
            )
        departments.save()

        department = Entity(
            name="Department of Cardiology", 
            parent=departments,
            slug="cardiology",
            )
        department.save() 
        
        section = Entity(
            name="Section of Heart Research", 
            parent=department,
            slug="heart-research",
            )
        section.save()         

        testing_centre = Entity(
            name="Testing Centre", 
            parent=department,
            slug="testing-centre",
            building_recapitulates_entity_name=True,
            building=heart_testing_centre,
            )
        testing_centre.save()         
        
        student_centre = Entity(
            name="Department of Cardiology Student Centre", 
            parent=department,
            slug="student-centre", 
            display_parent=False,
            )
        student_centre.save()

        web_editors = Entity(
            name="Group of web editors", 
            parent=school,
            slug="web-editors", 
            abstract_entity=True,
            )
        web_editors.save()
        
        # ---------- tests for Entity.get_building ----------
        
        # get_building works when building is assigned 
        self.assertEquals(school.get_building, main_building)
        # an abstract entity has no building *even if one is assigned*
        self.assertEquals(departments.get_building, None)
        # the section has no Building assigned so should inherit from its parent
        self.assertEquals(section.get_building, main_building)
        # the department has no Building assigned so should inherit from its parent
        self.assertEquals(department.get_building, main_building)

        # ---------- tests for Entity._get_institutional_address ----------

        # for section, should be a list of its ancestors excluding abstract entities
        self.assertEquals(section._get_institutional_address, [department, school])
        # for student_centre, should exclude department
        self.assertEquals(student_centre._get_institutional_address, [school,])
        
        
        # ---------- tests for Entity.get_full_address ----------

        # an entity with a building
        self.assertEquals(school.get_full_address, [u'Main Building', u"St Mary's Street", u'Cardiff '])
        # an abstract entity has no address
        self.assertEquals(departments.get_full_address, []) 
        # abstract entity is skipped in address
        self.assertEquals(department.get_full_address, [school, u'Main Building', u"St Mary's Street", u'Cardiff '])
        # an entity that doesn't display its parent in the address
        self.assertEquals(student_centre.get_full_address, [school, u'Main Building', u"St Mary's Street", u'Cardiff ']) 
        # an entity with building_recapitulates_entity_name flag shares 
        # its name with the building & drops the 1st line of postal address 
        self.assertEquals(testing_centre.get_full_address, [department, school, u"Queen Street", u'Cardiff ']) 
        

        # ---------- general person tests ----------

        smith = Person()
        smith.save()            
        
        # ---------- tests for Person methods: get_role, get_entity, get_building, get_full_address ----------

        # person with no memberships
        self.assertEquals(smith.get_role, None)
        self.assertEquals(smith.get_entity, None)
        self.assertEquals(smith.get_building, None)
        self.assertEquals(smith.get_full_address, [])
       
        # smith is a web editor and only has a membership of an abstract entity
        smith_web_editor_membership = Membership(
            person=smith,
            entity=web_editors,
            importance_to_person=5,
            importance_to_entity=4,
            role="Lead web editor",
            )
        smith_web_editor_membership.save()

        self.assertEquals(smith.get_role, None)
        self.assertEquals(smith.get_entity, None)
        self.assertEquals(smith.get_building, None)
        self.assertEquals(smith.get_full_address, [])

        # smith's best entity so far is technician in the department
        smith_department_membership = Membership(
            person=smith,
            entity=department,
            importance_to_person=2, # note that it's not as important his other one
            importance_to_entity=4,
            role="Technician",
            )
        smith_department_membership.save()

        self.assertEquals(smith.get_role, smith_department_membership)
        self.assertEquals(smith.get_entity, department)
        self.assertEquals(smith.get_building, main_building)
        self.assertEquals(smith.get_full_address, [school, u'Main Building', u"St Mary's Street", u'Cardiff '])                
                    
        # now we have a better entity: school 
        smith_school_membership = Membership(
            person=smith,
            entity=school,
            importance_to_person=5,
            importance_to_entity=5,
            role="Dean",
            )
        smith_school_membership.save()        

        self.assertEquals(smith.get_role, smith_school_membership)
        self.assertEquals(smith.get_entity, school)
        self.assertEquals(smith.get_building, main_building)
        self.assertEquals(smith.get_full_address, [u'Main Building', u"St Mary's Street", u'Cardiff '])        
        
        # now smith's best entity will be department
        smith_department_membership.importance_to_person = 5
        smith_department_membership.save()

        self.assertEquals(smith.get_role, smith_department_membership)
        self.assertEquals(smith.get_entity, department)
        self.assertEquals(smith.get_building, main_building)
        self.assertEquals(smith.get_full_address, [school, u'Main Building', u"St Mary's Street", u'Cardiff '])                
        # check that his membership of school has been downgraded by the save()
        self.assertEquals(Membership.objects.get(pk=smith_school_membership.pk).importance_to_person, 4) 