#%%
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

#%%
citylist = [("Portland", "OR"), ("Seattle", "WA"), ("Richland", "WA")]
ids_max = 1000

# %%
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:test@localhost/checkweb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

#%%
class dbhelper:
    @classmethod
    def get_elem_num(cls, key, val):
        return len(cls.query.filter_by(**{key: val}).all())

    @classmethod
    def pick(cls, key, val):  # make it uniform, return list at all time
        if cls.get_elem_num(key, val) == 0:
            print(f"No {cls.__name__} element picked")
            return []
        if cls.get_elem_num(key, val) == 1:
            print(f"1 {cls.__name__} element picked")
            return cls.query.filter_by(**{key: val}).all()
        if cls.get_elem_num(key, val) > 1:
            print(f"{cls.get_elem_num(key, val)} {cls.__name__} elements picked")
            return cls.query.filter_by(**{key: val}).all()

    @classmethod
    def pickone(cls, key, val):
        if cls.get_elem_num(key, val) != 1:
            print(f"No unique {cls.__name__} element picked")
            return None
        print(f"Unique {cls.__name__} element picked")
        return cls.query.filter_by(**{key: val}).first()

    @property
    def id(self):
        return self.__dict__["ID"]


class COMCHECK_BUILDING(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_BUILDING"]


class COMCHECK_USER_PROJECT(db.Model, dbhelper):
    __table__ = db.Model.metadata.tables["COMCHECK_USER_PROJECT"]


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


def dictize(cmobj):
    if cmobj is None:
        return None
    cmdict = cmobj.__dict__
    newdict = {}
    newdict["ID"] = cmdict["ID"]
    cmdict = {k: cmdict[k] for k in sorted(cmdict)}
    cmdict.pop("ID", None)
    cmdict.pop("_sa_instance_state", None)

    for (
        k,
        val,
    ) in (
        cmdict.items()
    ):  # if in the end we know for sure what fields are datetime, we can speed up this with filters
        if isinstance(val, datetime):
            cmdict[k] = val.__str__()

    return dict(newdict, **cmdict)


def dictize_list(cmobjs):
    if len(cmobjs) == 0:
        return None
    newdict = {}
    i = 0
    for cmobj in cmobjs:
        newdict[i] = dictize(cmobj)
        i += 1
    return newdict


# %%
def get_by_id(id):
    dump = {}
    building = COMCHECK_BUILDING.pickone("ID", id)
    dump["building"] = dictize(building)

    if building is not None:
        user_project = COMCHECK_USER_PROJECT.pickone("BUILDING_ID", id)
        dump["user_project"] = dictize(user_project)

        location = COMCHECK_LOCATION.pickone("BUILDING_ID", id)
        dump["location"] = dictize(location)

        control = COMCHECK_CONTROL.pickone("BUILDING_ID", id)
        dump["control"] = dictize(control)

        lighting = COMCHECK_LIGHTING.pickone("BUILDING_ID", id)
        dump["lighting"] = dictize(lighting)

        if lighting is not None:
            lighting_id = lighting.id
            building_area_uses = COMCHECK_BUILDING_AREA_USE.pick(
                "LIGHTING_ID", lighting_id
            )
            dump["lighting"]["building_area_use"] = dictize_list(building_area_uses)

            exterior_uses = COMCHECK_EXTERIOR_USE.pick(
                "LIGHTING_ID", lighting_id
            )  # use lighting id not building id
            dump["lighting"]["exterior_use"] = dictize_list(exterior_uses)
            i = 0
            for exterior_use in exterior_uses:
                exterior_use_id = exterior_use.id
                exterior_spaces = COMCHECK_EXTERIOR_SPACE.pick(
                    "EXTERIOR_USE_ID", exterior_use_id
                )
                dump["lighting"]["exterior_use"][i]["exterior_space"] = dictize_list(
                    exterior_spaces
                )
                j = 0
                for exterior_space in exterior_spaces:
                    exterior_space_id = exterior_space.id
                    fixtures = COMCHECK_FIXTURES.pick(
                        "EXTERIOR_SPACE_ID", exterior_space_id
                    )  # also have int space id back ref
                    dump["lighting"]["exterior_use"][i]["exterior_space"][j][
                        "fixtures"
                    ] = dictize_list(fixtures)
                    j += 1
                i += 1

        project_info = COMCHECK_PROJECT_INFO.pickone("BUILDING_ID", id)
        dump["project_info"] = dictize(project_info)

        swh_systems = COMCHECK_SWH_SYSTEMS.pick("BUILDING_ID", id)
        dump["swh_systems"] = dictize_list(swh_systems)

        envelope = COMCHECK_ENVELOPE.pickone("BUILDING_ID", id)
        dump["envelope"] = dictize(envelope)
        if envelope is not None:
            envelope_id = envelope.id
            floors = COMCHECK_FLOORS.pick("ENVELOPE_ID", envelope_id)
            dump["envelope"]["floors"] = dictize_list(floors)

            ag_walls = COMCHECK_AG_WALLS.pick("ENVELOPE_ID", envelope_id)
            dump["envelope"]["ag_walls"] = dictize_list(ag_walls)
            i = 0
            for ag_wall in ag_walls:
                ag_wall_id = ag_wall.id
                doors_ag = COMCHECK_DOORS.pick("AG_WALL_ID", ag_wall_id)
                dump["envelope"]["ag_walls"][i]["doors_ag"] = dictize_list(doors_ag)
                windows_ag = COMCHECK_WINDOWS.pick("AG_WALL_ID", ag_wall_id)
                dump["envelope"]["ag_walls"][i]["windows_ag"] = dictize_list(windows_ag)
                i += 1

            bg_walls = COMCHECK_BG_WALLS.pick("ENVELOPE_ID", envelope_id)
            dump["envelope"]["bg_walls"] = dictize_list(bg_walls)
            i = 0
            for bg_wall in bg_walls:
                bg_wall_id = bg_wall.id
                doors_bg = COMCHECK_DOORS.pick("BG_WALL_ID", bg_wall_id)
                dump["envelope"]["bg_walls"][i]["doors_bg"] = dictize_list(doors_bg)
                windows_bg = COMCHECK_WINDOWS.pick("BG_WALL_ID", bg_wall_id)
                dump["envelope"]["bg_walls"][i]["windows_bg"] = dictize_list(windows_bg)
                i += 1

            doors_envelope = COMCHECK_DOORS.pick("ENVELOPE_ID", envelope_id)
            dump["envelope"]["doors_envelope"] = dictize_list(doors_envelope)
            windows_envelope = COMCHECK_WINDOWS.pick("ENVELOPE_ID", envelope_id)
            dump["envelope"]["windows_envelope"] = dictize_list(windows_envelope)
            roofs = COMCHECK_ROOFS.pick("ENVELOPE_ID", envelope_id)
            dump["envelope"]["roofs"] = dictize_list(roofs)
            skylights = COMCHECK_SKYLIGHTS.pick("ENVELOPE_ID", envelope_id)
            dump["envelope"]["skylights"] = dictize_list(skylights)

        hvac = COMCHECK_HVAC.pickone("BUILDING_ID", id)
        dump["hvac"] = dictize(hvac)
        if hvac is not None:  # hvac_systems also have fan id back ref
            hvac_id = hvac.id
            hvac_plants = COMCHECK_HVAC_PLANTS.pick("HVAC_ID", hvac_id)
            dump["hvac"]["hvac_plants"] = dictize_list(hvac_plants)
            hvac_systems = COMCHECK_HVAC_SYSTEMS.pick("HVAC_ID", hvac_id)
            dump["hvac"]["hvac_systems"] = dictize_list(hvac_systems)

            fan_systems = COMCHECK_FAN_SYSTEMS.pick("HVAC_ID", hvac_id)
            dump["hvac"]["fan_systems"] = dictize_list(fan_systems)
            i = 0
            for fan_system in fan_systems:
                fan_system_id = fan_system.id
                fan = COMCHECK_FAN.pick("FAN_SYSTEM_ID", fan_system_id)
                dump["hvac"]["fan_systems"][i]["fan"] = dictize_list(fan)
                i += 1

        return dump


# %%
def bldg_ids_by_city_state(city, state):
    q_dict = {"PROJECT_CITY": city, "PROJECT_STATE": state}
    projects = COMCHECK_PROJECT_INFO.query.filter_by(**q_dict).all()
    ids = [project.__dict__["BUILDING_ID"] for project in projects]
    return ids


# %%
def json_by_city_state_list(tuples):
    for dual in tuples:
        ids = bldg_ids_by_city_state(dual[0], dual[1])
        city_size = len(ids)
        print(
            f"Getting {dual[0]}_{dual[1]}: {city_size} bldgs found in the database..."
        )

        i = 0
        for id in ids:
            i += 1
            print(f"\n\nDumping bldg {id} ({i} / {city_size})...\n")

            dump = get_by_id(id)
            with open(
                f"{dual[0]}_{dual[1]}_{id}_{datetime.now().strftime('%m%d_%H%M')}.json",
                "w",
            ) as f:
                json.dump(dump, f, indent=4)

            if i >= ids_max:
                break


# %% Run
def main():
    json_by_city_state_list(citylist)


if __name__ == "__main__":
    main()
