from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import store_tokens


from .service import GoogleRawFlowService
from .serializers import GoogleAPISerializer
from .models import OAuthSession, User


class PublicAPI(APIView):
    authentication_classes = []
    permission_classes = []


class GoogleRedirectAPI(PublicAPI):
    def get(self, request, *args, **kwargs):
        google_flow = GoogleRawFlowService()
        authorization_url, state = google_flow.get_authorization_url()
        OAuthSession.objects.create(session_state=state)
        return redirect(authorization_url)


class GoogleAPI(PublicAPI):
    def get(self, request):
        serializer = GoogleAPISerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get("code")
        error = serializer.validated_data.get("error")
        state = serializer.validated_data.get("state")

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if not code or not state:
            return Response(
                {"error": "code and state are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            oauth_session = OAuthSession.objects.get(session_state=state)
        except OAuthSession.DoesNotExist:
            return Response(
                {"error": "Session state not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        oauth_session.delete()

        google_flow = GoogleRawFlowService()
        google_tokens = google_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()
        user_email = id_token_decoded.get("email")
        user = User.objects.filter(email=user_email).first()

        if user is None:
            user = User.objects.create_user(
                email=user_email,
            )
        login(request, user)
        refresh = RefreshToken.for_user(user)
        token_serializer = TokenObtainPairSerializer()
        token = token_serializer.get_token(user)

        store_tokens(user, google_tokens.access_token, google_tokens.refresh_token)

        response = Response(
            {
                "access": str(token.access_token),
                "refresh": str(refresh),
            }
        )

        return response

