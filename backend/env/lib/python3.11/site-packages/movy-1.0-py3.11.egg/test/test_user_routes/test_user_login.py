"""
- User should be able to login
- User should not be able to login with incorrect password
- Inactive user should not be able to login
- Unverified user should not be able to login
"""


# def test_user_login(client, user, data):
#     """
#     test user login successful
#     """
#     data = {'email': user.email, "password": data['password']}
#     response = client.post("/auth/login", json=data)
#     assert response.status_code == 200
#     assert response.json()["access_token"] is not None
#     assert response.json()["refresh_token"] is not None
#     assert response.json()["expires_in"] is not None


# def test_user_login_wrong_password(client, user, data):
#     response = client.post("/auth/login", data={"email": user.email, "password": "qwknqe122!A"})
#     assert response.status_code == 400


