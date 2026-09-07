import unreal,json,time
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve().parent/'SourceArt/SlotMachine'
_capture_done=set()
_capture_start=time.time()
def _capture_tick(delta):
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if not world:return
    machine=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if a.get_class().get_name()=='BP_LuckyStarSlotMachine_C'),None)
    if not machine:return
    t=machine.skeletal_mesh_component.get_position()
    for name,lo,hi in [('LeverPulled',1.2,1.4),('Jackpot',8.,9.)]:
        if name not in _capture_done and lo<=t<=hi:
            unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(P/('previews/Unreal_'+name+'.png')),delay=0.)
            _capture_done.add(name)
    if len(_capture_done)==2 or time.time()-_capture_start>60:
        unreal.unregister_slate_post_tick_callback(_capture_handle)
        (P/'capture_report.json').write_text(json.dumps({'poses':list(_capture_done),'elapsed_seconds':time.time()-_capture_start}))
_capture_handle=unreal.register_slate_post_tick_callback(_capture_tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
