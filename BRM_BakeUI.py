#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! -Bram

bl_info = {
    "name": "BRM_BakeUI",
    "category": "3D View",
    "author": "Bram Eulaers",
    "description": "Simple texture baking UI for fast iteration. Can be found in the Tools panel."
    }

import bpy
import os
import bmesh
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatProperty, IntProperty

class BRM_BakeUIPanel(bpy.types.Panel):
    """BRM_BakeUIPanel Panel"""
    bl_label = "BRM Bake"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_region_type = "TOOLS"
    bl_category = "Bake"


    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='RADIO')

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)

        row = col.row(align = True)
        if context.scene.lowpolyGroup is True:
            row.prop_search(context.scene, "lowpoly", bpy.data, "groups", text="", icon="MESH_ICOSPHERE")
        if context.scene.lowpolyGroup is False:
            row.prop_search(context.scene, "lowpoly", context.scene, "objects", text="", icon="MESH_ICOSPHERE")
        
        row.prop(context.scene, "lowpolyGroup", text="", icon="GROUP")

        if context.scene.lowpolyActive is True:
            hideicon = "RESTRICT_VIEW_OFF"
        if context.scene.lowpolyActive is False:
            hideicon = "RESTRICT_VIEW_ON"
        op = row.operator("brm.bakeuihide", text="", icon=hideicon)
        op.targetmesh = "lowpoly"
        
        row = col.row(align = True)

        
        if context.scene.hipolyGroup is True:
            row.prop_search(context.scene, "hipoly", bpy.data, "groups", text="", icon="MESH_UVSPHERE")
        if context.scene.hipolyGroup is False:
            row.prop_search(context.scene, "hipoly", context.scene, "objects", text="", icon="MESH_UVSPHERE")

        row.enabled = not context.scene.UseLowOnly
        row.prop(context.scene, "hipolyGroup", text="", icon="GROUP")

        if context.scene.hipolyActive is True:
            hideicon = "RESTRICT_VIEW_OFF"
        if context.scene.hipolyActive is False:
            hideicon = "RESTRICT_VIEW_ON"
        op = row.operator("brm.bakeuihide", text="", icon=hideicon)
        op.targetmesh = "hipoly"

        

        col = box.column(align=True)
        row = col.row(align = True)
        row.operator("brm.bakeuitoggle", text="Toggle hi/low", icon="LAMP")
        row.prop(context.scene, "UseBlenderGame", icon="LOGIC", text="")

        

        

        col = layout.column(align=True)

        col.separator()
        row = col.row(align = True)
        row.prop(context.scene.render.bake, "cage_extrusion", text="Ray Distance")
        row.prop(context.scene, "cageEnabled", icon="BBOX", text="")
        row = col.row(align = True)
        #row.enabled = context.scene.cageEnabled
        
        if context.scene.cageEnabled:
            op = row.prop_search(context.scene, "cage", bpy.data, "objects", text="", icon="MESH_CUBE")
        #op.enabled = context.scene.cageEnabled
        
        col.separator()

        box = layout.box()
        col = box.column(align=True)

        row = col.row(align = True)
        row.label(text="Width:")
        row.operator("brm.bakeuiincrement", text="", icon="ZOOMOUT").target = "width/2"
        row.prop(context.scene, "bakeWidth", text="")
        row.operator("brm.bakeuiincrement", text="", icon="ZOOMIN").target = "width*2"
        
        row = col.row(align = True)
        row.label(text="Height:")
        row.operator("brm.bakeuiincrement", text="", icon="ZOOMOUT").target = "height/2"
        row.prop(context.scene, "bakeHeight", text="")
        row.operator("brm.bakeuiincrement", text="", icon="ZOOMIN").target = "height*2"
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
        row.prop(context.scene, "bakeNormal", icon="COLOR", text="Tangent Normal")
        if context.scene.bakeNormal:
            row.prop(context.scene, "samplesNormal", text="")

        row = col.row(align = True)
        row.enabled = not context.scene.UseLowOnly
        row.prop(context.scene, "bakeObject", icon="WORLD", text="Object Normal")
        if context.scene.bakeObject:
            row.prop(context.scene, "samplesObject", text="")
        row = col.row(align = True)
        row.prop(context.scene, "bakeAO", icon="MATSPHERE", text="Occlusion")
        if context.scene.bakeAO:
            row.prop(context.scene, "samplesAO", text="")
        
        row = col.row(align = True)
        row.enabled = not context.scene.UseLowOnly
        row.prop(context.scene, "bakeColor", icon="COLOR_GREEN", text="Color")

        row = col.row(align = True)
        row.prop(context.scene, "bakeUV", icon="TEXTURE_SHADED", text="UV Snapshot")
        
        
        
        col = layout.column(align=True)
        col.separator()
        row = col.row(align = True)
        op = row.operator("brm.bake", text="BAKE", icon="RENDER_STILL")
        row.prop(context.scene, "UseLowOnly", icon="MESH_ICOSPHERE", text="")
        

