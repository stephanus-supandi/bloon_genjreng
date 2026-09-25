#!/usr/bin/env python3
# =====================================================================
# GENJRENG - Basic Guitar Chord Training  (v0.3, single-file, layout fix)
# Pure ASCII: no tofu, no mojibake, on any OS/encoding.
# Icons/arrows DRAWN with pygame primitives, never font glyphs.
# "Press the strings. Make noise. Eventually call it music."
# =====================================================================
import os
import json
import math
import time
import random

import pygame

try:
    import numpy as np
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False


# ============================ CONFIG =================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "GENJRENG - Basic Guitar Chord Training"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 200, 0)
ORANGE = (255, 150, 0)
PURPLE = (150, 50, 200)
DARK_BG = (30, 30, 40)
PANEL_BG = (45, 45, 60)
FRETBOARD_BG = (139, 90, 43)
STRING_COLOR = (210, 210, 210)
FRET_COLOR = (180, 180, 180)
WOOD_DARK = (90, 55, 25)

STATE_MENU = "MENU"
STATE_LEARN = "LEARN"
STATE_PRACTICE = "PRACTICE"
STATE_CHALLENGE = "CHALLENGE"
STATE_STRUMMING = "STRUMMING"

CHORD_NAMES = ["C", "G", "D", "Em", "Am", "E", "A", "F", "Dm", "Bm"]

BLOONS_MESSAGES = [
    "Bro... itu bukan C chord.",
    "Jari lu sedang melakukan pemberontakan.",
    "Gitar tidak bersalah.",
    "Coba lagi. Jangan salahkan senarnya.",
    "Mungkin gitar lu yang salah beli?",
    "Tenang, semua guitarist pernah begini.",
    "Itu bukan musik, itu teror audio.",
    "Fingers lu butuh vacation.",
    "Chord itu bukan abstract art.",
    "Sabar, Mozart juga pernah salah.",
    "Senar lu nangis diam-diam.",
    "Itu chord atau lagi ngaduk nasi?",
    "F itu barre, bro. Bukan salah gitar lu doang.",
    "Lu pencet 6 senar atau 6 harapan?",
    "Itu Bm atau lu lagi nge-crunch kerupuk?",
    "Jari telunjuk lu jadi barre atau bendera putih?",
    "Sound-nya lebih ke 'errr' daripada 'chord'.",
    "Jari manis lu mogok kerja ya?",
    "Ini latihan, bukan konser. Santai.",
    "Salah lagi? Oke, gitar mulai menghakimi lu.",
    "Konsentrasi bro, bukan lagi mikirin mantan.",
    "Kelingking lu masih tidur?",
    "That was not a chord, that was a cry for help.",
    "Ulangi pelan-pelan. Speed nanti, bener dulu.",
]

# Names & numbers KEPT exactly as the player wrote them.
# Only row ORDER fixed to descending, else (2,ERIL..) swallows levels 2..6.
LEVEL_LADDER = [
    (7, "ERYL CHRSTY"),
    (5, "GUITAR PLAYER"),
    (3, "STRUMMER"),
    (2, "ERIL SAKE MODAL JAM"),
    (1, "CHORD NOVICE"),
    (0, "COMPLETE BLOON"),
]

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


# ============================ CHORDS =================================
CHORDS = {
    "C":  {"frets": [-1, 3, 2, 0, 1, 0],  "fingers": [0, 3, 2, 0, 1, 0], "name": "C Major"},
    "G":  {"frets": [3, 2, 0, 0, 0, 3],   "fingers": [3, 2, 0, 0, 0, 4],  "name": "G Major"},
    "D":  {"frets": [-1, -1, 0, 2, 3, 2], "fingers": [0, 0, 0, 1, 3, 2],  "name": "D Major"},
    "Em": {"frets": [0, 2, 2, 0, 0, 0],   "fingers": [0, 2, 3, 0, 0, 0],  "name": "E Minor"},
    "Am": {"frets": [-1, 0, 2, 2, 1, 0],  "fingers": [0, 0, 2, 3, 1, 0],  "name": "A Minor"},
    "E":  {"frets": [0, 2, 2, 1, 0, 0],   "fingers": [0, 2, 3, 1, 0, 0],  "name": "E Major"},
    "A":  {"frets": [-1, 0, 2, 2, 2, 0],  "fingers": [0, 0, 1, 2, 3, 0],  "name": "A Major"},
    "F":  {"frets": [1, 3, 3, 2, 1, 1],   "fingers": [1, 3, 4, 2, 1, 1],  "name": "F Major"},
    "Dm": {"frets": [-1, -1, 0, 2, 3, 1], "fingers": [0, 0, 0, 2, 3, 1],  "name": "D Minor"},
    "Bm": {"frets": [2, 4, 4, 3, 2, 2],   "fingers": [1, 3, 4, 2, 1, 1],  "name": "B Minor"},
}

