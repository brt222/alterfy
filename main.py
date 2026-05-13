"""
Alterfy — main application
"""
import sys
import os
import random
import time

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame,
    QSizePolicy, QStackedWidget, QDialog, QDialogButtonBox,
    QInputDialog, QMenu, QMessageBox, QStatusBar
)
from PyQt6.QtCore import (
    Qt, QThread, QObject, pyqtSignal, QTimer, QSize, QPoint
)
from PyQt6.QtGui import (
    QPixmap, QColor, QPainter, QPainterPath, QFont,
    QIcon, QCursor, QPalette, QAction
)

import yt_dlp
import requests

try:
    import vlc
    VLC_AVAILABLE = True
except Exception:
    VLC_AVAILABLE = False

try:
    import keyboard as kb
    KB_AVAILABLE = True
except Exception:
    KB_AVAILABLE = False

from data_manager import DataManager
import i18n
from i18n import t, LANGUAGES, save_lang

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
BG_COLOR        = "#0a0a0a"
BG_SECONDARY    = "#111111"
BG_CARD         = "#181818"
BG_HOVER        = "#282828"
BG_ELEVATED     = "#242424"
ACCENT          = "#1DB954"
ACCENT_DIM      = "#1aa34a"
TEXT_PRIMARY    = "#FFFFFF"
TEXT_SECONDARY  = "#B3B3B3"
TEXT_DIM        = "#535353"
PROGRESS_BG     = "#3E3E3E"
PLAYER_BG       = "#181818"
BORDER_COLOR    = "#282828"
SEARCH_DELAY_MS = 600


# ─────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────

def make_round_pixmap(pixmap: QPixmap, radius: int = 8) -> QPixmap:
    size = pixmap.size()
    rounded = QPixmap(size)
    rounded.fill(Qt.GlobalColor.transparent)
    p = QPainter(rounded)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
    p.setClipPath(path)
    p.drawPixmap(0, 0, pixmap)
    p.end()
    return rounded


def ms_to_str(ms: int) -> str:
    s = max(0, ms) // 1000
    return f"{s // 60}:{s % 60:02d}"


def sec_to_str(s: int) -> str:
    s = max(0, int(s))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h:
        return f"{h}h {m}m"
    return f"{m}m {sec}s"


def elide(text: str, n: int) -> str:
    return text[:n] + "…" if len(text) > n else text


# ─────────────────────────────────────────────
# SVG ICONS
# ─────────────────────────────────────────────

def svg_icon(body: str, size: int = 24, color: str = "#FFFFFF") -> QPixmap:
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtCore import QByteArray
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           f'width="{size}" height="{size}" fill="{color}">{body}</svg>')
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    r = QSvgRenderer(QByteArray(svg.encode()))
    p = QPainter(pix)
    r.render(p)
    p.end()
    return pix


I_PLAY    = '<path d="M8 5v14l11-7z"/>'
I_PAUSE   = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>'
I_PREV    = '<path d="M6 6h2v12H6zm3.5 6 8.5 6V6z"/>'
I_NEXT    = '<path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>'
I_SHUFFLE = '<path d="M10.59 9.17 5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/>'
I_REPEAT  = '<path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>'
I_HEART   = '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>'
I_VOLMAX  = '<path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>'
I_QUEUE   = '<path d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>'
I_SEARCH  = '<path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>'
I_HOME    = '<path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>'
I_LIBRARY = '<path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>'
I_PLUS    = '<path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>'
I_TRASH   = '<path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>'
I_EDIT    = '<path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a.9959.9959 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>'
I_CLOCK   = '<path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/>'
I_MUSIC   = '<path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>'
I_DOTS    = '<path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>'
I_BACK    = '<path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>'
I_CLOSE   = '<path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>'
I_LYRICS  = '<path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9c.83 0 1.5-.67 1.5-1.5 0-.39-.15-.74-.39-1.01-.23-.26-.38-.61-.38-.99 0-.83.67-1.5 1.5-1.5H16c2.76 0 5-2.24 5-5 0-4.42-4.03-8-9-8zm-5.5 9c-.83 0-1.5-.67-1.5-1.5S5.67 9 6.5 9 8 9.67 8 10.5 7.33 12 6.5 12zm3-4C8.67 8 8 7.33 8 6.5S8.67 5 9.5 5s1.5.67 1.5 1.5S10.33 8 9.5 8zm5 0c-.83 0-1.5-.67-1.5-1.5S13.67 5 14.5 5s1.5.67 1.5 1.5S15.33 8 14.5 8zm3 4c-.83 0-1.5-.67-1.5-1.5S16.67 9 17.5 9s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>'
I_SETTINGS= '<path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>'
I_INFO    = '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>'


def icon_btn(svg_body: str, size: int = 24, color: str = TEXT_SECONDARY,
             hover_color: str = TEXT_PRIMARY, icon_size: int = 0) -> QPushButton:
    if icon_size == 0:
        icon_size = size
    btn = QPushButton()
    btn.setFixedSize(size, size)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; }")
    pn = svg_icon(svg_body, icon_size, color)
    ph = svg_icon(svg_body, icon_size, hover_color)
    btn.setIcon(QIcon(pn))
    btn.setIconSize(QSize(icon_size, icon_size))
    btn.enterEvent = lambda e: (btn.setIcon(QIcon(ph)))
    btn.leaveEvent = lambda e: (btn.setIcon(QIcon(pn)))
    return btn


# ─────────────────────────────────────────────
# CUSTOM SLIDER
# ─────────────────────────────────────────────

from PyQt6.QtWidgets import QSlider

class SpotSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None,
                 track_col=PROGRESS_BG, fill_col=TEXT_SECONDARY,
                 hover_fill=ACCENT, h=4, thumb_r=6):
        super().__init__(orientation, parent)
        self._tc, self._fc, self._hf = track_col, fill_col, hover_fill
        self._h, self._tr = h, thumb_r
        self._hov = self._drag = False
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def enterEvent(self, e): self._hov = True;  self.update()
    def leaveEvent(self, e): self._hov = False; self.update()

    def mousePressEvent(self, e):
        self._drag = True
        self._pos_to_val(e.position().x())
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._drag = False
        super().mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        if self._drag:
            self._pos_to_val(e.position().x())
        super().mouseMoveEvent(e)

    def _pos_to_val(self, x):
        r = max(0.0, min(1.0, x / self.width()))
        self.setValue(int(self.minimum() + r * (self.maximum() - self.minimum())))

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h, cy = self.width(), self.height(), self.height() // 2
        r = self._h // 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self._tc))
        p.drawRoundedRect(0, cy - r, w, self._h, r, r)
        rng = self.maximum() - self.minimum() or 1
        ratio = (self.value() - self.minimum()) / rng
        fw = int(ratio * w)
        p.setBrush(QColor(self._hf if (self._hov or self._drag) else self._fc))
        p.drawRoundedRect(0, cy - r, fw, self._h, r, r)
        if self._hov or self._drag:
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(fw - self._tr, cy - self._tr, self._tr * 2, self._tr * 2)
        p.end()


# ─────────────────────────────────────────────
# WORKER THREADS
# ─────────────────────────────────────────────

class SearchWorker(QThread):
    results_ready = pyqtSignal(list)
    error         = pyqtSignal(str)

    def __init__(self, query: str):
        super().__init__()
        self.query   = query
        self._stop   = False

    def stop(self):
        self._stop = True
        self.quit()
        self.wait(2000)

    def run(self):
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True,
                                   "extract_flat": "in_playlist",
                                   "skip_download": True, "ignoreerrors": True}) as ydl:
                info = ydl.extract_info(f"ytsearch15:{self.query}", download=False)
            entries = (info or {}).get("entries", [])
            results = []
            for e in entries:
                if not e: continue
                dur = e.get("duration") or 0
                vid = e.get("id", "")
                results.append({
                    "id":        vid,
                    "title":     e.get("title", "Unknown"),
                    "uploader":  e.get("uploader") or e.get("channel") or "Unknown Artist",
                    "duration":  dur,
                    "thumbnail": e.get("thumbnail") or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                    "url":       e.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}",
                })
            self.results_ready.emit(results)
        except Exception as ex:
            self.error.emit(str(ex))


class StreamWorker(QThread):
    stream_ready = pyqtSignal(str, dict)
    error        = pyqtSignal(str)

    def __init__(self, url: str, meta: dict):
        super().__init__()
        self.url  = url
        self.meta = meta
        self.last_stream_url = ""

    def stop(self):
        self.quit()
        self.wait(3000)

    def run(self):
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True,
                                   "format": "bestaudio/best",
                                   "skip_download": True}) as ydl:
                info = ydl.extract_info(self.url, download=False)
            if not info:
                self.error.emit("No info"); return
            fmts = info.get("formats", [])
            audio_url, best_abr = None, -1
            for f in fmts:
                if f.get("acodec") != "none" and f.get("vcodec") == "none":
                    abr = f.get("abr") or 0
                    if abr > best_abr:
                        best_abr = abr
                        audio_url = f.get("url")
            if not audio_url:
                audio_url = info.get("url")
            if not audio_url:
                self.error.emit("No stream"); return
            self.last_stream_url = audio_url
            self.stream_ready.emit(audio_url, self.meta)
        except Exception as ex:
            self.error.emit(str(ex))


