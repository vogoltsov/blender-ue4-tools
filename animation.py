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


class UE4_TOOLS_ANIMATION_prefs(bpy.types.PropertyGroup):
    """Animation tools preferences."""
    pass


class UE4_TOOLS_ANIMATION_PT_main(bpy.types.Panel):
    """Animation tools main panel."""
    bl_label = 'Animation'
    bl_region_type = 'UI'
    bl_category = 'Unreal Engine 4'
    bl_space_type = 'VIEW_3D'

    def draw(self, context: bpy.types.Context):
        layout: bpy.types.UILayout = self.layout
        layout.use_property_split = True

        if context.mode == 'OBJECT':
            layout.operator(UE4_TOOLS_ANIMATION_OT_add_ue4_rig.bl_idname)


class UE4_TOOLS_ANIMATION_OT_add_ue4_rig(bpy.types.Operator):
    bl_idname = 'ue4_tools_animation.add_ue4_rig'
    bl_label = 'Add UE4 Rig'
    bl_description = 'Add rig based on UE4_Mannequin_Skeleton to current scene.'

    rig_name: bpy.props.StringProperty(
        name='Rig name',
        description='Customize rig name to be used',
        default=''
    )
    add_mesh: bpy.props.BoolProperty(
        name='Add UE4 mannequin mesh?',
        description='If set to True, UE4 default mannequin mesh will also be added to current scene.',
        default=False
    )
    use_mobile: bpy.props.BoolProperty(
        name='Use mobile version?',
        description='If set to True, mobile versions of skeleton and mannequin will be used instead.',
        default=False
    )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        if context.view_layer.objects.active is not None:
            self.rig_name = context.view_layer.objects.active.name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # check if rig name has been supplied by user
        if len(self.rig_name) == 0:
            self.report({'ERROR'}, 'Please, set a valid rig name')
            return {'CANCELLED'}
        # validate skeleton name
        skeleton_name = self.rig_name + '_Skeleton'
        if bpy.data.objects.get(skeleton_name) is not None:
            self.report({'ERROR'}, 'Object with name "%s" already exists in the scene.' % skeleton_name)
            return {'CANCELLED'}
        # validate mesh name
        mesh_name = self.rig_name + '_Mesh'
        if self.add_mesh and bpy.data.objects.get(mesh_name) is not None:
            self.report({'ERROR'}, 'Object with name "%s" already exists in the scene.' % mesh_name)
            return {'CANCELLED'}
        # get addon location
        import os
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(addon_dir, 'UE4_Mannequinn_Template.blend')
        template_object_path = os.path.join(template_path, 'Object')
        if not self.use_mobile:
            template_skeleton_name = 'UE4_Mannequin_Skeleton'
            template_mesh_name = 'SK_Mannequin'
        else:
            template_skeleton_name = 'UE4_Mannequin_Skeleton_Mobile'
            template_mesh_name = 'SK_Mannequin_Mobile'
        # import objects from template
        if self.add_mesh:
            bpy.ops.wm.link(filepath=os.path.join(template_object_path, template_mesh_name),
                            directory=template_object_path,
                            filename=template_mesh_name,
                            link=True,
                            relative_path=True,
                            autoselect=True,
                            active_collection=True)
        else:
            bpy.ops.wm.link(filepath=os.path.join(template_object_path, template_skeleton_name),
                            directory=template_object_path,
                            filename=template_skeleton_name,
                            link=True,
                            relative_path=True,
                            autoselect=True,
                            active_collection=True)
        # make linked objects local
        bpy.ops.object.make_local(type='ALL')
        # locate and setup skeleton
        skeleton: bpy.types.Object = bpy.data.objects[template_skeleton_name]
        skeleton.select_set(True)
        skeleton.name = skeleton_name
        # locate and setup mesh
        if self.add_mesh:
            mesh: bpy.types.Object = bpy.data.objects[template_mesh_name]
            mesh.select_set(True)
            mesh.name = mesh_name
            bpy.ops.object.make_local(type='ALL')
        # return success
        return {'FINISHED'}


def register():
    bpy.types.Scene.ue4_tools_animation = bpy.props.PointerProperty(type=UE4_TOOLS_ANIMATION_prefs)