class BRM_BakeUIToggle(bpy.types.Operator):
    """toggle lowpoly/hipoly"""
    bl_idname = "brm.bakeuitoggle"
    bl_label = "Toggle"
    bl_options = {"UNDO"}

    def execute(self, context):
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        #test lowpoly/hipoly exists
        if bpy.data.objects.get(context.scene.lowpoly) is None and not context.scene.lowpoly in bpy.data.groups:
            self.report({'WARNING'}, "Select a valid lowpoly object or group!")
            return {'FINISHED'}
        if bpy.data.objects.get(context.scene.hipoly) is None and not context.scene.hipoly in bpy.data.groups:
            self.report({'WARNING'}, "Select a valid hipoly object or group!")
            return {'FINISHED'}

        if context.scene.lowpolyActive is True:
            bpy.data.scenes["Scene"].render.engine = "CYCLES"

            context.scene.lowpolyActive = False
            if bpy.data.objects.get(context.scene.lowpoly) is None:
                for o in bpy.data.groups[context.scene.lowpoly].objects:
                    o.hide = True
            else:
                bpy.data.objects[context.scene.lowpoly].hide = True

            context.scene.hipolyActive = True
            if bpy.data.objects.get(context.scene.hipoly) is None:
                for o in bpy.data.groups[context.scene.hipoly].objects:
                    o.hide = False
            else:
                bpy.data.objects[context.scene.hipoly].hide = False

        else:
            if context.scene.UseBlenderGame:
                bpy.data.scenes["Scene"].render.engine = "BLENDER_GAME"
            context.scene.lowpolyActive = True
            if bpy.data.objects.get(context.scene.lowpoly) is None:
                for o in bpy.data.groups[context.scene.lowpoly].objects:
                    o.hide = False
            else:
                bpy.data.objects[context.scene.lowpoly].hide = False

            context.scene.hipolyActive = False
            if bpy.data.objects.get(context.scene.hipoly) is None:
                for o in bpy.data.groups[context.scene.hipoly].objects:
                    o.hide = True
            else:
                bpy.data.objects[context.scene.hipoly].hide = True

        return {'FINISHED'}

class BRM_BakeUIIncrement(bpy.types.Operator):
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

class BRM_BakeUIHide(bpy.types.Operator):
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

            if bpy.data.objects.get(context.scene.lowpoly) is None and not context.scene.lowpoly in bpy.data.groups:
                self.report({'WARNING'}, "Select a valid lowpoly object or group!")
                return {'FINISHED'}

            else:

                if context.scene.lowpolyActive is True:
                    context.scene.lowpolyActive = False
                    if bpy.data.objects.get(context.scene.lowpoly) is None:
                        for o in bpy.data.groups[context.scene.lowpoly].objects:
                            o.hide = True
                    else:
                        bpy.data.objects[context.scene.lowpoly].hide = True

                else:
                    context.scene.lowpolyActive = True
                    if bpy.data.objects.get(context.scene.lowpoly) is None:
                        for o in bpy.data.groups[context.scene.lowpoly].objects:
                            o.hide = False
                    else:
                        bpy.data.objects[context.scene.lowpoly].hide = False

        if self.targetmesh == "hipoly":

            if bpy.data.objects.get(context.scene.hipoly) is None and not context.scene.hipoly in bpy.data.groups:
                self.report({'WARNING'}, "Select a valid hipoly object or group!")
                return {'FINISHED'}

            else:

                if context.scene.hipolyActive is True:
                    context.scene.hipolyActive = False
                    if bpy.data.objects.get(context.scene.hipoly) is None:
                        for o in bpy.data.groups[context.scene.hipoly].objects:
                            o.hide = True
                    else:
                        bpy.data.objects[context.scene.hipoly].hide = True

                else:
                    context.scene.hipolyActive = True
                    if bpy.data.objects.get(context.scene.hipoly) is None:
                        for o in bpy.data.groups[context.scene.hipoly].objects:
                            o.hide = False
                    else:
                        bpy.data.objects[context.scene.hipoly].hide = False

        return {'FINISHED'}


