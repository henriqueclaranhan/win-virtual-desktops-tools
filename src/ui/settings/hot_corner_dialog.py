from __future__ import annotations
import os
import ctypes
import multiprocessing
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
import win32con
import win32gui

from src.core.models.config import CornerSettings
from src.core.models.monitor import MonitorInfo
from src.infrastructure.storage.path_resolver import PathResolver
from src.infrastructure.storage.config_repository import ConfigRepository
from src.infrastructure.os.win32_adapter import WindowsAdapter


WINDOW_TITLE = "Configurações dos Hot Corners"


class HotCornerSettingsViewModel:
    """Manages state, monitor data, and persistence logic for the Settings dialog."""

    def __init__(self, config_repo: ConfigRepository, win_adapter: WindowsAdapter):
        self.config_repo = config_repo
        self.win_adapter = win_adapter

        self.monitors: List[MonitorInfo] = self.win_adapter.get_connected_monitors()
        self.corner_vars: Dict[int, Dict[str, tk.BooleanVar]] = {}
        self._init_vars()

    def _init_vars(self) -> None:
        config = self.config_repo.get_config()
        for mon in self.monitors:
            corners = config.get_monitor_corners(mon.index)
            self.corner_vars[mon.index] = {
                "top_left": tk.BooleanVar(value=corners.top_left),
                "top_right": tk.BooleanVar(value=corners.top_right),
                "bottom_left": tk.BooleanVar(value=corners.bottom_left),
                "bottom_right": tk.BooleanVar(value=corners.bottom_right),
            }

    def copy_to_all(self, source_idx: int) -> None:
        src = self.corner_vars[source_idx]
        tl = src["top_left"].get()
        tr = src["top_right"].get()
        bl = src["bottom_left"].get()
        br = src["bottom_right"].get()

        for idx, vars_dict in self.corner_vars.items():
            if idx != source_idx:
                vars_dict["top_left"].set(tl)
                vars_dict["top_right"].set(tr)
                vars_dict["bottom_left"].set(bl)
                vars_dict["bottom_right"].set(br)

    def clear_corners(self, target_idx: int) -> None:
        vars_dict = self.corner_vars[target_idx]
        for var in vars_dict.values():
            var.set(False)

    def save(self) -> None:
        config = self.config_repo.get_config()
        new_map: Dict[str, CornerSettings] = {}

        for idx, vars_dict in self.corner_vars.items():
            new_map[str(idx)] = CornerSettings(
                top_left=vars_dict["top_left"].get(),
                top_right=vars_dict["top_right"].get(),
                bottom_left=vars_dict["bottom_left"].get(),
                bottom_right=vars_dict["bottom_right"].get(),
            )

        config.hot_corner_config = new_map
        self.config_repo.save_config(config)


