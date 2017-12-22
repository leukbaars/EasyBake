#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! -Bram

bl_info = {
    "name": "BRM_EasyBake",
    "category": "3D View",
    "author": "Bram Eulaers",
    "description": "one click bake setup"
    }

import bpy
import bmesh
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatProperty, IntProperty

class BRM_EasyBakePanel(bpy.types.Panel):
    """BRM_NormalHackPanel Panel"""
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

        col = layout.column(align=True)
        #col.label(text="Bake tools:")
        row = col.row(align = True)
        row.prop(context.scene, "lowpoly", text="", icon="MESH_ICOSPHERE")
        if context.scene.lowpolyActive is True:
            hideicon = "RESTRICT_VIEW_OFF"
        if context.scene.lowpolyActive is False:
            hideicon = "RESTRICT_VIEW_ON"
        op = row.operator("brm.easybakehide", text="", icon=hideicon)
        op.targetmesh = "lowpoly"
        
        row = col.row(align = True)
        row.prop(context.scene, "hipoly", text="", icon="MESH_UVSPHERE")
        if context.scene.hipolyActive is True:
            hideicon = "RESTRICT_VIEW_OFF"
        if context.scene.hipolyActive is False:
            hideicon = "RESTRICT_VIEW_ON"
        op = row.operator("brm.easybakehide", text="", icon=hideicon)
        op.targetmesh = "hipoly"

        
        
        #color baking disabled for now

        #row = col.row(align = True)
        #row.prop(context.scene, "bakeColor", icon="COLOR_GREEN", text="COLOR")
        #row.prop(context.scene, "samplesColor", text="")

        col = layout.column(align=True)
        col.prop(context.scene.render.bake, "cage_extrusion", text="Ray Distance")
        col.prop(context.scene.render.bake, "margin")

        col = layout.column(align=True)
        row = col.row(align = True)
        row.label(text="Width:")
        row.prop(context.scene, "bakeWidth", text="")
        row = col.row(align = True)
        row.label(text="Height:")
        row.prop(context.scene, "bakeHeight", text="")

        col = layout.column(align=True)
        col.prop(context.scene, 'bakeFolder', text="")

        

        col = layout.column(align=True)
        row = col.row(align = True)
        #row.label(text=" ")
        #row.label(text="Samples:", icon="LAMP_AREA")
        row = col.row(align = True)
        row.prop(context.scene, "bakeNormal", icon="COLOR", text="NORM")
        row.prop(context.scene, "samplesNormal", text="")
        row = col.row(align = True)
        row.prop(context.scene, "bakeAO", icon="MATSPHERE", text="AO")
        row.prop(context.scene, "samplesAO", text="")

        col = layout.column(align=True)
        row = col.row(align = True)
        op = row.operator("brm.easybake", text="BAKE", icon="RENDER_STILL")

class BRM_EasyBakeHide(bpy.types.Operator):
    """hide object"""
    bl_idname = "brm.easybakehide"
    bl_label = "hide"
    bl_options = {"UNDO"}

    targetmesh = bpy.props.StringProperty()

    def execute(self, context):
        if self.targetmesh == "lowpoly":
            if context.scene.lowpolyActive is True:
                context.scene.lowpolyActive = False
                bpy.data.objects[context.scene.lowpoly].hide = True
            else:
                context.scene.lowpolyActive = True
                bpy.data.objects[context.scene.lowpoly].hide = False

        if self.targetmesh == "hipoly":
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


