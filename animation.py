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
        # draw different panel content based on current active object
        active_object: bpy.types.Object = context.view_layer.objects.active
        if active_object is not None:
            if active_object.type == 'ARMATURE':
                self.__draw_armature(context, active_object)

    def __draw_armature(self, context: bpy.types.Context, active_object: bpy.types.Object):
        if context.mode == 'OBJECT':
            self.__draw_armature_in_object_mode(context, active_object)
        elif context.mode == 'POSE':
            self.__draw_armature_in_pose_mode(context, active_object)

    def __draw_armature_in_object_mode(self, context: bpy.types.Context, active_object: bpy.types.Object):
        if 'DeformBones' in active_object.pose.bone_groups:
            self.layout.label(text='TODO', icon='SCRIPT')
        else:
            self.layout.label(text='Incompatible armature', icon='ERROR')
            self.layout.label(text='Selected armature must')
            self.layout.label(text='have a bone group called')
            self.layout.label(text='\'DeformBones\' to be')
            self.layout.label(text=' used with this addon.')
            self.layout.operator(UE_TOOLS_ANIMATION_OT_add_deform_bones_group.bl_idname)
        pass

    def __draw_armature_in_pose_mode(self, context: bpy.types.Context, active_object: bpy.types.Object):
        if 'DeformBones' not in active_object.pose.bone_groups:
            self.layout.label(text='Incompatible armature', icon='ERROR')
            self.layout.label(text='Selected armature must')
            self.layout.label(text='have a bone group called')
            self.layout.label(text='\'DeformBones\' to be')
            self.layout.label(text=' used with this addon.')
            self.layout.label(text='Select the bones to be')
            self.layout.label(text='included in FBX export')
            self.layout.label(text='and hit the button below.')
            self.layout.operator(UE_TOOLS_ANIMATION_OT_set_deform_bones_group.bl_idname)
            pass
        else:
            self.layout.label(text='TODO', icon='SCRIPT')
            pass


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


class UE_TOOLS_ANIMATION_OT_add_deform_bones_group(bpy.types.Operator):
    bl_idname = 'ue4_tools_animation.add_deform_bones_group'
    bl_label = 'Auto-create deform bones'
    bl_description = 'Add \'DeformBones\' bone group to current armature to be compatible with UE4 Tools.'

    def execute(self, context: bpy.types.Context):
        armature_object: bpy.types.Armature = context.view_layer.objects.active
        # find all vertex groups with non-zero weights
        vertex_group_names = self.__get_vertex_group_names(armature_object)
        if len(vertex_group_names) == 0:
            self.report({'ERROR'}, 'Could not find any matching vertex groups in child meshes')
            return {'CANCELLED'}
        # select only armature and enter pose mode
        bpy.ops.object.select_all(action='DESELECT')
        armature_object.select_set(True)
        context.view_layer.objects.active = armature_object
        bpy.ops.object.mode_set(mode='POSE')
        # store visible bone layer visibility so it can be restored later
        # and set all bone layers visible
        visible_bone_layers = [len(armature_object.data.layers)]
        for n in range(0, len(armature_object.data.layers)):
            visible_bone_layers[n] = armature_object.data.layers[n]
            armature_object.data.layers[n] = True
        # select all bones for which there is a vertex group
        # in any of the child meshes with the same name
        bpy.ops.pose.select_all(action='DESELECT')
        for b in armature_object.pose.bones:
            if b.name in vertex_group_names:
                b.bone.select = True
        # create and assign 'DeformBones' group
        if len(context.selected_pose_bones) > 0:
            new_group_index: int = len(armature_object.pose.bone_groups)
            bpy.ops.pose.group_assign(new_group_index)
            armature_object.pose.bone_groups[new_group_index].name = 'DeformBones'
        else:
            self.report({'ERROR'}, "Any bones have vertex associated")
        # restore layer visibility
        for n in range(0, len(armature_object.data.layers)):
            armature_object.data.layers[n] = visible_bone_layers[n]
        # return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # return success
        return {'FINISHED'}

    def __get_vertex_group_names(self, armature_object: bpy.types.Object):
        """Retrieves vertex group names from children meshes.

        The operator iterates through all the bones and selects those
        for which there is vertex group with the same name.
        """
        non_zero_vertex_groups = set()
        for child in armature_object.children:
            if child.type == 'MESH':
                for vertex in child.data.vertices:
                    for vertex_group in vertex.groups:
                        if round(vertex_group.weight, 4) > .0000:
                            non_zero_vertex_groups.add(vertex_group.group)
        non_zero_vertex_group_names = set()
        for child in armature_object.children:
            if child.type == 'MESH':
                for vertex_group in child.vertex_groups:
                    if vertex_group.index in non_zero_vertex_groups:
                        non_zero_vertex_group_names.add(vertex_group.name)
        return non_zero_vertex_group_names


class UE_TOOLS_ANIMATION_OT_set_deform_bones_group(bpy.types.Operator):
    bl_idname = 'ue4_tools_animation.set_deform_bones_group'
    bl_label = 'Set deform bones'
    bl_description = 'Create \'DeformBones\' bone group based on currently selected bones.'

    def execute(self, context: bpy.types.Context):
        armature_object = context.view_layer.objects.active
        if len(context.selected_pose_bones) > 0:
            new_group_index: int = len(armature_object.pose.bone_groups)
            bpy.ops.pose.group_assign(new_group_index)
            armature_object.pose.bone_groups[new_group_index].name = 'DeformBones'
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "You have to select bones first.")
            return {'CANCELLED'}


def register():
    bpy.types.Scene.ue4_tools_animation = bpy.props.PointerProperty(type=UE4_TOOLS_ANIMATION_prefs)