class _ThumbSignals(QObject):
    loaded = pyqtSignal(str, QPixmap)


class ThumbnailWorker:
    """Uses threading.Thread to avoid QThread lifecycle issues for short HTTP fetches."""

    def __init__(self, vid_id: str, url: str):
        import threading
        self.vid_id  = vid_id
        self.url     = url
        self._sig    = _ThumbSignals()
        self.loaded  = self._sig.loaded
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        pass  # daemon thread exits when app closes

    def isRunning(self) -> bool:
        return self._thread.is_alive()

    def _run(self):
        try:
            r = requests.get(self.url, timeout=6)
            if r.status_code == 200:
                pix = QPixmap()
                pix.loadFromData(r.content)
                if not pix.isNull():
                    self._sig.loaded.emit(self.vid_id, pix)
        except Exception:
            pass


class RecommendWorker(QThread):
    results_ready = pyqtSignal(str, list)  # section_label, tracks

    def __init__(self, query: str, label: str):
        super().__init__()
        self.query = query
        self.label = label

    def stop(self):
        self.quit()
        self.wait(2000)

    def run(self):
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True,
                                   "extract_flat": "in_playlist",
                                   "skip_download": True, "ignoreerrors": True}) as ydl:
                info = ydl.extract_info(f"ytsearch8:{self.query}", download=False)
            entries = (info or {}).get("entries", [])
            results = []
            for e in entries:
                if not e: continue
                vid = e.get("id", "")
                results.append({
                    "id":        vid,
                    "title":     e.get("title", "Unknown"),
                    "uploader":  e.get("uploader") or e.get("channel") or "Unknown Artist",
                    "duration":  e.get("duration") or 0,
                    "thumbnail": e.get("thumbnail") or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                    "url":       e.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}",
                })
            self.results_ready.emit(self.label, results)
        except Exception:
            pass


# ─────────────────────────────────────────────
# AUDIO PLAYER
# ─────────────────────────────────────────────

class AudioPlayer(QObject):
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    state_changed    = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._inst = self._player = None
        self._vol  = 80
        self._timer = QTimer()
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._poll)
        self._last_state = ""
        self._init()

    def _init(self):
        if not VLC_AVAILABLE: return
        try:
            self._inst   = vlc.Instance("--no-video", "--quiet",
                                         "--network-caching=2000",
                                         "--live-caching=2000")
            self._player = self._inst.media_player_new()
            self._player.audio_set_volume(self._vol)
        except Exception as ex:
            print(f"VLC: {ex}")

    def load_and_play(self, url: str):
        if not self._player: return
        try:
            m = self._inst.media_new(url)
            m.add_option(":network-caching=2000")
            self._player.set_media(m)
            self._player.play()
            self._timer.start()
            self.state_changed.emit("playing")
        except Exception as ex:
            print(f"VLC play: {ex}")

    def play_pause(self):
        if not self._player: return
        s = self._player.get_state()
        if s == vlc.State.Playing:
            self._player.pause(); self.state_changed.emit("paused")
        elif s in (vlc.State.Paused, vlc.State.Stopped):
            self._player.play(); self.state_changed.emit("playing")

    def stop(self):
        if not self._player: return
        self._player.stop(); self._timer.stop()
        self.state_changed.emit("stopped")

    def seek(self, ms: int):
        if self._player: self._player.set_time(ms)

    def set_volume(self, v: int):
        self._vol = max(0, min(100, v))
        if self._player: self._player.audio_set_volume(self._vol)

    def is_playing(self) -> bool:
        return bool(self._player and self._player.get_state() == vlc.State.Playing)

    def _poll(self):
        if not self._player: return
        s   = self._player.get_state()
        pos = self._player.get_time()
        dur = self._player.get_length()
        if pos >= 0: self.position_changed.emit(pos)
        if dur >  0: self.duration_changed.emit(dur)
        label = {vlc.State.Playing:"playing", vlc.State.Paused:"paused",
                 vlc.State.Stopped:"stopped", vlc.State.Ended:"ended",
                 vlc.State.Error:"error"}.get(s, "")
        if label != self._last_state:
            self._last_state = label
            self.state_changed.emit(label)


# ─────────────────────────────────────────────
# RESULT CARD (shared across pages)
# ─────────────────────────────────────────────

class ResultCard(QFrame):
    play_requested   = pyqtSignal(dict)
    add_to_playlist  = pyqtSignal(dict)
    remove_requested = pyqtSignal(dict)  # for playlist detail

    def __init__(self, meta: dict, show_remove: bool = False, index: int = 0, parent=None):
        super().__init__(parent)
        self.meta        = meta
        self.show_remove = show_remove
        self.setFixedHeight(60)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("QFrame { background: transparent; border-radius: 6px; }")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._ctx_menu)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(12)

        # index number
        num = QLabel(str(index) if index else "")
        num.setFixedWidth(22)
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px; background: transparent;")
        lay.addWidget(num)

        # cover
        self.cover = QLabel()
        self.cover.setFixedSize(40, 40)
        self.cover.setStyleSheet(f"background: {BG_HOVER}; border-radius: 4px;")
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.cover)

        # text
        tc = QVBoxLayout()
        tc.setSpacing(1)
        tc.setContentsMargins(0, 0, 0, 0)
        self.title_lbl  = QLabel(elide(meta.get("title", ""), 58))
        self.title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600; background: transparent;")
        self.artist_lbl = QLabel(elide(meta.get("uploader", ""), 40))
        self.artist_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        tc.addWidget(self.title_lbl)
        tc.addWidget(self.artist_lbl)
        lay.addLayout(tc, 1)

        # duration
        dur = meta.get("duration", 0) or 0
        dur_s = f"{int(dur)//60}:{int(dur)%60:02d}" if dur else "—"
        dl = QLabel(dur_s)
        dl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; background: transparent;")
        lay.addWidget(dl)

        if show_remove:
            rb = icon_btn(I_TRASH, 20, TEXT_DIM, "#e55")
            rb.setToolTip("Remove from playlist")
            rb.clicked.connect(lambda: self.remove_requested.emit(self.meta))
            lay.addWidget(rb)

    def set_cover(self, pix: QPixmap):
        try:
            s = pix.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
            self.cover.setPixmap(make_round_pixmap(s, 4))
        except RuntimeError:
            pass

    def enterEvent(self, e):
        self.setStyleSheet(f"QFrame {{ background: {BG_HOVER}; border-radius: 6px; }}")
    def leaveEvent(self, e):
        self.setStyleSheet("QFrame { background: transparent; border-radius: 6px; }")
    def mouseDoubleClickEvent(self, e):
        self.play_requested.emit(self.meta)

    def _ctx_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 4px; }}
            QMenu::item {{ padding: 8px 20px; border-radius: 4px; }}
            QMenu::item:selected {{ background: {BG_HOVER}; }}
        """)
        a_play = menu.addAction("▶  Play now")
        a_add  = menu.addAction("＋  Add to playlist")
        act = menu.exec(self.mapToGlobal(pos))
        if act == a_play:
            self.play_requested.emit(self.meta)
        elif act == a_add:
            self.add_to_playlist.emit(self.meta)


# ─────────────────────────────────────────────
# MINI COVER CARD (for horizontal scroll rows)
# ─────────────────────────────────────────────

class MiniCard(QFrame):
    play_requested  = pyqtSignal(dict)
    add_to_playlist = pyqtSignal(dict)

    def __init__(self, meta: dict, parent=None):
        super().__init__(parent)
        self.meta = meta
        self.setFixedSize(160, 210)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border-radius: 8px; }}")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._ctx)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        self.cover = QLabel()
        self.cover.setFixedSize(136, 136)
        self.cover.setStyleSheet(f"background: {BG_HOVER}; border-radius: 6px;")
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.cover)

        t = QLabel(elide(meta.get("title", ""), 22))
        t.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 700; background: transparent;")
        t.setWordWrap(True)
        lay.addWidget(t)

        a = QLabel(elide(meta.get("uploader", ""), 22))
        a.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        lay.addWidget(a)
        lay.addStretch()

    def set_cover(self, pix: QPixmap):
        try:
            s = pix.scaled(136, 136, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
            self.cover.setPixmap(make_round_pixmap(s, 6))
        except RuntimeError:
            pass

    def enterEvent(self, e):
        self.setStyleSheet(f"QFrame {{ background: {BG_HOVER}; border-radius: 8px; }}")
    def leaveEvent(self, e):
        self.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border-radius: 8px; }}")
    def mouseDoubleClickEvent(self, e):
        self.play_requested.emit(self.meta)

    def _ctx(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 4px; }}
            QMenu::item {{ padding: 8px 20px; border-radius: 4px; }}
            QMenu::item:selected {{ background: {BG_HOVER}; }}
        """)
        a_play = menu.addAction("▶  Play now")
        a_add  = menu.addAction("＋  Add to playlist")
        act = menu.exec(self.mapToGlobal(pos))
        if act == a_play:   self.play_requested.emit(self.meta)
        elif act == a_add:  self.add_to_playlist.emit(self.meta)


