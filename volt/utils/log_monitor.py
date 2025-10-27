import os
from PySide6.QtCore import QFileSystemWatcher, Signal


class LogMonitor(QFileSystemWatcher):
    """
    Watches directories for appearance/disappearance of files listed in self._files.
    Only files that are present in self._files (the authoritative list) are ever added as file watchers.
    Directories for those files are always watched so newly-created files (that are in the list)
    will be detected and added automatically.
    """

    new_line = Signal(object)

    def __init__(self, profiles_manager):
        super().__init__()

        self._profiles_manager = profiles_manager
        # Authoritative list of file paths (may include files that don't exist yet)
        self._files = list(self._profiles_manager.files)

        # Track which file paths are currently added to QFileSystemWatcher
        self._watched_files = set()
        # Track which directories are currently watched
        self._watched_dirs = set()

        # Connect signals
        self.fileChanged.connect(self._file_changed_safe_wrap)
        self.directoryChanged.connect(self._directory_changed_safe_wrap)

        # Initialize watchers based on the current _files list
        self._update_watchers_initial()

        self._stats = {
            'log_file': '',
        }

    # -------------------------
    # Public API to mutate list
    # -------------------------
    def addLogFile(self, log_file):
        """Add a path to the authoritative list and update watchers."""
        if log_file in self._files:
            return

        self._files.append(log_file)
        dir_path = os.path.dirname(log_file) or '.'

        # Ensure we watch the directory so creation of the file will be detected later
        if dir_path not in self._watched_dirs:
            self.addPath(dir_path)
            self._watched_dirs.add(dir_path)

        # If file already exists, start watching it immediately
        if os.path.isfile(log_file) and log_file not in self._watched_files:
            self.addPath(log_file)
            self._watched_files.add(log_file)

    def removeLogFile(self, log_file):
        """Remove a path from the authoritative list and update watchers."""
        if log_file not in self._files:
            return

        self._files.remove(log_file)

        # If we were watching the file, stop watching it (we still keep directory watched)
        if log_file in self._watched_files:
            try:
                self.removePath(log_file)
            except Exception:
                pass
            self._watched_files.discard(log_file)

        # Optionally remove dir watcher if no other files (in _files) live in that dir
        dir_path = os.path.dirname(log_file) or '.'
        if dir_path in self._watched_dirs:
            # check whether any remaining file paths are in this dir
            still_need_dir = False
            for f in self._files:
                if os.path.dirname(f) == dir_path:
                    still_need_dir = True
                    break
            if not still_need_dir:
                try:
                    self.removePath(dir_path)
                except Exception:
                    pass
                self._watched_dirs.discard(dir_path)

    def stop(self):
        # Disconnect signals and clear watchers
        try:
            self.fileChanged.disconnect(self._file_changed_safe_wrap)
        except Exception:
            pass
        try:
            self.directoryChanged.disconnect(self._directory_changed_safe_wrap)
        except Exception:
            pass

        # remove paths we've explicitly added
        for f in list(self._watched_files):
            try:
                self.removePath(f)
            except Exception:
                pass
        self._watched_files.clear()

        for d in list(self._watched_dirs):
            try:
                self.removePath(d)
            except Exception:
                pass
        self._watched_dirs.clear()

    # -----------------------------------
    # Internal helpers and event handlers
    # -----------------------------------
    def _update_watchers_initial(self):
        """Initialize watchers from self._files list."""
        for f in self._files:
            dir_path = os.path.dirname(f) or '.'
            # ensure directory watcher exists
            if dir_path not in self._watched_dirs:
                try:
                    self.addPath(dir_path)
                except Exception:
                    # on some platforms, adding a non-existent dir raises; ignore
                    pass
                self._watched_dirs.add(dir_path)

            # if file exists now, watch it as a file
            if os.path.isfile(f) and f not in self._watched_files:
                try:
                    self.addPath(f)
                    self._watched_files.add(f)
                except Exception:
                    pass

    def _file_changed_safe_wrap(self, changed_file):
        try:
            self._file_changed(changed_file)
        except FileNotFoundError:
            # File disappeared between signal and handling — remove file watcher but keep dir
            if changed_file in self._watched_files:
                try:
                    self.removePath(changed_file)
                except Exception:
                    pass
                self._watched_files.discard(changed_file)
            print(f"File not found during change handling: {changed_file}")

    def _file_changed(self, changed_file):
        """
        Called when a watched file has changed or been removed/created (platform-dependent).
        We'll only react if changed_file is in the authoritative list (it should be).
        If the file has been removed, QFileSystemWatcher can emit fileChanged as well;
        we handle removal by dropping the file watcher so that directoryChanges can detect re-create.
        """
        # Only act for files that are in the authoritative list
        if changed_file not in self._files:
            return

        # If file no longer exists, remove the file watcher but keep the directory watcher.
        if not os.path.isfile(changed_file):
            if changed_file in self._watched_files:
                try:
                    self.removePath(changed_file)
                except Exception:
                    pass
                self._watched_files.discard(changed_file)
            return

        # At this point file exists and is in _files. Ensure it's watched (some platforms re-add)
        if changed_file not in self._watched_files:
            try:
                self.addPath(changed_file)
            except Exception:
                pass
            self._watched_files.add(changed_file)

        # Your original behavior when a file becomes active/changed
        if changed_file != self._stats.get('log_file'):
            self._stats['log_file'] = changed_file
            self._profiles_manager.setActiveByFile(changed_file)

    def _directory_changed_safe_wrap(self, changed_dir):
        try:
            self._directory_changed(changed_dir)
        except Exception as exc:
            print(f"Error handling directory change for {changed_dir}: {exc}")

    def _directory_changed(self, changed_dir):
        """
        Called when a directory we watch changes. We only care about files that are
        in self._files and that live in this directory. If any of those files now exist
        and are not yet being watched, start watching them and trigger activation.
        """
        # find authoritative files that live in this directory
        for target in list(self._files):
            if os.path.dirname(target) != changed_dir:
                continue
            # if file exists now and we're not yet watching it, add it
            if os.path.isfile(target) and target not in self._watched_files:
                try:
                    self.addPath(target)
                    self._watched_files.add(target)
                except Exception:
                    pass
                # Optionally set active immediately when it appears
                if target != self._stats.get('log_file'):
                    self._stats['log_file'] = target
                    self._profiles_manager.setActiveByFile(target)

    # -------------------------
    # Utility to resync externally
    # -------------------------
    def refresh_from_profiles(self):
        """
        If the profiles_manager may have updated the canonical file list externally,
        call this to resync watchers to match profiles_manager.files.
        This will add/remove watchers as needed to reflect the new authoritative list.
        """
        new_list = list(self._profiles_manager.files)
        # Remove any files that are no longer in the authoritative list
        for f in list(self._files):
            if f not in new_list:
                self.removeLogFile(f)

        # Add any new files from the authoritative list
        for f in new_list:
            if f not in self._files:
                self.addLogFile(f)
