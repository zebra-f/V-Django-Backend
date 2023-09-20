1. Users can still view `api/users/` endpoint
2. Validate `tags`, `nicknames` (add tests for nicknames)
3. Resend verification email
4. Change the `to_representation`` method of TagsField
5. Change paths in UserViewSet, replace _ with -
6. Check the response in SpeedFeedback, SpeedBoomark on create
7. Check SpeedFeedback `get_permissions` method
8. Pagination, check bookmark delete, check constraint error in feedback create
9. Add speed filtering (tag)
10. CORS
11. add index on username
12. remove speefeedback signal
13. Change email backed (admins, logger)