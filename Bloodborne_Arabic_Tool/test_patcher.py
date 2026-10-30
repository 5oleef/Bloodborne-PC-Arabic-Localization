import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

tool_dir = Path(r"E:\Bloodborne\Bloodborne_Arabic_Tool")
sys.path.insert(0, str(tool_dir))

from engine.patcher import BloodbornePatcher

patcher = BloodbornePatcher()
print("1. Auto-detected Game Root:", patcher.game_root)
print("   bbport dir:", patcher.bbport_dir)

status = patcher.get_status()
print("\n2. Initial Status:", status)

print("\n3. Testing Installation (mode='egyptian')...")
success = patcher.install(mode="egyptian", log_callback=lambda msg: print("   [LOG]", msg))
print("   Install result:", success)

status_after = patcher.get_status()
print("\n4. Status After Install:", status_after)

# Verify mods.json
mods_json = (patcher.bbport_dir / "mods.json").read_text(encoding="utf-8")
print("\n5. mods.json contents:\n", mods_json)

# Verify font and menu files
arabic_dir = patcher.bbport_dir / "mods" / "Arabic"
print("\n6. Arabic dir exists:", arabic_dir.is_dir())
print("   font.gfx exists:", (arabic_dir / "dvdroot_ps4" / "menu" / "engus" / "font.gfx").is_file())
print("   menu.msgbnd.dcx exists:", (arabic_dir / "dvdroot_ps4" / "msg" / "engus" / "menu.msgbnd.dcx").is_file())
print("   item.msgbnd.dcx exists:", (arabic_dir / "dvdroot_ps4" / "msg" / "engus" / "item.msgbnd.dcx").is_file())
