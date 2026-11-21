#!/usr/bin/env python3
"""Render a low-resolution, eight-direction character sprite prototype in Blender.

Run with Blender's Python, not the system Python:
  blender --background --python render_npc_sprite.py -- <output-dir> <name>

This first pass generates an atlas for art review. It intentionally does not
claim to be a complete Infinity Engine BAM exporter or production sprite rig.
"""

import bpy
import math
import os
import sys
from mathutils import Vector


def arguments():
	args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
	if len(args) != 2:
		raise SystemExit("expected: <output-dir> <character-name>")
	return args


def material(name, color, roughness=0.82):
	mat = bpy.data.materials.new(name)
	mat.diffuse_color = (*color, 1.0)
	mat.use_nodes = True
	shader = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
	shader.inputs["Base Color"].default_value = (*color, 1.0)
	shader.inputs["Roughness"].default_value = roughness
	return mat


def add_sphere(name, location, scale, mat, segments=10, rings=6):
	bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=location)
	obj = bpy.context.object
	obj.name = name
	obj.scale = scale
	obj.data.materials.append(mat)
	for face in obj.data.polygons:
		face.use_smooth = False
	return obj


def add_cone(name, location, radius_bottom, radius_top, depth, mat, vertices=8):
	bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius_bottom, radius2=radius_top,
		depth=depth, location=location)
	obj = bpy.context.object
	obj.name = name
	obj.data.materials.append(mat)
	return obj


def add_cylinder(name, location, radius, depth, mat, vertices=8):
	bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
	obj = bpy.context.object
	obj.name = name
	obj.data.materials.append(mat)
	return obj


def parent_at(obj, pivot, name):
	empty = bpy.data.objects.new(name, None)
	bpy.context.collection.objects.link(empty)
	empty.location = pivot
	obj.parent = empty
	obj.location = tuple(Vector(obj.location) - Vector(pivot))
	return empty


def make_actor(name):
	# A recognizable royal-court silhouette: broad mantle, long split gown, crown.
	# A different model/props per cast archetype will replace this prototype.
	cloth = material(name + " deep teal cloth", (0.055, 0.23, 0.29))
	trim = material(name + " brass trim", (0.8, 0.56, 0.19), 0.52)
	underskirt = material(name + " warm ivory", (0.74, 0.66, 0.49))
	hair = material(name + " chestnut hair", (0.19, 0.075, 0.035))
	skin = material(name + " skin", (0.72, 0.47, 0.31))
	boots = material(name + " dark shoes", (0.13, 0.09, 0.075))

	# Feet and legs beneath a two-tone skirt keep the figure's walk readable.
	parts = []
	for side, sign in (("left", -1), ("right", 1)):
		leg = add_cylinder(name + " " + side + " leg", (sign * 0.075, 0.0, 0.36), 0.055, 0.46, underskirt)
		leg_pivot = parent_at(leg, (sign * 0.075, 0.0, 0.59), name + " " + side + " leg pivot")
		parts.append((leg_pivot, sign, "leg"))
		add_sphere(name + " " + side + " shoe", (sign * 0.075, -0.06, 0.105), (0.075, 0.13, 0.07), boots)

	# Tapered gown and a short shoulder mantle create a distinct, wider contour.
	add_cone(name + " gown", (0, 0, 0.74), 0.31, 0.17, 0.92, cloth, vertices=10)
	add_cone(name + " ivory front panel", (0, -0.112, 0.52), 0.11, 0.09, 0.60, underskirt, vertices=6)
	add_sphere(name + " mantle", (0, 0.015, 1.27), (0.37, 0.25, 0.18), trim)
	add_sphere(name + " bodice", (0, -0.015, 1.16), (0.19, 0.17, 0.27), cloth)
	add_cylinder(name + " collar", (0, 0, 1.36), 0.13, 0.08, trim)

	# Arms swing around the shoulders. Sleeves and cuffs make the court outfit legible.
	for side, sign in (("left", -1), ("right", 1)):
		arm = add_sphere(name + " " + side + " sleeve", (sign * 0.27, 0, 1.13), (0.11, 0.12, 0.31), cloth)
		arm_pivot = parent_at(arm, (sign * 0.19, 0, 1.34), name + " " + side + " arm pivot")
		parts.append((arm_pivot, sign, "arm"))
		add_sphere(name + " " + side + " hand", (sign * 0.31, -0.015, 0.83), (0.065, 0.055, 0.08), skin)
		add_cylinder(name + " " + side + " cuff", (sign * 0.31, 0, 0.91), 0.08, 0.075, trim)

	add_cylinder(name + " neck", (0, 0, 1.44), 0.075, 0.12, skin)
	add_sphere(name + " face", (0, -0.005, 1.61), (0.17, 0.155, 0.20), skin)
	add_sphere(name + " hair", (0, 0.025, 1.72), (0.175, 0.15, 0.15), hair)
	# Crown points read as a recognizable royal silhouette at 32px scale.
	add_cylinder(name + " crown band", (0, -0.012, 1.79), 0.13, 0.055, trim, vertices=8)
	for index in range(5):
		x = -0.10 + index * 0.05
		add_cone(name + " crown point " + str(index), (x, -0.01, 1.855), 0.025, 0.002, 0.12, trim, vertices=5)

	return parts


