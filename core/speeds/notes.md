**Potentially essential:**  
queryset that allows to retrieve every field in the SpeedFeedback model  

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