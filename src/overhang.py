from io import StringIO
from typing import Dict
from eppy import modeleditor
from eppy.modeleditor import IDF
from recipes import copy_idf_objects

IDF.setiddname("../resources/V9-5-0-Energy+.idd")


class Overhang:
    def __init__(self, case: Dict, idf: IDF):

        self.idf = idf
        overhangflag = False

        if case["overhang"]["has_overhang"].lower() == "yes":
            overhangflag = True

        self.add_overhang(has_overhang=overhangflag)

    def set_overhang_objects(self) -> IDF:
        """Set overhang objects"""

        local_idf = IDF(StringIO(""))
        windows = self.idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]

        for window in windows:

            print(window.Name)
            overhang_dict = {
                "key": "SHADING:OVERHANG",
                "Name": window.Name + " overhang",
                "Window_or_Door_Name": window.Name,
                "Height_above_Window_or_Door": 0.1,
                "Tilt_Angle_from_WindowDoor": 90,
                "Left_extension_from_WindowDoor_Width": 0,
                "Right_extension_from_WindowDoor_Width": 0,
                "Depth": 0.5,
            }

            local_idf.newidfobject(**overhang_dict)

        return local_idf

    def add_overhang(self, has_overhang=False) -> IDF:
        """
        Set all overhang ojectcs
        """
        if has_overhang:
            self.idf = copy_idf_objects(self.idf, self.set_overhang_objects())

        return self.idf

    def save_idf(self, path):
        self.idf.saveas(path, lineendings="unix")
