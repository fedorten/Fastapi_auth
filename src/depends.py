# def authenticate_user(user_id, password, session: SessionDep):
#     user = get_user_by_id(user_id, session)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
