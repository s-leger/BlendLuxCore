import bpy
from bpy.props import PointerProperty, EnumProperty, StringProperty
from ..base import LuxCoreNodeTexture
from ... import utils
from ...utils.errorlog import LuxCoreErrorLog
from ...utils import node as utils_node


class LuxCoreNodeTexFresnel(bpy.types.Node, LuxCoreNodeTexture):
    bl_label = "Fresnel"
    bl_width_default = 200
    
    def change_input_type(self, context):
        self.inputs["Reflection Color"].enabled = self.input_type == "color"
        utils_node.force_viewport_update(self, context)

    input_type_items = [
        ("color", "Color", "Use custom color as input", 0),
        ("preset", "Preset", "Use a Preset fresnel texture as input", 1),
        ("nk", "File", "Use a fresnel texture file (.nk) as input", 2)
    ]
    input_type: EnumProperty(name="Type", description="Input Type", items=input_type_items, default="preset",
                             update=change_input_type)

    file_type_items = [
        ("luxpop", "Lux Pop", "Use Luxpop format for NK data file", 0),
        ("sopra", "Sopra", "Use Sopra format for NK data file", 1),
    ]
    file_type: EnumProperty(update=utils_node.force_viewport_update, name="FileType", description="File Type", items=file_type_items, default="luxpop")

    preset_items = [
                ("amorphous_carbon", "Amorphous carbon", "", 0),
                ("copper", "Copper", "", 1),
                ("gold", "Gold", "", 2),
                ("silver", "Silver", "", 3),
                ("aluminium", "Aluminium", "", 4),
    ]
    preset: EnumProperty(update=utils_node.force_viewport_update, name="Preset", description="NK data presets", items=preset_items,
                         default="aluminium")

    filepath: StringProperty(update=utils_node.force_viewport_update, name="Nk File", description="Nk file path", subtype="FILE_PATH")

    def init(self, context):
        self.add_input("LuxCoreSocketColor", "Reflection Color", (0.7, 0.7, 0.7))
        self.inputs["Reflection Color"].enabled = False
        self.outputs.new("LuxCoreSocketFresnel", "Fresnel")

    def draw_buttons(self, context, layout):
        layout.prop(self, "input_type", expand=True)
        
        if self.input_type == "preset":
            layout.prop(self, "preset")

        if self.input_type == "nk":
            layout.prop(self, "file_type", expand=True)            
            layout.prop(self, "filepath")

    def sub_export(self, exporter, depsgraph, props, luxcore_name=None, output_socket=None):
        if self.input_type == "color":
            definitions = {
                "type": "fresnelcolor",
                "kr": self.inputs["Reflection Color"].export(exporter, depsgraph, props),
            }
        elif self.input_type == "preset":
            definitions = {
                "type": "fresnelpreset",
                "name": self.preset,
            }
        else:
            #Fresnel data file
            try:
                filepath = utils.get_abspath(self.filepath, must_exist=True, must_be_existing_file=True)
            except OSError as error:
                # Make the error message more precise
                raise OSError('Could not find fresnel data at path "%s" (%s)'
                              % (self.filepath, error))

            definitions = {
                "file": filepath,
            }

            if self.input_type == "nk":
                if self.file_type == "luxpop":
                    definitions["type"] = "fresnelluxpop"
                else:
                    definitions["type"] = "fresnelsopra"                    
            else:
                # Fallback, file not found
                error = 'Could not find .nk file at path "%s"' % self.filepath
                msg = 'Node "%s" in tree "%s": %s' % (self.name, self.id_data.name, error)
                LuxCoreErrorLog.add_warning(msg)

                definitions = {
                    "type": "fresnelcolor",
                    "kr": [0, 0, 0],
                }
        
        return self.create_props(props, definitions, luxcore_name)
