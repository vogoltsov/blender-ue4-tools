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


def property_get_bool(object: bpy.types.Object, property: str) -> bool:
    return bool(object[property])


def property_set_int(object: bpy.types.Object, property: str, value: bool):
    object[property] = int(value)


def property_set_float(object: bpy.types.Object, property: str, value: bool):
    object[property] = float(value)


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
        # check if this is a compatible armature
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

        # visibility
        self.layout.label(text='Visibility Options')
        layout_visibility = self.layout.column()
        layout_visibility_row = layout_visibility.row()
        layout_visibility_row.use_property_split = False
        layout_visibility_row.prop(active_object, 'show_in_front', text='X Ray', toggle=True, icon='XRAY')
        layout_visibility_row.prop(active_object.data, 'show_names', text='Names', toggle=True, icon='TEXT')
        layout_visibility_row.prop(active_object.data, 'show_axes', text='Axes', toggle=True, icon='EMPTY_AXIS')
        layout_visibility_row = layout_visibility.row()
        layout_visibility_row.use_property_split = False
        layout_visibility_row.prop(active_object.data, 'layers', index=0, toggle=True, text='Deform', icon='BONE_DATA')
        layout_visibility_row.prop(active_object.data, 'layers', index=2, toggle=True, text='Helper', icon='POSE_HLT')

        # draw separator
        self.layout.separator()

        # constraints and ik
        self.layout.label(text='Constraints and IK')
        # toggle constraints on/off
        self.prop_toggle(active_object, 'Constraints_ON_OFF', text='Enable Constraints', icon='CONSTRAINT')
        # draw sublayout for ik
        self.prop_toggle(active_object, 'IKMAIN', text='Enable IK', icon='LINKED', icon_off='UNLINKED')
        layout_ik = self.layout.column()
        layout_ik.enabled = property_get_bool(active_object, 'IKMAIN')
        # draw sublayout for arms ik
        layout_ik_arms_root = layout_ik.box()
        self.prop_toggle(active_object, 'IKARMS', text='Enable Arms IK', layout=layout_ik_arms_root, icon='LINKED', icon_off='UNLINKED')
        layout_ik_arms = layout_ik_arms_root.column()
        layout_ik_arms.enabled = property_get_bool(active_object, 'IKARMS')
        layout_ik_arms_row = layout_ik_arms.row()
        layout_ik_arms_row.use_property_split = False
        if not property_get_bool(active_object, 'ShowAdvancedProps'):
            self.prop_toggle(active_object, 'Ik Arm R', text='Arm R', type='float', layout=layout_ik_arms_row, icon='LOCKED', icon_off='UNLOCKED')
            self.prop_toggle(active_object, 'IK Arm L', text='Arm L', type='float', layout=layout_ik_arms_row, icon='LOCKED', icon_off='UNLOCKED')
        else:
            layout_ik_arms_row.prop(active_object, '["Ik Arm R"]', text='Arm R', slider=True)
            layout_ik_arms_row.prop(active_object, '["IK Arm L"]', text='Arm L', slider=True)
        layout_ik_arms_row = layout_ik_arms.row()
        layout_ik_arms_row.use_property_split = False
        if not property_get_bool(active_object, 'ShowAdvancedProps'):
            self.prop_toggle(active_object, 'Ik hand R Lock', text='Hand R', type='float', layout=layout_ik_arms_row, icon='LOCKED', icon_off='UNLOCKED')
            self.prop_toggle(active_object, 'Ik Hand L Lock', text='Hand L', type='float', layout=layout_ik_arms_row, icon='LOCKED', icon_off='UNLOCKED')
        else:
            layout_ik_arms_row.prop(active_object, '["Ik hand R Lock"]', text='Hand R', slider=True)
            layout_ik_arms_row.prop(active_object, '["Ik Hand L Lock"]', text='Hand L', slider=True)
        # draw sublayout for legs ik
        layout_ik_legs_root = layout_ik.box()
        self.prop_toggle(active_object, 'IKLEGS', text='Enable Legs IK', layout=layout_ik_legs_root, icon='LINKED', icon_off='UNLINKED')
        layout_ik_legs = layout_ik_legs_root.column()
        layout_ik_legs.enabled = property_get_bool(active_object, 'IKLEGS')
        layout_ik_legs_row = layout_ik_legs.row()
        layout_ik_legs_row.use_property_split = False
        if not property_get_bool(active_object, 'ShowAdvancedProps'):
            self.prop_toggle(active_object, 'Ik Leg R', text='Leg R', type='float', layout=layout_ik_legs_row, icon='LOCKED', icon_off='UNLOCKED')
            self.prop_toggle(active_object, 'Ik Leg L', text='Leg L', type='float', layout=layout_ik_legs_row, icon='LOCKED', icon_off='UNLOCKED')
        else:
            layout_ik_legs_row.prop(active_object, '["Ik Leg R"]', text='Leg R', slider=True)
            layout_ik_legs_row.prop(active_object, '["Ik Leg L"]', text='Leg L', slider=True)
        layout_ik_legs_row = layout_ik_legs.row()
        layout_ik_legs_row.use_property_split = False
        if not property_get_bool(active_object, 'ShowAdvancedProps'):
            self.prop_toggle(active_object, 'Foot Lock R', text='Foot R', type='float', layout=layout_ik_legs_row, icon='LOCKED', icon_off='UNLOCKED')
            self.prop_toggle(active_object, 'Foot Lock L', text='Foot L', type='float', layout=layout_ik_legs_row, icon='LOCKED', icon_off='UNLOCKED')
        else:
            layout_ik_legs_row.prop(active_object, '["Foot Lock R"]', text='Foot R', slider=True)
            layout_ik_legs_row.prop(active_object, '["Foot Lock L"]', text='Foot L', slider=True)

        # rotation inheritance
        self.layout.label(text='Inherit Rotation')
        layout_rotation = self.layout.column()
        layout_rotation.use_property_split = False
        if not property_get_bool(active_object, 'ShowAdvancedProps'):
            self.prop_toggle(active_object, 'Head inherit Rotation', text='Head', type='float', layout=layout_rotation, icon='LOCKED', icon_off='UNLOCKED')
            self.prop_toggle(active_object, 'Arms inherit Rotation', text='Arms', type='float', layout=layout_rotation, icon='LOCKED', icon_off='UNLOCKED')
            self.prop_toggle(active_object, 'Waist Inherit Rotation', text='Waist', type='float', layout=layout_rotation, icon='LOCKED', icon_off='UNLOCKED')
        else:
            layout_rotation.prop(active_object, '["Head inherit Rotation"]', text='Head', slider=True)
            layout_rotation.prop(active_object, '["Arms inherit Rotation"]', text='Arms', slider=True)
            layout_rotation.prop(active_object, '["Waist Inherit Rotation"]', text='Waist', slider=True)

        # advanced view button
        self.layout.separator()
        self.prop_toggle(active_object, 'ShowAdvancedProps', text='Advanced View', icon='VISIBLE_IPO_ON', icon_off='VISIBLE_IPO_OFF')

    def prop_toggle(self, object: bpy.types.Object, property: str, type: str = 'int',
                    text: str = None, icon: str = 'NONE', icon_off=None,
                    layout: bpy.types.UILayout = None):

        operator: bpy.types.OperatorProperties
        operator = (layout or self.layout).operator(UE_TOOLS_ANIMATION_OT_toggle_rig_property.bl_idname,
                                                    text=text or property,
                                                    emboss=True, depress=property_get_bool(object, property),
                                                    icon=icon if property_get_bool(object, property) else (icon_off or icon))
        operator.property = property
        operator.type = type