# ─────────────────────────────────────────────
# HORIZONTAL SECTION ROW
# ─────────────────────────────────────────────

class SectionRow(QWidget):
    play_requested  = pyqtSignal(dict)
    add_to_playlist = pyqtSignal(dict)

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._cards: list[MiniCard] = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 800; background: transparent;")
        lay.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedHeight(220)
        scroll.setStyleSheet("background: transparent; border: none;")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        self._row_lay = QHBoxLayout(inner)
        self._row_lay.setContentsMargins(0, 0, 0, 0)
        self._row_lay.setSpacing(16)
        self._row_lay.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll)

    def add_card(self, meta: dict) -> MiniCard:
        card = MiniCard(meta)
        card.play_requested.connect(self.play_requested)
        card.add_to_playlist.connect(self.add_to_playlist)
        self._row_lay.insertWidget(self._row_lay.count() - 1, card)
        self._cards.append(card)
        return card

    def get_card(self, vid_id: str):
        for c in self._cards:
            if c.meta.get("id") == vid_id:
                return c
        return None


# ─────────────────────────────────────────────
# BOTTOM PLAYER BAR
# ─────────────────────────────────────────────

class PlayerBar(QFrame):
    seek_requested     = pyqtSignal(int)
    volume_requested   = pyqtSignal(int)
    play_pause_clicked = pyqtSignal()
    prev_clicked       = pyqtSignal()
    next_clicked       = pyqtSignal()
    shuffle_clicked    = pyqtSignal()
    repeat_clicked     = pyqtSignal()
    like_clicked       = pyqtSignal(bool)
    lyrics_clicked     = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.setStyleSheet(f"QFrame {{ background: {PLAYER_BG}; border-top: 1px solid {BORDER_COLOR}; }}")
        self._dur_ms   = 0
        self._seeking  = False
        self._shuffle  = False
        self._repeat   = False
        self._liked    = False
        self._playing  = False

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 0, 16, 0)
        outer.setSpacing(0)

        # LEFT
        left = QHBoxLayout()
        left.setSpacing(12)
        left.setContentsMargins(0, 0, 0, 0)

        self.cover = QLabel()
        self.cover.setFixedSize(56, 56)
        self.cover.setStyleSheet(f"background: {BG_HOVER}; border-radius: 4px;")
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(self.cover)

        info = QVBoxLayout()
        info.setSpacing(2); info.setContentsMargins(0, 0, 0, 0)
        self.title_lbl  = QLabel("—")
        self.title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        self.artist_lbl = QLabel("—")
        self.artist_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        info.addWidget(self.title_lbl)
        info.addWidget(self.artist_lbl)
        left.addLayout(info)

        self.like_btn = icon_btn(I_HEART, 20, TEXT_DIM, ACCENT)
        self.like_btn.clicked.connect(self._toggle_like)
        left.addWidget(self.like_btn)

        lw = QWidget(); lw.setLayout(left); lw.setFixedWidth(280)
        lw.setStyleSheet("background: transparent;")
        outer.addWidget(lw)

        # CENTER
        center = QVBoxLayout()
        center.setSpacing(6); center.setContentsMargins(0, 12, 0, 8)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(16); ctrl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.shuffle_btn = icon_btn(I_SHUFFLE, 20, TEXT_DIM, TEXT_PRIMARY)
        self.shuffle_btn.clicked.connect(self._toggle_shuffle)

        self.prev_btn = icon_btn(I_PREV, 28, TEXT_SECONDARY, TEXT_PRIMARY, 24)
        self.prev_btn.clicked.connect(self.prev_clicked)

        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.play_btn.setStyleSheet(f"""
            QPushButton {{ background: {TEXT_PRIMARY}; border-radius: 18px; border: none; }}
            QPushButton:hover {{ background: #e0e0e0; }}
            QPushButton:pressed {{ background: #b0b0b0; }}
        """)
        self._set_play_icon(False)
        self.play_btn.clicked.connect(self.play_pause_clicked)

        self.next_btn = icon_btn(I_NEXT, 28, TEXT_SECONDARY, TEXT_PRIMARY, 24)
        self.next_btn.clicked.connect(self.next_clicked)

        self.repeat_btn = icon_btn(I_REPEAT, 20, TEXT_DIM, TEXT_PRIMARY)
        self.repeat_btn.clicked.connect(self._toggle_repeat)

        for w in (self.shuffle_btn, self.prev_btn, self.play_btn,
                  self.next_btn, self.repeat_btn):
            ctrl.addWidget(w)
        center.addLayout(ctrl)

        prog = QHBoxLayout(); prog.setSpacing(8)
        self.time_lbl = QLabel("0:00")
        self.time_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; min-width: 36px;")
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.progress = SpotSlider()
        self.progress.setRange(0, 1000)
        self.progress.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self.progress.sliderReleased.connect(self._seek_rel)
        self.dur_lbl = QLabel("0:00")
        self.dur_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; min-width: 36px;")
        prog.addWidget(self.time_lbl); prog.addWidget(self.progress, 1); prog.addWidget(self.dur_lbl)
        center.addLayout(prog)

        cw = QWidget(); cw.setLayout(center); cw.setStyleSheet("background: transparent;")
        outer.addWidget(cw, 1)

        # RIGHT
        right = QHBoxLayout()
        right.setSpacing(8)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        right.setContentsMargins(0, 0, 0, 0)

        self.queue_btn  = icon_btn(I_QUEUE,   20, TEXT_DIM, TEXT_PRIMARY)
        self.lyrics_btn = icon_btn(I_LYRICS,  20, TEXT_DIM, TEXT_PRIMARY)
        self.lyrics_btn.setToolTip(t("lyrics_title"))
        self.lyrics_btn.clicked.connect(self.lyrics_clicked)
        self.vol_icon   = icon_btn(I_VOLMAX,  20, TEXT_DIM, TEXT_PRIMARY)

        self.vol_slider = SpotSlider(h=4, thumb_r=5)
        self.vol_slider.setRange(0, 100); self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(96)
        self.vol_slider.valueChanged.connect(self.volume_requested)

        for w in (self.queue_btn, self.lyrics_btn, self.vol_icon, self.vol_slider):
            right.addWidget(w)

        rw = QWidget(); rw.setLayout(right); rw.setFixedWidth(250)
        rw.setStyleSheet("background: transparent;")
        outer.addWidget(rw)

    def update_track(self, meta: dict, cover: QPixmap = None):
        t = meta.get("title", "—")
        a = meta.get("uploader", "—")
        self.title_lbl.setText(elide(t, 35))
        self.artist_lbl.setText(elide(a, 30))
        if cover and not cover.isNull():
            s = cover.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                             Qt.TransformationMode.SmoothTransformation)
            self.cover.setPixmap(make_round_pixmap(s, 4))
        else:
            self.cover.clear()
            self.cover.setStyleSheet(f"background: {BG_HOVER}; border-radius: 4px;")

    def update_position(self, ms: int):
        if self._seeking: return
        self.time_lbl.setText(ms_to_str(ms))
        if self._dur_ms > 0:
            self.progress.setValue(int(ms / self._dur_ms * 1000))

    def update_duration(self, ms: int):
        self._dur_ms = ms
        self.dur_lbl.setText(ms_to_str(ms))

    def set_playing(self, playing: bool):
        self._playing = playing
        self._set_play_icon(playing)

    def _set_play_icon(self, playing: bool):
        pix = svg_icon(I_PAUSE if playing else I_PLAY, 18, "#000")
        self.play_btn.setIcon(QIcon(pix))
        self.play_btn.setIconSize(QSize(18, 18))

    def _seek_rel(self):
        self._seeking = False
        if self._dur_ms > 0:
            self.seek_requested.emit(int(self.progress.value() / 1000 * self._dur_ms))

    def _toggle_shuffle(self):
        self._shuffle = not self._shuffle
        c = ACCENT if self._shuffle else TEXT_DIM
        self.shuffle_btn.setIcon(QIcon(svg_icon(I_SHUFFLE, 20, c)))
        self.shuffle_btn.setIconSize(QSize(20, 20))

    def _toggle_repeat(self):
        self._repeat = not self._repeat
        c = ACCENT if self._repeat else TEXT_DIM
        self.repeat_btn.setIcon(QIcon(svg_icon(I_REPEAT, 20, c)))
        self.repeat_btn.setIconSize(QSize(20, 20))

    def _toggle_like(self):
        self._liked = not self._liked
        c = ACCENT if self._liked else TEXT_DIM
        self.like_btn.setIcon(QIcon(svg_icon(I_HEART, 20, c)))
        self.like_btn.setIconSize(QSize(20, 20))
        self.like_clicked.emit(self._liked)

    def reset_like(self):
        self._liked = False
        self.like_btn.setIcon(QIcon(svg_icon(I_HEART, 20, TEXT_DIM)))
        self.like_btn.setIconSize(QSize(20, 20))

    @property
    def shuffle(self): return self._shuffle
    @property
    def repeat(self):  return self._repeat


