from rest_framework import viewsets, response, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer

from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from .models import Speed, SpeedFeedback, SpeedBookmark, SpeedReport
from .permissions import (
    UserIsAuthorized,
    SpeedFeedbackPermissions,
    SpeedBookmarkPermissions,
)
from .serializers import (
    SpeedBaseHyperlinkedSerializer,
    SpeedHyperlinkedSerializer,
    SpeedFeedbackSerializer,
    SpeedBookmarkSerializer,
    SpeedReportSerializer,
)
from core.common.renderers import CustomBrowsableAPIRenderer
from .queries import SpeedQueries, SpeedFeedbackQueries, SpeedBookmarkQueries
from .filters import SpeedFilter, SpeedFeedbackFilter, SpeedBookmarkFilter
from .services import get_random_speeds


class SpeedViewSet(viewsets.ModelViewSet):
    # ModelViewSet (6) attributes
    renderer_classes = [CustomBrowsableAPIRenderer, JSONRenderer] if settings.DEBUG else [JSONRenderer]

    queryset = Speed.objects.filter(is_public=True)
    serializer_class = SpeedHyperlinkedSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = SpeedFilter

    # custom attribute
    not_allowed_http_method_names = []
    # ModelViewSet attribute
    http_method_names = []
    for method_name in viewsets.ModelViewSet.http_method_names:
        if method_name not in not_allowed_http_method_names:
            http_method_names.append(method_name)

    # custom attribute
    object_level_actions = [
        "destroy",
        "update",
        "partial_update",
    ]
    # custom attribute
    forbidden_object_level_actions = []

    def get_permissions(self):
        if self.action in (
            "list",
            "retrieve",
        ):
            self.permission_classes = [AllowAny]
        if self.action in self.object_level_actions or self.action in (
            "personal_list",
            "create",
        ):
            self.permission_classes = [UserIsAuthorized]

        return super().get_permissions()

    def get_queryset(self):
        if (
            self.action in ("personal_list",)
            and not self.request.user.is_anonymous
        ):
            return SpeedQueries.get_authenticated_user_query(
                self.request.user, "personal"
            )

        if self.request.user.is_anonymous:
            return SpeedQueries.get_anonymous_user_query()
        # an user
        elif not self.request.user.is_admin:
            return SpeedQueries.get_authenticated_user_query(
                self.request.user, "public_and_personal"
            )
        # an admin
        else:
            return SpeedQueries.get_admin_query(self.request.user)

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return SpeedBaseHyperlinkedSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """
        This method handles `DELETE` requests for a resource, but instead of
        deleting data, it changes the user to `deleted` and public
        status to `False` of the resource.

        The actual deletion of the resource will be handled by a Celery periodic
        task at a later time.
        """
        serializer = self.get_serializer(instance, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        # invokes `to_represent` method resposible for syncing data
        serializer.data

    @action(methods=["get"], detail=False, url_path="personal-list")
    def personal_list(self, request, *args, **kwargs):
        """
        In this context, 'personal list' refers to all the `Speed` data, including both
        public and private entries, that have been added exclusively by the authenticated user.
        A queryset for this action is defined in the `get_queryset` method.
        A permission for this action is defined in the `get_permissions`.
        """
        return self.list(request, *args, **kwargs)

    @action(methods=["get"], detail=False, url_path="random-list")
    def random_list(self, request, *args, **kwargs):
        """
        An endpoint that retrieves a collection of random public Speed objects
        stored in the Redis cache.
        """
        random_speeds_ord_dict = get_random_speeds()
        if random_speeds_ord_dict["count"] > 0:
            return response.Response(data=random_speeds_ord_dict, status=200)
        else:
            data = {"message": "Data not available. Please try again later."}
            return response.Response(data=data, status=404)


class SpeedFeedbackViewSet(viewsets.ModelViewSet):
    """
    A user should always be authorized for any action in this ViewSet.
    """

    # ModelViewSet (5) attributes
    queryset = SpeedFeedback.objects.all()
    serializer_class = SpeedFeedbackSerializer
    permission_classes = [UserIsAuthorized]

    filter_backends = [DjangoFilterBackend]
    filterset_class = SpeedFeedbackFilter

    # custom attribute
    not_allowed_http_method_names = ["put", "delete"]
    # ModelViewSet attribute
    http_method_names = []
    for method_name in viewsets.ModelViewSet.http_method_names:
        if method_name not in not_allowed_http_method_names:
            http_method_names.append(method_name)

    # custom attribute
    object_level_actions = [
        "retrieve",
        "partial_update",
    ]
    # custom attribute
    forbidden_object_level_actions = [
        "update",  # handled by `not_allowed_http_method_names` attribute
        "destroy",  # handled by `not_allowed_http_method_names` attribute
    ]

    def get_permissions(self):
        if self.action in self.object_level_actions:
            self.permission_classes = [SpeedFeedbackPermissions]
        return super().get_permissions()

    def get_queryset(self):
        # secured by the permission_classes
        if (
            self.request.user.is_admin
            or self.action in self.object_level_actions
        ):
            return super().get_queryset()
        else:
            return SpeedFeedbackQueries.get_user_query(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SpeedBookmarkViewSet(viewsets.ModelViewSet):
    """
    A user should always be authorized for any action in this ViewSet.
    """

    # ModelViewSet (5) attributes
    queryset = SpeedBookmark.objects.all()
    serializer_class = SpeedBookmarkSerializer
    permission_classes = [UserIsAuthorized]

    filter_backends = [DjangoFilterBackend]
    filterset_class = SpeedBookmarkFilter

    # custom attribute
    not_allowed_http_method_names = ["put"]
    # ModelViewSet attribute
    http_method_names = []
    for method_name in viewsets.ModelViewSet.http_method_names:
        if method_name not in not_allowed_http_method_names:
            http_method_names.append(method_name)

    # custom attribute
    object_level_actions = ["destroy", "retrieve", "partial_update"]
    # custom attribute
    forbidden_object_level_actions = [
        "update",  # handled by `not_allowed_http_method_names` attribute
    ]

    def get_permissions(self):
        if self.action in self.object_level_actions:
            self.permission_classes = [SpeedBookmarkPermissions]
        return super().get_permissions()

    def get_queryset(self):
        # secured by the permission_classes
        if (
            self.request.user.is_admin
            or self.action in self.object_level_actions
        ):
            return super().get_queryset()
        else:
            return SpeedBookmarkQueries.get_user_query(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SpeedReportViewSet(viewsets.ModelViewSet):
    """
    A user should always be authorized for any action in this ViewSet.
    """

    # ModelViewSet (3) attributes
    queryset = SpeedReport.objects.all()
    serializer_class = SpeedReportSerializer
    permission_classes = [UserIsAuthorized]

    def get_queryset(self):
        if self.request.user.is_admin:
            return super().get_queryset()
        return SpeedReport.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        if self.request.user.is_admin:
            return super().retrieve(request, *args, **kwargs)

        return response.Response(
            {"detail": 'Method "GET" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def update(self, request, *args, **kwargs):
        if self.request.user.is_admin:
            return super().retrieve(request, *args, **kwargs)

        # handles both "PUT" and "PATCH" (`partial_update`)
        return response.Response(
            {"detail": f'Method "{request.method.upper()}" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_admin:
            return super().retrieve(request, *args, **kwargs)

        return response.Response(
            {"detail": 'Method "DELETE" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
