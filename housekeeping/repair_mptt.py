'''
Created on Sep 10, 2009

@author: stefanfoulis

/repair_mptt/cms.page/

'''
from cms.models import Page
import django.http as http
from django.db.models import get_model
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from cms.utils import get_cms_setting


def setup():
    from django.contrib.auth.models import User
    from cms.utils.permissions import set_current_user
    set_current_user(User.objects.get(id=1))
def check_no_moderator():
    print "  checking that CMS_MODERATOR is set to False"
    from django.conf import settings
    if get_cms_setting("MODERATOR"):
        print "!! Please set CMS_MODERATOR=False in settings before using this script !!"
        print 'aborted'
        raise Exception("!! Please set CMS_MODERATOR=False in settings before using this script !!")



def fix_tree_id(model):
    print "  rewriting tree_id..."
    #from django.db.models import Avg, Max, Min, Count
    #base_tree_id = Page.objects.filter(parent=None).aggregate(tree_id=Max('tree_id'))['tree_id'] + 1
    base_tree_id = 1
    for node in model.objects.filter(parent=None).order_by('tree_id'):
        node.tree_id = base_tree_id
        node.save()
        r_fix_tree_id(node.children.all(), base_tree_id)
        base_tree_id += 1
    return "I fixed some trees"

def r_fix_tree_id(nodes, tree_id):
    for node in nodes:
        node.tree_id = tree_id
        if node.__class__ == Page:
            node.save(no_signals=True)
        else:
            node.save()
        r_fix_tree_id(node.children.all(), tree_id)

def fix_leftright(model,do_alteration=True):
    setup()
    check_no_moderator()
    print "  fixing left and right..."
    def recur(node, counter):
        node.lft = counter
        counter += 1
        for child in node.children.all().order_by('tree_id', 'parent', 'lft'):
            counter = recur(child, counter)
        node.rght = counter
        counter += 1
        if node.__class__ == Page:
            node.save(no_signals=True)
        else:
            node.save()
        return counter
    for root_node in model.objects.filter(parent=None).order_by('tree_id', 'parent', 'lft'):
        counter = recur(root_node, 1)
        # sanity check
        total_nodes = model.objects.filter(tree_id=root_node.tree_id).count()
        if not total_nodes * 2 == counter-1:
            print "            something is wrong! %s != %s" % (total_nodes * 2, counter-1)
    return "did some leftright checking"

def fix_level(model):
    setup()
    print "  fixing level..."
    bad_level_count = 0
    level = 0
    all_nodes = model.objects.order_by('tree_id', 'parent', 'lft')
    for root_node in all_nodes.filter(parent=None):
        bad_level_count += r_fix_level(root_node, level=level)
    print "        fixed level of %s nodes" % bad_level_count
    return "I fixed level of %s nodes" % bad_level_count

def r_fix_level(node, level):
    bad_level_count = 0
    if not node.level == level:
        node.level = level
        if node.__class__ == Page:
            node.save(no_signals=True)
        else:
            node.save()
        bad_level_count += 1
    else:
        pass#print "    comparing level of page id:%s level:%s to level:%s: ok" % (page, page.level, level)
    for subnode in node.children.all():
        bad_level_count += r_fix_level(subnode, level+1)
    return bad_level_count


@login_required
def fix(request,slug):
    print "fixing mptt tree"
    model = get_model(*slug.split('.'))
    #print type(model)
    if model == Page:
        print "it's a page"
    #print model.objects.all()
        setup()
        check_no_moderator()
    tree_report = fix_tree_id(model)
    level_report = fix_level(model)
    leftright_report = fix_leftright(model)
    print "all done"
    #return http.HttpResponse("fixed")
    return shortcuts.render_to_response(
        "housekeeping/test.html",
        {"tree_report":tree_report,
        "level_report":level_report,
        "leftright_report":leftright_report,},
        RequestContext(request),
        )



def check_leftright():
    report = []
    report.append("Checking left/right")
    print "  checking left and right..."
    errors = {}
    def add_error(node, msg):
        if not node.id in errors.keys():
            errors[node.id] = [u"node: %s" % node]
        errors[node.id].append(msg)
    def recur(node, counter):
        if not node.lft == counter: add_error(node, u"lft is %s, should be %s." % (node.lft, counter))
        counter += 1
        for child in node.children.all().order_by('tree_id', 'parent', 'lft'):
            counter = recur(child, counter)
        if not node.rght == counter: add_error(node, u"rght is %s, should be %s." % (node.rght, counter))
        counter += 1
        return counter
    for root_page in Page.objects.filter(parent=None).order_by('tree_id', 'parent', 'lft'):
        counter = recur(root_page, 1)
        # sanity check
        total_pages = Page.objects.filter(tree_id=root_page.tree_id).count()
        if not total_pages * 2 == counter-1:
            print "            something is wrong! %s != %s" % (total_pages * 2, counter-1)
            report.append("something is wrong! %s != %s" % (total_pages * 2, counter-1))
    from pprint import pprint
    pprint(errors)
    return errors