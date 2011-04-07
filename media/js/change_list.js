// some very small jquery extensions
(function($) {
	// very simple yellow fade plugin..
	$.fn.yft = function(){ this.effect("highlight", {}, 1000); }
	
	// jquery replace plugin :)
	$.fn.replace = function(o) { 
		return this.after(o).remove().end(); 
	};
})(jQuery);

var tree;
function initTree(){
	tree = new tree_component();
	var options = {
		rules: {
			clickable: "all",
			renameable: "none",
			deletable: "all",
			creatable: "all",
			draggable: "all",
			dragrules: "all",
			droppable: "all",
			metadata : "mdata",
			use_inline: true,
			//droppable : ["tree_drop"]
		},
		path: false,
		ui: {
			dots: true,
			rtl: false,
			animation: 0,
			hover_mode: true,
			theme_path: false,
			theme_name: "default",
			a_class: "title"
		},
		cookies : {},
		callback: {
			beforemove  : function(what, where, position, tree) {
				//console.log("before move")
				item_id = what.id.split("page_")[1];
				target_id = where.id.split("page_")[1];
				old_node = what
				if($(what).parent().children("li").length > 1){
					//console.log("has siblings")
					if($(what).next("li").length){
						old_target = $(what).next("li")[0];
						old_position = "right"
						//console.log("has sibling after")
						//console.log($(what).next("li"))
					}
					if($(what).prev("li").length){
						old_target = $(what).prev("li")[0];
						old_position = "left"
						//console.log("has sibling befor")
						//console.log($(what).prev("li"))
					}
				}else{
					//console.log("no siblings")
					if($(what).attr("rel") != "topnode"){
						//console.log("has parent")
						//console.log($(what).parent().parent())
						old_target = $(what).parent().parent()[0];
						old_position = "inside"
					}else{
						0/0;
					}
				}
				
				addUndo(what, where, position)
				return true 
			},
			onmove: function(what, where, position, tree){
				item_id = what.id.split("page_")[1];
				target_id = where.id.split("page_")[1];
				if (position == "before") {
					position = "left"
				}else if (position == "after") {
					position = "right"
				}else if(position == "inside"){
					position = "first-child"
				}
				moveTreeItem(item_id, target_id, position, false)
			},
			onchange: function(node, tree){
				var url = $(node).find('a.title').attr("href")
				self.location = url;
			}
		}
	};
	
	
	if (!$($("div.tree").get(0)).hasClass('root_allow_children')){
		// disalow possibility for adding subnodes to main tree, user doesn't
		// have permissions for this
		options.rules.dragrules = ["node inside topnode", "topnode inside topnode", "node * node"];
	}
	
	//dragrules : [ "folder * folder", "folder inside root", "tree-drop * folder" ],
        
	tree.init($("div.tree"), options);
};