class HotCornerSettingsView:
    """Tkinter View for configuring monitor hot corners."""

    def __init__(self, root: tk.Tk, view_model: HotCornerSettingsViewModel):
        self.root = root
        self.vm = view_model

        self.root.title(WINDOW_TITLE)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self._apply_theme()
        self._build_ui()
        self._center_window(480, 460)

    def _apply_theme(self) -> None:
        icon_path = PathResolver.get_resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        style = ttk.Style()
        try:
            style.theme_use("vista")
        except Exception:
            pass

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding="16 16 16 16")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 12))

        title_label = ttk.Label(
            header,
            text="📐 Personalização dos Hot Corners",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor=tk.W)

        desc_label = ttk.Label(
            header,
            text="Escolha quais cantos ativam a Visão de Tarefas individualmente em cada monitor.",
            font=("Segoe UI", 9),
            wraplength=440
        )
        desc_label.pack(anchor=tk.W, pady=(3, 0))

        if len(self.vm.monitors) > 1:
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 14))

            for mon in self.vm.monitors:
                tab_frame = ttk.Frame(notebook, padding="14 12 14 12")
                tag = " (Principal)" if mon.is_primary else ""
                notebook.add(tab_frame, text=f"🖥️ Monitor {mon.index + 1}{tag}")
                self._build_monitor_controls(tab_frame, mon, show_copy_btn=True)
        else:
            mon = self.vm.monitors[0]
            mon_frame = ttk.LabelFrame(
                main_frame,
                text=f" 🖥️ Monitor 1 (Principal) — {mon.resolution_str} ",
                padding="14 12 14 12"
            )
            mon_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 14))
            self._build_monitor_controls(mon_frame, mon, show_copy_btn=False)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        save_btn = ttk.Button(
            btn_frame,
            text="Salvar",
            command=self._on_save,
            width=12
        )
        save_btn.pack(side=tk.RIGHT, padx=(6, 0))

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.root.destroy,
            width=12
        )
        cancel_btn.pack(side=tk.RIGHT)

    def _build_monitor_controls(self, parent: ttk.Widget, mon: MonitorInfo, show_copy_btn: bool = True) -> None:
        idx = mon.index
        vars_dict = self.vm.corner_vars[idx]

        info_label = ttk.Label(
            parent,
            text=f"Resolução: {mon.resolution_str}  |  Dispositivo: {mon.device_name}",
            font=("Segoe UI", 9, "italic")
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))

        corners_frame = ttk.LabelFrame(parent, text=" Cantos Ativos ", padding="12 10 12 10")
        corners_frame.pack(fill=tk.X, pady=(0, 10))

        grid_frame = ttk.Frame(corners_frame)
        grid_frame.pack(fill=tk.X, expand=True)

        chk_tl = ttk.Checkbutton(grid_frame, text="Superior Esquerdo ↖", variable=vars_dict["top_left"])
        chk_tl.grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=6)

        chk_tr = ttk.Checkbutton(grid_frame, text="Superior Direito ↗", variable=vars_dict["top_right"])
        chk_tr.grid(row=0, column=1, sticky=tk.W, pady=6)

        chk_bl = ttk.Checkbutton(grid_frame, text="Inferior Esquerdo ↙", variable=vars_dict["bottom_left"])
        chk_bl.grid(row=1, column=0, sticky=tk.W, padx=(0, 20), pady=6)

        chk_br = ttk.Checkbutton(grid_frame, text="Inferior Direito ↘", variable=vars_dict["bottom_right"])
        chk_br.grid(row=1, column=1, sticky=tk.W, pady=6)

        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill=tk.X, pady=(4, 0))

        if show_copy_btn and len(self.vm.monitors) > 1:
            copy_btn = ttk.Button(
                actions_frame,
                text="📋 Aplicar cantos a todos os monitores",
                command=lambda: self.vm.copy_to_all(idx)
            )
            copy_btn.pack(side=tk.LEFT, padx=(0, 6))

        clear_btn = ttk.Button(
            actions_frame,
            text="✖ Limpar cantos",
            command=lambda: self.vm.clear_corners(idx)
        )
        clear_btn.pack(side=tk.LEFT)

    def _on_save(self) -> None:
        self.vm.save()
        self.root.destroy()

    def _center_window(self, width: int, height: int) -> None:
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")


_ui_process: Optional[multiprocessing.Process] = None


def _apply_window_icon(hwnd: int, icon_path: str) -> None:
    if os.path.exists(icon_path):
        try:
            hicon_small = win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 16, 16, win32con.LR_LOADFROMFILE)
            hicon_big = win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 32, 32, win32con.LR_LOADFROMFILE)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon_small)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon_big)
        except Exception:
            pass


def run_ui_process() -> None:
    """Entry point for the isolated UI process."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("win_virtual_desktops_tools.hot_corners_ui")
    except Exception:
        pass

    root = tk.Tk()
    repo = ConfigRepository()
    win_adapter = WindowsAdapter()
    vm = HotCornerSettingsViewModel(config_repo=repo, win_adapter=win_adapter)
    HotCornerSettingsView(root, vm)

    icon_path = PathResolver.get_resource_path("assets/icon.ico")
    root.update_idletasks()
    try:
        hwnd = win32gui.GetParent(root.winfo_id()) or root.winfo_id()
        _apply_window_icon(hwnd, icon_path)
    except Exception:
        pass

    root.mainloop()


def open_hot_corner_settings_window() -> None:
    """Opens or focuses the settings dialog process."""
    global _ui_process

    try:
        hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return
    except Exception:
        pass

    if _ui_process is not None and _ui_process.is_alive():
        return

    _ui_process = multiprocessing.Process(target=run_ui_process, daemon=True)
    _ui_process.start()
