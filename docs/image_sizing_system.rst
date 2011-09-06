#######################
The image sizing system
#######################

***********
The problem
***********

Suppose we have a page with two columns, and an image, 500px wide, in the second column, which happens to be 500px wide itself:

 ________________________________________
|					   ________________  |
| this first column   |				   | |
| 				      |	 an image	   | |
| contains text and   |   500 px wide  | |  
| 		              |	 --------	   | |
| whatever else one   |________________| |
|				 					     |
| might want it to    the second column  |
|					  contains text as   |
| contain		 	  well as an image   |	
|________________________________________|

At the moment, that 500px width is correct for that image, but any one of a number of things could change that, for example:

* if the editor decides the layout should no longer be two columns but three
* ... or that the text column should be twice the width of the image columns
* if the editor applies a border to the image
* the designer decides that the site template should be 200px wider
* the designer applies CSS to the site placing borders on all images

Any of these will mean that the 500px wide image will no longer fit neatly into its column.

One solution is for the editor to work out the new correct size for the image and set it accordingly. Of course, if this is in the process of working out a new page layout it could be a rather tedious; it could be more tedious still if it's the result of a site-wide change, when there could be hundreds or thousands of images to correct.

The other solution is for Arkestra to do it all automatically, which it does.

************
The solution 
************

Arkestra can know about site templates, and use this information to work out the correct size of any image.

For example, suppose the body content area of in our example above is 960 pixels wide. Arkestra will know what the exact width of the image should be to fill it. 

Using the default CSS and values:

* to occupy that second column, it will be be 48% of 960
* for a three-column layout, or if the text column should be twice the width: 30.6667%
* if it has a border class applied: reduce the width by 16 pixels.

These are just the simplest examples. If your image has been told to 

* float right 
* have a border
* and occupy 50% of a column
* which itself has a background tint
* and is two-fifths of the second column in a two-column layout
* and the page has a menu down the side that makes the content area narrower

Arkestra will take account of all that to work out the size of the image to the nearest pixel. Every time any of those things changes, when the page is rendered, the image will appear at exactly the right size.

Arkestra comes with sensible defaults for columns and borders, but they are easy to override if you want your own templates to have different values.

************
How it works
************

The image plugin (or video, or carousel, or whatever - referred to here as 'image', just to make life easier) is told what width to be. 

If it's an absolute width or the native width of the image, then that's settled. But if it's one a width relative to the containing column, then Arkestra will need to make the calculation:

Calculate the width of the placeholder
======================================

The `get_placeholder_width` function is called by the rendering plugin, such as `arkestra_image_plugin.cms_plugins.FilerImagePlugin`.

This obtains the default `placeholder_width` value from the context.

(`placeholder_width` can be set in settings, or if your site uses different templates with different widths, then with {% with placeholder_width=<some_value> %} around the placeholder in the template.)

`get_placeholder_width` then calls each registered `placeholder_width` adjuster. There is one included by default: `SimplePlaceholderWidthAdjuster`.

`SimplePlaceholderWidthAdjuster`
--------------------------------

This examines the context for your clues on how placeholder widths should be adjusted. 

Suppose that if the page has a menu down the side, then the placeholder width should be different - 749px, say. So it might look like:

`{% with adjust_width=current_page.flags.local_menu width_adjuster="absolute" width_adjustment=749 %}`

This means: 

* adjust the width if current_page.flags.local_menu is found
* we want to use an absolute width
* which will be 749px 

`SimplePlaceholderWidthAdjuster` inspects the context for an `adjust_width` variable. If found, it will also look for `adjuster` and `adjustment`.

Possible `adjuster` values:

* divider (divide the `placeholder_width` by `adjustment`)
* multiplier (multiply it)
* percent (the calculated value will be `adjustment` percent of `placeholder_width`)
* relative (add `adjustment` percent to `placeholder_width`)
* absolute (set the new value to `adjustment`)

Obviously it's up to you and your HTML/CSS how all these things work...

Anyway, now Arkestra knows how wide the placeholder is.

Calculate image container width
===============================

The next thing `arkestra_image_plugin.cms_plugins.FilerImagePlugin` does is call `calculate_container_width`.

Now we need to find out where our image plugin finds itself. It might be directly placed in the placeholder, or it might be within a text plugin within the placeholder, or in a deeper structure still.

`calculate_container_width` gets the ancestry of the image plugin. 

Then, starting at the rootmost plugin, it will run each registered `plugin_width` adjuster.

There is one included by default: `KeyReducer`.

`AutoSpaceFloat`
----------------

AutoSpaceFloat uses a truth table to determine how to adjust the width of the container, depending upon whether not the width is set to automatic, whether the space-on-left or space-on-right classes have been used, and whether the image is floated.

Next it will examine the HTML of the plugin (using `BeautifulSoup`), and find where the next plugin is in the HTML structure. It will then examine the HTML structure of nested elements, from the root upwards.

For each element, it will run the `image_width` adjusters.

`ReduceForBackground`
---------------------

The second allows for backgrounds - if elements with background tints also have padding, which they usually do, we need to allow for that.

The effect of this padding is cumulative - if three nested elements all have padding, then the reduction for the padding will need to be applied for each one.

`ReduceForBackground` by default tests for `tint` or `outline` in the element class, and applies a 16px width reduction.

This can be overridden in the template by using {% with %}:

* background_classes="some-class some-other-class" (space-separated values)
* background_reduction=16

`ColumnWidths`
--------------

The second of these calculates the column width.

`ImageBorders`
--------------

The final kind of adjuster is the `mark_and_modify` adjusters, which run two functions, one to mark the elements that need acting on, and one to act on them afterwards.

These inspect every element, but don't modify the width for every one - they only act once per plugin.

For example, even if several elements in the image plugin's ancestry have a border class on them, the image can only have one border.

`ImageBorders` by default tests for `image-borders` and `no-image-borders` in the element classes.

These tests add a key - `markers["has_borders"]` to the dictionary that looks after this.

Finally, after all the rest is done, `calculate_container_width` will run the `modify` functions of these adjusters.

The defaults can be overridden in the template by using {% with %}:

* image_border_class="some-class"
* no_image_border_class="some-other-class"
* image_border_reduction=16
