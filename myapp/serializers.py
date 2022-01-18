from myapp.models import Person
from myapp.models import PersonTest
from myapp.models import RecommendResult
from myapp.models import RecommendTest
from myapp.models import SimulationStyleList
from myapp.models import GanRequest
from myapp.models import UserData
from myapp.models import SconData

from myapp.models import ColdStart
from rest_framework import serializers
import json
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
import base64
import uuid
from drf_extra_fields.fields import Base64ImageField

class SconDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SconData
        fields = ('version', 'personalcolor_info', 'face_shape_info', 'face_ratio_info', 'recommend_hair_domain')
    def create(self, validate_data):
        return SconData.objects.create(**validate_data)

class SimulationStyleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationStyleList
        fields = ('no', 'user_num', 'recommend', 'possible_style_img', 'simulation_style_img')
class GanRequestSeializer(serializers.ModelSerializer):
    #gan_image_base64 = serializers.ImageField(required = False)
    user_image = Base64ImageField()
    class Meta:
        model = GanRequest
        fields = ('user_image', 'hair_color', 'hair_style', 'gan_image_base64')
class ColdStartSerializer(serializers.ModelSerializer):
    selected_image = serializers.CharField(required = False)
    class Meta:
        model = ColdStart
        fields = ('user_id', 'coldstart', 'selected_image')

class RecommendTestSerializer(serializers.ModelSerializer):
    face_info=serializers.JSONField(required = False)
    color_info=serializers.JSONField(required = False)
    recommend_result_hairList_json = serializers.JSONField(required = False)
    image_input = serializers.CharField()
    class Meta:
        model = RecommendTest
        fields = ('no', 'person', 'face_info', 'color_info', 'recommend_result_hairList_json', 'hair_texture', 'hair_volume', 'hair_condition', 'date', 'image_input')
    def create(self, validated_data):
        return RecommendTest.objects.create(**validated_data)

class RecommendResultSerializer(serializers.ModelSerializer):
    face_info=serializers.JSONField(required = False)
    color_info=serializers.JSONField(required = False)
    recommend_result_hairList_json = serializers.JSONField(required = False)
    image_input = serializers.CharField()
    class Meta:
        model = RecommendResult
        fields = ('no', 'person', 'face_info', 'color_info', 'recommend_result_hairList_json', 'hair_texture', 'hair_volume', 'hair_condition', 'date', 'image_input')
    def create(self, validated_data):
        return RecommendResult.objects.create(**validated_data)

class PersonTestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonTest
        fields = ('user_num', 'user_id', 'last_recommend', 'isexist')
    def create(self, validated_data):
        return PersonTest.objects.create(**validated_data)

class PersonSerializer(serializers.HyperlinkedModelSerializer):
    recommend_result=serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='recommendresult-detail', required=False) #, context={'request': request})
    isexist = serializers.BooleanField(required=False)
    class Meta:
        model = Person
        fields = ('user_num', 'user_id', 'recommend_result', 'last_recommend', 'isexist', 'isrecommended')
    def create(self, validated_data):
        return Person.objects.create(**validated_data)

class PersonDetailSerializer(serializers.ModelSerializer):
    recommend_result=RecommendResultSerializer(many=False, read_only=False)
    class Meta:
        model = Person
        fields = ('no', 'first_name', 'last_name', 'image_input', 'recommend_result')
    def update(self, instance, validate_data):
        instance.recommendStyleFirstImg_1=validate_data.get('recommendStyleFirstImg_1', instance.image_result)
        instance.save()
        return instance

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ('version', 'userid_json', 'nofuser')