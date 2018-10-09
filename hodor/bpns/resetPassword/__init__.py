from flask import Blueprint
reset_password_api = Blueprint('reset_password_api', __name__)

from . import begin
from . import gather_portal_id
from . import check_portal_id
from . import gather_city
from . import check_city
from . import gather_contact_number
from . import check_phone_number
from . import gather_postal_code
from . import check_postal_code
from . import action_reset_password