def main():
	out_dir, name = arguments()
	os.makedirs(out_dir, exist_ok=True)
	bpy.ops.object.select_all(action="SELECT")
	bpy.ops.object.delete(use_global=False)

	scene = bpy.context.scene
	engines = [item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
	scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else engines[0]
	scene.render.resolution_x = 80
	scene.render.resolution_y = 96
	scene.render.resolution_percentage = 100
	scene.render.image_settings.file_format = "PNG"
	scene.render.image_settings.color_mode = "RGBA"
	scene.render.film_transparent = True
	scene.render.image_settings.color_depth = "8"
	scene.render.resolution_percentage = 100
	scene.world.color = (0.15, 0.15, 0.15)

	root = bpy.data.objects.new(name + " root", None)
	bpy.context.collection.objects.link(root)
	model_parts = make_actor(name)
	for obj in list(scene.objects):
		if obj.name.startswith(name) and obj is not root and obj.parent is None:
			obj.parent = root
			obj.matrix_parent_inverse = root.matrix_world.inverted()
	# Orthographic isometric-like view; rotate the model through the 9 native
	# GemRB orientations and preserve one fixed camera for alignment.
	bpy.ops.object.camera_add(location=(4.5, -6.5, 8.5))
	camera = bpy.context.object
	camera.name = "sprite camera"
	camera.rotation_euler = (Vector((0, 0, 0.90)) - camera.location).to_track_quat("-Z", "Y").to_euler()
	camera.data.type = "ORTHO"
	camera.data.ortho_scale = 1.8
	scene.camera = camera

	for location, power, size in (((-3, -4, 7), 850, 5), ((4, 2, 5), 450, 4)):
		bpy.ops.object.light_add(type="AREA", location=location)
		light = bpy.context.object
		light.data.energy = power
		light.data.shape = "DISK"
		light.data.size = size
		light.rotation_euler = (Vector((0, 0, 0.7)) - light.location).to_track_quat("-Z", "Y").to_euler()

	# Nine cycles correspond to GemRB's unmirrored 0..8 directions. Each cycle
	# holds four walk poses; the atlas is only a visual review artifact today.
	for direction in range(9):
		for frame in range(4):
			for pivot, sign, limb in model_parts:
				phase = (frame / 4.0) * math.tau
				amplitude = 0.32 if limb == "leg" else 0.24
				pivot.rotation_euler = (0, sign * math.sin(phase) * amplitude, 0)
			scene.frame_set(frame + 1)
			root.rotation_euler.z = math.radians(direction * 22.5)
			scene.render.filepath = os.path.join(out_dir, f"{direction:02d}_{frame:02d}.png")
			bpy.ops.render.render(write_still=True)

	print(f"Rendered 36 frames for {name} into {out_dir}")


if __name__ == "__main__":
	main()
