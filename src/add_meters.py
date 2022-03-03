from eppy.modeleditor import IDF
import os

# To be appended to the IDF
meters = '''Output:Meter,Electricity:Facility,Hourly;
            Output:Meter,Gas:Facility,Hourly;
            Output:Meter,InteriorLights:Electricity,Hourly;
            Output:Meter,ExteriorLights:Electricity,Hourly;
            Output:Meter,InteriorEquipment:Electricity,Hourly;
            Output:Meter,ExteriorEquipment:Electricity,Hourly;
            Output:Meter,Fans:Electricity,Hourly;
            Output:Meter,Pumps:Electricity,Hourly;
            Output:Meter,Heating:Electricity,Hourly;
            Output:Meter,Cooling:Electricity,Hourly;
            Output:Meter,HeatRejection:Electricity,Hourly;
            Output:Meter,Humidifier:Electricity,Hourly;
            Output:Meter,HeatRecovery:Electricity,Hourly;
            Output:Meter,DHW:Electricity,Hourly;
            Output:Meter,Cogeneration:Electricity,Hourly;
            Output:Meter,Refrigeration:Electricity,Hourly;
            Output:Meter,WaterSystems:Electricity,Hourly;

            Output:Meter,InteriorLights:Gas,Hourly;
            Output:Meter,ExteriorLights:Gas,Hourly;
            Output:Meter,InteriorEquipment:Gas,Hourly;
            Output:Meter,ExteriorEquipment:Gas,Hourly;
            Output:Meter,Fans:Gas,Hourly;
            Output:Meter,Pumps:Gas,Hourly;
            Output:Meter,Heating:Gas,Hourly;
            Output:Meter,Cooling:Gas,Hourly;
            Output:Meter,HeatRejection:Gas,Hourly;
            Output:Meter,Humidifier:Gas,Hourly;
            Output:Meter,HeatRecovery:Gas,Hourly;
            Output:Meter,DHW:Gas,Hourly;
            Output:Meter,Cogeneration:Gas,Hourly;
            Output:Meter,Refrigeration:Gas,Hourly;
            Output:Meter,WaterSystems:Gas,Hourly;
'''

# Set the IDD
IDF.setiddname('../resources/V9-5-0-Energy+.idd')

for filename in os.listdir('../ep_input/input'):

      # The path to the IDF
      idfPath = f'../ep_input/input/{filename}'

      # Read the IDF
      idf = IDF(idfPath)

      # Append Output:Meter objects to the IDF if they are not already included
      with open(idfPath, 'a') as file:
            if 'OUTPUT:METER' not in idf.idfobjects:
                  file.write(meters)

      # Read the IDF
      idf = IDF(idfPath)

      # Remove Output:Variable objects
      idf.idfobjects['OUTPUT:VARIABLE'].clear()

      # Save the IDF
      idf.save()