STRING_LABELS = ["E", "A", "D", "G", "B", "E"]
STRING_NUMS = ["6", "5", "4", "3", "2", "1"]
BASE_FREQS = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]


def get_chord(name):
    return CHORDS.get(name)


def get_all_chord_names():
    return list(CHORDS.keys())


def get_string_frequencies(name):
    chord = get_chord(name)
    if not chord:
        return []
    out = []
    for i, fret in enumerate(chord["frets"]):
        out.append(0.0 if fret == -1 else BASE_FREQS[i] * (2 ** (fret / 12.0)))
    return out


def describe_strings(name):
    chord = get_chord(name)
    if not chord:
        return ""
    played, muted = [], []
    for i, fret in enumerate(chord["frets"]):
        lbl = STRING_LABELS[i] + STRING_NUMS[i]
        (muted if fret == -1 else played).append(lbl)
    txt = "Strings played: " + (" ".join(played) if played else "(none)")
    if muted:
        txt += "   |   muted (X): " + " ".join(muted)
    return txt


# ============================ AUDIO ==================================
class GuitarAudio:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.enabled = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            self.enabled = HAS_NUMPY
        except Exception:
            self.enabled = False

    def _pluck_signal(self, frequency, duration=1.2):
        n = int(self.sample_rate * duration)
        t = np.arange(n) / self.sample_rate
        wave = (np.sin(2 * math.pi * frequency * t)
                + 0.5 * np.sin(2 * math.pi * frequency * 2 * t)
                + 0.25 * np.sin(2 * math.pi * frequency * 3 * t)
                + 0.12 * np.sin(2 * math.pi * frequency * 4 * t))
        env = np.exp(-t * 3.0)
        attack = max(1, int(0.004 * self.sample_rate))
        env[:attack] *= np.linspace(0, 1, attack)
        wave = wave * env
        peak = np.max(np.abs(wave)) or 1.0
        return wave / peak

    def _make_chord_buffer(self, name, duration=1.6, direction="down", stagger_ms=32):
        freqs = get_string_frequencies(name)
        active = [(i, f) for i, f in enumerate(freqs) if f > 0]
        if not active:
            return None
        order = active if direction == "down" else list(reversed(active))
        stagger = int(self.sample_rate * stagger_ms / 1000.0)
        parts = []
        for k, (_si, f) in enumerate(order):
            sig = self._pluck_signal(f, duration)
            parts.append(np.concatenate([np.zeros(k * stagger, dtype=np.float64), sig]))
        max_len = max(len(p) for p in parts)
        mixed = np.zeros(max_len, dtype=np.float64)
        for p in parts:
            mixed[:len(p)] += p
        peak = np.max(np.abs(mixed)) or 1.0
        mixed = mixed / peak * 0.5
        stereo = np.column_stack((mixed, mixed))
        return (stereo * 32767).astype(np.int16).tobytes()

    def _get_sound(self, name, direction="down"):
        key = "%s|%s" % (name, direction)
        if key not in self.sounds:
            buf = self._make_chord_buffer(name, direction=direction)
            if buf is None:
                return None
            self.sounds[key] = pygame.mixer.Sound(buffer=buf)
        return self.sounds[key]

    def play_chord(self, name, direction="down"):
        if not self.enabled:
            return
        snd = self._get_sound(name, direction)
        if snd:
            snd.play()

    def play_strum(self, name, direction="down"):
        self.play_chord(name, direction)

    def play_ui(self, good=True):
        if not self.enabled:
            return
        try:
            sig = self._pluck_signal(660.0 if good else 180.0, 0.12)
            stereo = np.column_stack((sig, sig))
            buf = (stereo * 32767 * 0.4).astype(np.int16).tobytes()
            pygame.mixer.Sound(buffer=buf).play()
        except Exception:
            pass


# ====================== UI HELPERS & WIDGETS =========================
def draw_arrow(screen, cx, cy, direction, size=18, color=WHITE, width=4):
    if direction == "down":
        tip, base = (cx, cy + size), (cx, cy - size)
        head = [(cx - size * 0.7, cy + size * 0.2), (cx + size * 0.7, cy + size * 0.2), tip]
    elif direction == "up":
        tip, base = (cx, cy - size), (cx, cy + size)
        head = [(cx - size * 0.7, cy - size * 0.2), (cx + size * 0.7, cy - size * 0.2), tip]
    elif direction == "left":
        tip, base = (cx - size, cy), (cx + size, cy)
        head = [(cx - size * 0.2, cy - size * 0.7), (cx - size * 0.2, cy + size * 0.7), tip]
    else:
        tip, base = (cx + size, cy), (cx - size, cy)
        head = [(cx + size * 0.2, cy - size * 0.7), (cx + size * 0.2, cy + size * 0.7), tip]
    pygame.draw.line(screen, color, base, tip, width)
    pygame.draw.polygon(screen, color, head)


