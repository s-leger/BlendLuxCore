import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty
from ..base import LuxCoreNodeTexture
from ... import utils
from ...utils import node as utils_node

class LuxCoreNodeTexMarble(bpy.types.Node, LuxCoreNodeTexture):
    bl_label = "Marble"
    bl_width_default = 200


    octaves: IntProperty(update=utils_node.force_viewport_update, name="Octaves", default=8, min=1, max=29)
    roughness: FloatProperty(update=utils_node.force_viewport_update, name="Roughness", default=0.5, min=0, max=1)
    scale: FloatProperty(update=utils_node.force_viewport_update, name="Scale", default=1.0, min=0)
    variation: FloatProperty(update=utils_node.force_viewport_update, name="Variation", default=0.2, min=0, max=1)
    
    def init(self, context):
        self.add_input("LuxCoreSocketMapping3D", "3D Mapping")

        self.outputs.new("LuxCoreSocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "octaves")
        layout.prop(self, "roughness")
        layout.prop(self, "scale")
        layout.prop(self, "variation")
    
    def sub_export(self, exporter, depsgraph, props, luxcore_name=None, output_socket=None):
        mapping_type, uvindex, transformation = self.inputs["3D Mapping"].export(exporter, depsgraph, props)
       
        definitions = {
            "type": "marble",
            "octaves": self.octaves,
            "roughness": self.roughness,
            "scale": self.scale,
            "variation": self.variation,
            # Mapping
            "mapping.type": mapping_type,
            "mapping.transformation": utils.matrix_to_list(transformation),
        }

        if mapping_type == "uvmapping3d":
            definitions["mapping.uvindex"] = uvindex

        return self.create_props(props, definitions, luxcore_name)
