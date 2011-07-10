from django.contrib import admin
from django import forms
from models import Category, SubCategory, Product

#first create a custom form to use in admin
class ProductAdminForm(forms.ModelForm):
    #The product model is defined with out the category, so add one in for display
    category = forms.ModelChoiceField(queryset=Category.objects.all().order_by('name'), widget=forms.Select(attrs={'id':'category'}), required=False)
    #This field is used exclusively for the javascript so that I can select the 
    #correct category when editing an existing product
    selected_cat = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Product

    class Media:
        #Alter these paths depending on where you put your media 
        js = (
            'js/mootools-1.2.3-core-yc.js',
            'js/products.js',
        )
    
    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['selected_cat'].initial = self.instance.subcategory.category.id

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    #I don't like using a fieldset here, because it makes the form more brittle,
    #if you change the model for form be sure to update the fieldset.
    #I'm using it in this instance because I need for category to show up 
    #right above the subcategory

admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    pass
    
class SubCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
