import typing
import strawberry


GenericScalar = strawberry.scalar(
    typing.NewType("GenericScalar", typing.Any),
    description="The GenericScalar scalar type represents a generic GraphQL scalar value that could be: List or Object.",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
