from .models import SpeedFeedback, Vote


# handlers

def speed_post_save_handler(sender, instance, created, **kwargs):
    if created:
        speed_feedback = SpeedFeedback(
            vote=Vote.UPVOTE, 
            user=instance.user, 
            speed=instance
            )
        speed_feedback.save()