class UE_TOOLS_ANIMATION_OT_toggle_rig_property(bpy.types.Operator):
    bl_idname = 'ue4_tools_animation.toggle_rig_property'
    bl_label = 'Toggle Rig property'

    property: bpy.props.StringProperty()
    type: bpy.props.StringProperty()

    def execute(self, context: bpy.types.Context):
        active_object = context.view_layer.objects.active
        # toggle property enabled state
        property_enabled = property_get_bool(active_object, self.property)
        property_enabled = not property_enabled
        if self.type == 'int':
            property_set_int(active_object, self.property, property_enabled)
        elif self.type == 'float':
            property_set_float(active_object, self.property, property_enabled)
        else:
            raise Exception('Unsupported toggle property type: %s' % self.type)
        # special callbacks for certain properties
        if self.property == 'IKMAIN':
            self.__toggle_ikmain(active_object, property_enabled)
        if self.property == 'IKARMS':
            self.__toggle_ikarms(active_object, property_enabled)
        if self.property == 'IKLEGS':
            self.__toggle_iklegs(active_object, property_enabled)
        return {'FINISHED'}

    def __toggle_ikmain(self, active_object: bpy.types.Object, property_enabled: bool):
        property_set_int(active_object, 'IKARMS', property_enabled)
        property_set_int(active_object, 'IKLEGS', property_enabled)
        self.__toggle_ikarms(active_object, property_enabled)
        self.__toggle_iklegs(active_object, property_enabled)

    def __toggle_ikarms(self, active_object: bpy.types.Object, property_enabled: bool):
        property_set_float(active_object, 'Ik Hand L Lock', property_enabled)
        property_set_float(active_object, 'Ik hand R Lock', property_enabled)
        property_set_float(active_object, 'IK Arm L', property_enabled)
        property_set_float(active_object, 'Ik Arm R', property_enabled)
        self.__set_bone_group_visibility(active_object, 'Ik_Arm_controls', property_enabled)
        self.__set_bone_group_visibility(active_object, 'roll_Arms_controls', property_enabled)

    def __toggle_iklegs(self, active_object: bpy.types.Object, property_enabled: bool):
        property_set_float(active_object, 'Foot Lock L', property_enabled)
        property_set_float(active_object, 'Foot Lock R', property_enabled)
        property_set_float(active_object, 'Ik Leg L', property_enabled)
        property_set_float(active_object, 'Ik Leg R', property_enabled)
        self.__set_bone_group_visibility(active_object, 'Ik_Leg_controls', property_enabled)
        self.__set_bone_group_visibility(active_object, 'roll_Legs_controls', property_enabled)

    def __set_bone_group_visibility(self, active_object: bpy.types.Object, bone_group_name: str, visible: bool):
        """ Updates visibility for all bones that are assigned a specified group."""
        bone_groups = active_object.pose.bone_groups
        bone_group_index = next((i for i in range(len(bone_groups)) if bone_groups[i].name == bone_group_name), None)
        if bone_group_index is None:
            self.report({'ERROR'}, 'Could not find bone group: %s' % bone_group_name)
            return
        for bone in (bone for bone in active_object.pose.bones if bone.bone_group_index == bone_group_index):
            # we can only set 'hide' property on EditBone
            active_object.data.bones[bone.name].hide = not visible


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
            self.report({'ERROR'}, 'No bones have corresponding vertex groups')
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
