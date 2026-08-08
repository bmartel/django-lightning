import asyncio

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django_bolt import BoltAPI, Depends
from django_bolt.exceptions import HTTPException

from app.auth import create_token, get_current_user
from app.schemas.auth import LoginIn, TokenOut, UserCreate, UserOut, UserUpdateIn

User = get_user_model()


def _verify_password(user, raw_password: str) -> bool:
    """Verify a password, running a dummy hash for unknown users to equalize timing."""
    if user is None:
        # Burn comparable CPU so login timing doesn't reveal whether the user exists.
        make_password(raw_password)
        return False
    return user.check_password(raw_password)


def register_auth_routes(api: BoltAPI):
    @api.post(
        "/api/auth/register",
        response_model=UserOut,
        status_code=201,
        tags=["Authentication"],
        summary="Register a new user account",
    )
    async def register(data: UserCreate):
        # Enforce Django's configured password validators (common-password, numeric-only,
        # user-attribute similarity, min length) — msgspec only checked the length bound.
        candidate = User(username=data.username, email=data.email)
        try:
            await asyncio.to_thread(validate_password, data.password, candidate)
        except ValidationError as exc:
            raise HTTPException(400, "; ".join(exc.messages))

        # Hash off the event loop, then create the row in a single write so a crash can't
        # leave an account with an empty password. A unique-constraint race surfaces as 400.
        password_hash = await asyncio.to_thread(make_password, data.password)
        try:
            user = await User.objects.acreate(
                username=data.username,
                email=data.email,
                password=password_hash,
                bio=data.bio,
                avatar_url=data.avatar_url,
            )
        except IntegrityError:
            raise HTTPException(400, "Username or email already registered")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "is_staff": user.is_staff,
        }

    @api.post(
        "/api/auth/login",
        response_model=TokenOut,
        tags=["Authentication"],
        summary="Authenticate user and receive JWT access token",
    )
    async def login(credentials: LoginIn):
        user = await User.objects.filter(username=credentials.username).afirst()
        # Verify the PBKDF2 hash off the event loop. Always run a check (even for an
        # unknown user) to avoid leaking account existence via response timing.
        valid = await asyncio.to_thread(_verify_password, user, credentials.password)
        if not valid:
            raise HTTPException(401, "Invalid username or password")

        token = create_token(user)
        return {"access_token": token, "token_type": "bearer"}

    @api.get(
        "/api/auth/me",
        response_model=UserOut,
        tags=["Authentication"],
        summary="Get authenticated user profile",
    )
    async def get_me(current_user: dict = Depends(get_current_user)):
        user = await User.objects.filter(id=int(current_user["sub"])).afirst()
        if not user:
            raise HTTPException(404, "User profile not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "is_staff": user.is_staff,
        }

    @api.patch(
        "/api/auth/me",
        response_model=UserOut,
        tags=["Authentication"],
        summary="Update authenticated user profile",
    )
    async def update_me(
        payload: UserUpdateIn,
        current_user: dict = Depends(get_current_user),
    ):
        user = await User.objects.filter(id=int(current_user["sub"])).afirst()
        if not user:
            raise HTTPException(404, "User profile not found")

        if payload.bio is not None:
            user.bio = payload.bio
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url

        await user.asave()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "is_staff": user.is_staff,
        }
