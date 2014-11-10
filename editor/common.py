# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>

"""Common functions, callbacks and other things"""

import os

import PyCEGUI


def cb_cut_copy_paste(args):
    """Event callback for text copy, cut and paste operations"""
    scancode = args.scancode
    syskeys = args.sysKeys
    if not ((syskeys & PyCEGUI.Key.LeftControl) or
            (syskeys & PyCEGUI.Key.RightControl)):
        return False
    retval = False
    window = args.window
    import Tkinter
    tk_win = Tkinter.Tk()
    tk_win.wm_withdraw()
    tk_win.update()
    clipboard = PyCEGUI.System.getSingleton().getClipboard()
    text = tk_win.clipboard_get()
    clipboard.setText(text)

    if scancode == PyCEGUI.Key.C:
        try:
            window.performCopy(clipboard)
            retval = True
        except AttributeError:
            return False
    elif scancode == PyCEGUI.Key.X:
        try:
            window.performCut(clipboard)
            retval = True
        except AttributeError:
            return False
    elif scancode == PyCEGUI.Key.V:
        try:
            window.performPaste(clipboard)
            retval = True
        except AttributeError:
            return False
    tk_win.clipboard_clear()
    text = clipboard.getText()
    tk_win.clipboard_append(text)
    return retval


def split_new_path(path):
    """Splits a path in a existing and new path and returns both"""
    path = os.path.normpath(path)
    if os.path.exists(path):
        return path, ""
    else:
        head, trail = os.path.split(path)
        exist_path, new_path = split_new_path(head)
        return exist_path, os.path.join(new_path, trail)


def is_dir_path_valid(path):
    """Checks if a directory path is valid

    Args:

        path: The directory path to check
    """
    if os.path.exists(path):
        return True
    exist_path, new_path = split_new_path(path)
    old_cwd = os.getcwdu()
    os.chdir(exist_path)
    try:
        os.makedirs(new_path)
        return True
    except OSError:
        return False
    finally:
        try:
            os.removedirs(new_path)
        except OSError:
            index = 0
            dir_tokens = os.path.normpath(new_path).split(os.sep)
            while os.path.exists(dir_tokens[0]):
                index -= 1
                try:
                    os.removedirs(os.path.join(*dir_tokens[:index]))
                except OSError:
                    pass
        os.chdir(old_cwd)


def select_path(title, initialdir=None):
    """Show a message browse dialog"""
    import Tkinter
    import tkFileDialog
    window = Tkinter.Tk()
    window.wm_withdraw()
    return tkFileDialog.askdirectory(title=title, initialdir=initialdir)


def ask_create_path(path):
    import Tkinter
    import tkMessageBox
    window = Tkinter.Tk()
    window.wm_withdraw()
    answer = tkMessageBox.askyesno(
        _("Create path"),
        _("Path does not exist, create it? "
            "(Must be manually deleted if changed later)"))
    if answer:
        os.makedirs(path)
        return True
    return False
