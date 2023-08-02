from .models import SpeedFeedback, SpeedFeedbackCounter, Vote


# handlers

def speed_post_save_hander(sender, instance, created, **kwargs):
    if created:
        speed_feedback = SpeedFeedback(
            vote=Vote.UPVOTE, 
            user=instance.author, 
            speed=instance
            )
        speed_feedback.save()
        
        speed_feedback_counter = SpeedFeedbackCounter(
            speed=instance, 
            upvotes=1
            )
        speed_feedback_counter.save()