# this script is dedicated to the public domain under CC0
# (https://creativecommons.org/publicdomain/zero/1.0/)
# do whatever you want with it! -Bram

from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatProperty, IntProperty
import bmesh
import os
import bpy
bl_info = {
    "name": "EasyBake",
    "category": "3D View",
    "blender": (2, 80, 0),
    "author": "Bram Eulaers",
    "description": "Simple texture baking UI for fast iteration. Can be found in the 3D View Sidebar under 'bake'."
}


# Current use of bpy.ops
# TODO: Remove usage of these from code base
"""
bpy.ops.object.mode_set()
bpy.ops.view3d.localview()  # can't safely remove this, Blender doesn't handle this data well
bpy.ops.object.hide_view_clear()
bpy.ops.object.duplicate()
bpy.ops.object.join()
bpy.ops.object.transform_apply()
bpy.ops.object.bake()
bpy.ops.mesh.select_all()
bpy.ops.object.editmode_toggle()
bpy.ops.uv.export_layout()
bpy.ops.object.select_all()
bpy.ops.object.delete()
"""


class bln:
    FINISHED = "FINISHED"
    WARNING = "WARNING"
    VIEW_3D = "VIEW_3D"
    UI = "UI"
    SELECT = "SELECT"
    DESELECT = "DESELECT"
    UNDO = "UNDO"
    EDIT = "EDIT"
    MESH = "MESH"
    OBJECT = "OBJECT"
    CYCLES = "CYCLES"
    TANGENT = "TANGENT"
    TARGA = "TARGA"
    NORMAL = "NORMAL"
    AO = "AO"
    DIFFUSE = "DIFFUSE"
    ROUGHNESS = "ROUGHNESS"
    EMIT = "EMIT"
    IMAGE_EDITOR = "IMAGE_EDITOR"
    DIR_PATH = "DIR_PATH"


class rna:
    OBJECT = "Object"
    COLLECTION = "Collection"


class icon:
    MESH_ICOSPHERE = "MESH_ICOSPHERE"
    HIDE_ON = "HIDE_ON"
    HIDE_OFF = "HIDE_OFF"
    FILE_REFRESH = "FILE_REFRESH"
    SCENE = "SCENE"
    GROUP = "GROUP"
    MESH_UVSPHERE = "MESH_UVSPHERE"
    OBJECT_DATAMODE = "OBJECT_DATAMODE"
    REMOVE = "REMOVE"
    ADD = "ADD"
    SHADING_RENDERED = "SHADING_RENDERED"
    SHADING_SOLID = "SHADING_SOLID"
    SHADING_TEXTURE = "SHADING_TEXTURE"
    SHADING_WIRE = "SHADING_WIRE"
    BLANK1 = "BLANK1"
    RENDER_RESULT = "RENDER_RESULT"


class target:
    INCREASE_WIDTH = "INCREASE_WIDTH"
    INCREASE_HEIGHT = "INCREASE_HEIGHT"
    DECREASE_WIDTH = "DECREASE_WIDTH"
    DECREASE_HEIGHT = "DECREASE_HEIGHT"


class brm:
    UI_TOGGLE = "brm.bakeuitoggle"
    UI_INCREMENT = "brm.bakeuiincrement"
    UI_HIDE = "brm.bakeuihide"
    BAKE = "brm.bake"


def unhide(objectType):
    if objectType is None:
        for o in objectType.objects:
            o.hide_viewport = False
    else:
        objectType.hide_viewport = False


def hidden(objectType):
    if objectType is None:
        hid = False
        try:
            for o in objectType.objects:
                if o.hide_viewport:
                    return True
        except AttributeError:
            pass
        return False
    else:
        return objectType.hide_viewport


def hide(objectType):
    if objectType is None:
        for o in objectType.objects:
            o.hide_viewport = True
    else:
        objectType.hide_viewport = True


