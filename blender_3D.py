import bpy
import bmesh
from mathutils import Vector

# https://atu-1.gitbooks.io/mirror-introduction/content/body/chapter_03/09_Use_Coordinate_Transformation_2.html
# https://blender.stackexchange.com/questions/284222/get-view-and-perspective-matrices-of-the-current-3d-viewport-not-camera
def delete_all():
#  for item in bpy.context.scene.objects:
#    bpy.context.scene.objects.unlink(item)

  for item in bpy.data.objects:
    bpy.data.objects.remove(item)

  for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)

  for item in bpy.data.materials:
    bpy.data.materials.remove(item)

# 射影座標からリージョン座標へ変換する関数
def viewport_transform(region, v):
    wh = region.width / 2.0
    hh = region.height / 2.0
    print("v : ", v.x, v.y, v.z, v.w)

    if v.w == 0:
      a = wh
      b = hh
    else:
      a = wh + wh * v.x / v.w
      b = hh + hh * v.y / v.w

    return Vector((a, b))


# 指定したエリア、リージョン、スペースを取得する関数
def get_region_and_space(area_type, region_type, space_type):
    region = None
    area = None
    space = None

    # 指定されたエリアを取得する
    for a in bpy.context.screen.areas:
        if a.type == area_type:
            area = a
            break
    else:
        return (None, None, None)
    # 指定されたリージョンを取得する
    for r in area.regions:
        if r.type == region_type:
            region = r
            break
    # 指定されたスペースを取得する
    for s in area.spaces:
        if s.type == space_type:
            space = s
            break

    return (area, region, space)



if __name__ == "__main__":
  delete_all()

  # 
  Target_Mesh_Name = 'Cube_Mesh'
  Target_Obj_Name = 'Cube'

  camera_data = bpy.data.cameras.new(name="Camera")
  #if camera_data is None:
  #  return {"CANCELLED"}
  my_camera = bpy.data.objects.new("Camera", camera_data)
  #if my_camera is None:
  #  return {"CANCELLED"}

  bpy.context.scene.collection.objects.link(my_camera)
  bpy.context.scene.camera = my_camera

  bpy.context.view_layer.objects.active = my_camera
  bpy.context.object.location[0] = 20
  bpy.context.object.rotation_euler[0] = -4.5
  bpy.context.object.rotation_euler[1] = 0.26
  bpy.context.object.rotation_euler[2] = 1.6
  #bpy.context.scene.camera = bpy.data.objects["Camera"]
  #bpy.ops.view3d.camera_to_view()

  for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_perspective = 'CAMERA'

#        area.spaces.active.region_3d.view_perspective = my_camera
#        bpy.ops.view3d.camera_to_view()
        #bpy.ops.view3d.object_as_camera()
#        override = bpy.context.copy()
#        override['area'] = area
#        bpy.ops.view3d.object_as_camera(override)
#        break

  #以下のtypeのぶぶんには、TOP,BOTTOM,FRONT,BACK,RIGHT,LEFTのいずれかが入ります。
  #bpy.ops.view3d.view_axis(type = 'TOP',align_active = True)

  #立方体を形成する頂点と面を定義する
  verts = [(0,0,0),(0,5,3),(5,5,0),(5,0,0),(0,0,5),(0,5,5),(5,5,5),(5,0,5)]
  faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
 
  #メッシュを定義する
  mesh = bpy.data.meshes.new(Target_Mesh_Name)
  #頂点と面のデータからメッシュを生成する
  mesh.from_pydata(verts,[],faces)
  mesh.update(calc_edges=True)

  #メッシュのデータからオブジェクトを定義する
  obj = bpy.data.objects.new(Target_Obj_Name, mesh)   
  #オブジェクトの生成場所をカーソルに指定する
  obj.location = bpy.context.scene.cursor.location
  #オブジェクトをシーンにリンク(表示)させる
  bpy.context.scene.collection.objects.link(obj)

  obj = bpy.data.objects[Target_Obj_Name]
  obj.select_set(True)

  bpy.context.view_layer.objects.active = obj

  bpy.ops.object.mode_set(mode="EDIT", toggle=False)

  # 3Dビューエリアのウィンドウリージョンのリージョンとスペースを取得
  (_, region, space) = get_region_and_space('VIEW_3D', 'WINDOW', 'VIEW_3D')

  print(region, space)
  if space is not None:
    # 選択中の頂点のローカル座標を取得する
    obj = bpy.context.active_object
    bm = bmesh.from_edit_mesh(obj.data)
    vert_local = [
      Vector((v.co[0], v.co[1], v.co[2], 1.0))
      for v in bm.verts if v.select
    ]
    print("vert_local", len(vert_local))
#    for i in range(len(vert_local)):
#      print(vert_local[i])

    #bm.verts.ensure_lookup_table()
    #for i in range(len( bm.verts)):
    #  print("bm.verts", bm.verts[i].co)

    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    # ローカル座標からグローバル座標への変換
    vert_global = [obj.matrix_world @ v for v in vert_local]
    # グローバル座標から射影座標への変換
    projection_matrix = bpy.context.scene.camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(), x=1920, y=1080)
    print(projection_matrix)
    print(space.region_3d.perspective_matrix)
    vert_perspective = [
#      space.region_3d.perspective_matrix @ v for v in vert_global
       projection_matrix @ v for v in vert_global
    ]
    for v in vert_global:
      print("global : ", v)
    for v in vert_perspective:
      print("perspective : ", v)
    # 射影座標からリージョン座標への変換
    vert_region = [viewport_transform(region, v) for v in vert_perspective]
    # 座標を出力
    for l, g, p, r in zip(vert_local, vert_global,
                          vert_perspective, vert_region):
      print("==========")
      print("local: " + repr(l))
      print("global: " + repr(g))
      print("perspective: " + repr(p))
      print("region: " + repr(r))