# ─────────────────────────────────────────────
# PAGE BASE
# ─────────────────────────────────────────────

class BasePage(QWidget):
    play_requested  = pyqtSignal(dict)
    add_to_playlist = pyqtSignal(dict)

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.setStyleSheet(f"background: {BG_COLOR};")

    def _scroll_page(self) -> tuple:
        """Returns (scroll_area, content_widget, content_layout)"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QWidget()
        content.setStyleSheet(f"background: {BG_COLOR};")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(28, 20, 28, 28)
        lay.setSpacing(24)
        scroll.setWidget(content)
        return scroll, content, lay

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: 800; background: transparent;")
        return lbl

    def _sub_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        return lbl

    def on_show(self):
        """Called when this page becomes visible."""
        pass


# ─────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────

class HomePage(BasePage):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(dm, parent)
        self._rec_workers: list[RecommendWorker] = []
        self._thumb_workers: dict = {}
        self._sections: dict[str, SectionRow] = {}
        self._built = False
        self._main_lay = QVBoxLayout(self)
        self._main_lay.setContentsMargins(0, 0, 0, 0)
        self._main_lay.setSpacing(0)

    def on_show(self):
        self._build()

    def _build(self):
        # Clear old
        while self._main_lay.count():
            item = self._main_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._sections.clear()
        self._rec_workers.clear()
        self._thumb_workers.clear()

        scroll, content, lay = self._scroll_page()
        self._main_lay.addWidget(scroll)

        # Greeting
        hour = time.localtime().tm_hour
        greet = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
        gl = QLabel(greet)
        gl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 28px; font-weight: 800; background: transparent;")
        lay.addWidget(gl)

        recent = self.dm.get_recent_tracks(12)
        top_artists = self.dm.get_top_artists(4)
        top_tracks  = self.dm.get_top_tracks(8)

        if not recent and not top_artists:
            self._show_empty(lay)
            return

        # Recently played
        if recent:
            row = SectionRow("Recently played")
            row.play_requested.connect(self.play_requested)
            row.add_to_playlist.connect(self.add_to_playlist)
            lay.addWidget(row)
            self._sections["recent"] = row
            for meta in recent[:8]:
                card = row.add_card(meta)
                if meta.get("thumbnail"):
                    self._load_thumb(meta["id"], meta["thumbnail"], card)

        # Top tracks
        if top_tracks:
            row2 = SectionRow("Your top tracks")
            row2.play_requested.connect(self.play_requested)
            row2.add_to_playlist.connect(self.add_to_playlist)
            lay.addWidget(row2)
            self._sections["top"] = row2
            for meta in top_tracks:
                card = row2.add_card(meta)
                if meta.get("thumbnail"):
                    self._load_thumb(meta["id"], meta["thumbnail"], card)

        # Artist-based recommendations
        for artist in top_artists:
            label = f"More from {artist}"
            w = RecommendWorker(f"{artist} songs", label)
            w.results_ready.connect(self._on_rec_results)
            w.start()
            self._rec_workers.append(w)

            row = SectionRow(label)
            row.play_requested.connect(self.play_requested)
            row.add_to_playlist.connect(self.add_to_playlist)
            lay.addWidget(row)
            self._sections[label] = row

        lay.addStretch()

    def _show_empty(self, lay):
        lbl = QLabel("Start listening to get personalized recommendations")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 15px; background: transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = QLabel("Search for music to begin")
        sub.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addStretch()
        lay.addWidget(lbl)
        lay.addWidget(sub)
        lay.addStretch()

    def _on_rec_results(self, label: str, tracks: list):
        row = self._sections.get(label)
        if not row: return
        for meta in tracks:
            card = row.add_card(meta)
            if meta.get("thumbnail"):
                self._load_thumb(meta["id"], meta["thumbnail"], card)

    def _load_thumb(self, vid_id: str, url: str, card):
        w = ThumbnailWorker(vid_id, url)
        w.loaded.connect(lambda vid, pix: self._on_thumb(vid, pix))
        w.start()
        self._thumb_workers[vid_id] = (w, card)

    def _on_thumb(self, vid_id: str, pix: QPixmap):
        entry = self._thumb_workers.get(vid_id)
        if entry:
            _, card = entry
            try: card.set_cover(pix)
            except RuntimeError: pass


# ─────────────────────────────────────────────
# SEARCH PAGE
# ─────────────────────────────────────────────

class SearchPage(BasePage):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(dm, parent)
        self._search_worker: SearchWorker | None = None
        self._thumb_workers: dict = {}
        self._card_map: dict = {}
        self._queue: list = []
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._do_search)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # top bar
        topbar = QFrame()
        topbar.setFixedHeight(64)
        topbar.setStyleSheet(f"background: {BG_COLOR}; border: none;")
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(24, 0, 24, 0)
        tb.setSpacing(12)

        search_wrap = QWidget()
        search_wrap.setStyleSheet("background: transparent;")
        sw = QHBoxLayout(search_wrap)
        sw.setContentsMargins(0, 0, 0, 0)
        sw.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search songs, artists…")
        self.search_input.setFixedHeight(44)
        self.search_input.textChanged.connect(self._on_text)
        self.search_input.returnPressed.connect(self._do_search)
        sw.addWidget(self.search_input)

        self._search_icon = QLabel(search_wrap)
        self._search_icon.setPixmap(svg_icon(I_SEARCH, 18, TEXT_SECONDARY))
        self._search_icon.setGeometry(12, 13, 18, 18)
        self._search_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        tb.addWidget(search_wrap, 1)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        tb.addWidget(self.status_lbl)

        root.addWidget(topbar)

        # scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.results_w = QWidget()
        self.results_w.setStyleSheet(f"background: {BG_COLOR};")
        self.results_lay = QVBoxLayout(self.results_w)
        self.results_lay.setContentsMargins(24, 12, 24, 24)
        self.results_lay.setSpacing(2)
        self.results_lay.addStretch()

        self.scroll.setWidget(self.results_w)
        root.addWidget(self.scroll, 1)

        self._show_history()

    def on_show(self):
        self._show_history()

    def get_queue(self): return self._queue

    def _on_text(self, text: str):
        if len(text) >= 2:
            self._timer.stop()
            self._timer.start(SEARCH_DELAY_MS)
        elif not text:
            self._timer.stop()
            self._clear()
            self._show_history()

    def _do_search(self):
        q = self.search_input.text().strip()
        if not q: return
        self.dm.add_search(q)
        self._clear()
        self.status_lbl.setText("Searching…")
        self._queue.clear()

        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.stop()
        self._search_worker = SearchWorker(q)
        self._search_worker.results_ready.connect(self._on_results)
        self._search_worker.error.connect(lambda e: self.status_lbl.setText(f"Error: {e}"))
        self._search_worker.start()

    def _on_results(self, results: list):
        self._clear()
        self._card_map.clear()
        self._queue = results
        if not results:
            self.status_lbl.setText("No results")
            return
        self.status_lbl.setText(f"{len(results)} results")

        hdr = QLabel("Search Results")
        hdr.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: 800; background: transparent; padding-bottom: 4px;")
        self.results_lay.insertWidget(0, hdr)

        for i, meta in enumerate(results):
            card = ResultCard(meta, index=i + 1)
            card.play_requested.connect(self.play_requested)
            card.add_to_playlist.connect(self.add_to_playlist)
            self.results_lay.insertWidget(i + 1, card)
            vid = meta.get("id", "")
            if vid:
                self._card_map[vid] = card
                self._load_thumb(vid, meta.get("thumbnail", ""))

    def _load_thumb(self, vid_id: str, url: str):
        if not url: return
        w = ThumbnailWorker(vid_id, url)
        w.loaded.connect(self._on_thumb)
        w.start()
        self._thumb_workers[vid_id] = w

    def _on_thumb(self, vid_id: str, pix: QPixmap):
        card = self._card_map.get(vid_id)
        if card:
            try: card.set_cover(pix)
            except RuntimeError: pass

    def _clear(self):
        self._card_map.clear()
        while self.results_lay.count() > 1:
            item = self.results_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def _show_history(self):
        hist = self.dm.get_search_history()
        if not hist: return
        self._clear()

        row0 = QHBoxLayout()
        row0.setContentsMargins(0, 0, 0, 0)
        hdr = QLabel("Recent searches")
        hdr.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: 800; background: transparent;")
        clear_btn = QPushButton("Clear all")
        clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SECONDARY}; border: none; font-size: 13px; font-weight: 600; }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        clear_btn.clicked.connect(self._clear_history)
        row0.addWidget(hdr); row0.addStretch(); row0.addWidget(clear_btn)
        row_w = QWidget(); row_w.setLayout(row0); row_w.setStyleSheet("background: transparent;")
        self.results_lay.insertWidget(0, row_w)

        for i, q in enumerate(hist[:15]):
            hw = self._history_chip(q, i + 1)
            self.results_lay.insertWidget(i + 1, hw)

    def _history_chip(self, query: str, idx: int) -> QFrame:
        f = QFrame()
        f.setFixedHeight(52)
        f.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        f.setStyleSheet("QFrame { background: transparent; border-radius: 6px; }")
        lay = QHBoxLayout(f)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(12)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(svg_icon(I_CLOCK, 18, TEXT_DIM))
        icon_lbl.setFixedSize(24, 24)
        lay.addWidget(icon_lbl)

        ql = QLabel(query)
        ql.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; background: transparent;")
        lay.addWidget(ql, 1)

        xb = icon_btn(I_CLOSE, 20, TEXT_DIM, TEXT_PRIMARY, 16)
        xb.setToolTip("Remove")
        xb.clicked.connect(lambda _, q=query: self._remove_history(q))
        lay.addWidget(xb)

        f.enterEvent = lambda e: f.setStyleSheet(f"QFrame {{ background: {BG_HOVER}; border-radius: 6px; }}")
        f.leaveEvent = lambda e: f.setStyleSheet("QFrame { background: transparent; border-radius: 6px; }")

        def click(e, q=query):
            if e.button() == Qt.MouseButton.LeftButton:
                self.search_input.setText(q)
                self._do_search()
        f.mousePressEvent = click
        return f

    def _clear_history(self):
        self.dm.clear_search_history()
        self._clear()

    def _remove_history(self, q: str):
        self.dm.remove_search(q)
        self._clear()
        self._show_history()


# ─────────────────────────────────────────────
# PLAYLIST DETAIL PAGE
# ─────────────────────────────────────────────

class PlaylistDetailPage(BasePage):
    back_clicked = pyqtSignal()

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(dm, parent)
        self._pl_id = ""
        self._thumb_workers: dict = {}
        self._card_map: dict = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # header bar
        hbar = QFrame()
        hbar.setFixedHeight(64)
        hbar.setStyleSheet(f"background: {BG_COLOR}; border: none;")
        hb = QHBoxLayout(hbar)
        hb.setContentsMargins(16, 0, 24, 0)
        hb.setSpacing(12)

        back = icon_btn(I_BACK, 32, TEXT_SECONDARY, TEXT_PRIMARY, 24)
        back.clicked.connect(self.back_clicked)
        hb.addWidget(back)

        self.pl_name_lbl = QLabel("")
        self.pl_name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 800;")
        hb.addWidget(self.pl_name_lbl)
        hb.addStretch()

        self.info_lbl = QLabel("")
        self.info_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        hb.addWidget(self.info_lbl)

        self.rename_btn = icon_btn(I_EDIT, 24, TEXT_DIM, TEXT_PRIMARY, 18)
        self.rename_btn.setToolTip("Rename playlist")
        self.rename_btn.clicked.connect(self._rename)
        hb.addWidget(self.rename_btn)

        root.addWidget(hbar)

        # scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.content_w = QWidget()
        self.content_w.setStyleSheet(f"background: {BG_COLOR};")
        self.content_lay = QVBoxLayout(self.content_w)
        self.content_lay.setContentsMargins(24, 12, 24, 24)
        self.content_lay.setSpacing(2)
        self.content_lay.addStretch()

        self.scroll.setWidget(self.content_w)
        root.addWidget(self.scroll, 1)

    def load_playlist(self, pl_id: str):
        self._pl_id = pl_id
        self._refresh()

    def _refresh(self):
        self._card_map.clear()
        while self.content_lay.count() > 1:
            item = self.content_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        pl = self.dm.get_playlist(self._pl_id)
        if not pl: return

        self.pl_name_lbl.setText(pl["name"])
        tracks = pl.get("tracks", [])
        total_dur = self.dm.playlist_total_duration(self._pl_id)
        self.info_lbl.setText(f"{len(tracks)} songs  •  {sec_to_str(total_dur)}")

        if not tracks:
            empty = QLabel("This playlist is empty.\nRight-click any song and choose 'Add to playlist'.")
            empty.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; background: transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_lay.insertWidget(0, empty)
            return

        for i, meta in enumerate(tracks):
            card = ResultCard(meta, show_remove=True, index=i + 1)
            card.play_requested.connect(self.play_requested)
            card.add_to_playlist.connect(self.add_to_playlist)
            card.remove_requested.connect(self._remove_track)
            self.content_lay.insertWidget(i, card)
            vid = meta.get("id", "")
            if vid:
                self._card_map[vid] = card
                if meta.get("thumbnail"):
                    self._load_thumb(vid, meta["thumbnail"])

    def _remove_track(self, meta: dict):
        self.dm.remove_track_from_playlist(self._pl_id, meta.get("id", ""))
        self._refresh()

    def _rename(self):
        pl = self.dm.get_playlist(self._pl_id)
        if not pl: return
        name, ok = QInputDialog.getText(self, "Rename Playlist", "New name:", text=pl["name"])
        if ok and name.strip():
            self.dm.rename_playlist(self._pl_id, name.strip())
            self._refresh()

    def _load_thumb(self, vid_id: str, url: str):
        w = ThumbnailWorker(vid_id, url)
        w.loaded.connect(self._on_thumb)
        w.start()
        self._thumb_workers[vid_id] = w

    def _on_thumb(self, vid_id: str, pix: QPixmap):
        card = self._card_map.get(vid_id)
        if card:
            try: card.set_cover(pix)
            except RuntimeError: pass


# ─────────────────────────────────────────────
# LIBRARY PAGE
# ─────────────────────────────────────────────

class LibraryPage(BasePage):
    open_playlist = pyqtSignal(str)  # pl_id

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(dm, parent)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)
        self._build()

    def on_show(self):
        self._rebuild_list()

    def _build(self):
        # toolbar
        tb = QFrame()
        tb.setFixedHeight(64)
        tb.setStyleSheet(f"background: {BG_COLOR}; border: none;")
        tbl = QHBoxLayout(tb)
        tbl.setContentsMargins(24, 0, 24, 0)
        tbl.setSpacing(12)

        lbl = QLabel("Your Library")
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 22px; font-weight: 800;")
        tbl.addWidget(lbl)
        tbl.addStretch()

        new_btn = QPushButton("New playlist")
        new_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: #000; border: none;
                border-radius: 20px; padding: 8px 20px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {ACCENT_DIM}; }}
        """)
        new_btn.clicked.connect(self._create_playlist)
        tbl.addWidget(new_btn)

        self._root.addWidget(tb)

        # scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.list_w = QWidget()
        self.list_w.setStyleSheet(f"background: {BG_COLOR};")
        self.list_lay = QVBoxLayout(self.list_w)
        self.list_lay.setContentsMargins(24, 12, 24, 24)
        self.list_lay.setSpacing(4)
        self.list_lay.addStretch()

        self.scroll.setWidget(self.list_w)
        self._root.addWidget(self.scroll, 1)
        self._rebuild_list()

    def _rebuild_list(self):
        while self.list_lay.count() > 1:
            item = self.list_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        pls = self.dm.get_playlists()
        if not pls:
            empty = QLabel("No playlists yet.\nClick 'New playlist' to create one.")
            empty.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; background: transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_lay.insertWidget(0, empty)
            return

        for i, pl in enumerate(pls):
            row = self._pl_row(pl)
            self.list_lay.insertWidget(i, row)

    def _pl_row(self, pl: dict) -> QFrame:
        tracks = pl.get("tracks", [])
        total  = self.dm.playlist_total_duration(pl["id"])
        f = QFrame()
        f.setFixedHeight(68)
        f.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        f.setStyleSheet("QFrame { background: transparent; border-radius: 8px; }")
        f.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        f.customContextMenuRequested.connect(lambda pos, p=pl: self._pl_ctx(pos, f, p))

        lay = QHBoxLayout(f)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(14)

        # cover placeholder (music icon)
        cov = QLabel()
        cov.setFixedSize(52, 52)
        cov.setStyleSheet(f"background: {BG_HOVER}; border-radius: 6px;")
        cov.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # try first track thumbnail
        thumb_url = tracks[0].get("thumbnail", "") if tracks else ""
        if thumb_url:
            self._set_pl_cover(cov, thumb_url)
        else:
            cov.setPixmap(svg_icon(I_MUSIC, 28, TEXT_DIM))
        lay.addWidget(cov)

        info = QVBoxLayout()
        info.setSpacing(2); info.setContentsMargins(0, 0, 0, 0)
        nl = QLabel(elide(pl["name"], 40))
        nl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: 700; background: transparent;")
        il = QLabel(f"Playlist  •  {len(tracks)} songs  •  {sec_to_str(total)}")
        il.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        info.addWidget(nl); info.addWidget(il)
        lay.addLayout(info, 1)

        dots = icon_btn(I_DOTS, 24, TEXT_DIM, TEXT_PRIMARY)
        dots.clicked.connect(lambda _, p=pl: self._pl_ctx(QPoint(0, 0), f, p))
        lay.addWidget(dots)

        f.enterEvent = lambda e: f.setStyleSheet(f"QFrame {{ background: {BG_HOVER}; border-radius: 8px; }}")
        f.leaveEvent = lambda e: f.setStyleSheet("QFrame { background: transparent; border-radius: 8px; }")
        f.mousePressEvent = lambda e, p=pl: (
            self.open_playlist.emit(p["id"]) if e.button() == Qt.MouseButton.LeftButton else None
        )
        return f

    def _set_pl_cover(self, label: QLabel, url: str):
        def worker():
            try:
                r = requests.get(url, timeout=6)
                if r.status_code == 200:
                    pix = QPixmap(); pix.loadFromData(r.content)
                    if not pix.isNull():
                        s = pix.scaled(52, 52, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                       Qt.TransformationMode.SmoothTransformation)
                        try: label.setPixmap(make_round_pixmap(s, 6))
                        except RuntimeError: pass
            except Exception: pass
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _create_playlist(self):
        name, ok = QInputDialog.getText(self, "New Playlist", "Playlist name:")
        if ok and name.strip():
            self.dm.create_playlist(name.strip())
            self._rebuild_list()

    def _pl_ctx(self, pos, frame: QFrame, pl: dict):
        menu = QMenu(frame)
        menu.setStyleSheet(f"""
            QMenu {{ background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 4px; }}
            QMenu::item {{ padding: 8px 20px; border-radius: 4px; }}
            QMenu::item:selected {{ background: {BG_HOVER}; }}
        """)
        a_open   = menu.addAction("Open")
        a_rename = menu.addAction("Rename")
        menu.addSeparator()
        a_del    = menu.addAction("Delete playlist")
        act = menu.exec(frame.mapToGlobal(pos) if pos != QPoint(0,0) else QCursor.pos())
        if act == a_open:   self.open_playlist.emit(pl["id"])
        elif act == a_rename:
            name, ok = QInputDialog.getText(self, "Rename", "New name:", text=pl["name"])
            if ok and name.strip():
                self.dm.rename_playlist(pl["id"], name.strip())
                self._rebuild_list()
        elif act == a_del:
            r = QMessageBox.question(self, "Delete", f"Delete '{pl['name']}'?")
            if r == QMessageBox.StandardButton.Yes:
                self.dm.delete_playlist(pl["id"])
                self._rebuild_list()


