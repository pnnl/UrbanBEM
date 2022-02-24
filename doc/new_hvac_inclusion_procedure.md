# New OSSTD HVAC type inclusion procedure

Things to modify/add (ordered by execution sequence):
1. Evaluate what idf object types would be needed for OSSTD function call. Edit value of key `idf_obj_types_for_osstd_use` in `hvac_settings.json`
2. Edit `../resources/exc_osstd_hvac_objtypes_meta.json`. Excluded idf object types do not need to cover non-needed objects in the input idf to the HVAC processor.
3. After collecting OSSTD added HVAC objects, if clean-up (e.g. renaming certain objects) is needed, do it in `clean_up_save_add_osstd_output`
4. After collecting OSSTD added HVAC objects, if more objects are needed (e.g. adding thermostat), do it in `add_misc_hvac_objs`
5. Schedule replacements should be added to `../resources/replace_osstd_hvac_schedules_refs.json`
6. After testing. Summarize info in doc `Object_deltas_for_osstd_hvac_call.md`

NOTE: polymorphism will be needed if too many different things need to be done for different HVAC types in steps 3 and 4.