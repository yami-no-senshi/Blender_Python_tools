import bpy
import bmesh
from mathutils import Vector

# https://atu-1.gitbooks.io/mirror-introduction/content/body/chapter_03/09_Use_Coordinate_Transformation_2.html
# https://blender.stackexchange.com/questions/284222/get-view-and-perspective-matrices-of-the-current-3d-viewport-not-camera
# https://blender.stackexchange.com/questions/16472/how-can-i-get-the-cameras-projection-matrix/50507#50507

def delete_all():
#  for item in bpy.context.scene.objects:
#    bpy.context.scene.objects.unlink(item)

  for item in bpy.data.objects:
    bpy.data.objects.remove(item)

  for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)

  for item in bpy.data.materials:
    bpy.data.materials.remove(item)

def project_3d_point(camera: bpy.types.Object,
                     p: Vector,
                     render: bpy.types.RenderSettings = bpy.context.scene.render) -> Vector:
    """
    Given a camera and its projection matrix M;
    given p, a 3d point to project:

    Compute P’ = M * P
    P’= (x’, y’, z’, w')

    Ignore z'
    Normalize in:
    x’’ = x’ / w’
    y’’ = y’ / w’

    x’’ is the screen coordinate in normalised range -1 (left) +1 (right)
    y’’ is the screen coordinate in  normalised range -1 (bottom) +1 (top)

    :param camera: The camera for which we want the projection
    :param p: The 3D point to project
    :param render: The render settings associated to the scene.
    :return: The 2D projected point in normalized range [-1, 1] (left to right, bottom to top)
    """

    if camera.type != 'CAMERA':
        raise Exception("Object {} is not a camera.".format(camera.name))

    if len(p) != 3:
        raise Exception("Vector {} is not three-dimensional".format(p))

    # Get the two components to calculate M
    modelview_matrix = camera.matrix_world.inverted()
    projection_matrix = camera.calc_matrix_camera(
        bpy.data.scenes["Scene"].view_layers["ViewLayer"].depsgraph,
        x = render.resolution_x,
        y = render.resolution_y,
        scale_x = render.pixel_aspect_x,
        scale_y = render.pixel_aspect_y,
    )

    # print(projection_matrix * modelview_matrix)

    # Compute P’ = M * P
    p1 = projection_matrix @ modelview_matrix @ Vector((p.x, p.y, p.z, 1))

    # Normalize in: x’’ = x’ / w’, y’’ = y’ / w’
    p2 = Vector(((p1.x/p1.w, p1.y/p1.w)))

    return p2


def get_2D_LeftTopRightBottom(obj):

  # 選択中の頂点のローカル座標を取得する
  bm = bmesh.from_edit_mesh(obj.data)
  vert_local = [
    Vector((v.co[0], v.co[1], v.co[2], 1.0))
    for v in bm.verts if v.select
  ]
  # ローカル座標からグローバル座標への変換
  vert_global = [obj.matrix_world @ v for v in vert_local]

  # 3次元座標のベクター形式に変換
  vs = [
    Vector((v[0], v[1], v[2]))
    for v in vert_global
  ]

  camera = bpy.data.objects['Camera']  # or bpy.context.active_object
  render = bpy.context.scene.render

  Left   = render.resolution_x-1
  Top    = render.resolution_y-1
  Right  = 0
  Bottom = 0

  for P in vs:
#    print("Projecting point {} for camera '{:s}' into resolution {:d}x{:d}..."
#        .format(P, camera.name, render.resolution_x, render.resolution_y))

    proj_p = project_3d_point(camera=camera, p=P, render=render)
#    print("Projected point (homogeneous coords): {}.".format(proj_p))

    proj_p_pixels = Vector(((render.resolution_x-1) * (proj_p.x + 1) / 2, (render.resolution_y - 1) * (proj_p.y - 1) / (-2)))
#    print("Projected point (pixel coords): {}.".format(proj_p_pixels))

    Left   = min(Left,   proj_p_pixels.x)
    Top    = min(Top,    proj_p_pixels.y)
    Right  = max(Right,  proj_p_pixels.x)
    Bottom = max(Bottom, proj_p_pixels.y)


  Left   = min(Left,   render.resolution_x-1)
  Top    = min(Top,    render.resolution_y-1)
  Right  = min(Right,  render.resolution_x-1)
  Bottom = min(Bottom, render.resolution_y-1)

  print("(", Left,  ",",  Top, ")")
  print("(", Right, ",",  Top, ")")
  print("(", Left,  ",",  Bottom, ")")
  print("(", Right, ",",  Bottom, ")")

  print("Done.")


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

  for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_perspective = 'CAMERA'

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

  get_2D_LeftTopRightBottom(obj)

#  bpy.context.scene.render.image_settings.file_format = 'PNG'
#  bpy.ops.render.render()
#  bpy.data.images['Render Result'].save_render( filepath = 'hoge.png')