class PANEL_PT_EasyBakeUIPanel(bpy.types.Panel):
    """EasyBakeUIPanel Panel"""
    bl_label = "EasyBake"
    bl_space_type = bln.VIEW_3D
    bl_region_type = bln.UI
    bl_category = "EasyBake"

    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon=icon.SCENE)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene, "lowpolyGroup", text="", icon=icon.GROUP)
        if context.scene.lowpolyGroup is True:
            row.prop_search(
                context.scene,
                "lowpoly",
                bpy.data,
                "collections",
                text="",
                icon=icon.MESH_ICOSPHERE)
        if context.scene.lowpolyGroup is False:
            row.prop_search(
                context.scene,
                "lowpoly",
                context.scene,
                "objects",
                text="",
                icon=icon.MESH_ICOSPHERE)
        if hidden(context.scene.lowpoly):
            hideicon = icon.HIDE_ON
        else:
            hideicon = icon.HIDE_OFF
        op = row.operator(brm.UI_HIDE, text="", icon=hideicon)
        op.targetmesh = "lowpoly"
        row = col.row(align=True)
        row.prop(context.scene, "hipolyGroup", text="", icon=icon.GROUP)
        if context.scene.hipolyGroup is True:
            row.prop_search(
                context.scene,
                "hipoly",
                bpy.data,
                "collections",
                text="",
                icon=icon.MESH_UVSPHERE)
        if context.scene.hipolyGroup is False:
            row.prop_search(
                context.scene,
                "hipoly",
                context.scene,
                "objects",
                text="",
                icon=icon.MESH_UVSPHERE)
        row.enabled = not context.scene.UseLowOnly
        if hidden(context.scene.hipoly):
            hideicon = icon.HIDE_ON
        else:
            hideicon = icon.HIDE_OFF
        op = row.operator(brm.UI_HIDE, text="", icon=hideicon)
        op.targetmesh = "hipoly"
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator(
            brm.UI_TOGGLE,
            text="Toggle hi/low",
            icon=icon.FILE_REFRESH)
        #row.prop(context.scene, "UseBlenderGame", icon=icon.MESH_UVSPHERE, text="")
        col = layout.column(align=True)
        col.separator()
        row = col.row(align=True)
        row.prop(
            context.scene.render.bake,
            "cage_extrusion",
            text="Ray Distance")
        row.prop(context.scene, "cageEnabled", icon=icon.OBJECT_DATAMODE, text="")
        row = col.row(align=True)
        #row.enabled = context.scene.cageEnabled
        if context.scene.cageEnabled:
            op = row.prop_search(
                context.scene,
                "cage",
                bpy.data,
                "objects",
                text="",
                icon=icon.MESH_UVSPHERE)
        #op.enabled = context.scene.cageEnabled
        col.separator()
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Width:")
        row.operator(
            brm.UI_INCREMENT,
            text="",
            icon=icon.REMOVE).target = target.DECREASE_WIDTH
        row.prop(context.scene, "bakeWidth", text="")
        row.operator(
            brm.UI_INCREMENT,
            text="",
            icon=icon.ADD).target = target.INCREASE_WIDTH
        row = col.row(align=True)
        row.label(text="Height:")
        row.operator(
            brm.UI_INCREMENT,
            text="",
            icon=icon.REMOVE).target = target.DECREASE_HEIGHT
        row.prop(context.scene, "bakeHeight", text="")
        row.operator(
            brm.UI_INCREMENT,
            text="",
            icon=icon.ADD).target = target.INCREASE_HEIGHT
        row = col.row(align=True)
        row.label(text="Padding:")
        row.prop(context.scene.render.bake, "margin", text="")
        col = layout.column(align=True)
        col.separator()
        col.prop(context.scene, "bakeFolder", text="")
        row = col.row(align=True)
        row.label(text="Filename:")
        row.prop(context.scene, "bakePrefix", text="")
        col.separator()
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.enabled = not context.scene.UseLowOnly
        if not context.scene.bakeNormal:
            row.prop(
                context.scene,
                "bakeNormal",
                icon=icon.SHADING_RENDERED,
                text="Tangent Normal")
        if context.scene.bakeNormal:
            row.prop(
                context.scene,
                "bakeNormal",
                icon=icon.SHADING_RENDERED,
                text=" ")
            row.prop(context.scene, "affixNormal", text="")
            row.prop(context.scene, "samplesNormal", text="")
        row = col.row(align=True)
        row.enabled = not context.scene.UseLowOnly
        if not context.scene.bakeObject:
            row.prop(
                context.scene,
                "bakeObject",
                icon=icon.SHADING_RENDERED,
                text="Object Normal")
        if context.scene.bakeObject:
            row.prop(
                context.scene,
                "bakeObject",
                icon=icon.SHADING_RENDERED,
                text=" ")
            row.prop(context.scene, "affixObject", text="")
            row.prop(context.scene, "samplesObject", text="")
        row = col.row(align=True)
        if not context.scene.bakeAO:
            row.prop(
                context.scene,
                "bakeAO",
                icon=icon.SHADING_SOLID,
                text="Occlusion")
        if context.scene.bakeAO:
            row.prop(context.scene, "bakeAO", icon=icon.SHADING_SOLID, text=" ")
            row.prop(context.scene, "affixAO", text="")
            row.prop(context.scene, "samplesAO", text="")
        row = col.row(align=True)
        row.enabled = not context.scene.UseLowOnly
        if not context.scene.bakeColor:
            row.prop(
                context.scene,
                "bakeColor",
                icon=icon.SHADING_TEXTURE,
                text="Color")
        if context.scene.bakeColor:
            row.prop(
                context.scene,
                "bakeColor",
                icon=icon.SHADING_TEXTURE,
                text=" ")
            row.prop(context.scene, "affixColor", text="")
            row.prop(context.scene, "samplesColor", text="")
        row = col.row(align=True)
        row.enabled = not context.scene.UseLowOnly
        if not context.scene.bakeRoughness:
            row.prop(
                context.scene,
                "bakeRoughness",
                icon=icon.SHADING_TEXTURE,
                text="Roughness")
        if context.scene.bakeRoughness:
            row.prop(
                context.scene,
                "bakeRoughness",
                icon=icon.SHADING_TEXTURE,
                text=" ")
            row.prop(context.scene, "affixRoughness", text="")
            row.prop(context.scene, "samplesRoughness", text="")
        row = col.row(align=True)
        row.enabled = not context.scene.UseLowOnly
        if not context.scene.bakeEmission:
            row.prop(
                context.scene,
                "bakeEmission",
                icon=icon.SHADING_TEXTURE,
                text="Emission")
        if context.scene.bakeEmission:
            row.prop(
                context.scene,
                "bakeEmission",
                icon=icon.SHADING_TEXTURE,
                text=" ")
            row.prop(context.scene, "affixEmission", text="")
            row.prop(context.scene, "samplesEmission", text="")
        row = col.row(align=True)
        if not context.scene.bakeUV:
            row.prop(
                context.scene,
                "bakeUV",
                icon=icon.SHADING_WIRE,
                text="UV Snapshot")
        if context.scene.bakeUV:
            row.prop(context.scene, "bakeUV", icon=icon.SHADING_WIRE, text=" ")
            row.prop(context.scene, "affixUV", text="")
            row.prop(context.scene, "bakeUV", icon=icon.BLANK1, text=" ")
        col = layout.column(align=True)
        col.separator()
        row = col.row(align=True)
        op = row.operator("brm.bake", text="BAKE", icon=icon.RENDER_RESULT)
        row.prop(context.scene, "UseLowOnly", icon=icon.MESH_ICOSPHERE, text="")


