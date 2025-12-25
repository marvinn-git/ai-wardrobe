from auth import register_user, login_user

email = "test@example.com"
password = "1234"

uid, err = register_user(email, password)
print("REGISTER:", uid, err)

uid2, err2 = login_user(email, password)
print("LOGIN:", uid2, err2)
