"""Run with Unreal Editor Python. Imports the baked animated FBX and installs it in the existing level."""
import unreal, json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve().parent/'SourceArt'/'SlotMachine'
D='/Game/SlotMachine'
AS=unreal.EditorAssetLibrary
AT=unreal.AssetToolsHelpers.get_asset_tools()
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
def import_file(path,name,options=None):
    task=unreal.AssetImportTask();task.filename=str(path);task.destination_path=D;task.destination_name=name
    task.automated=True;task.replace_existing=True;task.save=True
    if options:task.options=options
    AT.import_asset_tasks([task]);return [AS.load_asset(x) for x in task.imported_object_paths]
base=AS.load_asset(D+'/T_SlotMachine_BaseColor') or import_file(P/'textures/T_SlotMachine_BaseColor.png','T_SlotMachine_BaseColor')[0]
orm=AS.load_asset(D+'/T_SlotMachine_ORM') or import_file(P/'textures/T_SlotMachine_ORM.png','T_SlotMachine_ORM')[0]
orm.set_editor_property('srgb',False);orm.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS)
mat=AS.load_asset(D+'/M_SlotMachine_Baked')
if not mat:mat=AT.create_asset('M_SlotMachine_Baked',D,unreal.Material,unreal.MaterialFactoryNew())
mat.set_editor_property('two_sided',True)
ML=unreal.MaterialEditingLibrary;ML.delete_all_material_expressions(mat)
color=ML.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,-160);color.texture=base
masks=ML.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,180);masks.texture=orm;masks.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
for node,output,prop in [(color,'RGB',unreal.MaterialProperty.MP_BASE_COLOR),(masks,'G',unreal.MaterialProperty.MP_ROUGHNESS),(masks,'B',unreal.MaterialProperty.MP_METALLIC)]:ML.connect_material_property(node,output,prop)
ML.recompile_material(mat)
opts=unreal.FbxImportUI();opts.set_editor_property('import_mesh',True);opts.set_editor_property('import_as_skeletal',True);opts.set_editor_property('import_animations',True)
opts.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_SKELETAL_MESH);opts.set_editor_property('original_import_type',unreal.FBXImportType.FBXIT_SKELETAL_MESH)
opts.set_editor_property('automated_import_should_detect_type',False);opts.set_editor_property('import_materials',False);opts.set_editor_property('import_textures',False);opts.set_editor_property('create_physics_asset',False)
opts.skeletal_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
opts.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose',True)
opts.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
existing=AS.load_asset(D+'/SK_SlotMachine')
assets=[existing] if existing else import_file(P/'exports/SK_SlotMachine.fbx','SK_SlotMachine',opts)
mesh=next((a for a in assets if isinstance(a,unreal.SkeletalMesh)),None)
anim=next((a for a in assets if isinstance(a,unreal.AnimSequence)),None)
if not mesh or not anim:
    allassets=[AS.load_asset(x) for x in AS.list_assets(D)]
    mesh=next((a for a in allassets if isinstance(a,unreal.SkeletalMesh)),None);anim=next((a for a in allassets if isinstance(a,unreal.AnimSequence)),None)
if mesh and not anim:
    skeleton=mesh.get_editor_property('skeleton')
    assert skeleton,'Imported mesh requires its skeleton'
    AS.save_loaded_asset(skeleton)
    anim_opts=unreal.FbxImportUI()
    anim_opts.set_editor_properties({'import_mesh':False,'import_as_skeletal':True,'import_animations':True,'import_materials':False,'import_textures':False,'automated_import_should_detect_type':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_ANIMATION,'skeleton':skeleton})
    anim_opts.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    assets+=import_file(P/'exports/SK_SlotMachine.fbx','A_Pull_Spin_Jackpot_12s',anim_opts)
    anim=next((a for a in assets if isinstance(a,unreal.AnimSequence)),None)
assert mesh and anim,'FBX must import both skeletal mesh and animation'
materials=mesh.get_editor_property('materials')
for m in materials:m.set_editor_property('material_interface',mat)
mesh.set_editor_property('materials',materials)
def setup(comp):
    comp.set_skeletal_mesh_asset(mesh)
    comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    data=unreal.SingleAnimationPlayData();data.anim_to_play=anim;data.saved_looping=True;data.saved_playing=True;data.saved_play_rate=1.;data.saved_position=0.
    comp.set_editor_property('animation_data',data)
    comp.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    comp.set_update_animation_in_editor(True)
    comp.set_material(0,mat)
# A reusable Blueprint inherits the native single-node animation startup behavior.
bp=AS.load_asset(D+'/BP_LuckyStarSlotMachine')
if not bp:
    factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.SkeletalMeshActor)
    bp=AT.create_asset('BP_LuckyStarSlotMachine',D,unreal.Blueprint,factory)
default=unreal.get_default_object(bp.generated_class());setup(default.get_editor_property('skeletal_mesh_component'))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
AS.save_loaded_asset(bp)
for path in AS.list_assets(D):
    asset=AS.load_asset(path)
    if asset:AS.save_loaded_asset(asset)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
# The live project already has the only map open; avoid unnecessary reloads.
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world.get_name()!='Lvl_ThirdPerson':levels.load_level('/Game/ThirdPerson/Lvl_ThirdPerson')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Lucky Star | 1960s Slot Machine' or a.get_class()==bp.generated_class()),None)
if not actor:actor=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(1100,-300,0),unreal.Rotator(0,0,0))
actor.set_actor_label('Lucky Star | 1960s Slot Machine')
setup(actor.get_editor_property('skeletal_mesh_component'))
actor.set_editor_property('tags',['SlotMachine','Loop12Seconds','Jackpot777'])
actors.set_selected_level_actors([actor])
# Dedicated camera in the same existing map for an unobstructed showcase.
camera=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Slot Machine Showcase Camera'),None)
if not camera:camera=actors.spawn_actor_from_class(unreal.CameraActor,actor.get_actor_location()+unreal.Vector(-330,210,200))
camera.set_actor_label('Slot Machine Showcase Camera')
camera.set_actor_location(unreal.MathLibrary.transform_location(actor.get_actor_transform(),unreal.Vector(220,400,210)),False,False)
target=actor.get_actor_location()+unreal.Vector(0,0,90)
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),target),False)
camera.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view',45.)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
for a in [base,orm,mat,mesh,anim,bp]:AS.save_loaded_asset(a)
levels.save_current_level();AS.save_directory(D,only_if_is_dirty=True,recursive=True)
report={'mesh':mesh.get_path_name(),'animation':anim.get_path_name(),'animation_seconds':anim.get_editor_property('sequence_length'),'blueprint':bp.get_path_name(),'map':'/Game/ThirdPerson/Lvl_ThirdPerson','actor_location':str(actor.get_actor_location()),'looping':str(actor.skeletal_mesh_component.animation_data),'assets':[a.get_path_name() for a in assets]}
(P/'unreal_import_report.json').write_text(json.dumps(report,indent=2))
unreal.log('SLOT_MACHINE_IMPORT_COMPLETE '+json.dumps(report))
