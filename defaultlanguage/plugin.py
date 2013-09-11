import os
import sys
import logging
from gi.repository import GObject, Gedit, Gtk, PeasGtk, GtkSource

logging.basicConfig()
LOG_LEVEL = logging.WARN
 
# For a plugin tutorial, see http://www.micahcarrick.com/writing-plugins-for-gedit-3-in-python.html
class DefaultLanguagePlugin(GObject.Object, Gedit.ViewActivatable):
    """
    Default Language Plugin for Gedit 3.x
    """
    __gtype_name__ = "DefaultLanguagePlugin"
    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(LOG_LEVEL)
        self._is_loaded = False
    
    def do_activate(self):
        """ Activate plugin """
        self._log.debug("Activating plugin")
        self._init_settings()
        self._handlers = []
        self._language_manager = GtkSource.LanguageManager.get_default()
        self._doc = self.view.get_buffer()
        self.set_default_language()
        hid = self.view.connect("notify::editable", self.on_notify_editable)
        self._handlers.append((self.view, hid))
    
    def do_deactivate(self):
        """ Deactivate the plugin """
        self._log.debug("Deactivating plugin")
        for obj, hid in self._handlers:
          obj.disconnect(hid)
        self._handlers = None
        self._language_manager = None

    def on_notify_editable(self, view, pspec):
        if self._doc.get_location() is None:
          return
        # By setting a default language, GtkSourceView refuses to
        # switch the language, so we do it manually
        lang = self._language_manager.guess_language(None, self._doc.get_mime_type())
        if lang is None:
          return
        self._doc.set_language(lang)

    def set_default_language(self):
        # TODO read from preferences
        lang = self._language_manager.get_language('asciidoc')
        if lang is None:
          return
        self._doc.set_language(lang)

    def _init_settings(self):
        """ Initialize GSettings if available. """

