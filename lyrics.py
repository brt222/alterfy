"""
Alterfy — Lyrics panel (lrclib.net, synced + plain)
"""
import re
import random
import requests

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, pyqtProperty, QObject
)
from PyQt6.QtGui import (
    QColor, QPainter, QPainterPath, QFont, QCursor,
    QPixmap, QIcon, QLinearGradient
)

import i18n
from i18n import t

# ── weighted random bg colour ──────────────────────────────────────────
_PALETTE = [
    ("#1a3a6b", 25),   # blue
    ("#6b1a1a", 20),   # red
    ("#7a3b00", 25),   # orange
    ("#6b6b00", 15),   # yellow
    ("#0e4d1a", 10),   # green
    ("#3d0e6b", 4),    # purple
    ("#6b4f7a", 1),    # lavender
]

def random_bg_color() -> str:
    pool, weights = zip(*_PALETTE)
    return random.choices(pool, weights=weights, k=1)[0]


# ── LRC parser ────────────────────────────────────────────────────────

def parse_lrc(lrc_text: str) -> list[tuple[float, str]]:
    """Parse synced LRC into [(seconds_float, line_str), ...]"""
    pattern = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')
    lines = []
    for raw in lrc_text.splitlines():
        m = pattern.match(raw.strip())
        if m:
            mins = int(m.group(1))
            secs = int(m.group(2))
            ms_s = m.group(3)
            ms   = int(ms_s) if len(ms_s) == 3 else int(ms_s) * 10
            ts   = mins * 60 + secs + ms / 1000.0
            text = m.group(4).strip()
            lines.append((ts, text))
    return lines


# ── lyrics fetch worker ───────────────────────────────────────────────

class LyricsWorker(QThread):
    result = pyqtSignal(dict)   # {"synced": [...], "plain": str, "instrumental": bool, "error": str}

    def __init__(self, artist: str, title: str):
        super().__init__()
        self.artist = artist
        self.title  = title

    def run(self):
        try:
            url = "https://lrclib.net/api/get"
            r = requests.get(url, params={
                "artist_name": self.artist,
                "track_name":  self.title,
            }, timeout=10)

            if r.status_code == 404:
                self.result.emit({"error": "not_found"})
                return
            if r.status_code != 200:
                self.result.emit({"error": f"HTTP {r.status_code}"})
                return

            data = r.json()

            if data.get("instrumental"):
                self.result.emit({"instrumental": True})
                return

            synced_raw = data.get("syncedLyrics") or ""
            plain_raw  = data.get("plainLyrics")  or ""

            synced = parse_lrc(synced_raw) if synced_raw.strip() else []
            self.result.emit({
                "synced": synced,
                "plain":  plain_raw,
                "instrumental": False,
                "error": "",
            })
        except Exception as ex:
            self.result.emit({"error": str(ex)})


# ── single lyric line widget ──────────────────────────────────────────