class EasyBakeUIIncrement(bpy.types.Operator):
    """Double or half the size of the render target"""
    bl_idname = brm.UI_INCREMENT
    bl_label = "increment"

    def options(self, context):
        return (
            (target.INCREASE_WIDTH, "Increase Width", "Double the width"),
            (target.INCREASE_HEIGHT, "Increase Height", "Double the height"),
            (target.DECREASE_WIDTH, "Decrease Width", "Half the width"),
            (target.DECREASE_HEIGHT, "Decrease Height", "Half the height")
        )

    target: bpy.props.EnumProperty(items=options)

    def execute(self, context):
        if self.target == target.INCREASE_WIDTH:
            context.scene.bakeWidth = context.scene.bakeWidth * 2
        elif self.target == target.INCREASE_HEIGHT:
            context.scene.bakeHeight = context.scene.bakeHeight * 2
        elif self.target == target.DECREASE_HEIGHT and context.scene.bakeHeight > 4:
            context.scene.bakeHeight = context.scene.bakeHeight / 2
        elif self.target == target.DECREASE_WIDTH and context.scene.bakeWidth > 4:
            context.scene.bakeWidth = context.scene.bakeWidth / 2
        else:
            pass
        return {bln.FINISHED}


class EasyBakeUIHide(bpy.types.Operator):
    """hide object"""
    bl_idname = brm.UI_HIDE
    bl_label = "Hide"
    bl_options = {bln.UNDO}
    targetmesh: bpy.props.StringProperty()

    def execute(self, context):
        if bpy.context.object.mode == bln.EDIT:
            bpy.ops.object.mode_set(mode=bln.OBJECT)
        target = context.scene.lowpoly
        if not self.targetmesh:
            self.targetmesh = "lowpoly"
        if self.targetmesh == "hipoly":
            target = context.scene.hipoly
        if target is None and target not in bpy.data.collections:
            self.report(
                {bln.WARNING},
                "Select a valid {0} object or collection!".format(self.targetmesh))
            return {bln.FINISHED}
        else:
            if hidden(target):
                unhide(target)
            else:
                hide(target)
        return {bln.FINISHED}


