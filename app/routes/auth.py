from django.contrib.auth import get_user_model
from django_bolt import BoltAPI, Depends
from django_bolt.exceptions import HTTPException

from app.auth import create_token, get_current_user
from app.schemas.auth import LoginIn, TokenOut, UserCreate, UserOut, UserUpdateIn

User = get_user_model()


def register_auth_routes(api: BoltAPI):
    @api.post(
        "/api/auth/register",
        response_model=UserOut,
        status_code=201,
        tags=["Authentication"],
        summary="Register a new user account",
    )
    async def register(data: UserCreate):
        if await User.objects.filter(username=data.username).aexists():
            raise HTTPException(400, "Username already exists")
        if await User.objects.filter(email=data.email).aexists():
            raise HTTPException(400, "Email already registered")

        user = await User.objects.acreate(
            username=data.username,
            email=data.email,
            bio=data.bio,
            avatar_url=data.avatar_url,
        )
        user.set_password(data.password)
        await user.asave()

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
        if not user or not user.check_password(credentials.password):
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