class BRM_Bake(bpy.types.Operator):
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
        #test lowpoly/hipoly exists
        if bpy.data.objects.get(context.scene.lowpoly) is None and not context.scene.lowpoly in bpy.data.groups:
            self.report({'WARNING'}, "Select a valid lowpoly object or group!")
            return {'FINISHED'}
        if bpy.data.objects.get(context.scene.hipoly) is None and not context.scene.hipoly in bpy.data.groups:
            self.report({'WARNING'}, "Select a valid hipoly object or group!")
            return {'FINISHED'}
       
        #setup
           
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')


        #select lowpoly
        lowpolyobject = "null"
        orig_lowpoly = None

        #if group, create temporary lowpoly object
        if bpy.data.objects.get(context.scene.lowpoly) is None:
                
                #select all objects
                for o in bpy.data.groups[context.scene.lowpoly].objects:
                    o.hide = False
                    o.select = True
                    bpy.context.scene.objects.active = o
                    o.hide_render = True
                #duplicate selected and combine into new object
                bpy.ops.object.duplicate()
                bpy.ops.object.join()
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                lowpolyobject = bpy.context.selected_objects[0].name
                bpy.data.objects[lowpolyobject].hide_render = False


        else:
            bpy.data.objects[context.scene.lowpoly].hide = False
            bpy.data.objects[context.scene.lowpoly].select = True
            orig_lowpoly = bpy.data.objects[context.scene.lowpoly]
            lowpolyobject = context.scene.lowpoly

        #test if lowpoly has a material
        if len(bpy.data.objects[lowpolyobject].data.materials) == 0:
            if context.scene.lowpolyGroup:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[lowpolyobject].select = True
                bpy.ops.object.delete(use_global=False)
            self.report({'WARNING'}, "Material required on low poly mesh!")
            return {'FINISHED'}

        if len(bpy.data.objects[lowpolyobject].data.uv_layers) == 0:
            if context.scene.lowpolyGroup:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[lowpolyobject].select = True
                bpy.ops.object.delete(use_global=False)
            self.report({'WARNING'}, "low poly mesh has no UV!")
            return {'FINISHED'}



        orig_renderer = bpy.data.scenes["Scene"].render.engine
        bpy.data.scenes["Scene"].render.engine = "CYCLES"

        #create bake image and material
        bakeimage = bpy.data.images.new("BakeImage", width=context.scene.bakeWidth, height=context.scene.bakeHeight)
        bakemat = bpy.data.materials.new(name="bakemat")
        bakemat.use_nodes = True

        if not context.scene.UseLowOnly:
        #select hipoly object or group:
            if bpy.data.objects.get(context.scene.hipoly) is None:
                #bpy.data.groups[context.scene.hipoly].select = True
                for o in bpy.data.groups[context.scene.hipoly].objects:
                    o.hide = False
                    o.select = True
                #return {'FINISHED'}
            else:
                bpy.data.objects[context.scene.hipoly].hide = False
                bpy.data.objects[context.scene.hipoly].select = True

        bpy.context.scene.objects.active = bpy.data.objects[lowpolyobject]

        orig_mat = bpy.context.active_object.data.materials[0]
        bpy.context.active_object.data.materials[0] = bakemat

        node_tree = bakemat.node_tree
        node = node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        node_tree.nodes.active = node

        node.image = bakeimage

        if context.scene.cageEnabled:
            bpy.context.scene.render.bake.use_cage = True
            bpy.context.scene.render.bake.cage_object = context.scene.cage

        else:
            bpy.context.scene.render.bake.use_cage = False

        if context.scene.bakeNormal and not context.scene.UseLowOnly:

            bpy.context.scene.cycles.samples = context.scene.samplesNormal

            

            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=True, normal_space='TANGENT')

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

            bpy.context.scene.cycles.samples = 1
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True

            bpy.ops.object.bake(type='DIFFUSE', use_clear=True, use_selected_to_active=True)

            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_color.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()


        #return
        bpy.data.images.remove(bakeimage)
        bakemat.node_tree.nodes.remove(node)
        bpy.data.materials.remove(bakemat)

        #reset
        bpy.data.scenes["Scene"].render.engine = orig_renderer
        bpy.context.active_object.data.materials[0] = orig_mat

        bpy.ops.object.select_all(action='DESELECT')
        if not context.scene.lowpolyGroup:
            orig_lowpoly.select = True


        for image in bpy.data.images:
            image.reload()
        
        
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

        #remove temp lowpoly
        if context.scene.lowpolyGroup:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[lowpolyobject].select = True
            bpy.ops.object.delete(use_global=False)


        #rehide back to original state
        if context.scene.lowpolyActive is True:
            if bpy.data.objects.get(context.scene.lowpoly) is None:
                for o in bpy.data.groups[context.scene.lowpoly].objects:
                    o.hide = False
                    bpy.context.scene.objects.active = o
            else:
                bpy.data.objects[context.scene.lowpoly].hide = False
        else:
            if bpy.data.objects.get(context.scene.lowpoly) is None:
                for o in bpy.data.groups[context.scene.lowpoly].objects:
                    o.hide = True
            else:
                bpy.data.objects[context.scene.lowpoly].hide = True

        if context.scene.hipolyActive is True:
            if bpy.data.objects.get(context.scene.hipoly) is None:
                for o in bpy.data.groups[context.scene.hipoly].objects:
                    o.hide = False
                    bpy.context.scene.objects.active = o
            else:
                bpy.data.objects[context.scene.hipoly].hide = False
        else:
            if bpy.data.objects.get(context.scene.hipoly) is None:
                for o in bpy.data.groups[context.scene.hipoly].objects:
                    o.hide = True
            else:
                bpy.data.objects[context.scene.hipoly].hide = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(BRM_Bake)
    bpy.utils.register_class(BRM_BakeUIHide)
    bpy.utils.register_class(BRM_BakeUIPanel)
    bpy.utils.register_class(BRM_BakeUIToggle)
    bpy.utils.register_class(BRM_BakeUIIncrement)

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
        description = "enable group selection",
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
        description = "enable group selection",
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
        description = "samplesColor",
        )
    bpy.types.Scene.bakeWidth = bpy.props.IntProperty (
        name = "bakeWidth",
        default = 1024,
        description = "Export Texture Width",
        )  
    bpy.types.Scene.bakeHeight = bpy.props.IntProperty (
        name = "bakeHeight",
        default = 1024,
        description = "Export Texture Height",
        )
    bpy.types.Scene.bakePrefix = bpy.props.StringProperty (
        name = "bakePrefix",
        default = "export",
        description = "export filename",
        )
    bpy.types.Scene.bakeFolder = bpy.props.StringProperty (
        name = "bakeFolder",
        default = "destination folder",
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
    bpy.utils.unregister_class(BRM_Bake)
    bpy.utils.unregister_class(BRM_BakeUIHide)
    bpy.utils.unregister_class(BRM_BakeUIPanel)
    bpy.utils.unregister_class(BRM_BakeUIToggle)
    bpy.utils.unregister_class(BRM_BakeUIIncrement)

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
    del bpy.types.Scene.bakeUV
    del bpy.types.Scene.samplesNormal
    del bpy.types.Scene.samplesAO
    del bpy.types.Scene.samplesColor
    del bpy.types.Scene.samplesObject
    del bpy.types.Scene.bakeWidth
    del bpy.types.Scene.bakeHeight
    del bpy.types.Scene.bakeFolder
    del bpy.types.Scene.UseBlenderGame
    del bpy.types.Scene.UseLowOnly
    
if __name__ == "__main__":
    register()