class EasyBakeUIToggle(bpy.types.Operator):
    """toggle lowpoly/hipoly"""
    bl_idname = brm.UI_TOGGLE
    bl_label = "Toggle"
    bl_options = {bln.UNDO}

    def execute(self, context):
        if bpy.context.object.mode == bln.EDIT:
            bpy.ops.object.mode_set(mode=bln.OBJECT)
        # test lowpoly/hipoly exists
        if context.scene.lowpoly is None and context.scene.lowpoly not in bpy.data.collections:
            self.report({bln.WARNING}, "Select a valid lowpoly object or group!")
            return {bln.FINISHED}
        if context.scene.hipoly is None and context.scene.hipoly not in bpy.data.collections:
            self.report({bln.WARNING}, "Select a valid hipoly object or group!")
            return {bln.FINISHED}
        if hidden(context.scene.hipoly):
            hide(context.scene.lowpoly)
            unhide(context.scene.hipoly)
        else:
            unhide(context.scene.lowpoly)
            hide(context.scene.hipoly)
        return {bln.FINISHED}


class EasyBake(bpy.types.Operator):
    """Bake and save textures"""
    bl_idname = "brm.bake"
    bl_label = "set normal"
    bl_options = {bln.UNDO}

    def execute(self, context):
        # test if everything is set up OK first:
        # test folder
        hipoly_inactive = hidden(context.scene.hipoly)
        lopoly_incative = hidden(context.scene.lowpoly)
        hasfolder = os.access(context.scene.bakeFolder, os.W_OK)
        if hasfolder is False:
            self.report({bln.WARNING}, "Select a valid export folder!")
            return {bln.FINISHED}
        # test lowpoly/hipoly/cage exists
        if context.scene.lowpoly is None and context.scene.lowpoly not in bpy.data.collections:
            self.report(
                {bln.WARNING},
                "Select a valid lowpoly object or collection!")
            return {bln.FINISHED}
        if context.scene.hipoly is None and context.scene.hipoly not in bpy.data.collections and not context.scene.UseLowOnly:
            self.report(
                {bln.WARNING},
                "Select a valid hipoly object or collection!")
            return {bln.FINISHED}
        if bpy.data.objects.get(
                context.scene.cage) is None and context.scene.cageEnabled:
            self.report({bln.WARNING}, "Select a valid cage object!")
            return {bln.FINISHED}
        # test if lowpoly, highpoly and cage objects are actually models
        lowpolymeshes = 0
        if context.scene.lowpoly.bl_rna.name == rna.COLLECTION:
            for o in bpy.context.scene.lowpoly.all_objects:
                if o.type == bln.MESH:
                    lowpolymeshes += 1
        else:
            if context.scene.lowpoly.type == bln.MESH:
                lowpolymeshes = 1
        if lowpolymeshes == 0:
            self.report({bln.WARNING}, "lowpoly needs to have a mesh!")
            return {bln.FINISHED}
        if not context.scene.UseLowOnly:
            hipolymeshes = 0
            if context.scene.hipoly.bl_rna.name == rna.COLLECTION:
                for o in bpy.context.scene.hipoly.all_objects:
                    if o.type == bln.MESH:
                        hipolymeshes += 1
            else:
                if context.scene.hipoly.type == bln.MESH:
                    hipolymeshes = 1
            if hipolymeshes == 0:
                self.report({bln.WARNING}, "hipoly needs to have a mesh!")
                return {bln.FINISHED}
        if context.scene.cageEnabled and bpy.data.objects[context.scene.cage].type != bln.MESH:
            self.report({bln.WARNING}, "cage needs to be a mesh!")
            return {bln.FINISHED}
        # setup
    # HOTFIX get out of local view
        if context.space_data.local_view:
            bpy.ops.view3d.localview()
    # 1 unhide everything to be baked
        if not context.scene.UseLowOnly:
            unhide(context.scene.hipoly)
        unhide(context.scene.lowpoly)
        # temporary until I figure out how hiding is actually handled
        bpy.ops.object.hide_view_clear()
    # 2 make sure we are in object mode and nothing is selected
        try:
            if bpy.context.object.mode == bln.EDIT:
                bpy.ops.object.mode_set(mode=bln.OBJECT)
        except AttributeError:
            pass
        bpy.ops.object.select_all(action=bln.DESELECT)
    # 3 setup lowpoly for baking
        lowpolyobject = "null"
        orig_lowpoly = None
        # if collection, create temporary lowpoly object
        if context.scene.lowpoly.bl_rna.name == rna.COLLECTION:
            context.scene.lowpoly.hide_render = False
            for o in bpy.context.scene.lowpoly.all_objects:
                # if context.scene.lowpoly is None:
                #    context.scene.lowpoly.hide_render = False
                #    for o in context.scene.lowpoly.objects:
                if o.type == bln.MESH:
                    o.hide_viewport = False
                    o.select_set(state=True)
                    context.view_layer.objects.active = o
                    o.hide_render = True
            # duplicate selected and combine into new object
            bpy.ops.object.duplicate()
            bpy.ops.object.join()
            bpy.ops.object.transform_apply(
                location=False, rotation=True, scale=True)
            lowpolyobject = bpy.context.selected_objects[0].name
            bpy.data.objects[lowpolyobject].hide_render = False
        else:
            context.scene.lowpoly.hide_viewport = False
            context.scene.lowpoly.hide_render = False
            context.scene.lowpoly.select_set(state=True)
            orig_lowpoly = context.scene.lowpoly
            lowpolyobject = context.scene.lowpoly
    # test if cage has same tri count:
        if context.scene.cageEnabled:
            vcount_low = len(bpy.data.objects[lowpolyobject].data.vertices)
            vcount_cage = len(
                bpy.data.objects[context.scene.cage].data.vertices)
            if vcount_low != vcount_cage:
                if context.scene.lowpolyGroup:
                    bpy.ops.object.select_all(action=bln.DESELECT)
                    bpy.data.objects[lowpolyobject].select_set(state=True)
                    bpy.ops.object.delete(use_global=False)
                self.report(
                    {bln.WARNING},
                    "cage and low poly vertex count don't match!")
                return {bln.FINISHED}
    # 4 test if lowpoly has a material and UV
        # if len(context.scene.lowpoly.data.materials) == 0:
        #    if context.scene.lowpolyGroup:
        #        bpy.ops.object.select_all(action=bln.DESELECT)
        #        bpy.data.objects[lowpolyobject].select_set(state=True)
        #        bpy.ops.object.delete(use_global=False)
        #    self.report({bln.WARNING}, "Material required on low poly mesh!")
        #    return {bln.FINISHED}
        # if len(context.scene.lowpoly.data.uv_layers) == 0:
        #    if context.scene.lowpolyGroup:
        #        bpy.ops.object.select_all(action=bln.DESELECT)
        #        bpy.data.objects[lowpolyobject].select_set(state=True)
        #        bpy.ops.object.delete(use_global=False)
        #    self.report({bln.WARNING}, "low poly mesh has no UV!")
        #    return {bln.FINISHED}
    # 5 remember render engine and switch to CYCLES for baking
        orig_renderer = bpy.data.scenes[bpy.context.scene.name].render.engine
        bpy.data.scenes[bpy.context.scene.name].render.engine = bln.CYCLES
    # 6 create temporary bake image and material
        bakeimage = bpy.data.images.new(
            "BakeImage",
            width=context.scene.bakeWidth,
            height=context.scene.bakeHeight)
        bakemat = bpy.data.materials.new(name="bakemat")
        bakemat.use_nodes = True
    # 7 select hipoly target
        if not context.scene.UseLowOnly:
            # select hipoly object or collection:
            if context.scene.hipoly.bl_rna.name == rna.COLLECTION:
                context.scene.hipoly.hide_render = False
                for o in bpy.context.scene.hipoly.all_objects:
                    if o.type == bln.MESH:
                        o.hide_viewport = False
                        o.hide_render = False
                        o.select_set(state=True)
            else:
                context.scene.hipoly.hide_viewport = False
                context.scene.hipoly.hide_render = False
                context.scene.hipoly.select_set(state=True)
    # 8 select lowpoly target
        print("whats happening here?")
        print(context.scene.lowpoly)
        print(lowpolyobject)
        if isinstance(context.scene.lowpoly, bpy.types.Collection):
            bpy.context.view_layer.objects.active = bpy.data.objects[lowpolyobject]
        else:
            bpy.context.view_layer.objects.active = lowpolyobject
    # 9 select lowpoly material and create temporary render target
        orig_mat = None
        if bpy.context.active_object.data.materials:
            orig_mat = bpy.context.active_object.data.materials[0]
            bpy.context.active_object.data.materials[0] = bakemat
        else:
            bpy.context.active_object.data.materials.append(bakemat)
        bpy.context.active_object.active_material_index = 0
        node_tree = bakemat.node_tree
        node = node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        node_tree.nodes.active = node
        node.image = bakeimage
    # 10 check if theres a cage to be used
        if context.scene.cageEnabled:
            bpy.context.scene.render.bake.use_cage = True
            bpy.context.scene.render.bake.cage_object = bpy.data.objects[context.scene.cage]
        else:
            bpy.context.scene.render.bake.use_cage = False
    # 11 bake all maps!
        if context.scene.bakeNormal and not context.scene.UseLowOnly:
            bpy.context.scene.cycles.samples = context.scene.samplesNormal
            bpy.ops.object.bake(
                type=bln.NORMAL,
                use_clear=True,
                use_selected_to_active=True,
                normal_space=bln.TANGENT)
            bakeimage.filepath_raw = context.scene.bakeFolder + \
                context.scene.bakePrefix + context.scene.affixNormal + ".tga"
            bakeimage.file_format = bln.TARGA
            bakeimage.save()
        if context.scene.bakeObject and not context.scene.UseLowOnly:
            bpy.context.scene.cycles.samples = context.scene.samplesObject
            bpy.ops.object.bake(
                type=bln.NORMAL,
                use_clear=True,
                use_selected_to_active=True,
                normal_space=bln.OBJECT)
            bakeimage.filepath_raw = context.scene.bakeFolder + \
                context.scene.bakePrefix + context.scene.affixObject + ".tga"
            bakeimage.file_format = bln.TARGA
            bakeimage.save()
        if context.scene.bakeAO:
            bpy.context.scene.cycles.samples = context.scene.samplesAO
            bpy.ops.object.bake(
                type=bln.AO,
                use_clear=True,
                use_selected_to_active=not context.scene.UseLowOnly)
            bakeimage.filepath_raw = context.scene.bakeFolder + \
                context.scene.bakePrefix + context.scene.affixAO + ".tga"
            bakeimage.file_format = bln.TARGA
            bakeimage.save()
        if context.scene.bakeColor and not context.scene.UseLowOnly:
            bpy.context.scene.cycles.samples = context.scene.samplesColor
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True
            bpy.ops.object.bake(
                type=bln.DIFFUSE,
                use_clear=True,
                use_selected_to_active=True)
            bakeimage.filepath_raw = context.scene.bakeFolder + \
                context.scene.bakePrefix + context.scene.affixColor + ".tga"
            bakeimage.file_format = bln.TARGA
            bakeimage.save()
        if context.scene.bakeRoughness and not context.scene.UseLowOnly:
            bpy.context.scene.cycles.samples = context.scene.samplesRoughness
            bpy.ops.object.bake(
                type=bln.ROUGHNESS,
                use_clear=True,
                use_selected_to_active=True)
            bakeimage.filepath_raw = context.scene.bakeFolder + \
                context.scene.bakePrefix + context.scene.affixRoughness + ".tga"
            bakeimage.file_format = bln.TARGA
            bakeimage.save()
        if context.scene.bakeEmission and not context.scene.UseLowOnly:
            bpy.context.scene.cycles.samples = context.scene.samplesEmission
            bpy.ops.object.bake(
                type=bln.EMIT,
                use_clear=True,
                use_selected_to_active=True)
            bakeimage.filepath_raw = context.scene.bakeFolder + \
                context.scene.bakePrefix + context.scene.affixEmission + ".tga"
            bakeimage.file_format = bln.TARGA
            bakeimage.save()
        # UV SNAPSHOT
        if context.scene.bakeUV:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action=bln.SELECT)
            bpy.ops.object.editmode_toggle()
            original_type = bpy.context.area.type
            bpy.context.area.type = bln.IMAGE_EDITOR
            uvfilepath = context.scene.bakeFolder + \
                context.scene.bakePrefix + context.scene.affixUV + ".png"
            bpy.ops.uv.export_layout(
                filepath=uvfilepath,
                size=(
                    context.scene.bakeWidth,
                    context.scene.bakeHeight))
            bpy.context.area.type = original_type
        # cleanup temporary objects and materials
        bpy.ops.object.select_all(action=bln.DESELECT)
        if not context.scene.lowpolyGroup:
            orig_lowpoly.select_set(state=True)
        bpy.data.images.remove(bakeimage)
        bakemat.node_tree.nodes.remove(node)
        bpy.data.materials.remove(bakemat)
        if orig_mat:
            bpy.context.active_object.data.materials[0] = orig_mat
        bpy.data.scenes[bpy.context.scene.name].render.engine = orig_renderer
        if context.scene.lowpolyGroup:
            bpy.ops.object.select_all(action=bln.DESELECT)
            bpy.data.objects[lowpolyobject].select_set(state=True)
            bpy.ops.object.delete(use_global=False)
        # reload all textures
        for image in bpy.data.images:
            image.reload()
        # rehide back to original state
        if not lopoly_incative:
            if isinstance(context.scene.lowpoly, bpy.types.Collection):
                for o in context.scene.lowpoly.objects:
                    o.hide_viewport = False
                    context.view_layer.objects.active = o
            else:
                context.scene.lowpoly.hide_viewport = False
                context.view_layer.objects.active = context.scene.lowpoly
        else:
            if context.scene.lowpoly is None:
                for o in context.scene.lowpoly.objects:
                    o.hide_viewport = True
            else:
                context.scene.lowpoly.hide_viewport = True
        if not context.scene.UseLowOnly:
            if not hipoly_inactive:
                if isinstance(context.scene.hipoly, bpy.types.Collection):
                    for o in context.scene.hipoly.objects:
                        o.hide_viewport = False
                        context.view_layer.objects.active = o
                else:
                    context.scene.hipoly.hide_viewport = False
                    context.view_layer.objects.active = context.scene.hipoly
            else:
                if context.scene.hipoly is None:
                    for o in context.scene.hipoly.objects:
                        o.hide_viewport = True
                else:
                    context.scene.hipoly.hide_viewport = True
        return {bln.FINISHED}


classes = (
    EasyBake,
    EasyBakeUIHide,
    PANEL_PT_EasyBakeUIPanel,
    EasyBakeUIToggle,
    EasyBakeUIIncrement,
)


def register():
    for b_cls in classes:
        bpy.utils.register_class(b_cls)
    bpy.types.Scene.lowpoly = bpy.props.PointerProperty(
        name="lowpoly", type=bpy.types.Object, description="lowpoly object")
    bpy.types.Scene.lowpolyGroup = bpy.props.BoolProperty(
        name="lowpolyGroup", default=False, description="enable lowpoly collection")
    bpy.types.Scene.hipoly = bpy.props.PointerProperty(
        name="hipoly", type=bpy.types.Object, description="hipoly object or group")
    bpy.types.Scene.hipolyGroup = bpy.props.BoolProperty(
        name="hipolyGroup", default=False, description="enable hipoly collection")
    bpy.types.Scene.cage = bpy.props.StringProperty(
        name="cage", default="cage", description="cage object")
    bpy.types.Scene.cageActive = bpy.props.BoolProperty(
        name="cageActive", default=True, description="cageActive")
    bpy.types.Scene.cageEnabled = bpy.props.BoolProperty(
        name="cageEnabled", default=False, description="Enable cage object for baking")
    bpy.types.Scene.bakeNormal = bpy.props.BoolProperty(
        name="bakeNormal", default=False, description="Bake Tangent Space Normal Map")
    bpy.types.Scene.bakeObject = bpy.props.BoolProperty(
        name="bakeObject", default=False, description="Bake Object Space Normal Map")
    bpy.types.Scene.bakeAO = bpy.props.BoolProperty(
        name="bakeAO", default=False, description="Bake Ambient Occlusion Map")
    bpy.types.Scene.bakeColor = bpy.props.BoolProperty(
        name="bakeColor", default=False, description="Bake Albedo Color Map")
    bpy.types.Scene.bakeRoughness = bpy.props.BoolProperty(
        name="bakeRoughness", default=False, description="Bake Roughness Map")
    bpy.types.Scene.bakeEmission = bpy.props.BoolProperty(
        name="bakeEmission", default=False, description="Bake Emission Map")
    bpy.types.Scene.bakeUV = bpy.props.BoolProperty(
        name="bakeUV",
        default=False,
        description="Bake UV Wireframe Snapshot of Lowpoly Mesh")
    bpy.types.Scene.samplesNormal = bpy.props.IntProperty(
        name="samplesNormal",
        default=8,
        description="Tangent Space Normal Map Sample Count")
    bpy.types.Scene.samplesObject = bpy.props.IntProperty(
        name="samplesObject",
        default=8,
        description="Object Space Normal Map Sample Count")
    bpy.types.Scene.samplesAO = bpy.props.IntProperty(
        name="samplesAO", default=128, description="Ambient Occlusion Map Sample Count")
    bpy.types.Scene.samplesColor = bpy.props.IntProperty(
        name="samplesColor", default=1, description="Color Map Sample Count")
    bpy.types.Scene.samplesEmission = bpy.props.IntProperty(
        name="samplesEmission", default=1, description="Emission Map Sample Count")
    bpy.types.Scene.samplesRoughness = bpy.props.IntProperty(
        name="samplesRoughness", default=1, description="Roughness Map Sample Count")
    bpy.types.Scene.bakeWidth = bpy.props.IntProperty(
        name="bakeWidth", default=512, description="Export Texture Width")
    bpy.types.Scene.bakeHeight = bpy.props.IntProperty(
        name="bakeHeight", default=512, description="Export Texture Height")
    bpy.types.Scene.bakePrefix = bpy.props.StringProperty(
        name="bakePrefix", default="export", description="export filename")
    bpy.types.Scene.bakeFolder = bpy.props.StringProperty(
        name="bakeFolder",
        default="C:\\export\\",
        description="destination folder",
        subtype=bln.DIR_PATH)
    bpy.types.Scene.UseLowOnly = bpy.props.BoolProperty(
        name="UseLowOnly", default=False, description="Only bake lowpoly on itself")
    bpy.types.Scene.affixNormal = bpy.props.StringProperty(
        name="affixNormal", default="_normal", description="normal map affix")
    bpy.types.Scene.affixObject = bpy.props.StringProperty(
        name="affixObject", default="_object", description="object normal map affix")
    bpy.types.Scene.affixAO = bpy.props.StringProperty(
        name="affixAO", default="_ao", description="AO map affix")
    bpy.types.Scene.affixColor = bpy.props.StringProperty(
        name="affixColor", default="_color", description="color map affix")
    bpy.types.Scene.affixRoughness = bpy.props.StringProperty(
        name="affixRoughness", default="_rough", description="Roughness map affix")
    bpy.types.Scene.affixEmission = bpy.props.StringProperty(
        name="affixEmission", default="_emit", description="Emission map affix")
    bpy.types.Scene.affixUV = bpy.props.StringProperty(
        name="affixUV", default="_uv", description="UV map affix")


def unregister():
    for b_cls in reversed(classes):
        bpy.utils.unregister_class(b_cls)


if __name__ == "__main__":
    register()