$(document).ready(function() { 
    var selected_page = false;
    var action = false;
	
	var _oldAjax = $.ajax;
	
	$.ajax = function(s){
		// just override ajax function, so the loader message gets displayed 
		// always
		$('#loader-message').show();
		
		callback = s.success || false;
		s.success = function(data, status){
			if (callback) {
				callback(data, status);
			}
			$('#loader-message').hide();
			syncCols();
		}	
		
		// just for debuging!! 
		s.complete = function(xhr, status) {
			if (status == "error" && settings.debug) {
				$('body').before(xhr.responseText);
			}
		}
		// end just for debuging
		
		// TODO: add error state!
		return _oldAjax(s);
	}
	
	
	/**
	 * Reloads tree item (one line). If some filtering is found, adds 
	 * filtered variable into posted data. 
	 * 
	 * @param {HTMLElement} el Any child element of tree item
	 * @param {String} url Requested url
	 * @param {Object} data Optional posted data
	 * @param {Function} callback Optional calback function
	 */
	function reloadItem(el, url, data, callback) {
		if (data === undefined) data = {};
	
		if (/\/\?/ig.test(window.location.href)) {
			// probably some filter here, tell backend, we need a filtered
			// version of item	
			
			data['filtered'] = 1;
		}
		$.post(url, data, function(response){
			if (callback) callback(response);
			var target = $(el).parents('div.cont:first');
			var parent = target.parent();
			if (response == "NotFound") {
				return parent.remove();
			}
			target.replace(response);
			parent.find('div.cont:first').yft();
		});
	}
	
	function refresh(){
		window.location = window.location.href;
	}
	
	function refreshIfChildren(pageId){
		return $('#page_' + pageId).find('li[id^=page_]').length ? refresh : function(){};
	}
	// let's start event delegation
	
    $('#changelist li').click(function(e) {
        // I want a link to check the class
        if(e.target.tagName == 'IMG' || e.target.tagName == 'SPAN')
            var target = e.target.parentNode;
        else
            var target = e.target;
        var jtarget = $(target);
        
        if(jtarget.hasClass("move")) {
			var id = e.target.id.split("move-link-")[1];
			if(id==null){
				id = e.target.parentNode.id.split("move-link-")[1];
			}
            var page_id = id
            selected_page = page_id;
            action = "move";
			$('span.move-target-container, span.line, a.move-target').show();
            $('#page_'+page_id).addClass("selected")
			$('#page_'+page_id+' span.move-target-container').hide();
			e.stopPropagation();
            return false;
        }
       
        
        if (jtarget.hasClass("addlink")) {
			if (!/#$/g.test(jtarget.attr('href'))) {
				// if there is url instead of # inside href, follow this url
				// used if user haves add_page 
				return true;
			}
			
			$("tr").removeClass("target");
			$("#changelist table").removeClass("table-selected");
			var page_id = target.id.split("add-link-")[1];
			selected_page = page_id;
			action = "add";
			$('tr').removeClass("selected");
			$('#page-row-' + page_id).addClass("selected");
			$('.move-target-container').hide();
			$('a.move-target, span.line, #move-target-' + page_id).show();
			e.stopPropagation();
			return false;
		}
		
        if(jtarget.hasClass("move-target")) {
            if(jtarget.hasClass("left"))
                var position = "left";
            if(jtarget.hasClass("right"))
                var position = "right";
            if(jtarget.hasClass("first-child"))
                var position = "first-child";
            var target_id = target.parentNode.id.split("move-target-")[1];
            if(action=="move") {
				moveTreeItem(selected_page, target_id, position, tree);
                $('.move-target-container').hide();
            }else if(action=="add") {
                window.location.href = window.location.href.split("?")[0].split("#")[0] + 'add/?target='+target_id+"&position="+position+'&parent='+target_id;
            }else{
            	console.log("no action defined!")
            }
			e.stopPropagation();
            return false;
        }
        return true;
    });
	/* Colums width sync */
	$.fn.syncWidth = function(max) {
		$(this).each(function() {
			var val= $(this).width();
			if(val > max){max = val;}	
		});
 		$(this).each(function() {
  			$(this).css("width",max + 'px');
		});
		return this;
	};
	$("div#sitemap").show()
	
	function syncCols(){
		$('#sitemap ul .col-actions').syncWidth(0);
	} 
	
	syncCols();
});
function insert_into_url(url, name, value){
	if(url.substr(url.length-1, url.length)== "&"){
		url = url.substr(0, url.length-1)
	}
	dash_splits = url.split("#")
	url = dash_splits[0]
	var splits = url.split(name + "=");
	var get_args = false;
	if(url.split("?").length>1){
		get_args = true;
	}
	if(splits.length > 1){
		var after = ""
		if (splits[1].split("&").length > 1){
			after = splits[1].split("&")[1];
		}
		url = splits[0] + name + "=" + value + "&" + after;
	}else{
		if(get_args){
			url = url + "&" + name + "=" + value;
		}else{
			url = url + "?" + name + "=" + value;
		}
	}
	if(dash_splits.length>1){
		url += dash_splits[1]
	}
	if(url.substr(url.length-1, url.length)== "&"){
		url = url.substr(0, url.length-1)
	}
	return url
}

function remove_from_url(url, name){
	var splits = url.split(name + "=");
	if(splits.length > 1){
		var after = ""
		if (splits[1].split("&").length > 1){
			after = splits[1].split("&")[1];
		}
		if (splits[0].substr(splits[0].length-2, splits[0]-length-1)=="?"){
			url = splits[0] + after;
		}else{
			url = splits[0] + "&" + after;
		}
	}
	return url;
}


function moveTreeItem(item_id, target_id, position, tree){
	$.post("./"+item_id+"/move-page/", {
            position:position,
            target:target_id
        },
        function(html) {
			if(html=="ok"){
				if (tree) {
					var tree_pos = false;
					if (position == "left") {
						tree_pos = "before"
					}else if (position == "right") {
						tree_pos = "after"
					}else {
						tree_pos = "inside"
					}
					tree.moved("#page_" + item_id, $("#page_" + target_id + " a.title")[0], tree_pos, false, false)
				}else{
					moveSuccess($('#page_'+item_id + " div.col1:eq(0)"))
				}
			}else{
				moveError($('#page_'+item_id + " div.col1:eq(0)"))   
			}
        }
    );
};

var undos = []
function addUndo(node, target, position){
	//console.log("add undo")
	undos.push({node:node, target:target, position:position})
	//console.log(undos)
}