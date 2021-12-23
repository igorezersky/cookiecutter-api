from pathlib import Path

from {{ cookiecutter.project_slug }}.app.core import App, Security, EmailValidator, PasswordValidator
from {{ cookiecutter.project_slug }}.configs import Configs
from {{ cookiecutter.project_slug }}.orm import Database

# main server processors
configs = Configs(package_dir=Path(__file__).parent)
db = Database(configs=configs.db)
security = Security(configs=configs.security, db=db)
app = App(configs=configs, security=security, db=db)

# validators
email_validator = EmailValidator(configs=configs.validation)
password_validator = PasswordValidator(configs=configs.validation)
