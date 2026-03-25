import os
import sys
import shutil
import math
import time

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nPress Enter to continue...")

def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024

def safe_listdir(path):
    try:
        return sorted(os.listdir(path), key=lambda x: x.lower())
    except Exception:
        return []

def get_entry_info(base, name):
    full = os.path.join(base, name)
    try:
        is_dir = os.path.isdir(full)
    except Exception:
        is_dir = False
    try:
        size = 0 if is_dir else os.path.getsize(full)
    except Exception:
        size = 0
    try:
        mtime = os.path.getmtime(full)
        modified = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
    except Exception:
        modified = "unknown"
    return {
        "name": name,
        "path": full,
        "is_dir": is_dir,
        "size": size,
        "modified": modified,
    }

def show_banner():
    print("=" * 78)
    print("OS POWER TOOL".center(78))
    print("=" * 78)

def breadcrumb(path):
    drive, rest = os.path.splitdrive(os.path.abspath(path))
    parts = rest.strip(os.sep).split(os.sep) if rest.strip(os.sep) else []
    pieces = []
    current = drive + os.sep if drive else os.sep
    pieces.append(current)
    for part in parts:
        current = os.path.join(current, part)
        pieces.append(part)
    return "  >  ".join(pieces)

def print_directory(path, page=1, page_size=20):
    entries = safe_listdir(path)
    infos = [get_entry_info(path, name) for name in entries]
    total = len(infos)
    pages = max(1, math.ceil(total / page_size))
    page = max(1, min(page, pages))
    start = (page - 1) * page_size
    end = start + page_size
    view = infos[start:end]

    print(f"Current directory:\n{breadcrumb(path)}\n")
    print(f"{'#':>3}  {'Type':<6}  {'Name':<38}  {'Size':>12}  {'Modified':<19}")
    print("-" * 78)
    for idx, info in enumerate(view, start=start + 1):
        typ = "DIR" if info["is_dir"] else "FILE"
        size = "-" if info["is_dir"] else format_size(info["size"])
        name = info["name"]
        if len(name) > 38:
            name = name[:35] + "..."
        print(f"{idx:>3}  {typ:<6}  {name:<38}  {size:>12}  {info['modified']:<19}")
    print("-" * 78)
    print(f"Items: {total}    Page: {page}/{pages}")

def choose_entry(path):
    entries = safe_listdir(path)
    if not entries:
        print("No items found.")
        pause()
        return None
    page = 1
    page_size = 20
    while True:
        clear()
        show_banner()
        print_directory(path, page, page_size)
        print("\nEnter item number, N for next page, P for previous page, Q to cancel")
        choice = input("> ").strip()
        if choice.lower() == "q":
            return None
        if choice.lower() == "n":
            page += 1
            continue
        if choice.lower() == "p":
            page -= 1
            continue
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(entries):
                return os.path.join(path, entries[idx])

def scan_directory_stats(path):
    total_files = 0
    total_dirs = 0
    total_size = 0
    largest_files = []
    ext_count = {}
    for root, dirs, files in os.walk(path):
        total_dirs += len(dirs)
        total_files += len(files)
        for file in files:
            full = os.path.join(root, file)
            try:
                size = os.path.getsize(full)
            except Exception:
                size = 0
            total_size += size
            ext = os.path.splitext(file)[1].lower() or "[no extension]"
            ext_count[ext] = ext_count.get(ext, 0) + 1
            largest_files.append((size, full))
    largest_files.sort(reverse=True, key=lambda x: x[0])
    top_ext = sorted(ext_count.items(), key=lambda x: (-x[1], x[0]))[:10]
    return total_files, total_dirs, total_size, largest_files[:10], top_ext

def show_stats(path):
    clear()
    show_banner()
    print(f"Scanning:\n{path}\n")
    total_files, total_dirs, total_size, largest_files, top_ext = scan_directory_stats(path)
    print(f"Folders: {total_dirs}")
    print(f"Files:   {total_files}")
    print(f"Size:    {format_size(total_size)}\n")
    print("Top file types")
    print("-" * 78)
    for ext, count in top_ext:
        print(f"{ext:<20} {count:>8}")
    print("\nLargest files")
    print("-" * 78)
    for size, full in largest_files:
        shown = full
        if len(shown) > 62:
            shown = "..." + shown[-59:]
        print(f"{format_size(size):>12}  {shown}")
    pause()

