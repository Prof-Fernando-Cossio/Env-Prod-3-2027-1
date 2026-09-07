"""Temporary, project-local editor script runner for asset QA. No network listener."""
import unreal, traceback, time
from pathlib import Path
if '_slot_handle' in globals():unreal.unregister_slate_post_tick_callback(_slot_handle)
_slot_root=Path(unreal.Paths.project_dir()).resolve().parent/'SourceArt'/'SlotMachine'
_slot_seen=''
def _slot_tick(delta):
    global _slot_seen
    req=_slot_root/'live_request.txt'
    if not req.exists():return
    s=req.read_text(encoding='utf8').strip()
    if not s or s==_slot_seen:return
    _slot_seen=s
    try:
        f=Path(s.split('|',1)[1]).resolve()
        if not f.is_relative_to(_slot_root) and not f.is_relative_to(Path(unreal.Paths.project_content_dir()).resolve()/'Python'):raise ValueError('Only project scripts are accepted')
        exec(compile(f.read_text(encoding='utf-8-sig'),str(f),'exec'),globals())
        (_slot_root/'live_result.txt').write_text('OK '+s)
    except Exception:
        (_slot_root/'live_result.txt').write_text(traceback.format_exc())
_slot_handle=unreal.register_slate_post_tick_callback(_slot_tick)
(_slot_root/'live_ready.txt').write_text('Ready')
