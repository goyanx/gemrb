#!/usr/bin/env python3
"""Render low-resolution, eight-direction Terralum NPC sprites in Blender.

Run with Blender's Python, not the system Python:
  blender --background --python render_npc_sprite.py -- <output-dir> <name> <profile> <seed>
"""

import bpy
import math
import os
import sys
from mathutils import Vector


def arguments():
	args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
	if len(args) != 4:
		raise SystemExit("expected: <output-dir> <character-name> <profile> <seed>")
	return args[0], args[1], args[2], int(args[3])


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


def add_cube(name, location, scale, mat):
	bpy.ops.mesh.primitive_cube_add(size=1, location=location)
	obj = bpy.context.object
	obj.name = name
	obj.scale = scale
	obj.data.materials.append(mat)
	return obj


def add_mesh(name, vertices, faces, mat):
	mesh = bpy.data.meshes.new(name + " mesh")
	mesh.from_pydata(vertices, [], faces)
	mesh.update()
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.collection.objects.link(obj)
	obj.data.materials.append(mat)
	return obj


def parent_at(obj, pivot, name):
	empty = bpy.data.objects.new(name, None)
	bpy.context.collection.objects.link(empty)
	empty.location = pivot
	obj.parent = empty
	obj.location = tuple(Vector(obj.location) - Vector(pivot))
	return empty