def draw_guitar_icon(screen, cx, cy, scale=1.0, color=YELLOW):
    body_r = int(22 * scale)
    pygame.draw.ellipse(screen, color, (cx - body_r, cy - int(body_r * 0.8),
                                        body_r * 2, int(body_r * 1.6)))
    pygame.draw.circle(screen, DARK_BG, (cx, cy), int(7 * scale))
    neck_len = int(46 * scale)
    neck_w = max(2, int(7 * scale))
    pygame.draw.rect(screen, color, (cx + body_r - 2, cy - neck_w // 2, neck_len, neck_w))
    pygame.draw.rect(screen, color, (cx + body_r + neck_len - 4, cy - int(9 * scale),
                                     int(8 * scale), int(18 * scale)))
    for i in range(-1, 2):
        y = cy + i * max(1, int(2 * scale))
        pygame.draw.line(screen, DARK_BG, (cx + body_r, y), (cx + body_r + neck_len, y), 1)


def draw_panel(screen, rect, color=PANEL_BG, border=WHITE, radius=12):
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 2, border_radius=radius)


def draw_header(screen, title, icon_color=YELLOW, title_color=WHITE,
                font_size=46, subtitle=None, quote=None):
    """Single source of truth for every screen's top bar.
    Guitar icon is SMALL (scale 0.55) at x=46 so its neck ends ~x=86,
    and the title starts at x=110 -> physically impossible to overlap."""
    draw_guitar_icon(screen, 46, 46, 0.55, icon_color)
    t = pygame.font.Font(None, font_size).render(title, True, title_color)
    screen.blit(t, (110, 24))
    y = 24 + font_size + 4
    if subtitle:
        screen.blit(pygame.font.Font(None, 24).render(subtitle, True, LIGHT_GRAY), (112, y))
        y += 28
    if quote:
        screen.blit(pygame.font.Font(None, 18).render(quote, True, GRAY), (112, y))


class Button:
    def __init__(self, x, y, w, h, text, color=BLUE, text_color=WHITE, font_size=32):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
        self.active = False

    def draw(self, screen):
        col = self.color
        if self.active:
            col = tuple(min(255, c + 60) for c in self.color)
        elif self.hovered:
            col = tuple(min(255, c + 30) for c in self.color)
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        border = YELLOW if self.active else WHITE
        pygame.draw.rect(screen, border, self.rect, 3 if self.active else 2, border_radius=8)
        surf = pygame.font.Font(None, self.font_size).render(self.text, True, self.text_color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def check_click(self, pos):
        return self.rect.collidepoint(pos)


class Fretboard:
    def __init__(self, x, y, w, h, num_frets=5):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.num_frets = num_frets
        self.num_strings = 6

    def draw(self, screen, chord_data=None):
        fs = self.width / (self.num_frets + 1)
        ss = self.height / (self.num_strings + 1)
        pygame.draw.rect(screen, FRETBOARD_BG, (self.x, self.y, self.width, self.height), border_radius=6)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x, self.y + self.height), 6)
        for i in range(1, self.num_frets + 1):
            fx = self.x + i * fs
            pygame.draw.line(screen, FRET_COLOR, (fx, self.y), (fx, self.y + self.height), 2)
        fnum = pygame.font.Font(None, 18)
        for i in range(1, self.num_frets + 1):
            fx = self.x + (i - 0.5) * fs
            t = fnum.render(str(i), True, LIGHT_GRAY)
            screen.blit(t, t.get_rect(center=(fx, self.y + self.height + 11)))
        for i in range(self.num_strings):
            sy = self.y + (i + 1) * ss
            pygame.draw.line(screen, STRING_COLOR, (self.x, sy), (self.x + self.width, sy), 4 - i // 2)
        lbl = pygame.font.Font(None, 20)
        for i, name in enumerate(STRING_LABELS):
            sy = self.y + (i + 1) * ss
            screen.blit(lbl.render(name, True, WHITE), (self.x + self.width + 8, sy - 9))
        if not chord_data:
            return
        frets, fingers = chord_data["frets"], chord_data["fingers"]
        dot_font = pygame.font.Font(None, 20)
        for si, fret in enumerate(frets):
            sy = self.y + (si + 1) * ss
            if fret == -1:
                pygame.draw.line(screen, RED, (self.x - 22, sy - 7), (self.x - 8, sy + 7), 3)
                pygame.draw.line(screen, RED, (self.x - 22, sy + 7), (self.x - 8, sy - 7), 3)
            elif fret == 0:
                pygame.draw.circle(screen, GREEN, (self.x - 15, sy), 8, 3)
            else:
                dx = self.x + (fret - 0.5) * fs
                pygame.draw.circle(screen, YELLOW, (int(dx), int(sy)), 12)
                pygame.draw.circle(screen, WOOD_DARK, (int(dx), int(sy)), 12, 2)
                if fingers[si] > 0:
                    t = dot_font.render(str(fingers[si]), True, BLACK)
                    screen.blit(t, t.get_rect(center=(dx, sy)))


class StrummingIndicator:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.width, self.height = x, y, w, h

    def draw(self, screen, pattern, current_step=-1):
        draw_panel(screen, (self.x, self.y, self.width, self.height))
        n = max(1, len(pattern))
        step_w = self.width / n
        cy = self.y + self.height / 2
        for i, sym in enumerate(pattern):
            cx = self.x + i * step_w + step_w / 2
            active = (i == current_step)
            col = YELLOW if active else (GREEN if sym == "down" else BLUE)
            if active:
                pygame.draw.rect(screen, (70, 70, 30),
                                 (self.x + i * step_w + 4, self.y + 6, step_w - 8, self.height - 12),
                                 border_radius=8)
            draw_arrow(screen, cx, cy, sym, size=int(self.height * 0.32), color=col, width=5)
            tag = pygame.font.Font(None, 16).render("D" if sym == "down" else "U", True, LIGHT_GRAY)
            screen.blit(tag, tag.get_rect(center=(cx, self.y + self.height - 10)))


class ProgressBar:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.width, self.height = x, y, w, h

    def draw(self, screen, progress, color=GREEN, label=""):
        progress = max(0.0, min(1.0, progress))
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height), border_radius=6)
        pw = int(self.width * progress)
        if pw > 0:
            pygame.draw.rect(screen, color, (self.x, self.y, pw, self.height), border_radius=6)
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2, border_radius=6)
        if label:
            t = pygame.font.Font(None, 16).render(label, True, WHITE)
            screen.blit(t, t.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2)))