class BRM_EasyBake(bpy.types.Operator):
    """Bake and save textures"""
    bl_idname = "brm.easybake"
    bl_label = "set normal"
    bl_options = {"UNDO"}
    

    def execute(self, context):  
        
        #setup
        bpy.ops.object.select_all(action='DESELECT')

        orig_renderer = bpy.data.scenes["Scene"].render.engine
        bpy.data.scenes["Scene"].render.engine = "CYCLES"

        #create bake image and material
        bakeimage = bpy.data.images.new("BakeImage", width=context.scene.bakeWidth, height=context.scene.bakeHeight)
        bakemat = bpy.data.materials.new(name="bakemat")
        bakemat.use_nodes = True

            
        #select lowpoly
        bpy.data.objects[context.scene.lowpoly].hide = False
        bpy.data.objects[context.scene.lowpoly].select = True
        orig_lowpoly = bpy.data.objects[context.scene.lowpoly]

        #select hipoly object or group:
        if bpy.data.objects.get(context.scene.hipoly) is None:
            print("no hipoly")
            #bpy.data.groups[context.scene.hipoly].select = True
            for o in bpy.data.groups[context.scene.hipoly].objects:
                o.hide = False
                o.select = True
            #return {'FINISHED'}
        else:
            bpy.data.objects[context.scene.hipoly].hide = False
            bpy.data.objects[context.scene.hipoly].select = True

        

       # bpy.context.active_object=bpy.data.objects[context.scene.lowpoly]
        bpy.context.scene.objects.active = bpy.data.objects[context.scene.lowpoly]

        orig_mat = bpy.context.active_object.data.materials[0]
        bpy.context.active_object.data.materials[0] = bakemat

        node_tree = bakemat.node_tree
        node = node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        node_tree.nodes.active = node

        node.image = bakeimage

        

        if context.scene.bakeNormal:

            bpy.context.scene.cycles.samples = context.scene.samplesNormal

            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=True)



            bakeimage.filepath_raw = context.scene.bakeFolder+"export_normal.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        if context.scene.bakeAO:

            bpy.context.scene.cycles.samples = context.scene.samplesAO

            bpy.ops.object.bake(type='AO', use_clear=True, use_selected_to_active=True)

            bakeimage.filepath_raw = context.scene.bakeFolder+"export_ao.tga"
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
        orig_lowpoly.select = True

        for image in bpy.data.images:
            image.reload()
        
        #rehide back to original state
        if context.scene.lowpolyActive is True:
            bpy.data.objects[context.scene.lowpoly].hide = False
        else:
            bpy.data.objects[context.scene.lowpoly].hide = True

        
        if context.scene.hipolyActive is True:
            if bpy.data.objects.get(context.scene.hipoly) is None:
                for o in bpy.data.groups[context.scene.hipoly].objects:
                    o.hide = False
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
    bpy.utils.register_class(BRM_EasyBake)
    bpy.utils.register_class(BRM_EasyBakeHide)
    bpy.utils.register_class(BRM_EasyBakePanel)

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
    bpy.types.Scene.bakeNormal = bpy.props.BoolProperty (
        name = "bakeNormal",
        default = True,
        description = "bakeNormal",
        )
    bpy.types.Scene.bakeAO = bpy.props.BoolProperty (
        name = "bakeAO",
        default = True,
        description = "bakeAO",
        )
    bpy.types.Scene.bakeColor = bpy.props.BoolProperty (
        name = "bakeColor",
        default = False,
        description = "bakeColor",
        )
    bpy.types.Scene.samplesNormal = bpy.props.IntProperty (
        name = "samplesNormal",
        default = 8,
        description = "samplesNormal",
        )
    bpy.types.Scene.samplesAO = bpy.props.IntProperty (
        name = "samplesAO",
        default = 128,
        description = "samplesAO",
        )
    bpy.types.Scene.samplesColor = bpy.props.IntProperty (
        name = "samplesColor",
        default = 1,
        description = "samplesColor",
        )
    bpy.types.Scene.bakeWidth = bpy.props.IntProperty (
        name = "bakeWidth",
        default = 1024,
        description = "bakeWidth",
        )  
    bpy.types.Scene.bakeHeight = bpy.props.IntProperty (
        name = "bakeHeight",
        default = 1024,
        description = "bakeHeight",
        )
    bpy.types.Scene.bakeFolder = bpy.props.StringProperty (
        name = "bakeFolder",
        default = "C:\\export\\",
        description = "bakeFolder",
        subtype = 'DIR_PATH'
        )

def unregister():
    bpy.utils.unregister_class(BRM_EasyBake)
    bpy.utils.unregister_class(BRM_EasyBakeHide)
    bpy.utils.unregister_class(BRM_EasyBakePanel)

    del bpy.types.Scene.lowpoly
    del bpy.types.Scene.lowpolyActive
    del bpy.types.Scene.hipoly
    del bpy.types.Scene.hipolyActive
    del bpy.types.Scene.bakeNormal
    del bpy.types.Scene.bakeAO
    del bpy.types.Scene.bakeColor
    del bpy.types.Scene.samplesNormal
    del bpy.types.Scene.samplesAO
    del bpy.types.Scene.samplesColor
    del bpy.types.Scene.bakeWidth
    del bpy.types.Scene.bakeHeight
    del bpy.types.Scene.bakeFolder
    
if __name__ == "__main__":
    register()
