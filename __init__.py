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

bl_info = {
    'name': 'Unreal Engine 4 Tools',
    'author': 'Vitaly Ogoltsov',
    'wiki_url': 'https://github.com/vogoltsov/blender-ue4-tools/wiki',
    'tracker_url': 'https://github.com/vogoltsov/blender-ue4-tools/issues',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'View 3D > Tool Shelf > Unreal Engine 4',
    'category': 'Game Development'
}


from . import auto_load

auto_load.init()

def register():
    auto_load.register()

def unregister():
    auto_load.unregister()
