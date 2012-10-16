from django.test import TestCase

from contacts_and_people.models import Site, Person, Building, Entity, Membership

class EntityTestObjectsMixin(object):
    """
    Create a set of inter-related objects that we'll use in a series of tests
    """

    def setUp(self): 
        # a geographical Site
        self.cardiff = Site(
            site_name="Main site",
            post_town="Cardiff",
            country="UK",
            )
        self.cardiff.save()

        # a couple of Buildings on the Site
        self.main_building = Building(
            name="Main Building",
            street="St Mary's Street",
            site=self.cardiff,
            )
        self.main_building.save()
    
        self.heart_testing_centre = Building(
            name="Heart Testing Centre",
            street="Queen Street",
            site=self.cardiff,
            )
        self.heart_testing_centre.save()        

        # create some Entities in a hierarchy

        #   School of Medicine
        #       Departments (an abstract entity)
        #           Department of Cardiology
        #               Section of Heart Research
        #               Heart Testing Centre
        #               Department of Cardiology Student Centre
        #       Web editors (an abstract entity)
    
        self.school = Entity(
            name="School of Medicine", 
            building=self.main_building,
            slug="medicine",
            )
        self.school.save()

        self.departments = Entity(
            name="departments", 
            parent=self.school,
            slug="departments",
            abstract_entity=True,
            building=self.heart_testing_centre, # this should be ignored by everything!
            )
        self.departments.save()

        self.department = Entity(
            name="Department of Cardiology", 
            parent=self.departments,
            slug="cardiology",
            )
        self.department.save() 
    
        self.section = Entity(
            name="Section of Heart Research", 
            parent=self.department,
            slug="heart-research",
            )
        self.section.save()         

        self.testing_centre = Entity(
            name="Testing Centre", 
            parent=self.department,
            slug="testing-centre",
            building_recapitulates_entity_name=True,
            building=self.heart_testing_centre,
            )
        self.testing_centre.save()         
    
        self.student_centre = Entity(
            name="Department of Cardiology Student Centre", 
            parent=self.department,
            slug="student-centre", 
            display_parent=False,
            )
        self.student_centre.save()

        self.web_editors = Entity(
            name="Group of web editors", 
            parent=self.school,
            slug="web-editors", 
            abstract_entity=True,
            )
        self.web_editors.save()

        # set up a Person - we will add memberships later in the tests
        self.smith = Person()
        self.smith.save()            


class ModelTests(EntityTestObjectsMixin, TestCase):
    def test_entity_get_building(self):
        """
        test Entity.get_building
        check that Entities report the correct Building
        """
        
        # get_building works when building is assigned 
        self.assertEquals(self.school.get_building, self.main_building)
        # an abstract entity has no building *even if one is assigned*
        self.assertEquals(self.departments.get_building, None)
        # the section has no Building assigned so should inherit from its parent
        self.assertEquals(self.section.get_building, self.main_building)
        # the department has no Building assigned so should inherit from its real ancestor
        self.assertEquals(self.department.get_building, self.main_building)
        
    def test_entity_get_institutional_address(self):
        """
        test Entity.get_institutional_address
        check that Entities report the correct internal addresses
        """
        
        # for section, should be a list of its ancestors excluding abstract entities
        self.assertEquals(self.section._get_institutional_address, [self.department, self.school])
        # for student_centre, should exclude department
        self.assertEquals(self.student_centre._get_institutional_address, [self.school,])

    def test_entity_get_full_address(self):
        """
        test Entity.get_full_address
        check that Entities report the correct full addresses
        """
        
        # an entity with a building
        self.assertEquals(self.school.get_full_address, [u'Main Building', u"St Mary's Street", u'Cardiff'])
        # an abstract entity has no address
        self.assertEquals(self.departments.get_full_address, []) 
        # abstract entity is skipped in address
        self.assertEquals(self.department.get_full_address, [self.school, u'Main Building', u"St Mary's Street", u'Cardiff'])
        # an entity that doesn't display its parent in the address
        self.assertEquals(self.student_centre.get_full_address, [self.school, u'Main Building', u"St Mary's Street", u'Cardiff']) 
        # an entity with building_recapitulates_entity_name flag shares 
        # its name with the building & drops the 1st line of postal address 
        self.assertEquals(self.testing_centre.get_full_address, [self.department, self.school, u"Queen Street", u'Cardiff']) 

    def test_person_methods(self):
        """
        test Person methods: get_role, get_entity, get_building, get_full_address
        check that Person reports the correct information in different circumstances
        """
        
        # smith has no Memberships
        self.assertEquals(self.smith.get_role, None)
        self.assertEquals(self.smith.get_entity, None)
        self.assertEquals(self.smith.get_building, None)
        self.assertEquals(self.smith.get_full_address, [])
       
        # smith is a web editor and only has a membership of an abstract entity
        smith_web_editor_membership = Membership(
            person=self.smith,
            entity=self.web_editors,
            importance_to_person=5,
            importance_to_entity=4,
            role="Lead web editor",
            )
        smith_web_editor_membership.save()

        self.assertEquals(self.smith.get_role, None)
        self.assertEquals(self.smith.get_entity, None)
        self.assertEquals(self.smith.get_building, None)
        self.assertEquals(self.smith.get_full_address, [])

        # smith's best entity so far is technician in the department
        smith_department_membership = Membership(
            person=self.smith,
            entity=self.department,
            importance_to_person=2, # note that it's not as important his other one
            importance_to_entity=4,
            role="Technician",
            )
        smith_department_membership.save()

        self.assertEquals(self.smith.get_role, smith_department_membership)
        self.assertEquals(self.smith.get_entity, self.department)
        self.assertEquals(self.smith.get_building, self.main_building)
        self.assertEquals(self.smith.get_full_address, [self.school, u'Main Building', u"St Mary's Street", u'Cardiff'])                
                    
        # now smith has a better entity: school 
        smith_school_membership = Membership(
            person=self.smith,
            entity=self.school,
            importance_to_person=5,
            importance_to_entity=5,
            role="Dean",
            )
        smith_school_membership.save()        

        self.assertEquals(self.smith.get_role, smith_school_membership)
        self.assertEquals(self.smith.get_entity, self.school)
        self.assertEquals(self.smith.get_building, self.main_building)
        self.assertEquals(self.smith.get_full_address, [u'Main Building', u"St Mary's Street", u'Cardiff'])        
        
        # now smith's best entity will be department
        smith_department_membership.importance_to_person = 5
        smith_department_membership.save()

        self.assertEquals(self.smith.get_role, smith_department_membership)
        self.assertEquals(self.smith.get_entity, self.department)
        self.assertEquals(self.smith.get_building, self.main_building)
        self.assertEquals(self.smith.get_full_address, [self.school, u'Main Building', u"St Mary's Street", u'Cardiff'])                
        # check that his membership of school has been downgraded by the save()
        self.assertEquals(Membership.objects.get(pk=smith_school_membership.pk).importance_to_person, 4) 
