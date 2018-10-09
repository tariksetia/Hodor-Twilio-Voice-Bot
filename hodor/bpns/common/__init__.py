from flask import Blueprint
common = Blueprint('common', __name__)

from . import begin
from . import gather_portal_id
from . import check_portal_id
from . import gather_city
from . import gather_contact_number
from . import gather_postal_code
from . import action_reset_password