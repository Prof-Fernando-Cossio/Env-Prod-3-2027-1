import unreal, json
from pathlib import Path
out=Path(r'D:/Repositories/School/Env Prod 3 2027-1/SourceArt/SlotMachine/unreal_probe.txt')
lines=[]
for name in ['SkeletalMeshActor','SkeletalMeshComponent','FbxImportUI','AnimSingleNodeInstance','SingleAnimationPlayData','LevelSequenceActor','EditorActorSubsystem','EditorLevelLibrary','BlueprintFactory']:
    cls=getattr(unreal,name,None)
    lines.append(name+': '+str(dir(cls)))
world=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/ThirdPerson/Lvl_ThirdPerson')
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    lines.append(str((a.get_actor_label(),a.get_class().get_name(),str(a.get_actor_location()))))
out.write_text('\n'.join(lines),encoding='utf8')
