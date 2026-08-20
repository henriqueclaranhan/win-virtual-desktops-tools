from modules import hot_corner
from components import settings
import os
import sys
import ctypes
import multiprocessing
import tkinter as tk
from tkinter import ttk
import win32api
import win32con
import win32gui

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
	sys.path.insert(0, _project_root)


WINDOW_TITLE = "Configurações dos Hot Corners"


def _get_resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


def _get_connected_monitors():
	monitors = []
	try:
		enum_mons = win32api.EnumDisplayMonitors()
		primary_mon = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTOPRIMARY)
		primary_info = win32api.GetMonitorInfo(primary_mon)
		primary_device = primary_info.get("Device")

		for idx, (h_mon, hdc, rect) in enumerate(enum_mons):
			info = win32api.GetMonitorInfo(h_mon)
			width = rect[2] - rect[0]
			height = rect[3] - rect[1]
			is_primary = info.get("Device") == primary_device
			monitors.append({
				"index": idx,
				"device": info.get("Device", f"Display {idx + 1}"),
				"resolution": f"{width}x{height}",
				"is_primary": is_primary,
			})
	except Exception as err:
		print(f"Error enumerating monitors: {err}")
		monitors.append({
			"index": 0,
			"device": "Display 1",
			"resolution": "Primary",
			"is_primary": True,
		})

	return monitors


