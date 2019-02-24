###
# Blender UE4 Tools
# Copyright (C) 2019 Vitaly Ogoltsov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.###
###

import bpy


class UE4_TOOLS_SCENE_prefs(bpy.types.PropertyGroup):
    """Scene tools preferences."""
    pass


class UE4_TOOLS_SCENE_PT_main(bpy.types.Panel):
    """Scene tools main panel."""
    bl_label = 'Scene'
    bl_region_type = 'UI'
    bl_category = 'Unreal Engine 4'
    bl_space_type = 'VIEW_3D'

    def draw(self, context: bpy.types.Context):
        layout: bpy.types.UILayout = self.layout
        layout.use_property_split = True

        layout.operator(UE4_TOOLS_SCENE_OT_set_ue4_scale.bl_idname)


class UE4_TOOLS_SCENE_OT_set_ue4_scale(bpy.types.Operator):
    bl_idname = 'ue4_tools_scene.set_ue4_scale'
    bl_label = 'Set UE4 Scale'
    bl_description = 'Set scene scale in Blender to match units in Unreal Engine 4 (1 unit = 1 cm).'

    scale_selected: bpy.props.BoolProperty(
        name='Scale selected objects',
        description='If set to True, currently selected objects will also be scaled.',
        default=True,
        options={'SKIP_SAVE'}
    )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context):
        scene: bpy.types.Scene = context.scene
        # update scene unit settings
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = 0.01
        # update view space clipping settings
        context.space_data.clip_start = 0.1
        context.space_data.clip_end = 1000000.0
        # scale selected objects if needed
        if self.scale_selected:
            bpy.ops.transform.resize(value=(100, 100, 100), center_override=(0, 0, 0))
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # return success
        return {'FINISHED'}


def register():
    bpy.types.Scene.ue4_tools_scene = bpy.props.PointerProperty(type=UE4_TOOLS_SCENE_prefs)
