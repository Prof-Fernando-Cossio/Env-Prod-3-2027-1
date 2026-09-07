import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve().parent/'SourceArt/SlotMachine'
mat=unreal.EditorAssetLibrary.load_asset('/Game/SlotMachine/M_SlotMachine_Baked')
assert mat
# The printed plates are intentional single-quad surfaces.
mat.set_editor_property('two_sided',True)
unreal.MaterialEditingLibrary.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(P/'material_fix_report.json').write_text(json.dumps({'material':mat.get_path_name(),'two_sided':mat.get_editor_property('two_sided')}))
