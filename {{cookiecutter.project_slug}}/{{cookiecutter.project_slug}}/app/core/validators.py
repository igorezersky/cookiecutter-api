import re

from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel

from {{ cookiecutter.project_slug }}.configs import ValidationConfigs


class ValidationResult(BaseModel):
    success: bool
    message: str


class EmailValidator:
    def __init__(self, configs: ValidationConfigs) -> None:
        self.messages = configs.email['messages']

    def __call__(self, email: str) -> ValidationResult:
        """ Validate `email` and return formatted result """

        try:
            validate_email(email)
        except EmailNotValidError:
            success, message = False, self.messages['invalid']
        else:
            success, message = True, self.messages['success']
        return ValidationResult(success=success, message=message)


class PasswordValidator:
    def __init__(self, configs: ValidationConfigs) -> None:
        self.regex = configs.password['regex']
        self.messages = configs.password['messages']

    def __call__(self, password: str) -> ValidationResult:
        """ Validate `password` and return formatted result """

        success = bool(re.match(self.regex, password))
        return ValidationResult(success=success, message=self.messages['success' if success else 'invalid'])
