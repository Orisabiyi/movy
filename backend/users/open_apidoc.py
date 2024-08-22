signup_response_doc = {
    201: {
        "description": "User account created successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": "User account created successfully",
                    "status_code": 201,
                }
            }
        },
    },
    400: {
        "description": "User with email already exists",
        "content": {
            "application/json": {
                "example": {
                    "message": "User with email already exists",
                    "status_code": 400,
                }
            }
        },
    },
}

login_response_doc = {
    200: {
        "description": "Successful login",
        "content": {
            "application/json": {
                "example": {
                    "refresh_token": "some_refresh_token",
                    "access_token": "some_access_token",
                    "expires_at": 3600,
                }
            }
        },
    },
    400: {
        "description": "Bad request",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_credentials": {
                        "summary": "Invalid email or password",
                        "value": {
                            "message": "Invalid email or password",
                            "status_code": 400,
                        },
                    },
                    "unverified_account": {
                        "summary": "Account not verified",
                        "value": {
                            "message": "Your account is not verified please check your mail box",
                            "status_code": 400,
                        },
                    },
                    "deactivated_account": {
                        "summary": "Account deactivated",
                        "value": {
                            "message": "Your account has been deactivated please contact admin",
                            "status_code": 400,
                        },
                    },
                }
            }
        },
    },
}

verify_token_response = {
    200: {
        "description": "Email successfully verified",
        "content": {
            "application/json": {
                "example": {
                    "id": "qkwk-aqk1A0-1lnlwq",
                    "name": "User name",
                    "refresh_token": "some_refresh_token",
                    "refresh_token": "some_access_token_token",
                    "status_code": 200,
                }
            }
        },
    },
    400: {
        "description": "Bad request",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_token": {
                        "summary": "Invalid token",
                        "value": {
                            "message": "Invalid token provided",
                            "status_code": 400,
                        },
                    },
                    "expired_token": {
                        "summary": "Token expired",
                        "value": {
                            "message": "Invalid token provided or token has expired",
                            "status_code": 400,
                        },
                    },
                }
            }
        },
    },
}

refresh_response_doc = {
    200: {
        "description": "Successful Token Refresh",
        "content": {
            "application/json": {
                "example": {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                    "expires_at": 1690000000,
                }
            }
        },
    },
    400: {
        "description": "Invalid Token",
        "content": {
            "application/json": {
                "example": {
                    "message": "Invalid token provided",
                    "status_code": 400,
                }
            }
        },
    },
}

forgot_password_response_doc = {
    200: {
        "description": "Password Reset Email Sent",
        "content": {
            "application/json": {
                "example": {
                    "message": "Check your mail for reset password link",
                    "status_code": 200,
                }
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {
                    "message": "Email has been deactivated please contact support",
                    "status_code": 400,
                }
            }
        },
    },
    404: {
        "description": "Email Not Found",
        "content": {
            "application/json": {
                "example": {
                    "message": "Email does not exist",
                    "status_code": 400,
                }
            }
        },
    },
}

reset_password_response_doc = {
    200: {
        "description": "Password Successfully Reset",
        "content": {
            "application/json": {
                "example": {
                    "message": "Password has been successfully reset",
                    "status_code": 200
                }
            }
        }
    },
    400: {
        "description": "Invalid Token",
        "content": {
            "application/json": {
                "example": {
                    "message": "Invalid token passed",
                    "status_code": 400
                }
            }
        }
    }
}