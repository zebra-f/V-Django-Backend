def handle_user_ban(sender, instance, **kwargs):
    user = instance
    if user.is_banned:
        pre_save_user = sender.objects.get(pk=user.pk)
        # user was just banned
        if not pre_save_user.is_banned:
            from core.speeds.tasks import delete_meilisearch_banned_user_data

            delete_meilisearch_banned_user_data.delay(user.pk)
