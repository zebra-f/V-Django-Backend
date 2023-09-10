**Potentially essential:**  
a queryset that allows to retrieve every field in the related SpeedFeedback model  

```
qs = Speed.objects.filter(
        Q(is_public=True) | Q(user=self.request.user)
    ).prefetch_related(
        'feedback_counter'
    ).prefetch_related(Prefetch('speedfeedback_set', queryset=SpeedFeedback.objects.filter(
            user=self.request.user
        ), to_attr='speed_feedback')
    )
```

a queryset that allows to retrieve additional fields `vote` and `category` with a subquery from related models (SpeedFeedback, SpeedBookmark)
```
    # query
    @staticmethod
    def get_authenticated_user_query(user: User):
        return Speed.objects.filter(
                Q(is_public=True) | Q(user=user)
            ).prefetch_related(
                'feedback_counter'
            ).annotate(
                user_speed_feedback_vote=Subquery(
                    SpeedFeedback.objects.filter(
                        speed=OuterRef('pk'), user=user).values('vote')
                    ),
                user_speed_bookmark=Subquery(
                    SpeedBookmark.objects.filter(
                        speed=OuterRef('pk'), user=user).values('category')
                    ),
            )

class SpeedSerializer(BaseSpeedSerializer):
    ''' SpeedSerialzier for authenticated users '''
    # user_speed_feedback directions:
    #  1 upvote 
    #  0 default, 
    # -1 downvote, 
    # -2 no data for authenticated user,
    # -3 an anonymous user
    # -4 a response for the update/post method default, nested related object in serializers with speed=SpeedSerializer() field
    user_speed_feedback_vote = serializers.SerializerMethodField()
    user_speed_bookmark = serializers.SerializerMethodField()
    test = serializers.SerializerMethodField()

    class Meta(BaseSpeedSerializer.Meta):
        fields = [
            *BaseSpeedSerializer.Meta.fields, 
            'user_speed_feedback_vote',
            'user_speed_bookmark',
            ]
        read_only_fields = [*BaseSpeedSerializer.Meta.read_only_fields, 'user_speed_feedback_vote', 'user_speed_bookmark']

    def get_user_speed_feedback_vote(self, obj) -> int:
        try:
            # obj.user_speed_feebdack might be equal to 0
            # in this context user might be anonymous (-3)
            if obj.user_speed_feedback_vote in (1, 0, -1, -3,):
                return obj.user_speed_feedback_vote
            return -2
        except:
            return -4
    
    def get_user_speed_bookmark(self, obj) -> Union[None, str]:
        try:
            if obj.user_speed_bookmark:
                return obj.user_speed_bookmark
            # obj.user_speed_feedback == False
            return None
        except:
            return None
        
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        # set by a signal on create
        instance.user_speed_feedback_vote = 1
        instance.user_speed_bookmark = None
        return instance
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.user_speed_feedback_vote = -4
        instance.user_speed_bookmark = None
        return instance
```

partial update wihout id

```
    @action(methods=['patch'], detail=False, url_path='frontend-partial-update')
    def frontend_partial_update(self, request):
        ''' used by a frontend client, with no access to a SpeedFeedback primary key '''
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            speed_feedback = get_object_or_404(
                SpeedFeedback,
                speed=serializer.data['speed'], 
                user=self.request.user
                )
            speed_feedback.vote = serializer.data['vote']
            speed_feedback.save(update_fields=['vote'])
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

class SpeedFeedbackFrontendSerializer(serializers.ModelSerializer):
    ''' Utilized by methods in views.py tailored for frontend requests that do not include a Vote pk. '''

    class Meta:
        model = SpeedFeedback
        fields = ['vote', 'speed']
```

