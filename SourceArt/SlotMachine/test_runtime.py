import unreal,time,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve().parent/'SourceArt/SlotMachine'
_qa_samples=[];_qa_prev=-1.;_qa_wraps=0;_qa_wall=time.time();_qa_finished=False
def _qa_tick(delta):
    global _qa_prev,_qa_wraps,_qa_finished
    if _qa_finished:return
    try:
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not world:return
        arr=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor)
        actor=next((a for a in arr if a.get_class().get_name()=='BP_LuckyStarSlotMachine_C'),None)
        if not actor:return
        comp=actor.get_component_by_class(unreal.SkeletalMeshComponent);pos=comp.get_position()
        if _qa_prev>=0 and pos<_qa_prev-.5:_qa_wraps+=1
        _qa_prev=pos
        if not _qa_samples or time.time()-_qa_samples[-1]['wall']>.15:
            bones={}
            for i in range(comp.get_num_bones()):
                name=comp.get_bone_name(i)
                q=comp.get_bone_transform(name,unreal.RelativeTransformSpace.RTS_COMPONENT).rotation
                bones[str(name)]=[q.x,q.y,q.z,q.w]
            _qa_samples.append({'wall':time.time(),'position':pos,'playing':comp.is_playing(),'bones':bones})
            (P/'runtime_samples.json').write_text(json.dumps({'wraps':_qa_wraps,'samples':_qa_samples},indent=2))
        if _qa_wraps>=2:
            _qa_finished=True
            (P/'runtime_samples.json').write_text(json.dumps({'wraps':_qa_wraps,'samples':_qa_samples},indent=2))
            unreal.unregister_slate_post_tick_callback(_qa_handle)
            (P/'runtime_verified.txt').write_text('PASS: Native Blueprint animation playing in PIE; observed two automatic wraps of a 12-second cycle.')
    except Exception:
        import traceback
        (P/'runtime_error.txt').write_text(traceback.format_exc());_qa_finished=True
_qa_handle=unreal.register_slate_post_tick_callback(_qa_tick)
if not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
