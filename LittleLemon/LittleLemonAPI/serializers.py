from rest_framework import serializers
from .models import MenuItem
from .models import Category
from decimal import Decimal
from rest_framework.validators import UniqueValidator
import bleach

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Category
        fields = ['id','slug','title']

class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    
    title = serializers.CharField(max_length=255,
                                  validators=[UniqueValidator(queryset=MenuItem.objects.all())])
    
    stock=serializers.IntegerField(source='inventory')
    price_after_tax = serializers.SerializerMethodField(method_name = 'calculate_tax')
    category=CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=2)
    
    def validate(self, attrs):
        
        attrs['title'] = bleach.clean(attrs['title'])
        if(attrs['price']<2):
            raise serializers.ValidationError('Price should not be less than 2.0')
        if(attrs['inventory']<0):
            raise serializers.ValidationError('Stock cannot be negative')
        return super().validate(attrs)
    
    def validate_title(self, value):
        return bleach.clean(value)
    
    class Meta:
        model=MenuItem
        fields = ['id','title','price','stock','price_after_tax','category','category_id']
        extra_kwargs = {
            'price': {'min_value': 2},
            'inventory':{'min_value':0},
            #'stock':{'source':'inventory', 'min_value': 0} -- other way of validation
        }

      
        
    def calculate_tax(self, product:MenuItem): 
        return product.price * Decimal(1.1)    