# ======================== PROGRESS TRACKER ===========================
class ProgressTracker:
    def __init__(self):
        self.score = 0
        self.best_score = 0
        self.chords_mastered = set()
        self.total_attempts = 0
        self.correct_attempts = 0
        self.save_file = os.path.join(ASSETS_DIR, "progress.json")
        self.load_progress()

    def record_attempt(self, correct, chord_name=None):
        self.total_attempts += 1
        if correct:
            self.correct_attempts += 1
            if chord_name:
                self.chords_mastered.add(chord_name)

    def get_accuracy(self):
        if self.total_attempts == 0:
            return 0.0
        return self.correct_attempts / self.total_attempts * 100.0

    def get_level(self):
        n = len(self.chords_mastered)
        for need, name in LEVEL_LADDER:
            if n >= need:
                return name
        return "COMPLETE BLOON"

    def save_progress(self):
        data = {
            "score": self.score,
            "best_score": self.best_score,
            "chords_mastered": sorted(self.chords_mastered),
            "total_attempts": self.total_attempts,
            "correct_attempts": self.correct_attempts,
        }
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def load_progress(self):
        if not os.path.exists(self.save_file):
            return
        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                d = json.load(f)
            self.score = int(d.get("score", 0))
            self.best_score = int(d.get("best_score", 0))
            self.chords_mastered = set(d.get("chords_mastered", []))
            self.total_attempts = int(d.get("total_attempts", 0))
            self.correct_attempts = int(d.get("correct_attempts", 0))
        except Exception:
            pass