def tree(path, depth=2, prefix=""):
    try:
        items = sorted(os.listdir(path), key=lambda x: x.lower())
    except Exception:
        return
    for i, item in enumerate(items):
        full = os.path.join(path, item)
        connector = "└── " if i == len(items) - 1 else "├── "
        print(prefix + connector + item)
        if depth > 0 and os.path.isdir(full):
            extension = "    " if i == len(items) - 1 else "│   "
            tree(full, depth - 1, prefix + extension)

def show_tree(path):
    clear()
    show_banner()
    print(path)
    tree(path, depth=2)
    pause()

def search_by_name(path, query):
    results = []
    q = query.lower()
    for root, dirs, files in os.walk(path):
        for name in dirs + files:
            if q in name.lower():
                results.append(os.path.join(root, name))
    return results

def search_menu(path):
    clear()
    show_banner()
    query = input("Search name contains: ").strip()
    if not query:
        return
    print("\nSearching...\n")
    results = search_by_name(path, query)
    print(f"Found {len(results)} results\n")
    for i, result in enumerate(results[:200], start=1):
        shown = result
        if len(shown) > 74:
            shown = "..." + shown[-71:]
        print(f"{i:>3}. {shown}")
    if len(results) > 200:
        print(f"\nShowing first 200 of {len(results)}")
    pause()

def preview_text_file(path):
    clear()
    show_banner()
    print(path)
    print("-" * 78)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= 40:
                    print("\n[Preview limited to 40 lines]")
                    break
                print(line.rstrip())
    except Exception as e:
        print(f"Could not read file: {e}")
    pause()

def make_folder(path):
    clear()
    show_banner()
    name = input("New folder name: ").strip()
    if not name:
        return
    full = os.path.join(path, name)
    try:
        os.makedirs(full, exist_ok=False)
        print(f"Created: {full}")
    except Exception as e:
        print(f"Failed: {e}")
    pause()

def make_text_file(path):
    clear()
    show_banner()
    name = input("New text file name: ").strip()
    if not name:
        return
    full = os.path.join(path, name)
    print("Enter lines. Type :save on its own line to finish.\n")
    lines = []
    while True:
        line = input()
        if line == ":save":
            break
        lines.append(line)
    try:
        with open(full, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Saved: {full}")
    except Exception as e:
        print(f"Failed: {e}")
    pause()

def rename_entry(path):
    target = choose_entry(path)
    if not target:
        return
    clear()
    show_banner()
    print(f"Selected:\n{target}\n")
    new_name = input("New name: ").strip()
    if not new_name:
        return
    dest = os.path.join(os.path.dirname(target), new_name)
    try:
        os.rename(target, dest)
        print("Renamed.")
    except Exception as e:
        print(f"Failed: {e}")
    pause()

def copy_entry(path):
    target = choose_entry(path)
    if not target:
        return
    clear()
    show_banner()
    print(f"Selected:\n{target}\n")
    dest_dir = input("Destination folder path: ").strip()
    if not dest_dir:
        return
    if not os.path.isdir(dest_dir):
        print("Destination is not a folder.")
        pause()
        return
    try:
        if os.path.isdir(target):
            base = os.path.basename(target)
            out = os.path.join(dest_dir, base)
            shutil.copytree(target, out)
        else:
            shutil.copy2(target, dest_dir)
        print("Copied.")
    except Exception as e:
        print(f"Failed: {e}")
    pause()

def move_entry(path):
    target = choose_entry(path)
    if not target:
        return
    clear()
    show_banner()
    print(f"Selected:\n{target}\n")
    dest_dir = input("Destination folder path: ").strip()
    if not dest_dir:
        return
    if not os.path.isdir(dest_dir):
        print("Destination is not a folder.")
        pause()
        return
    try:
        shutil.move(target, dest_dir)
        print("Moved.")
    except Exception as e:
        print(f"Failed: {e}")
    pause()

def delete_entry(path):
    target = choose_entry(path)
    if not target:
        return
    clear()
    show_banner()
    print(f"Delete this?\n{target}\n")
    confirm = input("Type DELETE to confirm: ").strip()
    if confirm != "DELETE":
        return
    try:
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)
        print("Deleted.")
    except Exception as e:
        print(f"Failed: {e}")
    pause()

