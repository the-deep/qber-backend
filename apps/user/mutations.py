import strawberry
from strawberry.types import Info

from asgiref.sync import sync_to_async
from django.contrib.auth import login, logout, update_session_auth_hash

from utils.strawberry.transformers import convert_serializer_to_type
from utils.strawberry.mutations import (
    process_input_data,
    mutation_is_not_valid,
    MutationResponseType,
    MutationEmptyResponseType,
)

from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetTriggerSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
    UserMeSerializer,
)
from .queries import UserMeType


LoginInput = convert_serializer_to_type(LoginSerializer, name='LoginInput')
RegisterInput = convert_serializer_to_type(RegisterSerializer, name='RegisterInput')
PasswordResetTriggerInput = convert_serializer_to_type(PasswordResetTriggerSerializer, name='PasswordResetTriggerInput')
PasswordResetConfirmInput = convert_serializer_to_type(PasswordResetConfirmSerializer, name='PasswordResetConfirmInput')
PasswordChangeInput = convert_serializer_to_type(PasswordChangeSerializer, name='PasswordChangeInput')
UserMeInput = convert_serializer_to_type(UserMeSerializer, partial=True, name='UserMeInput')


@strawberry.type
class PublicMutation:

    @strawberry.mutation
    @sync_to_async
    def register(self, data: RegisterInput, info: Info) -> MutationResponseType[UserMeType]:
        serializer = RegisterSerializer(data=process_input_data(data), context={'request': info.context.request})
        if errors := mutation_is_not_valid(serializer):
            return MutationResponseType(
                ok=False,
                errors=errors,
            )
        instance = serializer.save()
        return MutationResponseType(result=instance)

    @strawberry.mutation
    @sync_to_async
    def login(self, data: LoginInput, info: Info) -> MutationResponseType[UserMeType]:
        serializer = LoginSerializer(data=process_input_data(data), context={'request': info.context.request})
        if errors := mutation_is_not_valid(serializer):
            return MutationResponseType(
                ok=False,
                errors=errors,
            )
        user = serializer.validated_data['user']
        login(info.context.request, user)
        return MutationResponseType(
            result=user,
        )

    @strawberry.mutation
    @sync_to_async
    def logout(self, info: Info) -> MutationEmptyResponseType:
        if info.context.request.user.is_authenticated:
            logout(info.context.request)
            return MutationEmptyResponseType(ok=True)
        return MutationEmptyResponseType(ok=False)

    @strawberry.mutation
    @sync_to_async
    def password_reset_trigger(self, data: PasswordResetTriggerInput, info: Info) -> MutationEmptyResponseType:
        serializer = PasswordResetTriggerSerializer(data=process_input_data(data), context={'request': info.context.request})
        if errors := mutation_is_not_valid(serializer):
            return MutationEmptyResponseType(
                ok=False,
                errors=errors,
            )
        serializer.save()
        return MutationEmptyResponseType()

    @strawberry.mutation
    @sync_to_async
    def password_reset_confirm(self, data: PasswordResetConfirmInput, info: Info) -> MutationEmptyResponseType:
        serializer = PasswordResetConfirmSerializer(data=process_input_data(data), context={'request': info.context.request})
        if errors := mutation_is_not_valid(serializer):
            return MutationEmptyResponseType(
                ok=False,
                errors=errors,
            )
        serializer.save()
        return MutationEmptyResponseType()


@strawberry.type
class PrivateMutation:

    @strawberry.mutation
    @sync_to_async
    def change_user_password(self, data: PasswordChangeInput, info: Info) -> MutationEmptyResponseType:
        serializer = PasswordChangeSerializer(data=process_input_data(data), context={'request': info.context.request})
        if errors := mutation_is_not_valid(serializer):
            return MutationEmptyResponseType(
                ok=False,
                errors=errors,
            )
        serializer.save()
        update_session_auth_hash(info.context.request, info.context.request.user)
        return MutationEmptyResponseType()

    @strawberry.mutation
    @sync_to_async
    def update_me(self, data: UserMeInput, info: Info) -> MutationResponseType[UserMeType]:
        serializer = UserMeSerializer(data=process_input_data(data), context={'request': info.context.request}, partial=True)
        if errors := mutation_is_not_valid(serializer):
            return MutationResponseType(
                ok=False,
                errors=errors,
            )
        user = serializer.save()
        return MutationResponseType(
            result=user,
        )