class LyricLine(QLabel):
    seek_to = pyqtSignal(float)   # seconds

    def __init__(self, text: str, ts: float, bg_color: str, parent=None):
        super().__init__(text or "♪", parent)
        self.ts       = ts
        self.bg_color = bg_color
        self._active  = False
        self.setWordWrap(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._apply_style(False)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setContentsMargins(0, 4, 0, 4)

    def _apply_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QLabel {{
                    color: #FFFFFF;
                    font-size: 22px;
                    font-weight: 800;
                    background: transparent;
                    padding: 2px 0;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255,255,255,0.45);
                    font-size: 17px;
                    font-weight: 500;
                    background: transparent;
                    padding: 2px 0;
                }}
            """)

    def set_active(self, active: bool):
        if self._active == active:
            return
        self._active = active
        self._apply_style(active)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.seek_to.emit(self.ts)


# ── main lyrics panel ────────────────────────────────────────────────

class LyricsPanel(QWidget):
    seek_requested = pyqtSignal(int)   # ms
    close_requested = pyqtSignal()

    PANEL_WIDTH = 340

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(self.PANEL_WIDTH)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._bg_color   = random_bg_color()
        self._synced: list[tuple[float, str]] = []
        self._plain  = ""
        self._lines: list[LyricLine] = []
        self._active_idx = -1
        self._worker: LyricsWorker | None = None
        self._current_lang = i18n._current_lang

        self._build_ui()
        self._apply_bg()

    # ── build ─────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # header bar
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 12, 0)
        hl.setSpacing(8)

        self.title_lbl = QLabel(t("lyrics_title"))
        self.title_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.9); font-size: 15px; "
            "font-weight: 800; background: transparent; letter-spacing: 0.5px;"
        )
        hl.addWidget(self.title_lbl)
        hl.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.12);
                color: rgba(255,255,255,0.8);
                border: none; border-radius: 14px;
                font-size: 13px; font-weight: 700;
            }
            QPushButton:hover { background: rgba(255,255,255,0.22); color: #fff; }
        """)
        close_btn.clicked.connect(self.close_requested)
        hl.addWidget(close_btn)
        root.addWidget(header)

        # divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: rgba(255,255,255,0.12);")
        root.addWidget(div)

        # scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: transparent; width: 4px; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,0.25); border-radius: 2px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.content_lay = QVBoxLayout(self.content)
        self.content_lay.setContentsMargins(20, 16, 20, 40)
        self.content_lay.setSpacing(10)
        self.content_lay.addStretch()

        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll, 1)

        # status label (loading / not found)
        self.status_lbl = QLabel("")
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.6); font-size: 14px; "
            "background: transparent; padding: 24px 20px;"
        )
        root.addWidget(self.status_lbl)

    def _apply_bg(self):
        # gradient from bg_color (top) to slightly darker (bottom)
        c = QColor(self._bg_color)
        r2 = max(0, c.red()   - 20)
        g2 = max(0, c.green() - 20)
        b2 = max(0, c.blue()  - 20)
        darker = f"#{r2:02x}{g2:02x}{b2:02x}"
        self.setStyleSheet(f"""
            LyricsPanel {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._bg_color},
                    stop:1 {darker}
                );
            }}
        """)

    # ── public API ────────────────────────────────

    def load_lyrics(self, artist: str, title: str):
        """Called when a new track starts playing."""
        self._synced.clear()
        self._plain  = ""
        self._lines.clear()
        self._active_idx = -1
        self._bg_color   = random_bg_color()
        self._apply_bg()
        self._clear_content()
        self.status_lbl.setText(t("lyrics_loading"))
        self.status_lbl.show()

        # update header language
        self.title_lbl.setText(t("lyrics_title"))

        if self._worker and self._worker.isRunning():
            self._worker.terminate()
        self._worker = LyricsWorker(artist, title)
        self._worker.result.connect(self._on_result)
        self._worker.start()

    def update_position(self, ms: int):
        """Called every ~500ms with current playback position."""
        if not self._synced:
            return
        secs = ms / 1000.0
        idx = self._find_line_idx(secs)
        if idx == self._active_idx:
            return
        # deactivate old
        if 0 <= self._active_idx < len(self._lines):
            self._lines[self._active_idx].set_active(False)
        self._active_idx = idx
        if 0 <= idx < len(self._lines):
            self._lines[idx].set_active(True)
            self._scroll_to_line(idx)

    def retranslate(self):
        self.title_lbl.setText(t("lyrics_title"))

    # ── internals ─────────────────────────────────

    def _on_result(self, data: dict):
        self.status_lbl.hide()
        self._clear_content()

        if data.get("error") == "not_found":
            self.status_lbl.setText(t("lyrics_not_found"))
            self.status_lbl.show()
            return
        if data.get("error"):
            self.status_lbl.setText(t("lyrics_not_found"))
            self.status_lbl.show()
            return
        if data.get("instrumental"):
            self.status_lbl.setText(t("lyrics_instrumental"))
            self.status_lbl.show()
            return

        self._synced = data.get("synced", [])
        self._plain  = data.get("plain", "")

        if self._synced:
            self._build_synced_lines()
        elif self._plain:
            self._build_plain_lines()
        else:
            self.status_lbl.setText(t("lyrics_not_found"))
            self.status_lbl.show()

    def _build_synced_lines(self):
        for i, (ts, text) in enumerate(self._synced):
            if not text:
                continue
            line = LyricLine(text, ts, self._bg_color)
            line.seek_to.connect(lambda s: self.seek_requested.emit(int(s * 1000)))
            self.content_lay.insertWidget(self.content_lay.count() - 1, line)
            self._lines.append(line)

    def _build_plain_lines(self):
        for raw_line in self._plain.splitlines():
            text = raw_line.strip()
            lbl = QLabel(text if text else " ")
            lbl.setWordWrap(True)
            lbl.setStyleSheet(
                "color: rgba(255,255,255,0.75); font-size: 16px; "
                "font-weight: 500; background: transparent; padding: 2px 0;"
            )
            self.content_lay.insertWidget(self.content_lay.count() - 1, lbl)

    def _clear_content(self):
        self._lines.clear()
        while self.content_lay.count() > 1:
            item = self.content_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _find_line_idx(self, secs: float) -> int:
        idx = -1
        for i, (ts, _) in enumerate(self._synced):
            if ts <= secs:
                idx = i
            else:
                break
        return idx

    def _scroll_to_line(self, idx: int):
        if 0 <= idx < len(self._lines):
            line = self._lines[idx]
            QTimer.singleShot(50, lambda: self.scroll.ensureWidgetVisible(line, 0, 120))