# ─────────────────────────────────────────────
# ADD TO PLAYLIST DIALOG
# ─────────────────────────────────────────────

class AddToPlaylistDialog(QDialog):
    def __init__(self, dm: DataManager, meta: dict, parent=None):
        super().__init__(parent)
        self.dm   = dm
        self.meta = meta
        self.setWindowTitle("Add to playlist")
        self.setModal(True)
        self.setFixedWidth(360)
        self.setStyleSheet(f"""
            QDialog {{ background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; border-radius: 12px; }}
            QLabel {{ color: {TEXT_PRIMARY}; background: transparent; }}
            QPushButton {{ background: {BG_HOVER}; color: {TEXT_PRIMARY}; border: none;
                           border-radius: 6px; padding: 10px 16px; font-size: 13px; }}
            QPushButton:hover {{ background: #383838; }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        title = QLabel("Add to playlist")
        title.setStyleSheet(f"font-size: 18px; font-weight: 800;")
        lay.addWidget(title)

        track_lbl = QLabel(elide(meta.get("title", ""), 40))
        track_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        lay.addWidget(track_lbl)

        new_btn = QPushButton("＋  Create new playlist")
        new_btn.setStyleSheet(f"""
            QPushButton {{ background: {ACCENT}; color: #000; border-radius: 6px;
                           padding: 10px 16px; font-weight: 700; }}
            QPushButton:hover {{ background: {ACCENT_DIM}; }}
        """)
        new_btn.clicked.connect(self._create_and_add)
        lay.addWidget(new_btn)

        pls = dm.get_playlists()
        if pls:
            div = QFrame(); div.setFixedHeight(1)
            div.setStyleSheet(f"background: {BORDER_COLOR};")
            lay.addWidget(div)

        for pl in pls:
            btn = QPushButton(elide(pl["name"], 36))
            btn.clicked.connect(lambda _, p=pl: self._add_to(p))
            lay.addWidget(btn)

        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(f"background: transparent; color: {TEXT_SECONDARY};")
        cancel.clicked.connect(self.reject)
        lay.addWidget(cancel)

    def _add_to(self, pl: dict):
        self.dm.add_track_to_playlist(pl["id"], self.meta)
        self.accept()

    def _create_and_add(self):
        name, ok = QInputDialog.getText(self, "New Playlist", "Playlist name:")
        if ok and name.strip():
            pl = self.dm.create_playlist(name.strip())
            self.dm.add_track_to_playlist(pl["id"], self.meta)
            self.accept()


# ─────────────────────────────────────────────
# ABOUT PAGE
# ─────────────────────────────────────────────

ABOUT_TEXT = (
    "Alterfy, masaüstünüzde reklamsız ve orta hızlı biçimde müzik dinleyebilmenizi "
    "ve sözlerini bile canlı olarak görebilmenizi sağlayan bir masaüstü Python programıdır.\n\n"
    "Bu proje sayesinde:\n"
    "  •  Müzik dinleyebilirsiniz\n"
    "  •  Sözler butonuna basarak şarkı sözlerini canlı olarak görebilirsiniz\n"
    "  •  Hızlı biçimde arama yapabilirsiniz\n"
    "  •  Oynatma listesi oluşturabilirsiniz\n\n"
    "Sunucumuz olmadığı için uygulama sizin internet hızınıza bağımlı olarak hızlıdır.\n\n"
    "Arama ve oynatma için YouTube altyapısı kullanılmaktadır (yt-dlp). "
    "Şarkı sözleri lrclib.net servisinden sağlanmaktadır; kayıt veya giriş gerektirmez.\n\n"
    "© 2026 Alterfy Music Player Project"
)


class AboutPage(BasePage):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(dm, parent)
        self._build()

    def _build(self):
        scroll, content, lay = self._scroll_page()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

        # Logo + başlık
        top = QHBoxLayout()
        top.setSpacing(20)
        top.setContentsMargins(0, 0, 0, 0)

        logo_lbl = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        logo_lbl.setFixedSize(72, 72)
        logo_lbl.setStyleSheet("background: transparent;")
        top.addWidget(logo_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.setContentsMargins(0, 0, 0, 0)
        t1 = QLabel("Alterfy")
        t1.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 32px; font-weight: 900; background: transparent;")
        t2 = QLabel("Music Player")
        t2.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 15px; background: transparent;")
        title_col.addWidget(t1)
        title_col.addWidget(t2)
        top.addLayout(title_col)
        top.addStretch()
        lay.addLayout(top)

        lay.addSpacing(28)

        # Divider
        div = QFrame(); div.setFixedHeight(1)
        div.setStyleSheet(f"background: {BORDER_COLOR};")
        lay.addWidget(div)
        lay.addSpacing(24)

        # About text
        txt = QLabel(ABOUT_TEXT)
        txt.setWordWrap(True)
        txt.setStyleSheet(f"""
            color: {TEXT_SECONDARY};
            font-size: 14px;
            line-height: 1.7;
            background: transparent;
        """)
        txt.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(txt)

        lay.addSpacing(24)

        # Tech stack badges
        badges_lbl = QLabel("Built with")
        badges_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; background: transparent;")
        lay.addWidget(badges_lbl)

        badges_row = QHBoxLayout()
        badges_row.setSpacing(10)
        badges_row.setContentsMargins(0, 6, 0, 0)
        for badge in ("Python 3.13", "PyQt6", "yt-dlp", "VLC", "lrclib.net"):
            b = QLabel(badge)
            b.setStyleSheet(f"""
                color: {TEXT_PRIMARY};
                background: {BG_ELEVATED};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 600;
            """)
            badges_row.addWidget(b)
        badges_row.addStretch()
        lay.addLayout(badges_row)

        lay.addStretch()


# ─────────────────────────────────────────────
# SETTINGS PAGE
# ─────────────────────────────────────────────

class SettingsPage(BasePage):
    language_changed = pyqtSignal(str)   # new lang code

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(dm, parent)
        self._lang_btns: dict[str, QPushButton] = {}
        self._build()

    def _build(self):
        scroll, content, lay = self._scroll_page()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

        # title
        title = QLabel(t("nav_settings"))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 26px; font-weight: 800; background: transparent;")
        lay.addWidget(title)

        lay.addSpacing(8)

        # ── Language section ──────────────────────────
        lang_hdr = QLabel(t("settings_language"))
        lang_hdr.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 700; background: transparent;")
        lay.addWidget(lang_hdr)

        lang_sub = QLabel(t("settings_language_sub"))
        lang_sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        lay.addWidget(lang_sub)

        lay.addSpacing(12)

        # grid of language buttons (3 per row)
        grid_w = QWidget()
        grid_w.setStyleSheet("background: transparent;")
        grid = QHBoxLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        col_w = QVBoxLayout()
        col_w.setSpacing(8)
        col_mid = QVBoxLayout()
        col_mid.setSpacing(8)
        col_r = QVBoxLayout()
        col_r.setSpacing(8)

        items = list(LANGUAGES.items())
        for i, (code, name) in enumerate(items):
            btn = self._lang_btn(code, name)
            self._lang_btns[code] = btn
            col = [col_w, col_mid, col_r][i % 3]
            col.addWidget(btn)

        for col in (col_w, col_mid, col_r):
            col.addStretch()
            cw = QWidget(); cw.setLayout(col)
            cw.setStyleSheet("background: transparent;")
            grid.addWidget(cw, 1)

        lay.addWidget(grid_w)

        # note
        lay.addSpacing(16)
        note = QLabel(t("settings_restart_note"))
        note.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; background: transparent;")
        lay.addWidget(note)

        lay.addStretch()
        self._highlight_current()

    def _lang_btn(self, code: str, name: str) -> QPushButton:
        btn = QPushButton(name)
        btn.setFixedHeight(44)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD}; color: {TEXT_SECONDARY};
                border: 1px solid {BORDER_COLOR}; border-radius: 8px;
                padding: 0 16px; font-size: 13px; font-weight: 600;
                text-align: left;
            }}
            QPushButton:hover {{ background: {BG_HOVER}; color: {TEXT_PRIMARY}; border-color: {TEXT_DIM}; }}
        """)
        btn.clicked.connect(lambda _, c=code: self._select_lang(c))
        return btn

    def _select_lang(self, code: str):
        save_lang(code)
        self._highlight_current()
        self.language_changed.emit(code)

    def _highlight_current(self):
        cur = i18n._current_lang
        for code, btn in self._lang_btns.items():
            if code == cur:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {ACCENT}; color: #000;
                        border: 1px solid {ACCENT}; border-radius: 8px;
                        padding: 0 16px; font-size: 13px; font-weight: 700;
                        text-align: left;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {BG_CARD}; color: {TEXT_SECONDARY};
                        border: 1px solid {BORDER_COLOR}; border-radius: 8px;
                        padding: 0 16px; font-size: 13px; font-weight: 600;
                        text-align: left;
                    }}
                    QPushButton:hover {{ background: {BG_HOVER}; color: {TEXT_PRIMARY}; border-color: {TEXT_DIM}; }}
                """)

    def on_show(self):
        self._highlight_current()


# ─────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────

class AlterfyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alterfy")
        self.resize(1140, 740)
        self.setMinimumSize(820, 560)

        # window icon
        _icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(_icon_path):
            self.setWindowIcon(QIcon(_icon_path))

        self.dm = DataManager()

        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window,        QColor(BG_COLOR))
        pal.setColor(QPalette.ColorRole.WindowText,    QColor(TEXT_PRIMARY))
        pal.setColor(QPalette.ColorRole.Base,          QColor(BG_CARD))
        pal.setColor(QPalette.ColorRole.Text,          QColor(TEXT_PRIMARY))
        pal.setColor(QPalette.ColorRole.Button,        QColor(BG_CARD))
        pal.setColor(QPalette.ColorRole.ButtonText,    QColor(TEXT_PRIMARY))
        pal.setColor(QPalette.ColorRole.Highlight,     QColor(ACCENT))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000"))
        QApplication.setPalette(pal)

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {BG_COLOR}; color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 14px; }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 6px; }}
            QScrollBar::handle:vertical {{ background: {TEXT_DIM}; border-radius: 3px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: {TEXT_SECONDARY}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
            QScrollBar:horizontal {{ background: transparent; height: 4px; }}
            QScrollBar::handle:horizontal {{ background: {TEXT_DIM}; border-radius: 2px; }}
            QScrollBar::handle:horizontal:hover {{ background: {TEXT_SECONDARY}; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
            QLineEdit {{
                background: {BG_HOVER}; color: {TEXT_PRIMARY};
                border: 1px solid transparent; border-radius: 24px;
                padding: 10px 16px 10px 44px; font-size: 14px;
                selection-background-color: {ACCENT};
            }}
            QLineEdit:focus {{ background: #333; border: 1px solid {TEXT_SECONDARY}; }}
            QInputDialog {{ background: {BG_ELEVATED}; }}
            QMessageBox {{ background: {BG_ELEVATED}; }}
        """)

        # state
        self._current_meta   = {}
        self._current_cover  = None
        self._queue: list    = []
        self._queue_idx: int = -1
        self._stream_worker: StreamWorker | None = None
        self._thumb_workers: dict = {}

        # audio
        self.player = AudioPlayer()
        self.player.position_changed.connect(self._on_pos)
        self.player.duration_changed.connect(self._on_dur)
        self.player.state_changed.connect(self._on_state)

        self._build_ui()
        self._build_statusbar()
        self._register_media_keys()

    # ── UI ──────────────────────────────────────

    def _build_ui(self):
        from lyrics import LyricsPanel

        root = QWidget()
        rl = QVBoxLayout(root)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        self.setCentralWidget(root)

        # ── body row: sidebar + stack + lyrics panel ──
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {BG_COLOR};")

        self.home_page    = HomePage(self.dm)
        self.search_page  = SearchPage(self.dm)
        self.library_page = LibraryPage(self.dm)
        self.detail_page  = PlaylistDetailPage(self.dm)
        self.settings_page = SettingsPage(self.dm)
        self.about_page   = AboutPage(self.dm)

        for page in (self.home_page, self.search_page,
                     self.library_page, self.detail_page,
                     self.settings_page, self.about_page):
            page.play_requested.connect(self._play_track)
            page.add_to_playlist.connect(self._show_add_to_playlist)
            self.stack.addWidget(page)

        self.library_page.open_playlist.connect(self._open_playlist)
        self.detail_page.back_clicked.connect(lambda: self._nav(2))
        self.settings_page.language_changed.connect(self._on_lang_change)

        body.addWidget(self.stack, 1)

        # ── lyrics panel (hidden by default) ──
        self.lyrics_panel = LyricsPanel()
        self.lyrics_panel.seek_requested.connect(self.player.seek)
        self.lyrics_panel.close_requested.connect(self._hide_lyrics)
        self.lyrics_panel.hide()
        body.addWidget(self.lyrics_panel)

        body_w = QWidget()
        body_w.setLayout(body)
        body_w.setStyleSheet(f"background: {BG_COLOR};")
        rl.addWidget(body_w, 1)

        self.player_bar = PlayerBar()
        self.player_bar.play_pause_clicked.connect(self._toggle_play)
        self.player_bar.prev_clicked.connect(self._prev)
        self.player_bar.next_clicked.connect(self._next)
        self.player_bar.seek_requested.connect(self.player.seek)
        self.player_bar.volume_requested.connect(self.player.set_volume)
        self.player_bar.lyrics_clicked.connect(self._toggle_lyrics)
        rl.addWidget(self.player_bar)

        self._nav(0)

    def _build_sidebar(self) -> QWidget:
        sb = QFrame()
        sb.setFixedWidth(220)
        sb.setStyleSheet(f"background: {BG_SECONDARY}; border: none;")
        sl = QVBoxLayout(sb)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)

        # logo
        logo_w = QWidget()
        logo_w.setFixedHeight(72)
        logo_w.setStyleSheet("background: transparent;")
        ll = QHBoxLayout(logo_w)
        ll.setContentsMargins(16, 8, 16, 8)
        ll.setSpacing(10)
        _icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(_icon_path):
            logo_img = QLabel()
            pix = QPixmap(_icon_path).scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
            logo_img.setPixmap(pix)
            logo_img.setFixedSize(44, 44)
            logo_img.setStyleSheet("background: transparent;")
            ll.addWidget(logo_img)
        logo_name = QLabel("Alterfy")
        logo_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 900; background: transparent; letter-spacing: -0.3px;")
        ll.addWidget(logo_name)
        ll.addStretch()
        sl.addWidget(logo_w)

        # nav
        self._nav_btns = []
        # idx: 0=Home,1=Search,2=Library,3=detail(no btn),4=Settings,5=About
        self._nav_svgs = [I_HOME, I_SEARCH, I_LIBRARY, I_LIBRARY, I_SETTINGS, I_INFO]
        nav_items = [
            (I_HOME,     t("nav_home"),    0),
            (I_SEARCH,   t("nav_search"),  1),
            (I_LIBRARY,  t("nav_library"), 2),
        ]
        for svg, label, idx in nav_items:
            btn = self._make_nav_btn(svg, label, idx)
            sl.addWidget(btn)
            self._nav_btns.append((btn, idx))

        sl.addSpacing(20)
        div = QFrame(); div.setFixedHeight(1)
        div.setStyleSheet(f"background: {BORDER_COLOR};")
        sl.addWidget(div)
        sl.addSpacing(16)

        sl.addStretch()

        # About + Settings at the bottom
        about_btn = self._make_nav_btn(I_INFO, t("nav_about"), 5)
        sl.addWidget(about_btn)
        self._nav_btns.append((about_btn, 5))

        settings_btn = self._make_nav_btn(I_SETTINGS, t("nav_settings"), 4)
        sl.addWidget(settings_btn)
        self._nav_btns.append((settings_btn, 4))
        sl.addSpacing(8)
        return sb

    def _make_nav_btn(self, svg: str, label: str, idx: int) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setCheckable(True)
        btn.setIcon(QIcon(svg_icon(svg, 22, TEXT_SECONDARY)))
        btn.setIconSize(QSize(22, 22))
        btn.setText(f"  {label}")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SECONDARY};
                border: none; text-align: left; padding: 12px 24px;
                font-size: 14px; font-weight: 600;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
            QPushButton:checked {{ color: {TEXT_PRIMARY}; }}
        """)
        btn.clicked.connect(lambda _, i=idx: self._nav(i))
        return btn

    def _nav(self, idx: int):
        self.stack.setCurrentIndex(idx)
        page = self.stack.currentWidget()
        if hasattr(page, "on_show"): page.on_show()
        for btn, i in self._nav_btns:
            btn.setChecked(i == idx)
            color = TEXT_PRIMARY if i == idx else TEXT_SECONDARY
            svg = self._nav_svgs[i] if i < len(self._nav_svgs) else I_SETTINGS
            btn.setIcon(QIcon(svg_icon(svg, 22, color)))
            btn.setIconSize(QSize(22, 22))

    def _open_playlist(self, pl_id: str):
        self.detail_page.load_playlist(pl_id)
        self.stack.setCurrentWidget(self.detail_page)
        # uncheck all nav
        for btn, _ in self._nav_btns:
            btn.setChecked(False)

    # ── lyrics ────────────────────────────────

    def _toggle_lyrics(self):
        if self.lyrics_panel.isVisible():
            self._hide_lyrics()
        else:
            self._show_lyrics()

    def _show_lyrics(self):
        self.lyrics_panel.show()
        if self._current_meta:
            self.lyrics_panel.load_lyrics(
                self._current_meta.get("uploader", ""),
                self._current_meta.get("title", "")
            )

    def _hide_lyrics(self):
        self.lyrics_panel.hide()

    # ── language change ───────────────────────

    def _build_statusbar(self):
        sb = QStatusBar()
        sb.setStyleSheet(f"""
            QStatusBar {{
                background: {BG_SECONDARY};
                color: {TEXT_DIM};
                font-size: 11px;
                border-top: 1px solid {BORDER_COLOR};
                padding: 0 12px;
            }}
            QStatusBar::item {{ border: none; }}
        """)
        self.setStatusBar(sb)
        self._status_bar = sb
        # left: message area (auto-clears after 5s)
        self._status_msg = QLabel("")
        self._status_msg.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        sb.addWidget(self._status_msg)
        # right: copyright
        copy_lbl = QLabel("\u00a9 2026 Alterfy Music Player Project")
        copy_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; background: transparent; padding-right: 4px;")
        sb.addPermanentWidget(copy_lbl)
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self._status_msg.setText(""))

    def show_status(self, msg: str, ms: int = 5000):
        self._status_msg.setText(msg)
        self._status_timer.stop()
        if ms > 0:
            self._status_timer.start(ms)

    def _on_lang_change(self, code: str):
        labels = [t("nav_home"), t("nav_search"), t("nav_library"), "", t("nav_settings"), t("nav_about")]
        for btn, idx in self._nav_btns:
            if idx < len(labels) and labels[idx]:
                btn.setText(f"  {labels[idx]}")
        self.lyrics_panel.retranslate()
        self.player_bar.lyrics_btn.setToolTip(t("lyrics_title"))
        self.show_status(f"Language changed to {LANGUAGES.get(code, code)}", 4000)

    # ── playback ─────────────────────────────

    def _play_track(self, meta: dict):
        self._current_meta  = meta
        self._current_cover = None
        self.player_bar.update_track(meta)
        self.player_bar.set_playing(False)
        self.player_bar.reset_like()

        # sync queue from search page
        sq = self.search_page.get_queue()
        if sq:
            self._queue = sq
        vid_id = meta.get("id", "")
        for i, m in enumerate(self._queue):
            if m.get("id") == vid_id:
                self._queue_idx = i
                break
        else:
            self._queue     = [meta]
            self._queue_idx = 0

        # cover
        thumb_url = meta.get("thumbnail", "")
        if thumb_url:
            w = ThumbnailWorker(vid_id, thumb_url)
            w.loaded.connect(self._on_bar_thumb)
            w.start()
            self._thumb_workers["bar"] = w

        self.player.stop()
        if self._stream_worker and self._stream_worker.isRunning():
            self._stream_worker.stop()
        self._stream_worker = StreamWorker(meta.get("url", ""), meta)
        self._stream_worker.stream_ready.connect(self._on_stream)
        self._stream_worker.error.connect(lambda e: self.show_status(f"Stream error: {e}", 6000))
        self._stream_worker.start()

    def _on_stream(self, url: str, meta: dict):
        self.player.load_and_play(url)
        self.player_bar.set_playing(True)
        self.dm.record_play(meta)
        self.show_status(f"Now playing: {meta.get('title','')[:60]}", 5000)
        if self.lyrics_panel.isVisible():
            self.lyrics_panel.load_lyrics(
                meta.get("uploader", ""),
                meta.get("title", "")
            )

    def _on_bar_thumb(self, vid_id: str, pix: QPixmap):
        self._current_cover = pix
        self.player_bar.update_track(self._current_meta, pix)

    def _toggle_play(self):
        if not self._current_meta: return
        self.player.play_pause()

    def _prev(self):
        if not self._queue: return
        idx = self._queue_idx - 1
        if idx < 0: idx = len(self._queue) - 1
        self._queue_idx = idx
        self._play_track(self._queue[idx])

    def _next(self):
        if not self._queue: return
        if self.player_bar.shuffle:
            idx = random.randint(0, len(self._queue) - 1)
        else:
            idx = (self._queue_idx + 1) % len(self._queue)
        self._queue_idx = idx
        self._play_track(self._queue[idx])

    # ── player signals ────────────────────────

    def _on_pos(self, ms: int):
        self.player_bar.update_position(ms)
        self.lyrics_panel.update_position(ms)

    def _on_dur(self, ms: int):   self.player_bar.update_duration(ms)

    def _on_state(self, state: str):
        self.player_bar.set_playing(state == "playing")
        if state == "ended":
            if self.player_bar.repeat and self._stream_worker:
                self.player.load_and_play(self._stream_worker.last_stream_url)
            else:
                self._next()

    # ── playlist dialog ───────────────────────

    def _show_add_to_playlist(self, meta: dict):
        dlg = AddToPlaylistDialog(self.dm, meta, self)
        dlg.exec()
        self.library_page._rebuild_list()

    # ── media keys ────────────────────────────

    def _register_media_keys(self):
        if not KB_AVAILABLE: return
        try:
            kb.add_hotkey("play/pause media", self._toggle_play)
            kb.add_hotkey("next track",       self._next)
            kb.add_hotkey("previous track",   self._prev)
        except Exception: pass

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key.Key_Space:                       self._toggle_play()
        elif k == Qt.Key.Key_MediaTogglePlayPause:      self._toggle_play()
        elif k == Qt.Key.Key_MediaNext:                 self._next()
        elif k == Qt.Key.Key_MediaPrevious:             self._prev()
        else: super().keyPressEvent(e)

    def closeEvent(self, e):
        self.player.stop()
        if self._stream_worker and self._stream_worker.isRunning():
            self._stream_worker.stop()
        for w in self._thumb_workers.values():
            if hasattr(w, 'stop') and w.isRunning():
                w.stop()
        if KB_AVAILABLE:
            try: kb.unhook_all()
            except Exception: pass
        super().closeEvent(e)


# ─────────────────────────────────────────────
# ENTRY
# ─────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Alterfy")
    win = AlterfyWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