def organize_by_extension(path):
    clear()
    show_banner()
    print(f"Organize files in:\n{path}\n")
    confirm = input("Type YES to continue: ").strip()
    if confirm != "YES":
        return
    moved = 0
    skipped = 0
    for name in safe_listdir(path):
        full = os.path.join(path, name)
        if os.path.isfile(full):
            ext = os.path.splitext(name)[1].lower().replace(".", "")
            folder = ext if ext else "no_extension"
            dest_folder = os.path.join(path, folder)
            os.makedirs(dest_folder, exist_ok=True)
            dest = os.path.join(dest_folder, name)
            base, extension = os.path.splitext(name)
            counter = 1
            while os.path.exists(dest):
                dest = os.path.join(dest_folder, f"{base}_{counter}{extension}")
                counter += 1
            try:
                shutil.move(full, dest)
                moved += 1
            except Exception:
                skipped += 1
    print(f"Moved: {moved}")
    print(f"Skipped: {skipped}")
    pause()

def duplicate_report(path):
    clear()
    show_banner()
    print(f"Scanning for possible duplicates by size and filename in:\n{path}\n")
    groups = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            full = os.path.join(root, file)
            try:
                size = os.path.getsize(full)
            except Exception:
                size = -1
            key = (file.lower(), size)
            groups.setdefault(key, []).append(full)
    dupes = [v for v in groups.values() if len(v) > 1]
    dupes.sort(key=lambda g: (-len(g), g[0].lower()))
    if not dupes:
        print("No likely duplicates found.")
        pause()
        return
    shown_groups = 0
    for group in dupes:
        shown_groups += 1
        print("-" * 78)
        print(f"{os.path.basename(group[0])}    {format_size(os.path.getsize(group[0])) if os.path.exists(group[0]) else '?'}")
        for item in group:
            shown = item
            if len(shown) > 76:
                shown = "..." + shown[-73:]
            print(shown)
        if shown_groups >= 20:
            break
    if len(dupes) > 20:
        print("-" * 78)
        print(f"Showing first 20 groups of {len(dupes)}")
    pause()

def open_entry(path):
    target = choose_entry(path)
    if not target:
        return path
    if os.path.isdir(target):
        return target
    preview_text_file(target)
    return path

def jump_to_path():
    clear()
    show_banner()
    target = input("Enter folder path: ").strip()
    if os.path.isdir(target):
        return os.path.abspath(target)
    print("That folder does not exist.")
    pause()
    return None

def main_menu():
    current = os.getcwd()
    while True:
        clear()
        show_banner()
        print_directory(current, page=1, page_size=15)
        print("\n1  Open folder or preview file")
        print("2  Go up one folder")
        print("3  Jump to a path")
        print("4  Search by name")
        print("5  Directory stats")
        print("6  Show tree")
        print("7  Create folder")
        print("8  Create text file")
        print("9  Rename item")
        print("10 Copy item")
        print("11 Move item")
        print("12 Delete item")
        print("13 Organize files by extension")
        print("14 Duplicate report")
        print("15 Refresh")
        print("0  Exit")
        choice = input("\nChoose: ").strip()

        if choice == "1":
            current = open_entry(current)
        elif choice == "2":
            parent = os.path.dirname(current)
            if parent and parent != current:
                current = parent
        elif choice == "3":
            new_path = jump_to_path()
            if new_path:
                current = new_path
        elif choice == "4":
            search_menu(current)
        elif choice == "5":
            show_stats(current)
        elif choice == "6":
            show_tree(current)
        elif choice == "7":
            make_folder(current)
        elif choice == "8":
            make_text_file(current)
        elif choice == "9":
            rename_entry(current)
        elif choice == "10":
            copy_entry(current)
        elif choice == "11":
            move_entry(current)
        elif choice == "12":
            delete_entry(current)
        elif choice == "13":
            organize_by_extension(current)
        elif choice == "14":
            duplicate_report(current)
        elif choice == "15":
            pass
        elif choice == "0":
            clear()
            print("Goodbye.")
            sys.exit()
        else:
            print("Invalid choice.")
            pause()

if __name__ == "__main__":
    main_menu()

# End of code
""" This code is essentially a simple
Python-based file explorer tool. It uses the terminal that the code was run on to access.
It may not be a very powerful file explorer, but it has a lot of nice features!
Explore the features thorugh the menu, and have fun!
Run this in VS Code's terminal for best outcome!

 """