def make_actor(name, profile, seed):
	# Each cast archetype changes the silhouette and props; the seed rotates its
	# clothing hue so two scholars or wardens still read as different people.
	if profile == "queen":
		cloth_rgb, trim_rgb, lining_rgb = (0.035, 0.25, 0.32), (0.88, 0.62, 0.16), (0.86, 0.79, 0.64)
	elif profile == "king":
		cloth_rgb, trim_rgb, lining_rgb = (0.38, 0.035, 0.055), (0.88, 0.60, 0.16), (0.92, 0.84, 0.68)
	elif profile == "scholar":
		hue = 0.60 + ((seed % 5) - 2) * 0.025
		cloth_rgb = tuple(__import__("colorsys").hsv_to_rgb(hue, 0.72, 0.44))
		trim_rgb = (0.62, 0.34, 0.12)
		lining_rgb = (0.82, 0.74, 0.59)
	else:
		hue = (seed * 0.61803398875 + 0.08) % 1.0
		cloth_rgb = tuple(__import__("colorsys").hsv_to_rgb(hue, 0.58, 0.72))
		trim_rgb = tuple(__import__("colorsys").hsv_to_rgb((hue + 0.12) % 1.0, 0.43, 0.82))
		lining_rgb = tuple(__import__("colorsys").hsv_to_rgb((hue + 0.50) % 1.0, 0.22, 0.86))
	cloth = material(name + " cloth", cloth_rgb)
	trim = material(name + " trim", trim_rgb, 0.52)
	lining = material(name + " lining", lining_rgb)
	hair = material(name + " hair", (0.19, 0.075, 0.035))
	skin = material(name + " skin", (0.72, 0.47, 0.31))
	boots = material(name + " boots", (0.13, 0.09, 0.075))
	parts = []
	for side, sign in (("left", -1), ("right", 1)):
		if profile in ("ranger", "guard", "citizen", "king", "scholar"):
			leg = add_cylinder(name + " " + side + " trouser", (sign * 0.075, 0.0, 0.36), 0.062, 0.46, lining)
		else:
			leg = add_cylinder(name + " " + side + " leg", (sign * 0.075, 0.0, 0.36), 0.055, 0.46, lining)
		leg_pivot = parent_at(leg, (sign * 0.075, 0.0, 0.59), name + " " + side + " leg pivot")
		parts.append((leg_pivot, sign, "leg"))
		add_sphere(name + " " + side + " shoe", (sign * 0.075, -0.06, 0.105), (0.075, 0.13, 0.07), boots)

	if profile in ("ranger", "guard", "citizen", "king", "scholar"):
		tunic_depth = 0.46 if profile == "ranger" else 0.50 if profile == "king" else 0.62
		add_cylinder(name + " tunic", (0, 0, 0.98), 0.23, tunic_depth, cloth, vertices=8)
		if profile == "king":
			add_cube(name + " royal overcoat", (0, -0.17, 0.94), (0.48, 0.08, 0.50), trim)
			add_cylinder(name + " royal belt", (0, -0.10, 0.85), 0.24, 0.08, lining, vertices=8)
			add_sphere(name + " royal shoulder cape", (0, 0.02, 1.29), (0.44, 0.28, 0.24), cloth)
		elif profile == "scholar":
			add_cube(name + " archivist's book", (-0.32, -0.17, 0.87), (0.25, 0.10, 0.36), trim)
			add_cube(name + " book pages", (-0.32, -0.228, 0.87), (0.19, 0.025, 0.30), lining)
			add_cube(name + " cross-body satchel", (0.19, -0.19, 0.92), (0.22, 0.08, 0.24), boots)
		elif profile == "ranger":
			# A short shoulder cape leaves the trousers visible, separating the
			# pathfinder silhouette from the long-robed scholars and mages.
			add_mesh(name + " short travel cape", [
				(-0.34, -0.23, 1.34), (0.34, -0.23, 1.34),
				(0.23, -0.23, 1.02), (0.0, -0.23, 0.93), (-0.23, -0.23, 1.02),
			], [(0, 1, 2, 3, 4)], trim)
			add_sphere(name + " hood", (0, 0.055, 1.67), (0.23, 0.22, 0.24), cloth)
			add_cube(name + " trail pack", (0.31, 0.02, 1.17), (0.27, 0.25, 0.42), lining)
		elif profile == "guard":
			add_cylinder(name + " cuirass", (0, -0.09, 1.04), 0.25, 0.42, trim, vertices=8)
			for sign in (-1, 1):
				add_sphere(name + " pauldron", (sign * 0.28, 0, 1.31), (0.16, 0.20, 0.15), trim)
			add_sphere(name + " helmet", (0, 0.02, 1.76), (0.23, 0.21, 0.18), trim)
			add_cone(name + " helmet crest", (0, 0.025, 1.96), 0.045, 0.008, 0.28, lining, vertices=5)
			add_cube(name + " shield", (0.39, -0.12, 0.79), (0.28, 0.11, 0.56), lining)
		elif profile == "citizen":
			add_cube(name + " work apron", (0, -0.18, 0.81), (0.32, 0.07, 0.48), trim)
	else:
		flare = 0.40 if profile == "queen" else 0.34 if profile in ("royal", "mage") else 0.27
		add_cone(name + " robe", (0, 0, 0.75), flare, 0.17, 0.95, cloth, vertices=10)
		add_cone(name + " front panel", (0, -0.13, 0.52), 0.11, 0.09, 0.60, lining, vertices=6)
		if profile in ("queen", "royal", "king"):
			add_sphere(name + " royal mantle", (0, 0.015, 1.27), (0.37, 0.25, 0.18), trim)
		elif profile == "mage":
			add_cone(name + " star mantle", (0, 0.04, 1.25), 0.34, 0.18, 0.26, trim, vertices=8)
		elif profile == "scholar":
			add_cube(name + " field book", (0.30, -0.13, 0.92), (0.16, 0.09, 0.23), trim)
		add_sphere(name + " bodice", (0, -0.015, 1.16), (0.19, 0.17, 0.27), cloth)
		add_cylinder(name + " collar", (0, 0, 1.36), 0.13, 0.08, trim)

	for side, sign in (("left", -1), ("right", 1)):
		arm = add_sphere(name + " " + side + " sleeve", (sign * 0.27, 0, 1.13), (0.11, 0.12, 0.31), cloth)
		arm_pivot = parent_at(arm, (sign * 0.19, 0, 1.34), name + " " + side + " arm pivot")
		parts.append((arm_pivot, sign, "arm"))
		add_sphere(name + " " + side + " hand", (sign * 0.31, -0.015, 0.83), (0.065, 0.055, 0.08), skin)

	add_cylinder(name + " neck", (0, 0, 1.44), 0.075, 0.12, skin)
	add_sphere(name + " face", (0, -0.005, 1.61), (0.17, 0.155, 0.20), skin)
	if profile not in ("ranger", "guard"):
		add_sphere(name + " hair", (0, 0.025, 1.72), (0.175, 0.15, 0.15), hair)
	if profile == "king":
		add_sphere(name + " beard", (0, -0.12, 1.51), (0.13, 0.075, 0.13), hair)
	if profile in ("queen", "royal", "king"):
		add_cylinder(name + " crown band", (0, -0.012, 1.79), 0.16, 0.075, trim, vertices=8)
		for index in range(5):
			x = -0.13 + index * 0.065
			add_cone(name + " crown point " + str(index), (x, -0.01, 1.88), 0.035, 0.002, 0.18, trim, vertices=5)
	elif profile == "mage":
		add_cone(name + " pointed hat", (0, 0.025, 1.91), 0.16, 0.005, 0.34, trim, vertices=7)
		add_cylinder(name + " mage staff", (0.39, 0.02, 1.13), 0.025, 1.18, trim, vertices=6)
		add_sphere(name + " staff crystal", (0.39, 0.02, 1.75), (0.08, 0.08, 0.10), lining)
	elif profile == "ranger":
		add_cylinder(name + " bow", (0.43, -0.24, 1.11), 0.035, 1.0, trim, vertices=6)
	elif profile == "king":
		add_cylinder(name + " royal scepter", (0.42, -0.22, 1.10), 0.028, 0.88, trim, vertices=6)
		add_sphere(name + " scepter jewel", (0.42, -0.22, 1.57), (0.065, 0.065, 0.08), lining)
	elif profile == "scholar":
		add_sphere(name + " scholar cap", (0, 0.01, 1.78), (0.20, 0.18, 0.10), trim)
	return parts


def main():
	out_dir, name, profile, seed = arguments()
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
	model_parts = make_actor(name, profile, seed)
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
	camera.data.ortho_scale = 1.65
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

	print(f"Rendered 36 frames for {name} ({profile}) into {out_dir}")


if __name__ == "__main__":
	main()
