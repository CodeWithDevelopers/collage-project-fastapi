def user_helper(user) -> dict:
    return {
        "id": str(user.get("id")),
        "password": str(user.get("password")),
        "name": user.get("name") or "",
        "email": user.get("email") or "",
        "role": user.get("role", "user"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
        "is_deleted": user.get("is_deleted", False),
    }
