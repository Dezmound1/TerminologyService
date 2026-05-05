from rest_framework.response import Response


from datetime import datetime

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, views
from rest_framework.response import Response

from refbooks.api.serializers import (
    CheckElementResponseSerializer,
    ElementSerializer,
    RefBookSerializer,
)
from refbooks.domain.exceptions import RefBookNotFound, VersionNotFound
from refbooks.services.refbook_service import (
    ElementService,
    RefBookService,
)


class RefBooksListView(views.APIView):
    """Get list of all reference books"""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                description="Date in YYYY-MM-DD format to filter refbooks",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: OpenApiParameter(
                name="refbooks",
                description="List of reference books",
                type=str,
            ),
            400: {"description": "Invalid date format"},
        },
        summary="Get list of reference books",
        description="Returns list of reference books that have a version for given date",
        tags=["RefBooks"],
    )
    def get(self, request) -> Response:
        date_str = request.query_params.get("date")
        target_date = None

        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        service = RefBookService()
        refbooks = service.get_refbooks_list(target_date)

        return Response({"refbooks": [RefBookSerializer.from_entity(rb) for rb in refbooks]})


class RefBookElementsView(views.APIView):
    """Get elements of a specific reference book version"""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                description="Reference book ID",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="version",
                description="Version string (optional, uses current if not provided)",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: OpenApiParameter(
                name="elements",
                description="List of elements",
                type=str,
            ),
            404: {"description": "Reference book or version not found"},
        },
        summary="Get elements of reference book",
        description="Returns list of elements for specific or current version",
        tags=["RefBooks"],
    )
    def get(self, request, id) -> Response:
        version_string = request.query_params.get("version")

        service = ElementService()
        try:
            elements = service.get_elements_for_version(id, version_string)
            return Response({"elements": [ElementSerializer.from_entity(e) for e in elements]})
        except RefBookNotFound:
            return Response(
                {"detail": "Справочник не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except VersionNotFound:
            return Response(
                {"detail": "Версия не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )


class CheckElementView(views.APIView):
    """Check if element exists in reference book version"""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                description="Reference book ID",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="code",
                description="Element code",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="value",
                description="Element value",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="version",
                description="Version string (optional, uses current if not provided)",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: CheckElementResponseSerializer,
            400: {"description": "Missing required parameters"},
            404: {"description": "Reference book or version not found"},
        },
        summary="Check element in reference book",
        description="Check if element with given code and value exists in version",
        tags=["RefBooks"],
    )
    def get(self, request, id) -> Response:
        code = request.query_params.get("code")
        value = request.query_params.get("value")
        version_string = request.query_params.get("version")

        if not code or not value:
            return Response(
                {"detail": "Parameters 'code' and 'value' are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = ElementService()
        try:
            exists = service.check_element_exists(id, code, value, version_string)
            return Response({"exists": exists})
        except RefBookNotFound:
            return Response(
                {"detail": "Справочник не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except VersionNotFound:
            return Response(
                {"detail": "Версия не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )
