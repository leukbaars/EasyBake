#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! -Bram

bl_info = {
    "name": "EasyBake",
    "category": "3D View",
    "blender": (2, 80, 0),
    "author": "Bram Eulaers",
    "description": "Simple texture baking UI for fast iteration. Can be found in the 3D View Sidebar under 'bake'."
    }

import bpy
import os
import bmesh
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatProperty, IntProperty



def unhide(objectType):
    if bpy.data.objects.get(objectType) is None:
        for o in bpy.data.collections[objectType].objects:
            o.hide_viewport = False
    else:
        bpy.data.objects[objectType].hide_viewport = False

def hide(objectType):
    if bpy.data.objects.get(objectType) is None:
        for o in bpy.data.collections[objectType].objects:
            o.hide_viewport = True
    else:
        bpy.data.objects[objectType].hide_viewport = True


class EasyBakeUIPanel(bpy.types.Panel):
    """EasyBakeUIPanel Panel"""
    bl_label = "EasyBake"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Bake"


    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='SCENE')

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)

        row = col.row(align = True)
        row.prop(context.scene, "lowpolyGroup", text="", icon="GROUP")
        if context.scene.lowpolyGroup is True:
            row.prop_search(context.scene, "lowpoly", bpy.data, "collections", text="", icon="MESH_ICOSPHERE")
        if context.scene.lowpolyGroup is False:
            row.prop_search(context.scene, "lowpoly", context.scene, "objects", text="", icon="MESH_ICOSPHERE")
        
        

        if context.scene.lowpolyActive is True:
            hideicon = "HIDE_OFF"
        if context.scene.lowpolyActive is False:
            hideicon = "HIDE_ON"
        op = row.operator("brm.bakeuihide", text="", icon=hideicon)
        op.targetmesh = "lowpoly"
        
        row = col.row(align = True)

        row.prop(context.scene, "hipolyGroup", text="", icon="GROUP")
        if context.scene.hipolyGroup is True:
            row.prop_search(context.scene, "hipoly", bpy.data, "collections", text="", icon="MESH_UVSPHERE")
        if context.scene.hipolyGroup is False:
            row.prop_search(context.scene, "hipoly", context.scene, "objects", text="", icon="MESH_UVSPHERE")

        row.enabled = not context.scene.UseLowOnly
        
        

        if context.scene.hipolyActive is True:
            hideicon = "HIDE_OFF"
        if context.scene.hipolyActive is False:
            hideicon = "HIDE_ON"
        op = row.operator("brm.bakeuihide", text="", icon=hideicon)
        op.targetmesh = "hipoly"

        

        col = box.column(align=True)
        row = col.row(align = True)
        row.operator("brm.bakeuitoggle", text="Toggle hi/low", icon="FILE_REFRESH")
        #row.prop(context.scene, "UseBlenderGame", icon="MESH_UVSPHERE", text="")

        col = layout.column(align=True)

        col.separator()
        row = col.row(align = True)
        row.prop(context.scene.render.bake, "cage_extrusion", text="Ray Distance")
        row.prop(context.scene, "cageEnabled", icon="OBJECT_DATAMODE", text="")
        row = col.row(align = True)
        #row.enabled = context.scene.cageEnabled
        
        if context.scene.cageEnabled:
            op = row.prop_search(context.scene, "cage", bpy.data, "objects", text="", icon="MESH_UVSPHERE")
        #op.enabled = context.scene.cageEnabled
        
        col.separator()

        box = layout.box()
        col = box.column(align=True)

        row = col.row(align = True)
        row.label(text="Width:")
        row.operator("brm.bakeuiincrement", text="", icon="REMOVE").target = "width/2"
        row.prop(context.scene, "bakeWidth", text="")
        row.operator("brm.bakeuiincrement", text="", icon="ADD").target = "width*2"
        
        row = col.row(align = True)
        row.label(text="Height:")
        row.operator("brm.bakeuiincrement", text="", icon="REMOVE").target = "height/2"
        row.prop(context.scene, "bakeHeight", text="")
        row.operator("brm.bakeuiincrement", text="", icon="ADD").target = "height*2"
        row = col.row(align = True)
        row.label(text="Padding:")
        row.prop(context.scene.render.bake, "margin", text="")
        
        

        col = layout.column(align=True)
        col.separator()
        col.prop(context.scene, 'bakeFolder', text="")
        row = col.row(align = True)
        row.label(text="Filename:")
        row.prop(context.scene, "bakePrefix", text="")
        
        col.separator()

        box = layout.box()
        col = box.column(align=True)
        
        row = col.row(align = True)
        row.enabled = not context.scene.UseLowOnly
        row.prop(context.scene, "bakeNormal", icon="SHADING_RENDERED", text="Tangent Normal")
        if context.scene.bakeNormal:
            row.prop(context.scene, "samplesNormal", text="")

        row = col.row(align = True)
        row.enabled = not context.scene.UseLowOnly
        row.prop(context.scene, "bakeObject", icon="SHADING_RENDERED", text="Object Normal")
        if context.scene.bakeObject:
            row.prop(context.scene, "samplesObject", text="")
        row = col.row(align = True)
        row.prop(context.scene, "bakeAO", icon="SHADING_SOLID", text="Occlusion")
        if context.scene.bakeAO:
            row.prop(context.scene, "samplesAO", text="")
        
        row = col.row(align = True)
        row.enabled = not context.scene.UseLowOnly
        row.prop(context.scene, "bakeColor", icon="SHADING_TEXTURE", text="Color")
        if context.scene.bakeColor:
            row.prop(context.scene, "samplesColor", text="")

        row = col.row(align = True)
        row.enabled = not context.scene.UseLowOnly
        row.prop(context.scene, "bakeRoughness", icon="SHADING_TEXTURE", text="Roughness")
        if context.scene.bakeRoughness:
            row.prop(context.scene, "samplesRoughness", text="")

        row = col.row(align = True)
        row.prop(context.scene, "bakeUV", icon="SHADING_WIRE", text="UV Snapshot")
        
        
        
        col = layout.column(align=True)
        col.separator()
        row = col.row(align = True)
        op = row.operator("brm.bake", text="BAKE", icon="RENDER_RESULT")
        row.prop(context.scene, "UseLowOnly", icon="MESH_ICOSPHERE", text="")
        











class EasyBakeUIToggle(bpy.types.Operator):
    """toggle lowpoly/hipoly"""
    bl_idname = "brm.bakeuitoggle"
    bl_label = "Toggle"
    bl_options = {"UNDO"}

    def execute(self, context):

        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        #test lowpoly/hipoly exists
        if bpy.data.objects.get(context.scene.lowpoly) is None and not context.scene.lowpoly in bpy.data.collections:
            self.report({'WARNING'}, "Select a valid lowpoly object or group!")
            return {'FINISHED'}
        if bpy.data.objects.get(context.scene.hipoly) is None and not context.scene.hipoly in bpy.data.collections:
            self.report({'WARNING'}, "Select a valid hipoly object or group!")
            return {'FINISHED'}

        if context.scene.lowpolyActive is True:
            context.scene.lowpolyActive = False
            hide(context.scene.lowpoly)
            context.scene.hipolyActive = True
            unhide(context.scene.hipoly)
        else:
            context.scene.lowpolyActive = True
            unhide(context.scene.lowpoly)
            context.scene.hipolyActive = False
            hide(context.scene.hipoly)

        return {'FINISHED'}







class EasyBakeUIIncrement(bpy.types.Operator):
    """multiply/divide value"""
    bl_idname = "brm.bakeuiincrement"
    bl_label = "increment"

    target = bpy.props.StringProperty()

    def execute(self, context):
        if self.target == "width/2" and context.scene.bakeWidth > 4:
            context.scene.bakeWidth = context.scene.bakeWidth / 2
        if self.target == "width*2":
            context.scene.bakeWidth = context.scene.bakeWidth * 2
        if self.target == "height/2" and context.scene.bakeHeight > 4:
            context.scene.bakeHeight = context.scene.bakeHeight / 2
        if self.target == "height*2":
            context.scene.bakeHeight = context.scene.bakeHeight * 2
        return {'FINISHED'}












class EasyBakeUIHide(bpy.types.Operator):
    """hide object"""
    bl_idname = "brm.bakeuihide"
    bl_label = "hide"
    bl_options = {"UNDO"}

    targetmesh = bpy.props.StringProperty()

    def execute(self, context):

        #test lowpoly/hipoly exists
        
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        

        if self.targetmesh == "lowpoly":

            if bpy.data.objects.get(context.scene.lowpoly) is None and not context.scene.lowpoly in bpy.data.collections:
                self.report({'WARNING'}, "Select a valid lowpoly object or collection!")
                return {'FINISHED'}

            else:
                if context.scene.lowpolyActive is True:
                    context.scene.lowpolyActive = False
                    hide(context.scene.lowpoly)
                else:
                    context.scene.lowpolyActive = True
                    unhide(context.scene.lowpoly)

        if self.targetmesh == "hipoly":

            if bpy.data.objects.get(context.scene.hipoly) is None and not context.scene.hipoly in bpy.data.collections:
                self.report({'WARNING'}, "Select a valid hipoly object or collection!")
                return {'FINISHED'}

            else:
                if context.scene.hipolyActive is True:
                    context.scene.hipolyActive = False
                    hide(context.scene.hipoly)
                else:
                    context.scene.hipolyActive = True
                    unhide(context.scene.hipoly)

        return {'FINISHED'}













class EasyBake(bpy.types.Operator):
    """Bake and save textures"""
    bl_idname = "brm.bake"
    bl_label = "set normal"
    bl_options = {"UNDO"}
    

    def execute(self, context):  
        
        #test if everything is set up OK first:
        #test folder
        hasfolder = os.access(context.scene.bakeFolder, os.W_OK)
        if hasfolder is False:
            self.report({'WARNING'}, "Select a valid export folder!")
            return {'FINISHED'}


        #test lowpoly/hipoly/cage exists
        if bpy.data.objects.get(context.scene.lowpoly) is None and not context.scene.lowpoly in bpy.data.collections:
            self.report({'WARNING'}, "Select a valid lowpoly object or collection!")
            return {'FINISHED'}
        if bpy.data.objects.get(context.scene.hipoly) is None and not context.scene.hipoly in bpy.data.collections and not context.scene.UseLowOnly:
            self.report({'WARNING'}, "Select a valid hipoly object or collection!")
            return {'FINISHED'}
        if bpy.data.objects.get(context.scene.cage) is None and context.scene.cageEnabled:
            self.report({'WARNING'}, "Select a valid cage object!")
            return {'FINISHED'}


        #test if lowpoly, highpoly and cage objects are actually models
        lowpolymeshes = 0
        if bpy.data.objects.get(context.scene.lowpoly) is None:
            for o in bpy.data.collections[context.scene.lowpoly].objects:
                if o.type == 'MESH':
                    lowpolymeshes+=1
        else:
            if bpy.data.objects[context.scene.lowpoly].type == 'MESH':
                lowpolymeshes = 1
        if lowpolymeshes == 0:
            self.report({'WARNING'}, "lowpoly needs to have a mesh!")
            return {'FINISHED'}   
        
        hipolymeshes = 0
        if bpy.data.objects.get(context.scene.hipoly) is None:
            for o in bpy.data.collections[context.scene.hipoly].objects:
                if o.type == 'MESH':
                    hipolymeshes+=1
        else:
            if bpy.data.objects[context.scene.hipoly].type == 'MESH':
                hipolymeshes = 1
        if hipolymeshes == 0:
            self.report({'WARNING'}, "hipoly needs to have a mesh!")
            return {'FINISHED'}
        
        if context.scene.cageEnabled and bpy.data.objects[context.scene.cage].type != 'MESH':
            self.report({'WARNING'}, "cage needs to be a mesh!")
            return {'FINISHED'}

        
        #setup

    #HOTFIX get out of local view 
        if context.space_data.local_view:
            bpy.ops.view3d.localview()

    #1 unhide everything to be baked
        if not context.scene.UseLowOnly:
            unhide(context.scene.hipoly)
        unhide(context.scene.lowpoly)
        bpy.ops.object.hide_view_clear() #temporary until I figure out how hiding is actually handled
        
    #2 make sure we are in object mode and nothing is selected
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

    #3 setup lowpoly for baking
        lowpolyobject = "null"
        orig_lowpoly = None

        #if collection, create temporary lowpoly object
        if bpy.data.objects.get(context.scene.lowpoly) is None:   
            bpy.data.collections[context.scene.lowpoly].hide_render = False
            for o in bpy.data.collections[context.scene.lowpoly].objects:
                if o.type == 'MESH':
                    o.hide_viewport = False
                    o.select_set(state=True)
                    context.view_layer.objects.active = o
                    o.hide_render = True
            #duplicate selected and combine into new object
            bpy.ops.object.duplicate()
            bpy.ops.object.join()
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            lowpolyobject = bpy.context.selected_objects[0].name
            bpy.data.objects[lowpolyobject].hide_render = False
        else:
            bpy.data.objects[context.scene.lowpoly].hide_viewport = False
            bpy.data.objects[context.scene.lowpoly].hide_render = False
            bpy.data.objects[context.scene.lowpoly].select_set(state=True)
            orig_lowpoly = bpy.data.objects[context.scene.lowpoly]
            lowpolyobject = context.scene.lowpoly

    # test if cage has same tri count:
        if context.scene.cageEnabled:
            vcount_low = len(bpy.data.objects[lowpolyobject].data.vertices)
            vcount_cage = len(bpy.data.objects[context.scene.cage].data.vertices)
            if vcount_low != vcount_cage:
                if context.scene.lowpolyGroup:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.data.objects[lowpolyobject].select_set(state=True)
                    bpy.ops.object.delete(use_global=False)
                self.report({'WARNING'}, "cage and low poly vertex count don't match!")
                return {'FINISHED'}

    #4 test if lowpoly has a material and UV
        if len(bpy.data.objects[lowpolyobject].data.materials) == 0:
            if context.scene.lowpolyGroup:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[lowpolyobject].select_set(state=True)
                bpy.ops.object.delete(use_global=False)
            self.report({'WARNING'}, "Material required on low poly mesh!")
            return {'FINISHED'}

        if len(bpy.data.objects[lowpolyobject].data.uv_layers) == 0:
            if context.scene.lowpolyGroup:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[lowpolyobject].select_set(state=True)
                bpy.ops.object.delete(use_global=False)
            self.report({'WARNING'}, "low poly mesh has no UV!")
            return {'FINISHED'}

    #5 remember render engine and switch to CYCLES for baking
        orig_renderer = bpy.data.scenes[bpy.context.scene.name].render.engine
        bpy.data.scenes[bpy.context.scene.name].render.engine = "CYCLES"

    #6 create temporary bake image and material
        bakeimage = bpy.data.images.new("BakeImage", width=context.scene.bakeWidth, height=context.scene.bakeHeight)
        bakemat = bpy.data.materials.new(name="bakemat")
        bakemat.use_nodes = True

    #7 select hipoly target
        if not context.scene.UseLowOnly:
        #select hipoly object or collection:
            if bpy.data.objects.get(context.scene.hipoly) is None:
                bpy.data.collections[context.scene.hipoly].hide_render = False
                for o in bpy.data.collections[context.scene.hipoly].objects:
                    if o.type == 'MESH':
                        o.hide_viewport = False
                        o.hide_render = False
                        o.select_set(state=True)
            else:
                bpy.data.objects[context.scene.hipoly].hide_viewport = False
                bpy.data.objects[context.scene.hipoly].hide_render = False
                bpy.data.objects[context.scene.hipoly].select_set(state=True)

    #8 select lowpoly target
        bpy.context.view_layer.objects.active = bpy.data.objects[lowpolyobject]

    #9 select lowpoly material and create temporary render target
        orig_mat = bpy.context.active_object.data.materials[0]
        bpy.context.active_object.data.materials[0] = bakemat
        node_tree = bakemat.node_tree
        node = node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        node_tree.nodes.active = node
        node.image = bakeimage

    #10 check if theres a cage to be used
        if context.scene.cageEnabled:
            bpy.context.scene.render.bake.use_cage = True
            bpy.context.scene.render.bake.cage_object = bpy.data.objects[context.scene.cage]
        else:
            bpy.context.scene.render.bake.use_cage = False








    #11 bake all maps!
        if context.scene.bakeNormal and not context.scene.UseLowOnly:

            bpy.context.scene.cycles.samples = context.scene.samplesNormal
            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=True, normal_space='TANGENT')
            #bpy.ops.object.bake('INVOKE_DEFAULT', type='NORMAL', use_clear=True, use_selected_to_active=True, normal_space='TANGENT')

            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_normal.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()
        
        if context.scene.bakeObject and not context.scene.UseLowOnly:

            bpy.context.scene.cycles.samples = context.scene.samplesObject

            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=True, normal_space='OBJECT')

            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_object.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        if context.scene.bakeAO:

            bpy.context.scene.cycles.samples = context.scene.samplesAO

            bpy.ops.object.bake(type='AO', use_clear=True, use_selected_to_active=not context.scene.UseLowOnly)

            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_ao.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        if context.scene.bakeColor and not context.scene.UseLowOnly:

            bpy.context.scene.cycles.samples = context.scene.samplesColor
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True

            bpy.ops.object.bake(type='DIFFUSE', use_clear=True, use_selected_to_active=True)

            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_color.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()
        
        if context.scene.bakeRoughness and not context.scene.UseLowOnly:

            bpy.context.scene.cycles.samples = context.scene.samplesRoughness

            bpy.ops.object.bake(type='ROUGHNESS', use_clear=True, use_selected_to_active=True)

            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_roughness.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        #UV SNAPSHOT
        if context.scene.bakeUV:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.editmode_toggle()
            original_type = bpy.context.area.type
            bpy.context.area.type = "IMAGE_EDITOR"
            uvfilepath = context.scene.bakeFolder+context.scene.bakePrefix+"_uv.png"
            bpy.ops.uv.export_layout(filepath=uvfilepath, size=(context.scene.bakeWidth, context.scene.bakeHeight))
            bpy.context.area.type = original_type






        #cleanup temporary objects and materials
        bpy.ops.object.select_all(action='DESELECT')
        if not context.scene.lowpolyGroup:
            orig_lowpoly.select_set(state=True)
        bpy.data.images.remove(bakeimage)
        bakemat.node_tree.nodes.remove(node)
        bpy.data.materials.remove(bakemat)
        bpy.context.active_object.data.materials[0] = orig_mat
        bpy.data.scenes[bpy.context.scene.name].render.engine = orig_renderer

        if context.scene.lowpolyGroup:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[lowpolyobject].select_set(state=True)
            bpy.ops.object.delete(use_global=False)

        #reload all textures
        for image in bpy.data.images:
            image.reload()

        #rehide back to original state 
        if context.scene.lowpolyActive is True:
            if bpy.data.objects.get(context.scene.lowpoly) is None:
                for o in bpy.data.collections[context.scene.lowpoly].objects:
                    o.hide_viewport = False
                    context.view_layer.objects.active = o
            else:
                bpy.data.objects[context.scene.lowpoly].hide_viewport = False
                context.view_layer.objects.active = bpy.data.objects[context.scene.lowpoly]
        else:
            if bpy.data.objects.get(context.scene.lowpoly) is None:
                for o in bpy.data.collections[context.scene.lowpoly].objects:
                    o.hide_viewport = True
            else:
                bpy.data.objects[context.scene.lowpoly].hide_viewport = True

        if not context.scene.UseLowOnly:
            if context.scene.hipolyActive is True:
                if bpy.data.objects.get(context.scene.hipoly) is None:
                    for o in bpy.data.collections[context.scene.hipoly].objects:
                        o.hide_viewport = False
                        context.view_layer.objects.active = o
                else:
                    bpy.data.objects[context.scene.hipoly].hide_viewport = False
                    context.view_layer.objects.active = bpy.data.objects[context.scene.hipoly]
            else:
                if bpy.data.objects.get(context.scene.hipoly) is None:
                    for o in bpy.data.collections[context.scene.hipoly].objects:
                        o.hide_viewport = True
                else:
                    bpy.data.objects[context.scene.hipoly].hide_viewport = True

        return {'FINISHED'}














def register():
    bpy.utils.register_class(EasyBake)
    bpy.utils.register_class(EasyBakeUIHide)
    bpy.utils.register_class(EasyBakeUIPanel)
    bpy.utils.register_class(EasyBakeUIToggle)
    bpy.utils.register_class(EasyBakeUIIncrement)

    bpy.types.Scene.lowpoly = bpy.props.StringProperty (
        name = "lowpoly",
        default = "lowpoly",
        description = "lowpoly object",
        )
    bpy.types.Scene.lowpolyActive = bpy.props.BoolProperty (
        name = "lowpolyActive",
        default = True,
        description = "lowpolyActive",
        )
    bpy.types.Scene.lowpolyGroup = bpy.props.BoolProperty (
        name = "lowpolyGroup",
        default = False,
        description = "enable lowpoly collection",
        )
    bpy.types.Scene.hipoly = bpy.props.StringProperty (
        name = "hipoly",
        default = "hipoly",
        description = "hipoly object or group",
        )
    bpy.types.Scene.hipolyActive = bpy.props.BoolProperty (
        name = "hipolyActive",
        default = True,
        description = "hipolyActive",
        )
    bpy.types.Scene.hipolyGroup = bpy.props.BoolProperty (
        name = "hipolyGroup",
        default = False,
        description = "enable hipoly collection",
        )
    bpy.types.Scene.cage = bpy.props.StringProperty (
        name = "cage",
        default = "cage",
        description = "cage object",
        )
    bpy.types.Scene.cageActive = bpy.props.BoolProperty (
        name = "cageActive",
        default = True,
        description = "cageActive",
        )
    bpy.types.Scene.cageEnabled = bpy.props.BoolProperty (
        name = "cageEnabled",
        default = False,
        description = "Enable cage object for baking",
        )
    bpy.types.Scene.bakeNormal = bpy.props.BoolProperty (
        name = "bakeNormal",
        default = False,
        description = "Bake Tangent Space Normal Map",
        )
    bpy.types.Scene.bakeObject = bpy.props.BoolProperty (
        name = "bakeObject",
        default = False,
        description = "Bake Object Space Normal Map",
        )
    bpy.types.Scene.bakeAO = bpy.props.BoolProperty (
        name = "bakeAO",
        default = False,
        description = "Bake Ambient Occlusion Map",
        )
    bpy.types.Scene.bakeColor = bpy.props.BoolProperty (
        name = "bakeColor",
        default = False,
        description = "Bake Albedo Color Map",
        )
    bpy.types.Scene.bakeRoughness = bpy.props.BoolProperty (
        name = "bakeRoughness",
        default = False,
        description = "Bake Roughness Map",
        )
    
    bpy.types.Scene.bakeUV = bpy.props.BoolProperty (
        name = "bakeUV",
        default = False,
        description = "Bake UV Wireframe Snapshot of Lowpoly Mesh",
        )
    bpy.types.Scene.samplesNormal = bpy.props.IntProperty (
        name = "samplesNormal",
        default = 8,
        description = "Tangent Space Normal Map Sample Count",
        )
    bpy.types.Scene.samplesObject = bpy.props.IntProperty (
        name = "samplesObject",
        default = 8,
        description = "Object Space Normal Map Sample Count",
        )
    bpy.types.Scene.samplesAO = bpy.props.IntProperty (
        name = "samplesAO",
        default = 128,
        description = "Ambient Occlusion Map Sample Count",
        )
    bpy.types.Scene.samplesColor = bpy.props.IntProperty (
        name = "samplesColor",
        default = 1,
        description = "Color Map Sample Count",
        )
    bpy.types.Scene.samplesRoughness = bpy.props.IntProperty (
        name = "samplesRoughness",
        default = 1,
        description = "Roughness Map Sample Count",
        )
    bpy.types.Scene.bakeWidth = bpy.props.IntProperty (
        name = "bakeWidth",
        default = 512,
        description = "Export Texture Width",
        )  
    bpy.types.Scene.bakeHeight = bpy.props.IntProperty (
        name = "bakeHeight",
        default = 512,
        description = "Export Texture Height",
        )
    bpy.types.Scene.bakePrefix = bpy.props.StringProperty (
        name = "bakePrefix",
        default = "export",
        description = "export filename",
        )
    bpy.types.Scene.bakeFolder = bpy.props.StringProperty (
        name = "bakeFolder",
        default = "C:\\export\\",
        description = "destination folder",
        subtype = 'DIR_PATH'
        )
    bpy.types.Scene.UseBlenderGame = bpy.props.BoolProperty (
        name = "UseBlenderGame",
        default = True,
        description = "Use Blender Game for lowpoly display",
        )
    bpy.types.Scene.UseLowOnly = bpy.props.BoolProperty (
        name = "UseLowOnly",
        default = False,
        description = "Only bake lowpoly on itself",
        )

def unregister():
    bpy.utils.unregister_class(EasyBake)
    bpy.utils.unregister_class(EasyBakeUIHide)
    bpy.utils.unregister_class(EasyBakeUIPanel)
    bpy.utils.unregister_class(EasyBakeUIToggle)
    bpy.utils.unregister_class(EasyBakeUIIncrement)

    del bpy.types.Scene.lowpoly
    del bpy.types.Scene.lowpolyActive
    del bpy.types.Scene.hipoly
    del bpy.types.Scene.hipolyActive
    del bpy.types.Scene.cage
    del bpy.types.Scene.cageActive
    del bpy.types.Scene.cageEnabled
    del bpy.types.Scene.bakeNormal
    del bpy.types.Scene.bakeObject
    del bpy.types.Scene.bakeAO
    del bpy.types.Scene.bakeColor
    del bpy.types.Scene.bakeRoughness
    del bpy.types.Scene.bakeUV
    del bpy.types.Scene.samplesNormal
    del bpy.types.Scene.samplesAO
    del bpy.types.Scene.samplesColor
    del bpy.types.Scene.samplesRoughness
    del bpy.types.Scene.samplesObject
    del bpy.types.Scene.bakeWidth
    del bpy.types.Scene.bakeHeight
    del bpy.types.Scene.bakeFolder
    del bpy.types.Scene.UseBlenderGame
    del bpy.types.Scene.UseLowOnly
    
if __name__ == "__main__":
    register()