# =========================== LEARN MODE ==============================
class LearnMode:
    def __init__(self, screen, audio):
        self.screen = screen
        self.audio = audio
        self.chord_names = get_all_chord_names()
        self.idx = 0
        self.feedback = ""
        self.feedback_color = LIGHT_GRAY
        self.fretboard = Fretboard(165, 90, 470, 210)
        self.prev_btn = Button(120, 488, 110, 50, "< Prev")
        self.next_btn = Button(250, 488, 110, 50, "Next >")
        self.play_btn = Button(420, 488, 200, 50, "PLAY CHORD", GREEN)
        self.back_btn = Button(660, 20, 120, 40, "BACK", RED)

    def _cur(self):
        return self.chord_names[self.idx]

    def _do_play(self):
        name = self._cur()
        self.audio.play_chord(name, "down")
        self.feedback = "Nah, itu suara %s. Rasain getarannya, terus pindahin jarinya." % get_chord(name)["name"]
        self.feedback_color = GREEN

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if self.back_btn.check_click(pos):
                return STATE_MENU
            if self.prev_btn.check_click(pos):
                self.idx = (self.idx - 1) % len(self.chord_names); self.feedback = ""
            elif self.next_btn.check_click(pos):
                self.idx = (self.idx + 1) % len(self.chord_names); self.feedback = ""
            elif self.play_btn.check_click(pos):
                self._do_play()
        return None

    def handle_key(self, event):
        if event.key == pygame.K_SPACE:
            self._do_play()
        elif event.key == pygame.K_LEFT:
            self.idx = (self.idx - 1) % len(self.chord_names); self.feedback = ""
        elif event.key == pygame.K_RIGHT:
            self.idx = (self.idx + 1) % len(self.chord_names); self.feedback = ""
        return None

    def draw(self):
        s = self.screen
        s.fill(DARK_BG)
        name = self._cur()
        data = get_chord(name)
        draw_header(s, "LEARN MODE - %s" % data["name"], YELLOW, WHITE, 42)
        self.back_btn.draw(s)
        self.fretboard.draw(s, data)
        f22 = pygame.font.Font(None, 22)
        f20 = pygame.font.Font(None, 20)
        s.blit(f22.render(describe_strings(name), True, LIGHT_GRAY), (120, 340))
        lines = [
            "- Kuning = posisi fret, angka di dalam = jari (1 telunjuk ... 4 kelingking)",
            "- X = senar mati (jangan dipetik), O = senar lepas (open)",
            "- Tekan PLAY CHORD atau SPASI buat dengerin suaranya",
        ]
        y = 372
        for ln in lines:
            s.blit(f20.render(ln, True, LIGHT_GRAY), (120, y)); y += 22
        if self.feedback:
            s.blit(f22.render(self.feedback, True, self.feedback_color), (120, 448))
        self.prev_btn.draw(s); self.next_btn.draw(s); self.play_btn.draw(s)
        pygame.display.flip()