class HotCornerSettingsApp:
	def __init__(self, root):
		self.root = root
		self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
		self.root.title(WINDOW_TITLE)
		self.root.resizable(False, False)

		icon_path = _get_resource_path("assets/icon.ico")
		if os.path.exists(icon_path):
			try:
				self.root.iconbitmap(icon_path)
			except Exception:
				pass

		self.style = ttk.Style()
		try:
			self.style.theme_use("vista")
		except Exception:
			pass

		self.monitors_info = _get_connected_monitors()
		self.monitor_corner_vars = {}

		for mon in self.monitors_info:
			idx = mon["index"]
			corners = settings.get_monitor_corners(idx)
			self.monitor_corner_vars[idx] = {
				"top_left": tk.BooleanVar(value=corners.get("top_left", False if idx > 0 else True)),
				"top_right": tk.BooleanVar(value=corners.get("top_right", False)),
				"bottom_left": tk.BooleanVar(value=corners.get("bottom_left", False)),
				"bottom_right": tk.BooleanVar(value=corners.get("bottom_right", False)),
			}

		self.__build_ui()
		self.__center_window(480, 460)

	def __build_ui(self):
		main_frame = ttk.Frame(self.root, padding="16 16 16 16")
		main_frame.pack(fill=tk.BOTH, expand=True)

		# Header
		header_frame = ttk.Frame(main_frame)
		header_frame.pack(fill=tk.X, pady=(0, 12))

		title_label = ttk.Label(
			header_frame,
			text="📐 Personalização dos Hot Corners",
			font=("Segoe UI", 12, "bold")
		)
		title_label.pack(anchor=tk.W)

		desc_label = ttk.Label(
			header_frame,
			text="Escolha quais cantos ativam a Visão de Tarefas individualmente em cada monitor.",
			font=("Segoe UI", 9),
			wraplength=440
		)
		desc_label.pack(anchor=tk.W, pady=(3, 0))

		# Monitor Notebook or Frame
		if len(self.monitors_info) > 1:
			notebook = ttk.Notebook(main_frame)
			notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 14))

			for mon in self.monitors_info:
				tab_frame = ttk.Frame(notebook, padding="14 12 14 12")
				idx = mon["index"]
				tag = " (Principal)" if mon["is_primary"] else ""
				tab_title = f"🖥️ Monitor {idx + 1}{tag}"
				notebook.add(tab_frame, text=tab_title)

				self.__build_monitor_controls(tab_frame, mon)
		else:
			mon = self.monitors_info[0]
			mon_frame = ttk.LabelFrame(
				main_frame,
				text=f" 🖥️ Monitor 1 (Principal) — {mon['resolution']} ",
				padding="14 12 14 12"
			)
			mon_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 14))
			self.__build_monitor_controls(mon_frame, mon, show_copy_btn=False)

		# Bottom Action Buttons
		btn_frame = ttk.Frame(main_frame)
		btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

		save_btn = ttk.Button(
			btn_frame,
			text="Salvar",
			command=self.__on_save,
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

	def __build_monitor_controls(self, parent, mon, show_copy_btn=True):
		idx = mon["index"]
		vars_dict = self.monitor_corner_vars[idx]

		info_label = ttk.Label(
			parent,
			text=f"Resolução: {mon['resolution']}  |  Dispositivo: {mon['device']}",
			font=("Segoe UI", 9, "italic")
		)
		info_label.pack(anchor=tk.W, pady=(0, 10))

		corners_frame = ttk.LabelFrame(parent, text=" Cantos Ativos ", padding="12 10 12 10")
		corners_frame.pack(fill=tk.X, pady=(0, 10))

		# 2x2 Grid Layout for Corners
		grid_frame = ttk.Frame(corners_frame)
		grid_frame.pack(fill=tk.X, expand=True)

		chk_tl = ttk.Checkbutton(
			grid_frame,
			text="Superior Esquerdo ↖",
			variable=vars_dict["top_left"]
		)
		chk_tl.grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=6)

		chk_tr = ttk.Checkbutton(
			grid_frame,
			text="Superior Direito ↗",
			variable=vars_dict["top_right"]
		)
		chk_tr.grid(row=0, column=1, sticky=tk.W, pady=6)

		chk_bl = ttk.Checkbutton(
			grid_frame,
			text="Inferior Esquerdo ↙",
			variable=vars_dict["bottom_left"]
		)
		chk_bl.grid(row=1, column=0, sticky=tk.W, padx=(0, 20), pady=6)

		chk_br = ttk.Checkbutton(
			grid_frame,
			text="Inferior Direito ↘",
			variable=vars_dict["bottom_right"]
		)
		chk_br.grid(row=1, column=1, sticky=tk.W, pady=6)

		# Quick action buttons
		actions_frame = ttk.Frame(parent)
		actions_frame.pack(fill=tk.X, pady=(4, 0))

		if show_copy_btn and len(self.monitors_info) > 1:
			copy_btn = ttk.Button(
				actions_frame,
				text="📋 Aplicar cantos a todos os monitores",
				command=lambda: self.__copy_to_all(idx)
			)
			copy_btn.pack(side=tk.LEFT, padx=(0, 6))

		clear_btn = ttk.Button(
			actions_frame,
			text="✖ Limpar cantos",
			command=lambda: self.__clear_corners(idx)
		)
		clear_btn.pack(side=tk.LEFT)

	def __copy_to_all(self, source_idx):
		src_vars = self.monitor_corner_vars[source_idx]
		tl = src_vars["top_left"].get()
		tr = src_vars["top_right"].get()
		bl = src_vars["bottom_left"].get()
		br = src_vars["bottom_right"].get()

		for idx, vars_dict in self.monitor_corner_vars.items():
			if idx != source_idx:
				vars_dict["top_left"].set(tl)
				vars_dict["top_right"].set(tr)
				vars_dict["bottom_left"].set(bl)
				vars_dict["bottom_right"].set(br)

	def __clear_corners(self, target_idx):
		vars_dict = self.monitor_corner_vars[target_idx]
		vars_dict["top_left"].set(False)
		vars_dict["top_right"].set(False)
		vars_dict["bottom_left"].set(False)
		vars_dict["bottom_right"].set(False)

	def __on_save(self):
		config = {}
		for idx, vars_dict in self.monitor_corner_vars.items():
			config[str(idx)] = {
				"top_left": vars_dict["top_left"].get(),
				"top_right": vars_dict["top_right"].get(),
				"bottom_left": vars_dict["bottom_left"].get(),
				"bottom_right": vars_dict["bottom_right"].get(),
			}

		settings.set_hot_corner_config(config)
		hot_corner.refresh_active_corners()
		self.root.destroy()

	def __center_window(self, width, height):
		self.root.update_idletasks()
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()
		x = (screen_width - width) // 2
		y = (screen_height - height) // 2
		self.root.geometry(f"{width}x{height}+{x}+{y}")


_ui_process = None


def _apply_window_icon(hwnd, icon_path):
	if os.path.exists(icon_path):
		try:
			hicon_small = win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 16, 16, win32con.LR_LOADFROMFILE)
			hicon_big = win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 32, 32, win32con.LR_LOADFROMFILE)
			win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon_small)
			win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon_big)
		except Exception:
			pass


def run_ui_process():
	try:
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("win_virtual_desktops_tools.hot_corners_ui")
	except Exception:
		pass

	root = tk.Tk()
	HotCornerSettingsApp(root)

	icon_path = _get_resource_path("assets/icon.ico")
	root.update_idletasks()
	try:
		hwnd = win32gui.GetParent(root.winfo_id()) or root.winfo_id()
		_apply_window_icon(hwnd, icon_path)
	except Exception:
		pass

	root.mainloop()


def open_hot_corner_settings_window():
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


if __name__ == "__main__":
	run_ui_process()
