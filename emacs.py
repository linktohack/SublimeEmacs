import os
import sublime, sublime_plugin
from SublimeEmacs.libemacs import Emacs, EMACS, CLIENT, PARAM, SOCKET, INIT_FILE, ALTERNATE_EDITOR

debug = lambda *args, **kwargs: None
# debug = print

def _settings(view):
    return {
        'emacs': view.settings().get('emacs', EMACS), 
        'client': view.settings().get('emacs_client', CLIENT), 
        'param': view.settings().get('emacs_param', PARAM), 
        'socket': view.settings().get('emacs_socket', SOCKET), 
        'init_file': view.settings().get('emacs_init_file', INIT_FILE),
        'alternate_editor': view.settings().get('emacs_alternate_editor', ALTERNATE_EDITOR)
    }

class EmacsEvalCommand(sublime_plugin.TextCommand):
    def run(self, edit, body):
        emacs = Emacs(**_settings(self.view))
        view = self.view
        file_name = self.view.file_name()
        file_ext = None
        if file_name is not None:
            _, file_ext = os.path.splitext(file_name)
        tempdir = view.settings().get('emacs_tempdir', '.')
        if tempdir == '.':
            tempdir = os.path.dirname(file_name)
        elif tempdir == '':
            tempdir = None
        sel = view.sel()
        beg = sel[0].begin()
        end = sel[0].end()
        buffer_region = sublime.Region(0, view.size())
        buffer_string = view.substr(buffer_region)
        new_buffer_string, stdout = emacs.eval_in_buffer_string(buffer_string,
                                                                body, beg, end, 
                                                                tempdir=tempdir,
                                                                file_ext=file_ext)
        debug('stdout', stdout)
        view.replace(edit, buffer_region, new_buffer_string)
        def to_int(x):
            try: return int(float(x))
            except: return 0
        mark, point, mark_active = map(to_int, stdout[1:-2].split())
        if not mark_active or not point:
            mark = point
        sel.clear()
        sel.add(sublime.Region(mark, point))

class EmacsKillDaemonCommand(sublime_plugin.WindowCommand):
    def run(self):
        emacs = Emacs(**_settings(self.window.active_view()))
        emacs.eval("(kill-emacs)")

class EmacsOpenCurrentFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        emacs = Emacs(**_settings(self.view))
        file_name = self.view.file_name()
        (row,col) = self.view.rowcol(self.view.sel()[0].begin())
        emacs.open_file(file_name, row+1, col+1)
