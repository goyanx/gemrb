#!/usr/bin/env python3
"""Render low-resolution, eight-direction Terralum NPC sprites in Blender.

Run with Blender's Python, not the system Python:
  blender --background --python render_npc_sprite.py -- <output-dir> <name> <profile> <seed>
"""

import bpy
import colorsys
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
	# Keep the general animation rig, but let recurring cast leads carry a
	# distinct role silhouette and signature prop instead of only a new color.
	archetype = {"inessa": "scholar", "dorian": "mage", "tessa": "ranger", "doma": "citizen", "fen": "ranger",
		"sella": "ranger", "ilya": "ranger", "eren": "ranger", "pell": "ranger",
		"saren": "guard", "lorian": "guard", "wayfarer": "ranger"}.get(profile, profile)
	# Each identity gets a high-contrast cloth color and a visible accessory
	# variant. At 80x96, one strong prop or head silhouette reads better than
	# several tiny costume details.
	hue = (seed * 0.61803398875 + 0.08) % 1.0
	identity_cloth = tuple(colorsys.hsv_to_rgb(hue, 0.76, 0.58))
	identity_trim = tuple(colorsys.hsv_to_rgb((hue + 0.10) % 1.0, 0.76, 0.88))
	if profile == "queen":
		cloth_rgb, trim_rgb, lining_rgb = (0.035, 0.25, 0.32), (0.88, 0.62, 0.16), (0.86, 0.79, 0.64)
	elif profile == "mara":
		cloth_rgb, trim_rgb, lining_rgb = (0.055, 0.17, 0.34), (0.82, 0.52, 0.14), (0.78, 0.72, 0.57)
	elif profile == "leora":
		cloth_rgb, trim_rgb, lining_rgb = (0.28, 0.10, 0.29), (0.22, 0.60, 0.55), (0.88, 0.78, 0.57)
	elif profile == "king":
		cloth_rgb, trim_rgb, lining_rgb = (0.38, 0.035, 0.055), (0.88, 0.60, 0.16), (0.92, 0.84, 0.68)
	elif profile == "inessa":
		cloth_rgb, trim_rgb, lining_rgb = (0.10, 0.16, 0.30), (0.70, 0.40, 0.18), (0.82, 0.78, 0.63)
	elif profile == "tessa":
		cloth_rgb, trim_rgb, lining_rgb = (0.12, 0.26, 0.17), (0.72, 0.46, 0.18), (0.58, 0.40, 0.25)
	elif profile == "saren":
		cloth_rgb, trim_rgb, lining_rgb = (0.10, 0.18, 0.28), (0.72, 0.58, 0.25), (0.77, 0.73, 0.62)
	elif profile == "wayfarer":
		cloth_rgb, trim_rgb, lining_rgb = (0.19, 0.22, 0.17), (0.48, 0.36, 0.22), (0.62, 0.53, 0.40)
	elif profile == "dorian":
		cloth_rgb, trim_rgb, lining_rgb = (0.055, 0.105, 0.26), (0.78, 0.54, 0.16), (0.84, 0.78, 0.62)
	elif profile == "lorian":
		cloth_rgb, trim_rgb, lining_rgb = (0.035, 0.27, 0.25), (0.68, 0.43, 0.15), (0.79, 0.76, 0.63)
	elif profile == "ilya":
		cloth_rgb, trim_rgb, lining_rgb = (0.36, 0.105, 0.075), (0.78, 0.63, 0.32), (0.24, 0.16, 0.10)
	elif profile == "pell":
		cloth_rgb, trim_rgb, lining_rgb = (0.14, 0.23, 0.34), (0.72, 0.48, 0.18), (0.58, 0.45, 0.29)
	elif profile == "fen":
		cloth_rgb, trim_rgb, lining_rgb = (0.10, 0.20, 0.10), (0.60, 0.48, 0.28), (0.27, 0.17, 0.10)
	elif profile == "sella":
		cloth_rgb, trim_rgb, lining_rgb = (0.23, 0.30, 0.18), (0.77, 0.66, 0.39), (0.67, 0.59, 0.45)
	elif profile == "doma":
		cloth_rgb, trim_rgb, lining_rgb = (0.32, 0.22, 0.13), (0.70, 0.47, 0.20), (0.63, 0.57, 0.46)
	elif profile == "eren":
		cloth_rgb, trim_rgb, lining_rgb = (0.08, 0.27, 0.29), (0.87, 0.58, 0.13), (0.44, 0.30, 0.18)
	else:
		cloth_rgb, trim_rgb, lining_rgb = identity_cloth, identity_trim, (0.82, 0.76, 0.62)
	cloth = material(name + " cloth", cloth_rgb)
	trim = material(name + " trim", trim_rgb, 0.52)
	lining = material(name + " lining", lining_rgb)
	hair_rgb = (0.62, 0.58, 0.48) if profile in ("dorian", "sella") else (0.16, 0.08, 0.035) if profile == "fen" else (0.19, 0.075, 0.035)
	hair = material(name + " hair", hair_rgb)
	skin_rgb = (0.31, 0.17, 0.11) if profile == "ilya" else (0.47, 0.29, 0.18) if profile == "eren" else (0.72, 0.47, 0.31)
	skin = material(name + " skin", skin_rgb)
	boots = material(name + " boots", (0.13, 0.09, 0.075))
	parts = []
	for side, sign in (("left", -1), ("right", 1)):
		if archetype in ("ranger", "guard", "citizen", "king", "scholar"):
			leg = add_cylinder(name + " " + side + " trouser", (sign * 0.075, 0.0, 0.36), 0.062, 0.46, lining)
		else:
			leg = add_cylinder(name + " " + side + " leg", (sign * 0.075, 0.0, 0.36), 0.055, 0.46, lining)
		leg_pivot = parent_at(leg, (sign * 0.075, 0.0, 0.59), name + " " + side + " leg pivot")
		parts.append((leg_pivot, sign, "leg"))
		add_sphere(name + " " + side + " shoe", (sign * 0.075, -0.06, 0.105), (0.075, 0.13, 0.07), boots)

	if archetype in ("ranger", "guard", "citizen", "king", "scholar"):
		tunic_depth = 0.46 if archetype == "ranger" else 0.50 if archetype == "king" else 0.62
		add_cylinder(name + " tunic", (0, 0, 0.98), 0.23, tunic_depth, cloth, vertices=8)
		if archetype == "king":
			add_cube(name + " royal overcoat", (0, -0.17, 0.94), (0.48, 0.08, 0.50), trim)
			add_cylinder(name + " royal belt", (0, -0.10, 0.85), 0.24, 0.08, lining, vertices=8)
			add_sphere(name + " royal shoulder cape", (0, 0.02, 1.29), (0.44, 0.28, 0.24), cloth)
		elif archetype == "scholar":
			variant = seed % 4
			if variant == 0:
				add_cube(name + " archivist's book", (-0.32, -0.17, 0.87), (0.25, 0.10, 0.36), trim)
				add_cube(name + " book pages", (-0.32, -0.228, 0.87), (0.19, 0.025, 0.30), lining)
			elif variant == 1:
				add_cylinder(name + " tall scroll case", (0.33, 0.02, 1.20), 0.075, 0.82, trim, vertices=8)
				add_sphere(name + " scroll cap", (0.33, 0.02, 1.62), (0.09, 0.09, 0.08), lining)
			elif variant == 2:
				add_cube(name + " open folio", (-0.31, -0.16, 0.91), (0.34, 0.10, 0.27), trim)
				add_cube(name + " folio pages", (-0.31, -0.22, 0.91), (0.27, 0.025, 0.21), lining)
			else:
				add_cylinder(name + " field scroll", (-0.33, -0.12, 0.96), 0.07, 0.48, trim, vertices=8)
				add_cube(name + " broad satchel", (0.28, -0.18, 0.89), (0.30, 0.10, 0.34), boots)
			if variant in (1, 3):
				add_cube(name + " cross-body strap", (0.02, -0.20, 1.06), (0.07, 0.06, 0.64), trim)
		elif archetype == "ranger":
			# Short front-facing capes and identity-specific trail gear distinguish
			# pathfinders from the long-coated scholars and from one another.
			variant = 0 if profile in ("tessa", "wayfarer") else 1 if profile == "fen" else 3 if profile == "eren" else 2 if profile == "sella" else seed % 4
			add_mesh(name + " short travel cape", [
				(-0.40 if variant == 2 else -0.34, -0.23, 1.34),
				(0.40 if variant == 2 else 0.34, -0.23, 1.34),
				(0.23, -0.23, 1.02), (0.0, -0.23, 0.93), (-0.23, -0.23, 1.02),
			], [(0, 1, 2, 3, 4)], trim)
			if profile == "fen":
				pass  # Fen's broad hunter hat is modeled below.
			elif variant in (0, 2):
				add_sphere(name + " hood", (0, 0.055, 1.67), (0.23, 0.22, 0.24), cloth)
			else:
				add_cylinder(name + " broad trail hat", (0, 0.025, 1.72), 0.26, 0.09, trim, vertices=8)
				add_cone(name + " travel cap", (0, 0.025, 1.83), 0.15, 0.02, 0.18, cloth, vertices=7)
			if variant in (0, 3):
				add_cube(name + " trail pack", (0.31, 0.02, 1.17), (0.27, 0.25, 0.42), lining)
			else:
				add_cylinder(name + " bedroll", (0.34, 0.02, 1.22), 0.12, 0.58, lining, vertices=8)
		elif archetype == "guard":
			variant = 2 if profile == "saren" else seed % 4
			add_cylinder(name + " cuirass", (0, -0.09, 1.04), 0.25, 0.42, trim, vertices=8)
			for sign in (-1, 1):
				add_sphere(name + " pauldron", (sign * 0.28, 0, 1.31), (0.16, 0.20, 0.15), trim)
			if variant in (0, 1, 3):
				add_sphere(name + " helmet", (0, 0.02, 1.76), (0.23, 0.21, 0.18), trim)
				add_cone(name + " helmet crest", (0, 0.025, 1.96), 0.045, 0.008, 0.28, lining, vertices=5)
			else:
				add_sphere(name + " guard hood", (0, 0.03, 1.72), (0.25, 0.23, 0.27), cloth)
				add_cube(name + " brow plate", (0, -0.17, 1.72), (0.28, 0.08, 0.10), trim)
			if variant in (0, 2):
				add_cube(name + " shield", (0.39, -0.12, 0.79), (0.28, 0.11, 0.56), lining)
			else:
				add_cylinder(name + " patrol spear", (0.42, 0.02, 1.12), 0.025, 1.22, lining, vertices=6)
				add_cone(name + " spear head", (0.42, 0.02, 1.78), 0.07, 0.005, 0.24, trim, vertices=5)
		elif archetype == "citizen":
			add_cube(name + " work apron", (0, -0.18, 0.81), (0.32, 0.07, 0.48), trim)
			variant = seed % 3
			if variant == 0:
				add_sphere(name + " work cap", (0, 0.03, 1.76), (0.23, 0.20, 0.13), lining)
			elif variant == 1:
				add_cylinder(name + " tool hammer", (0.39, -0.04, 0.94), 0.04, 0.58, boots, vertices=6)
				add_cube(name + " hammer head", (0.39, -0.04, 1.25), (0.20, 0.10, 0.12), trim)
			else:
				add_cube(name + " market satchel", (0.33, 0.02, 1.05), (0.30, 0.25, 0.32), lining)
		if profile == "inessa":
			# Her broad scholar's stole and open folio give Inessa a recognizable
			# outline distinct from the cap-and-scroll silhouette used by librarians.
			add_mesh(name + " scholar stole", [(-0.42, -0.24, 1.34), (0.42, -0.24, 1.34),
				(0.27, -0.25, 0.94), (0.0, -0.26, 1.02), (-0.27, -0.25, 0.94)], [(0, 1, 2, 3, 4)], trim)
			add_cube(name + " open route folio", (-0.30, -0.22, 0.92), (0.24, 0.08, 0.24), lining)
			add_cube(name + " folio cover", (-0.30, -0.27, 0.92), (0.25, 0.02, 0.25), trim)
		elif profile == "tessa":
			# The scout's high hood and feather marker remain legible at map scale.
			add_sphere(name + " scout hood mantle", (0, 0.07, 1.65), (0.30, 0.27, 0.32), cloth)
			add_cone(name + " scout feather", (0.14, 0.04, 1.98), 0.045, 0.004, 0.42, trim, vertices=5)
			add_cube(name + " scout quiver", (0.34, 0.10, 1.25), (0.18, 0.18, 0.48), boots)
		elif profile == "saren":
			# Saren's marshal mantle, badge and long spear mark the relay authority.
			add_mesh(name + " marshal mantle", [(-0.44, 0.10, 1.38), (0.44, 0.10, 1.38),
				(0.30, 0.10, 0.76), (0.0, 0.10, 0.91), (-0.30, 0.10, 0.76)], [(0, 1, 2, 3, 4)], cloth)
			add_sphere(name + " marshal badge", (0, -0.24, 1.27), (0.09, 0.045, 0.09), lining)
			add_cylinder(name + " relay spear", (0.46, 0.02, 1.28), 0.03, 1.58, lining, vertices=6)
			add_cone(name + " relay spear point", (0.46, 0.02, 2.12), 0.08, 0.004, 0.24, trim, vertices=5)
		elif profile == "wayfarer":
			# An uneven weather cloak and carried lantern distinguish the traveler
			# from the equipped scouts who know these roads.
			add_mesh(name + " patched weather cloak", [(-0.39, 0.12, 1.36), (0.39, 0.12, 1.36),
				(0.34, 0.12, 0.72), (0.18, 0.12, 0.86), (0.0, 0.12, 0.68),
				(-0.16, 0.12, 0.84), (-0.34, 0.12, 0.70)], [(0, 1, 2, 3, 4, 5, 6)], trim)
			add_cylinder(name + " travel lantern handle", (-0.39, -0.06, 1.02), 0.018, 0.34, boots, vertices=6)
			add_cube(name + " travel lantern", (-0.39, -0.06, 0.82), (0.17, 0.14, 0.21), lining)
		elif profile == "ilya":
			add_mesh(name + " rust trail scarf", [(-0.18, -0.24, 1.35), (0.18, -0.24, 1.35),
				(0.10, -0.25, 1.03), (0.30, -0.24, 0.87), (0.22, -0.24, 1.20)], [(0, 1, 2, 3, 4)], trim)
			add_cube(name + " ranger field pack", (0.31, 0.03, 1.16), (0.27, 0.26, 0.45), lining)
			add_cylinder(name + " trail quiver", (0.39, 0.02, 1.19), 0.08, 0.58, boots, vertices=7)
		elif profile == "pell":
			add_cube(name + " dispatch tube", (0.34, 0.01, 1.28), (0.13, 0.16, 0.62), trim)
			add_sphere(name + " dispatch tube cap", (0.34, 0.01, 1.61), (0.09, 0.10, 0.08), lining)
			add_cube(name + " courier satchel", (-0.33, 0.02, 0.99), (0.30, 0.24, 0.34), boots)
			add_mesh(name + " courier sash", [(-0.16, -0.24, 1.30), (0.15, -0.24, 1.31),
				(0.28, -0.24, 0.82), (0.12, -0.24, 0.82)], [(0, 1, 2, 3)], trim)
		elif profile == "lorian":
			add_mesh(name + " guardian mantle", [(-0.48, 0.12, 1.40), (0.48, 0.12, 1.40),
				(0.43, 0.12, 0.72), (0.0, 0.12, 0.82), (-0.43, 0.12, 0.72)], [(0, 1, 2, 3, 4)], cloth)
			add_cube(name + " guardian shield", (0.42, -0.12, 0.89), (0.36, 0.14, 0.62), trim)
			add_cylinder(name + " guardian spear", (-0.43, 0.02, 1.18), 0.035, 1.46, lining, vertices=6)
		elif profile == "fen":
			add_sphere(name + " hunter fur collar", (0, -0.02, 1.34), (0.43, 0.24, 0.20), trim)
			add_cylinder(name + " feathered hunting quiver", (0.34, 0.05, 1.25), 0.09, 0.68, boots, vertices=7)
			add_cylinder(name + " longbow", (-0.39, -0.13, 1.10), 0.03, 1.18, trim, vertices=6)
		elif profile == "sella":
			add_mesh(name + " waykeeper's mantle", [(-0.42, 0.12, 1.40), (0.42, 0.12, 1.40),
				(0.36, 0.12, 0.64), (0.0, 0.12, 0.82), (-0.36, 0.12, 0.64)], [(0, 1, 2, 3, 4)], trim)
			add_cylinder(name + " carved marker staff", (0.42, 0.02, 1.17), 0.035, 1.46, boots, vertices=6)
			add_cube(name + " waystone charm", (-0.31, -0.21, 0.92), (0.20, 0.08, 0.26), lining)
		elif profile == "doma":
			add_cube(name + " stonework apron", (0, -0.22, 0.88), (0.43, 0.08, 0.59), trim)
			add_cylinder(name + " carver's mallet handle", (0.38, -0.05, 0.89), 0.035, 0.58, boots, vertices=6)
			add_cube(name + " carver's mallet head", (0.38, -0.05, 1.20), (0.23, 0.13, 0.16), lining)
			add_cylinder(name + " stone chisel", (-0.34, -0.04, 1.08), 0.025, 0.49, trim, vertices=6)
		elif profile == "eren":
			add_mesh(name + " courier scarf", [(-0.18, -0.25, 1.34), (0.18, -0.25, 1.34),
				(0.17, -0.26, 1.03), (0.34, -0.24, 0.88), (0.25, -0.25, 1.18)], [(0, 1, 2, 3, 4)], trim)
			add_cube(name + " courier route pack", (0.30, 0.03, 1.16), (0.31, 0.25, 0.48), lining)
			add_cylinder(name + " coil of ford rope", (-0.37, -0.05, 0.93), 0.12, 0.12, trim, vertices=8)
	else:
		flare = 0.46 if profile == "queen" else 0.37 if profile == "mara" else 0.31 if profile == "leora" else 0.34 if profile in ("royal", "mage") else 0.27
		add_cone(name + " robe", (0, 0, 0.75), flare, 0.17, 0.95, cloth, vertices=10)
		add_cone(name + " front panel", (0, -0.13, 0.52), 0.11, 0.09, 0.60, lining, vertices=6)
		if profile == "mara":
			# Mara's archive-blue hood, shoulder cape, spectacles, and folio make
			# her readable as the route archivist even at native map scale.
			add_mesh(name + " archivist shoulder cape", [(-0.34, 0.12, 1.34), (0.34, 0.12, 1.34), (0.30, 0.12, 0.93), (0, 0.12, 0.80), (-0.30, 0.12, 0.93)], [(0, 1, 2, 3, 4)], trim)
			add_cube(name + " route folio", (-0.31, -0.20, 0.91), (0.25, 0.10, 0.34), boots)
			add_cube(name + " folio pages", (-0.31, -0.258, 0.91), (0.18, 0.018, 0.27), lining)
		elif profile == "leora":
			# Leora carries a capped dispatch scroll and wears a distinctive
			# high archive hood over her layered robe.
			add_sphere(name + " archive hood", (0, 0.055, 1.71), (0.25, 0.23, 0.29), cloth)
			add_cylinder(name + " sealed dispatch tube", (0.34, 0.02, 1.16), 0.075, 0.82, trim, vertices=8)
			add_sphere(name + " dispatch tube cap", (0.34, 0.02, 1.59), (0.09, 0.09, 0.07), lining)
		if archetype in ("queen", "royal", "king"):
			add_sphere(name + " royal mantle", (0, 0.015, 1.27), (0.37, 0.25, 0.18), trim)
		elif profile in ("mage", "dorian"):
			variant = seed % 3
			if variant == 0:
				add_cone(name + " star mantle", (0, 0.04, 1.25), 0.34, 0.18, 0.26, trim, vertices=8)
			elif variant == 1:
				add_sphere(name + " shoulder mantle", (0, 0.02, 1.28), (0.40, 0.27, 0.21), trim)
			else:
				add_cube(name + " spell folio", (-0.30, -0.17, 0.94), (0.24, 0.10, 0.33), trim)
		elif archetype == "scholar":
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
	if archetype not in ("ranger", "guard", "leora"):
		add_sphere(name + " hair", (0, 0.025, 1.72), (0.175, 0.15, 0.15), hair)
	if profile == "mara":
		# A visible braid and spectacles distinguish her face from the shared
		# scholar base model without relying on tiny color changes.
		add_sphere(name + " archive hood", (0, 0.055, 1.72), (0.24, 0.22, 0.25), cloth)
		add_cylinder(name + " long braid", (0.18, 0.035, 1.40), 0.055, 0.47, hair, vertices=6)
		for x in (-0.075, 0.075):
			add_cube(name + " spectacles " + str(x), (x, -0.155, 1.64), (0.09, 0.025, 0.055), boots)
		add_cube(name + " spectacles bridge", (0, -0.171, 1.64), (0.06, 0.02, 0.018), boots)
	if profile == "king":
		beard = material(name + " silver beard", (0.58, 0.55, 0.48))
		add_sphere(name + " beard", (0, -0.12, 1.51), (0.15, 0.085, 0.16), beard)
	elif profile == "dorian":
		add_cone(name + " silver beard", (0, -0.13, 1.48), 0.13, 0.025, 0.28, hair, vertices=7)
		add_cylinder(name + " brass star circlet", (0, -0.01, 1.79), 0.18, 0.055, trim, vertices=8)
		add_sphere(name + " seer's orb", (0.40, 0.01, 1.78), (0.10, 0.10, 0.11), lining)
	elif profile == "fen":
		add_sphere(name + " hunter beard", (0, -0.11, 1.48), (0.16, 0.10, 0.17), hair)
		add_cylinder(name + " broad hunter hat", (0, 0.02, 1.79), 0.29, 0.09, boots, vertices=8)
	elif profile == "sella":
		add_cylinder(name + " silver trail braid", (0.16, 0.03, 1.38), 0.05, 0.53, hair, vertices=6)
	elif profile == "doma":
		add_sphere(name + " close-cropped gray hair", (0, 0.02, 1.73), (0.18, 0.15, 0.11), lining)
	elif profile == "eren":
		add_sphere(name + " courier hair knot", (0.11, 0.04, 1.74), (0.10, 0.12, 0.13), hair)
	if archetype in ("queen", "royal", "king"):
		add_cylinder(name + " crown band", (0, -0.012, 1.79), 0.16, 0.075, trim, vertices=8)
		for index in range(5):
			x = -0.13 + index * 0.065
			add_cone(name + " crown point " + str(index), (x, -0.01, 1.88), 0.035, 0.002, 0.18, trim, vertices=5)
	elif profile in ("mage", "dorian"):
		if seed % 3 != 1:
			add_cone(name + " pointed hat", (0, 0.025, 1.91), 0.16, 0.005, 0.34, trim, vertices=7)
		add_cylinder(name + " mage staff", (0.39, 0.02, 1.13), 0.025, 1.18, trim, vertices=6)
		add_sphere(name + " staff crystal", (0.39, 0.02, 1.75), (0.08, 0.08, 0.10), lining)
	elif archetype == "ranger" and profile != "pell":
		add_cylinder(name + " bow", (0.43, -0.24, 1.11), 0.035, 1.0, trim, vertices=6)
	elif profile == "pell":
		add_cylinder(name + " dispatch pennant", (0.43, -0.20, 1.14), 0.025, 0.72, trim, vertices=6)
	elif profile == "king":
		add_cylinder(name + " royal scepter", (0.42, -0.22, 1.10), 0.028, 0.88, trim, vertices=6)
		add_sphere(name + " scepter jewel", (0.42, -0.22, 1.57), (0.065, 0.065, 0.08), lining)
	elif archetype == "scholar":
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
