from app.extensions import db
from app.models import DropdownOption


PROJECT_SECTOR = 'project_sector'
COST_TYPE = 'cost_type'

DEFAULT_PROJECT_SECTORS = [
    'Roads',
    'Bridges',
    'Buildings',
    'Water Supply',
    'Drainage',
    'Electricity',
]

DEFAULT_COST_TYPES = [
    'Civil Labour',
    'Electric Labour',
    'Tiles Labour',
    'Paint Labour',
    'Dhalai Labour',
    'Thai Labour',
    'Carpenter Labour',
    'Welding Labour',
    'Sanitary Labour',
    'Sand',
    'Cement',
    'Rod',
    'Rock',
    'Brick',
    'Work Assistant',
    'Night Guard',
    'Manager',
    'Office Charge',
    'Bitumen',
    'Others',
]


def seed_dropdown_options():
    for option_type, names in (
        (PROJECT_SECTOR, DEFAULT_PROJECT_SECTORS),
        (COST_TYPE, DEFAULT_COST_TYPES),
    ):
        existing = {
            row[0]
            for row in db.session.query(DropdownOption.name)
            .filter_by(option_type=option_type)
            .all()
        }
        for name in names:
            if name not in existing:
                db.session.add(DropdownOption(option_type=option_type, name=name))

    db.session.commit()


def get_dropdown_options(option_type):
    return [
        option.name
        for option in DropdownOption.query
        .filter_by(option_type=option_type)
        .order_by(DropdownOption.name.asc())
        .all()
    ]
