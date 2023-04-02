#######################################
# BlenderのTextEditorに読み込んで使用する
#######################################

import bpy
import json
import os
import glob
import sys

def export_json(export_file):
  amt = bpy.data.objects['Armature']
  bone_info = {}

  bpy.ops.object.mode_set(mode='EDIT')

  for k in amt.pose.bones.keys():
    amt.pose.bones[k].rotation_mode = 'XYZ'
    dict = {}
    has_parent = amt.pose.bones[k].parent != None
    if has_parent:
      dict['parent'] = amt.pose.bones[k].parent.name
    else:
      dict['parent'] = None
    #
    dict['length'] = amt.pose.bones[k].length
    dict['z'] = amt.pose.bones[k].rotation_euler.z
    dict['y'] = amt.pose.bones[k].rotation_euler.y
    dict['x'] = amt.pose.bones[k].rotation_euler.x
    #
    is_disconnected_to_parent = has_parent and amt.pose.bones[k].parent.tail !=  amt.pose.bones[k].head
    dict['is_disconnected_to_parent'] = is_disconnected_to_parent
    if is_disconnected_to_parent:
      delta = {}
      delta['x'] = amt.pose.bones[k].head.x - amt.pose.bones[k].parent.tail.x
      delta['y'] = amt.pose.bones[k].head.y - amt.pose.bones[k].parent.tail.y
      delta['z'] = amt.pose.bones[k].head.z - amt.pose.bones[k].parent.tail.z
      dict['parent_offset'] = delta
    bone_info[k] = dict

  with open(export_file, 'wt') as f:
      json.dump(bone_info, f, indent=2)

  bpy.ops.object.mode_set(mode='POSE')

def import_json(import_file):
  if bpy.context.mode != 'OBJECT':
    raise Exception("Error: Current mode is not OBJECT mode")

  postures = None
  with open(import_file) as f:
    postures = json.load(f)
  if postures == None:
    raise Exception("Error: json load failed")

  amt = bpy.data.objects['Armature']
  bpy.ops.object.select_all(action='DESELECT')
  amt.select_set(True)
  bpy.context.view_layer.objects.active = amt

  bpy.ops.object.mode_set(mode='EDIT')

  for k in postures.keys():
    posture = postures[k]
    if not k in amt.data.edit_bones.keys():
      bone = amt.data.edit_bones.new(k)

  for k in amt.data.edit_bones.keys():
    if not k in postures.keys():
      continue
    posture = postures[k]
    has_parent = posture['parent'] != None
    if has_parent:
      amt.data.edit_bones[k].parent = amt.data.edit_bones[posture['parent']]

  bone_keys = amt.data.edit_bones.keys()
  bone_keys.sort(key=lambda k: len(amt.data.edit_bones[k].parent_recursive))

  for k in bone_keys:
    if not k in postures.keys():
      continue
    posture = postures[k]
    target_edit_bone = amt.data.edit_bones[k]
    
    has_parent = target_edit_bone.parent != None
    if has_parent:
      parent = target_edit_bone.parent
      if posture['is_disconnected_to_parent']:
        target_edit_bone.parent = None
        target_edit_bone.parent = parent
        
        offset = posture['parent_offset']
        
        target_edit_bone.head.x = parent.tail.x + offset['x']
        target_edit_bone.head.y = parent.tail.y + offset['y']
        target_edit_bone.head.z = parent.tail.z + offset['z']
        target_edit_bone.tail.x = target_edit_bone.head.x
        target_edit_bone.tail.y = target_edit_bone.head.y
        target_edit_bone.tail.z = target_edit_bone.head.z + posture['length']
      else:
        target_edit_bone.head.x = parent.tail.x
        target_edit_bone.head.y = parent.tail.y
        target_edit_bone.head.z = parent.tail.z
        target_edit_bone.tail.x = target_edit_bone.head.x
        target_edit_bone.tail.y = target_edit_bone.head.y
        target_edit_bone.tail.z = target_edit_bone.head.z + posture['length']
    target_edit_bone.roll = 0.
    target_edit_bone.length = posture['length']

  bpy.ops.object.mode_set(mode='POSE')

  for k in amt.pose.bones.keys():
    if not k in postures.keys():
      continue
    posture = postures[k]
    amt.pose.bones[k].rotation_mode = 'XYZ'
    amt.pose.bones[k].rotation_euler.z = posture['z']
    amt.pose.bones[k].rotation_euler.y = posture['y']
    amt.pose.bones[k].rotation_euler.x = posture['x']

def wait_paint(divided_files_folder):
  if bpy.context.mode != 'OBJECT':
    raise Exception("Error: Current mode is not OBJECT mode")
  files = []
  if os.path.exists(divided_files_folder):
    files = glob.glob(os.path.join(divided_files_folder,"*.stl"))
  for file in files:
    name = file.split(os.sep)[-1].split('.')[0]
    bpy.ops.import_mesh.stl(filepath=file)
  bpy.ops.object.select_all(action='DESELECT')
  for file in files:
    name = file.split(os.sep)[-1].split('.')[0]
    bpy.data.objects[name].select_set(True)
  bpy.data.objects['Armature'].select_set(True)
  bpy.context.view_layer.objects.active = bpy.data.objects['Armature']
  bpy.ops.object.parent_set(type='ARMATURE')
  bpy.ops.object.select_all(action='DESELECT')
  for file in files:
    name = file.split(os.sep)[-1].split('.')[0]
    obj = bpy.context.scene.objects[name]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    vg = obj.vertex_groups.new(name=name)
    index_list = []
    for vert in obj.data.vertices:
      index_list.append(vert.index)
    vg.add(index_list, 1.0, 'REPLACE')

# import_file = r'jsonファイルのフルパス'
# import_json(import_file)

# export_file = r'jsonファイルのフルパス'
# export_json(export_file)

#　divided_files_folder = r'分割したSTLファイルの配置先フォルダのフルパス'
#　wait_paint(divided_files_folder)