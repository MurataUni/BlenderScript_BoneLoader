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
    location = {}
    location['x'] = amt.pose.bones[k].location.x
    location['y'] = amt.pose.bones[k].location.y
    location['z'] = amt.pose.bones[k].location.z
    dict['location'] = location
    #
    if amt.pose.bones[k].scale[0] != 1.0:
        dict['scale'] = amt.pose.bones[k].scale[0]
    #
    bone_info[k] = dict

  with open(export_file, 'wt') as f:
      json.dump(bone_info, f, indent=2)

  bpy.ops.object.mode_set(mode='OBJECT')

def import_postures(import_file):
  postures = None
  with open(import_file) as f:
    postures = json.load(f)
  if postures == None:
    raise Exception("Error: json load failed")
  return postures

def load_bones(json_postures, divided_files_folder):
  if bpy.context.mode != 'OBJECT':
    raise Exception("Error: Current mode is not OBJECT mode")

  postures = import_postures(json_postures)

  amt = bpy.data.objects['Armature']
  bpy.ops.object.select_all(action='DESELECT')
  amt.select_set(True)
  bpy.context.view_layer.objects.active = amt

  bpy.ops.object.mode_set(mode='EDIT')

  for k in postures.keys():
    posture = postures[k]
    if not k in amt.data.edit_bones.keys():
      bone_new = amt.data.edit_bones.new(k)
      bone_new.roll = 0.
      bone_new.length = posture['length']
  
  if divided_files_folder != None:
    bpy.ops.object.mode_set(mode='OBJECT')
    wait_paint(divided_files_folder)
    amt = bpy.data.objects['Armature']
    bpy.ops.object.select_all(action='DESELECT')
    amt.select_set(True)
    bpy.context.view_layer.objects.active = amt
    bpy.ops.object.mode_set(mode='EDIT')

  for k in amt.data.edit_bones.keys():
    if not k in postures.keys():
      continue
    posture = postures[k]
    has_parent = posture['parent'] != None
    if has_parent:
      amt.data.edit_bones[k].parent = amt.data.edit_bones[posture['parent']]

  bone_keys = amt.data.edit_bones.keys()
  bone_keys.sort(key=lambda k: len(amt.data.edit_bones[k].parent_recursive))

  bpy.ops.object.mode_set(mode='POSE')

  for k in amt.pose.bones.keys():
    if not k in postures.keys():
      continue
    posture = postures[k]
    amt.pose.bones[k].rotation_mode = 'XYZ'
    amt.pose.bones[k].rotation_euler.z = posture['z']
    amt.pose.bones[k].rotation_euler.y = posture['y']
    amt.pose.bones[k].rotation_euler.x = posture['x']
    if 'location' in posture:
      location = posture['location']
      amt.pose.bones[k].location[0] = location['x']
      amt.pose.bones[k].location[1] = location['y']
      amt.pose.bones[k].location[2] = location['z']
    if 'scale' in posture:
      amt.pose.bones[k].scale = [posture['scale'], posture['scale'], posture['scale']]
    
  bpy.ops.object.mode_set(mode='OBJECT')

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
    
  bpy.ops.object.mode_set(mode='OBJECT')

posture_json = r'インポートするjsonファイルのフルパス'
folder_parts = r'パーツのフォルダのフルパス'
load_bones(posture_json, folder_parts)

#export_json(r'出力先のjsonファイルのフルパス')