# ========================= STRUMMING MODE ============================
class StrummingMode:
    PATTERNS = {
        "1: Down only": ["down"],
        "2: Down-Up": ["down", "up"],
        "3: D-U-D-U": ["down", "up", "down", "up"],
        "4: D-D-U-U-D": ["down", "down", "up", "up", "down"],
    }
    BEAT_MS = 480

    def __init__(self, screen, audio):
        self.screen = screen
        self.audio = audio
        self.chord_names = get_all_chord_names()
        self.chord_idx = 0
        self.pattern_keys = list(self.PATTERNS.keys())
        self.pattern_idx = 0
        self.start_tick = pygame.time.get_ticks()
        self.indicator = StrummingIndicator(120, 290, 560, 110)
        self.back_btn = Button(660, 20, 120, 40, "BACK", RED)
        self.chord_btn = Button(120, 140, 200, 48, "", BLUE)
        self.strum_btn = Button(340, 140, 240, 48, "STRUM (SPACE)", GREEN)
        self.pattern_btns = []
        x = 120
        for k in self.pattern_keys:
            self.pattern_btns.append(Button(x, 230, 110, 40, k.split(":")[0].strip(), PURPLE))
            x += 122

    def _pattern(self):
        return self.PATTERNS[self.pattern_keys[self.pattern_idx]]

    def _current_step(self):
        p = self._pattern()
        return int((pygame.time.get_ticks() - self.start_tick) // self.BEAT_MS) % len(p)

    def _do_strum(self):
        self.audio.play_strum(self.chord_names[self.chord_idx], self._pattern()[self._current_step()])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if self.back_btn.check_click(pos):
                return STATE_MENU
            if self.chord_btn.check_click(pos):
                self.chord_idx = (self.chord_idx + 1) % len(self.chord_names)
            elif self.strum_btn.check_click(pos):
                self._do_strum()
            else:
                for i, b in enumerate(self.pattern_btns):
                    if b.check_click(pos):
                        self.pattern_idx = i
                        self.start_tick = pygame.time.get_ticks()
                        break
        return None

    def handle_key(self, event):
        if event.key == pygame.K_SPACE:
            self._do_strum()
        elif event.key == pygame.K_RIGHT:
            self.chord_idx = (self.chord_idx + 1) % len(self.chord_names)
        elif event.key == pygame.K_LEFT:
            self.chord_idx = (self.chord_idx - 1) % len(self.chord_names)
        return None

    def draw(self):
        s = self.screen
        s.fill(DARK_BG)
        draw_header(s, "STRUMMING PATTERNS", PURPLE, WHITE, 42)
        self.back_btn.draw(s)
        f24 = pygame.font.Font(None, 24)
        s.blit(f24.render("Chord (klik / panah kiri-kanan):", True, LIGHT_GRAY), (120, 110))
        self.chord_btn.text = self.chord_names[self.chord_idx]
        self.chord_btn.draw(s)
        self.strum_btn.draw(s)
        s.blit(f24.render("Pola:", True, LIGHT_GRAY), (120, 200))
        for i, b in enumerate(self.pattern_btns):
            b.active = (i == self.pattern_idx); b.draw(s)
        self.indicator.draw(s, self._pattern(), self._current_step())
        s.blit(pygame.font.Font(None, 20).render(
            "Ikutin panah yang nyala. SPASI / STRUM = genjreng arah sesuai step.", True, YELLOW), (120, 420))
        demo = pygame.font.Font(None, 44).render(self.chord_names[self.chord_idx], True, GREEN)
        s.blit(demo, demo.get_rect(center=(400, 500)))
        pygame.display.flip()


# ==================== PRACTICE / CHALLENGE ===========================
def _make_chord_buttons(y_start=410, per_row=7):
    btns = []
    names = get_all_chord_names()
    bw, bh, gap = 84, 60, 14
    row_gap = 12
    for idx, n in enumerate(names):
        r = idx // per_row
        c = idx % per_row
        in_row = min(per_row, len(names) - r * per_row)
        row_w = in_row * bw + (in_row - 1) * gap
        x = (SCREEN_WIDTH - row_w) // 2 + c * (bw + gap)
        y = y_start + r * (bh + row_gap)
        btns.append((n, Button(x, y, bw, bh, n, BLUE, font_size=30)))
    return btns


class _BaseChordGame:
    def __init__(self, screen, audio, progress):
        self.screen = screen
        self.audio = audio
        self.progress = progress
        self.chord_names = get_all_chord_names()
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.wrong_count = 0
        self.bloon = ""
        self.chord_btns = _make_chord_buttons(410)
        self.back_btn = Button(660, 20, 120, 40, "BACK", RED)

    def _key_to_chord(self, key):
        mapping = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
                   pygame.K_5: 4, pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7,
                   pygame.K_9: 8, pygame.K_0: 9}
        if key in mapping and mapping[key] < len(self.chord_names):
            return self.chord_names[mapping[key]]
        return None

    def _register(self, correct, chord_name):
        self.progress.record_attempt(correct, chord_name if correct else None)
        if correct:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.wrong_count = 0
            self.bloon = ""
        else:
            self.combo = 0
            self.wrong_count += 1
            if self.wrong_count >= 3:
                self.bloon = random.choice(BLOONS_MESSAGES)
        if self.score > self.progress.best_score:
            self.progress.best_score = self.score

    def _draw_hud(self, title, time_str=None, time_color=YELLOW):
        s = self.screen
        s.fill(DARK_BG)
        # row 1: title (left) + BACK (right)  -> never share a row with TIME
        draw_header(s, title, YELLOW, WHITE, 42)
        self.back_btn.draw(s)
        # row 2: score/combo/best (left) + TIME (right-aligned)
        f = pygame.font.Font(None, 28)
        s.blit(f.render("Score: %d" % self.score, True, YELLOW), (50, 80))
        s.blit(f.render("Combo: %d" % self.combo, True, ORANGE), (210, 80))
        s.blit(f.render("Best: %d" % self.progress.best_score, True, LIGHT_GRAY), (360, 80))
        if time_str:
            tf = pygame.font.Font(None, 44)
            ts = tf.render(time_str, True, time_color)
            s.blit(ts, (SCREEN_WIDTH - 20 - ts.get_width(), 74))

    def _draw_buttons(self):
        for _n, b in self.chord_btns:
            b.draw(self.screen)

    def _draw_bloon(self, y):
        if self.bloon:
            bt = pygame.font.Font(None, 28).render(self.bloon, True, RED)
            self.screen.blit(bt, bt.get_rect(center=(SCREEN_WIDTH // 2, y)))


class PracticeMode(_BaseChordGame):
    def __init__(self, screen, audio, progress):
        super().__init__(screen, audio, progress)
        self.progression = []
        self.cur = 0
        self.flash = 0
        self.new_progression()

    def new_progression(self):
        self.progression = random.sample(self.chord_names, 4)
        self.cur = 0

    def target(self):
        return self.progression[self.cur]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if self.back_btn.check_click(pos):
                return STATE_MENU
            for n, b in self.chord_btns:
                if b.check_click(pos):
                    self.answer(n); break
        return None

    def handle_key(self, event):
        c = self._key_to_chord(event.key)
        if c:
            self.answer(c)
        return None

    def answer(self, chosen):
        tgt = self.target()
        correct = (chosen == tgt)
        if correct:
            self.score += 10 * (1 + self.combo // 5)
            self.audio.play_chord(chosen, "down")
            self.flash = 10
        self._register(correct, tgt)
        if correct:
            self.cur += 1
            if self.cur >= len(self.progression):
                self.new_progression()

    def draw(self):
        self._draw_hud("PRACTICE MODE")
        s = self.screen
        if self.flash > 0:
            self.flash -= 1
            pygame.draw.rect(s, (40, 160, 40), (0, 0, SCREEN_WIDTH, 6))
        # centered progression row
        f = pygame.font.Font(None, 76)
        items = []
        for i, ch in enumerate(self.progression):
            col = GREEN if i < self.cur else (YELLOW if i == self.cur else GRAY)
            items.append((ch, col, i))
        widths = [f.size(c)[0] for c, _col, _i in items]
        gap = 46
        total = sum(widths) + gap * (len(items) - 1)
        x = (SCREEN_WIDTH - total) // 2
        for (ch, col, i), w in zip(items, widths):
            t = f.render(ch, True, col)
            s.blit(t, (x, 150))
            if i == self.cur:
                draw_arrow(s, x + w // 2, 250, "down", size=15, color=YELLOW, width=4)
            x += w + gap
        self._draw_bloon(300)
        hint = pygame.font.Font(None, 22).render("Pilih chord yang ditunjuk (klik atau tekan 1-9 / 0).", True, LIGHT_GRAY)
        s.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 360)))
        self._draw_buttons()
        pygame.display.flip()


class ChallengeMode(_BaseChordGame):
    def __init__(self, screen, audio, progress, time_limit=60):
        super().__init__(screen, audio, progress)
        self.time_limit = time_limit
        self.start = time.time()
        self.time_left = float(time_limit)
        self.current = random.choice(self.chord_names)
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if self.back_btn.check_click(pos):
                return STATE_MENU
            if not self.game_over:
                for n, b in self.chord_btns:
                    if b.check_click(pos):
                        self.answer(n); break
        return None

    def handle_key(self, event):
        if not self.game_over:
            c = self._key_to_chord(event.key)
            if c:
                self.answer(c)
        return None

    def answer(self, chosen):
        # capture correctness BEFORE mutating self.current
        correct = (chosen == self.current)
        answered_chord = self.current
        if correct:
            speed_bonus = max(1, int(self.time_left / 10))
            self.score += 10 * (1 + self.combo // 3) * speed_bonus
            self.audio.play_chord(chosen, "down")
            self.current = random.choice(self.chord_names)
        self._register(correct, answered_chord)

    def update(self):
        if not self.game_over:
            self.time_left = max(0.0, self.time_limit - (time.time() - self.start))
            if self.time_left <= 0:
                self.game_over = True
                self.progress.save_progress()

    def draw(self):
        tc = RED if self.time_left < 10 else YELLOW
        time_str = None if self.game_over else "Time: %ds" % int(self.time_left)
        self._draw_hud("CHALLENGE MODE", time_str, tc)
        s = self.screen
        if not self.game_over:
            lbl = pygame.font.Font(None, 24).render("MAIN CHORD INI:", True, LIGHT_GRAY)
            s.blit(lbl, lbl.get_rect(center=(SCREEN_WIDTH // 2, 140)))
            big = pygame.font.Font(None, 120).render(self.current, True, GREEN)
            s.blit(big, big.get_rect(center=(SCREEN_WIDTH // 2, 225)))
            self._draw_bloon(315)
            hint = pygame.font.Font(None, 22).render("Cepet + bener = skor gede. Salah = combo reset.", True, LIGHT_GRAY)
            s.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 365)))
            self._draw_buttons()
        else:
            go = pygame.font.Font(None, 72).render("TIME'S UP!", True, RED)
            s.blit(go, go.get_rect(center=(SCREEN_WIDTH // 2, 200)))
            fs = pygame.font.Font(None, 44).render("Final Score: %d" % self.score, True, YELLOW)
            s.blit(fs, fs.get_rect(center=(SCREEN_WIDTH // 2, 270)))
            mc = pygame.font.Font(None, 32).render("Max Combo: %d" % self.max_combo, True, ORANGE)
            s.blit(mc, mc.get_rect(center=(SCREEN_WIDTH // 2, 320)))
            again = pygame.font.Font(None, 26).render("Klik BACK buat balik, atau ESC.", True, LIGHT_GRAY)
            s.blit(again, again.get_rect(center=(SCREEN_WIDTH // 2, 380)))
        pygame.display.flip()


# ============================= GAME ==================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.audio = GuitarAudio()
        self.progress = ProgressTracker()
        self.state = STATE_MENU
        self.running = True
        self.learn_mode = None
        self.practice_mode = None
        self.challenge_mode = None
        self.strumming_mode = None
        # left column buttons (menu)
        self.menu_buttons = [
            Button(120, 180, 240, 56, "LEARN MODE", BLUE, font_size=32),
            Button(120, 250, 240, 56, "PRACTICE MODE", ORANGE, font_size=32),
            Button(120, 320, 240, 56, "CHALLENGE MODE", RED, font_size=32),
            Button(120, 390, 240, 56, "STRUMMING", PURPLE, font_size=32),
        ]
        self.menu_actions = [STATE_LEARN, STATE_PRACTICE, STATE_CHALLENGE, STATE_STRUMMING]

    def _enter(self, new_state):
        if new_state == STATE_LEARN and self.learn_mode is None:
            self.learn_mode = LearnMode(self.screen, self.audio)
        elif new_state == STATE_PRACTICE:
            self.practice_mode = PracticeMode(self.screen, self.audio, self.progress)
        elif new_state == STATE_CHALLENGE:
            self.challenge_mode = ChallengeMode(self.screen, self.audio, self.progress)
        elif new_state == STATE_STRUMMING and self.strumming_mode is None:
            self.strumming_mode = StrummingMode(self.screen, self.audio)
        self.state = new_state

    def _to_menu(self):
        self.progress.save_progress()
        self.state = STATE_MENU

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.progress.save_progress()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state != STATE_MENU:
                    self._to_menu()
                continue
            if event.type == pygame.MOUSEMOTION and self.state == STATE_MENU:
                pos = pygame.mouse.get_pos()
                for b in self.menu_buttons:
                    b.check_hover(pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == STATE_MENU:
                pos = pygame.mouse.get_pos()
                for b, act in zip(self.menu_buttons, self.menu_actions):
                    if b.check_click(pos):
                        self._enter(act); break
            mode = {STATE_LEARN: self.learn_mode, STATE_PRACTICE: self.practice_mode,
                    STATE_CHALLENGE: self.challenge_mode, STATE_STRUMMING: self.strumming_mode}.get(self.state)
            if mode is None:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mode.handle_event(event):
                    self._to_menu()
            elif event.type == pygame.KEYDOWN:
                if mode.handle_key(event):
                    self._to_menu()

    def update(self):
        if self.state == STATE_CHALLENGE and self.challenge_mode:
            self.challenge_mode.update()

    def draw_menu(self):
        s = self.screen
        s.fill(DARK_BG)
        draw_header(s, "GENJRENG", YELLOW, YELLOW, 64,
                    "Basic Guitar Chord Training",
                    '"Press the strings. Make noise. Eventually call it music."')
        # left column: buttons
        for b in self.menu_buttons:
            b.draw(s)
        # right column: stats panel (x=470..790)
        names = get_all_chord_names()
        mastered = len(self.progress.chords_mastered)
        px = 470
        f22 = pygame.font.Font(None, 22)
        s.blit(f22.render("Level:", True, LIGHT_GRAY), (px, 180))
        s.blit(f22.render(self.progress.get_level(), True, GREEN), (px, 206))
        s.blit(f22.render("Best Score: %d" % self.progress.best_score, True, ORANGE), (px, 238))
        s.blit(f22.render("Accuracy: %.1f%%" % self.progress.get_accuracy(), True, YELLOW), (px, 264))
        s.blit(f22.render("Mastered: %d / %d" % (mastered, len(names)), True, WHITE), (px, 290))
        ProgressBar(px, 314, 300, 16).draw(s, mastered / len(names), GREEN, "chord mastery")
        # checklist 2 columns x 5 rows (10 chords fit cleanly)
        cf = pygame.font.Font(None, 18)
        half = (len(names) + 1) // 2
        for i, n in enumerate(names):
            col = 0 if i < half else 1
            row = i if i < half else i - half
            cx = px + col * 160
            cy = 342 + row * 22
            mark = "[x]" if n in self.progress.chords_mastered else "[ ]"
            mcol = GREEN if n in self.progress.chords_mastered else GRAY
            s.blit(cf.render("%s %s" % (mark, n), True, mcol), (cx, cy))
        s.blit(pygame.font.Font(None, 18).render(
            "ESC = back  |  mouse / touch  |  keys 1-9 and 0 = pick chord", True, GRAY), (120, 560))
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            if not self.running:
                break
            self.update()
            if self.state == STATE_MENU:
                self.draw_menu()
            elif self.state == STATE_LEARN and self.learn_mode:
                self.learn_mode.draw()
            elif self.state == STATE_PRACTICE and self.practice_mode:
                self.practice_mode.draw()
            elif self.state == STATE_CHALLENGE and self.challenge_mode:
                self.challenge_mode.draw()
            elif self.state == STATE_STRUMMING and self.strumming_mode:
                self.strumming_mode.draw()
            self.clock.tick(FPS)
        pygame.quit()


def main():
    print("=" * 52)
    print("  GENJRENG - Basic Guitar Chord Training")
    print("=" * 52)
    print('  "Press the strings. Make noise. Eventually call it music."')
    print()
    print("  Controls: mouse / touch to click, ESC to go back,")
    print("  SPACE to play/strum, keys 1-9 and 0 to pick chords.")
    print()
    print("  Starting game...")
    Game().run()


if __name__ == "__main__":
    main()
# ========================= END OF FILE ===============================
