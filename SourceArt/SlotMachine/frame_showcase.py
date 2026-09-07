import unreal
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve().parent/'SourceArt/SlotMachine'
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
for world in [editor.get_editor_world(),editor.get_game_world()]:
    if not world:continue
    arr=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor)
    machine=next(a for a in arr if a.get_class().get_name()=='BP_LuckyStarSlotMachine_C')
    camera=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.CameraActor) if a.get_actor_label()=='Slot Machine Showcase Camera')
    camera.set_actor_location(unreal.MathLibrary.transform_location(machine.get_actor_transform(),unreal.Vector(220,400,210)),False,False)
    camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),machine.get_actor_location()+unreal.Vector(0,0,86)),False)
    camera.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view',45.)
    if world==editor.get_game_world():
        unreal.GameplayStatics.get_player_controller(world,0).set_view_target_with_blend(camera,0.)
    else:unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
# Native engine screenshot preserves the actual running scene.
unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(P/'previews/Unreal_Runtime.png'),delay=1.)
