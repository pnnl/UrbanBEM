#%%
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# %%
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:test@localhost/checkweb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

# %%
id = 752
#%%


class dbhelper:
    @classmethod
    def get_elem_num(cls, key, val):
        return len(cls.query.filter_by(**{key: val}).all())

    @classmethod
    def pick(cls, key="BUILDING_ID", val=id):
        if cls.get_elem_num(key, val) == 0:
            print(f"No {cls.__name__} element picked")
            return None
        if cls.get_elem_num(key, val) == 1:
            print(f"1 {cls.__name__} element picked")
            return cls.query.filter_by(**{key: val}).first()
        if cls.get_elem_num(key, val) > 1:
            print(f"{cls.get_elem_num(key, val)} {cls.__name__} elements picked")
            return cls.query.filter_by(**{key: val}).all()

    @property
    def id(self):
        return self.__dict__["ID"]


class COMCHECK_BUILDING(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_BUILDING"]


class COMCHECK_LOCATION(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_LOCATION"]


class COMCHECK_LIGHTING(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_LIGHTING"]


class COMCHECK_BUILDING_AREA_USE(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_BUILDING_AREA_USE"]


class COMCHECK_PROJECT_INFO(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_PROJECT_INFO"]


class COMCHECK_CONTROL(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_CONTROL"]


class COMCHECK_SWH_SYSTEMS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_SWH_SYSTEMS"]


class COMCHECK_SWH_SYSTEMS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_SWH_SYSTEMS"]


class COMCHECK_ENVELOPE(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_ENVELOPE"]


class COMCHECK_FLOORS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_FLOORS"]


class COMCHECK_AG_WALLS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_AG_WALLS"]


class COMCHECK_BG_WALLS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_BG_WALLS"]


class COMCHECK_DOORS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_DOORS"]


class COMCHECK_WINDOWS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_WINDOWS"]


class COMCHECK_ROOFS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_ROOFS"]


class COMCHECK_SKYLIGHTS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_SKYLIGHTS"]


class COMCHECK_HVAC(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_HVAC"]


class COMCHECK_HVAC_PLANTS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_HVAC_PLANTS"]


class COMCHECK_HVAC_SYSTEMS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_HVAC_SYSTEMS"]


class COMCHECK_FAN_SYSTEMS(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_FAN_SYSTEMS"]


class COMCHECK_FAN(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_FAN"]


class COMCHECK_EXTERIOR_USE(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_EXTERIOR_USE"]


class COMCHECK_EXTERIOR_SPACE(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_EXTERIOR_SPACE"]


class COMCHECK_FIXTURES(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_FIXTURES"]


# %%
building = COMCHECK_BUILDING.pick("ID", id)

if building is not None:
    location = COMCHECK_LOCATION.pick()
    control = COMCHECK_CONTROL.pick()

    lighting = COMCHECK_LIGHTING.pick()
    if lighting is not None:
        lighting_id = lighting.id
        building_area_use = COMCHECK_BUILDING_AREA_USE.pick("LIGHTING_ID", lighting_id)

    project_info = COMCHECK_PROJECT_INFO.pick()
    swh_systems = COMCHECK_SWH_SYSTEMS.pick()

    envelope = COMCHECK_ENVELOPE.pick()
    if envelope is not None:
        envelope_id = envelope.id
        floor = COMCHECK_FLOORS.pick("ENVELOPE_ID", envelope_id)

        ag_walls = COMCHECK_AG_WALLS.pick("ENVELOPE_ID", envelope_id)
        if ag_walls is not None:
            ag_wall_id = ag_walls.id
            doors_ag = COMCHECK_DOORS.pick("AG_WALL_ID", ag_wall_id)
            windows_ag = COMCHECK_WINDOWS.pick("AG_WALL_ID", ag_wall_id)

        bg_walls = COMCHECK_BG_WALLS.pick("ENVELOPE_ID", envelope_id)
        if bg_walls is not None:
            bg_wall_id = bg_walls.id
            doors_bg = COMCHECK_DOORS.pick("BG_WALL_ID", bg_wall_id)
            windows_bg = COMCHECK_WINDOWS.pick("BG_WALL_ID", bg_wall_id)

        doors_envelope = COMCHECK_DOORS.pick("ENVELOPE_ID", envelope_id)
        windows_envelope = COMCHECK_WINDOWS.pick("ENVELOPE_ID", envelope_id)
        roofs = COMCHECK_ROOFS.pick("ENVELOPE_ID", envelope_id)
        skylights = COMCHECK_SKYLIGHTS.pick("ENVELOPE_ID", envelope_id)

    hvac = COMCHECK_HVAC.pick()
    if hvac is not None:  # hvac_xx also have fan id back ref
        hvac_id = hvac.id
        hvac_plants = COMCHECK_HVAC_PLANTS.pick("HVAC_ID", hvac_id)
        hvac_systems = COMCHECK_HVAC_SYSTEMS.pick("HVAC_ID", hvac_id)
        fan_systems = COMCHECK_FAN_SYSTEMS.pick("HVAC_ID", hvac_id)
        fan = COMCHECK_FAN.pick("HVAC_ID", hvac_id)





# %%
