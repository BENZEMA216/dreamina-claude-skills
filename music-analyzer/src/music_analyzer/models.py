"""Pydantic data models for music analysis results."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Rhythm
# ---------------------------------------------------------------------------

class BeatInfo(BaseModel):
    """Individual beat position."""
    time: float = Field(description="Beat time in seconds")
    strength: float = Field(default=1.0, description="Beat strength 0-1")


class SongSection(BaseModel):
    """A structural section of the song."""
    label: str = Field(description="Section label: intro, verse, chorus, bridge, outro, etc.")
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    confidence: float = Field(default=0.5, description="Detection confidence 0-1")


class RhythmAnalysis(BaseModel):
    """Rhythm and structural analysis results."""
    bpm: float = Field(description="Estimated tempo in BPM")
    bpm_confidence: float = Field(default=0.5, description="BPM estimation confidence 0-1")
    time_signature: str = Field(default="4/4", description="Estimated time signature")
    beats: list[BeatInfo] = Field(default_factory=list, description="Beat positions")
    downbeats: list[float] = Field(default_factory=list, description="Downbeat times in seconds")
    sections: list[SongSection] = Field(default_factory=list, description="Song structure sections")
    duration: float = Field(description="Total duration in seconds")


# ---------------------------------------------------------------------------
# Emotion
# ---------------------------------------------------------------------------

class EmotionAnalysis(BaseModel):
    """Emotion, energy, and style classification."""
    primary_emotion: str = Field(description="Dominant emotion: happy, sad, angry, calm, energetic, melancholic, etc.")
    secondary_emotions: list[str] = Field(default_factory=list, description="Secondary emotion tags")
    overall_energy: float = Field(description="Overall energy level 0-1")
    energy_curve: list[float] = Field(default_factory=list, description="Energy values per segment (normalized 0-1)")
    valence: float = Field(description="Emotional valence: -1 (negative) to 1 (positive)")
    arousal: float = Field(default=0.5, description="Arousal level 0-1")
    genre: str = Field(default="unknown", description="Detected genre")
    mood_tags: list[str] = Field(default_factory=list, description="Mood descriptor tags")
    method: str = Field(default="heuristic", description="Detection method: clap or heuristic")


# ---------------------------------------------------------------------------
# Timbre
# ---------------------------------------------------------------------------

class SpectralFeatures(BaseModel):
    """Spectral feature summary statistics."""
    spectral_centroid_mean: float = Field(description="Mean spectral centroid in Hz")
    spectral_centroid_std: float = Field(description="Std dev of spectral centroid")
    spectral_bandwidth_mean: float = Field(description="Mean spectral bandwidth in Hz")
    spectral_rolloff_mean: float = Field(description="Mean spectral rolloff in Hz")
    zero_crossing_rate_mean: float = Field(description="Mean zero crossing rate")


class MFCCSummary(BaseModel):
    """MFCC coefficient summary."""
    means: list[float] = Field(description="Mean of each MFCC coefficient")
    stds: list[float] = Field(description="Std dev of each MFCC coefficient")
    n_mfcc: int = Field(default=13, description="Number of MFCC coefficients")


class StemPaths(BaseModel):
    """Paths to separated audio stems (if demucs available)."""
    vocals: Optional[str] = None
    drums: Optional[str] = None
    bass: Optional[str] = None
    other: Optional[str] = None


class TimbreAnalysis(BaseModel):
    """Timbre and spectral analysis results."""
    mfcc: MFCCSummary = Field(description="MFCC summary statistics")
    spectral: SpectralFeatures = Field(description="Spectral feature statistics")
    loudness_lufs: Optional[float] = Field(default=None, description="Integrated loudness in LUFS")
    loudness_range: Optional[float] = Field(default=None, description="Loudness range in LU")
    dynamic_range_db: float = Field(description="Estimated dynamic range in dB")
    brightness: float = Field(description="Brightness score 0-1 (spectral centroid normalized)")
    warmth: float = Field(description="Warmth score 0-1 (low-frequency energy ratio)")
    stems: Optional[StemPaths] = Field(default=None, description="Separated stem file paths")


# ---------------------------------------------------------------------------
# Tonality
# ---------------------------------------------------------------------------

class ChordEvent(BaseModel):
    """A detected chord at a time position."""
    time: float = Field(description="Chord onset time in seconds")
    duration: float = Field(description="Chord duration in seconds")
    chord: str = Field(description="Chord label (e.g. 'C', 'Am', 'F#m7')")
    confidence: float = Field(default=0.5, description="Detection confidence 0-1")


class TonalityAnalysis(BaseModel):
    """Key, chord, and melody analysis results."""
    key: str = Field(description="Estimated key (e.g. 'C major', 'A minor')")
    key_confidence: float = Field(default=0.5, description="Key estimation confidence 0-1")
    mode: str = Field(description="Mode: major or minor")
    chords: list[ChordEvent] = Field(default_factory=list, description="Chord progression")
    melody_contour: list[float] = Field(default_factory=list, description="Melody pitch contour (Hz values, sampled)")
    method: str = Field(default="librosa", description="Detection method: librosa or essentia")


# ---------------------------------------------------------------------------
# Lyrics
# ---------------------------------------------------------------------------

class LyricSegment(BaseModel):
    """A timestamped lyrics segment."""
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    text: str = Field(description="Transcribed text")
    confidence: float = Field(default=0.5, description="Transcription confidence 0-1")


class LyricsAnalysis(BaseModel):
    """Lyrics transcription results."""
    segments: list[LyricSegment] = Field(default_factory=list, description="Timestamped lyrics")
    full_text: str = Field(default="", description="Full concatenated lyrics text")
    language: str = Field(default="unknown", description="Detected language")
    has_vocals: bool = Field(default=False, description="Whether vocals were detected")
    method: str = Field(default="none", description="Transcription method: whisper or none")


# ---------------------------------------------------------------------------
# Onsets
# ---------------------------------------------------------------------------

class OnsetInfo(BaseModel):
    """Onset detection results for visual sync."""
    onset_times: list[float] = Field(default_factory=list, description="Onset times in seconds")
    onset_strengths: list[float] = Field(default_factory=list, description="Onset strengths (normalized 0-1)")
    onset_rate: float = Field(default=0.0, description="Average onsets per second")


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------

class ColorPalette(BaseModel):
    """Color palette derived from musical characteristics."""
    primary: str = Field(description="Primary color hex code")
    secondary: str = Field(description="Secondary color hex code")
    accent: str = Field(description="Accent color hex code")
    background: str = Field(description="Background color hex code")
    text: str = Field(description="Text color hex code")
    palette: list[str] = Field(default_factory=list, description="Full palette of hex codes")
    mood_association: str = Field(default="", description="Mood/emotion the palette represents")


# ---------------------------------------------------------------------------
# Dreamina Prompt
# ---------------------------------------------------------------------------

class DreaminaSectionPrompt(BaseModel):
    """Dreamina prompt for a single song section."""
    section: str = Field(description="Section label (e.g. 'chorus_1')")
    time_range: dict = Field(description="{'start': float, 'end': float}")
    prompt_zh: str = Field(description="Chinese prompt for Dreamina")
    prompt_en: str = Field(description="English prompt for Dreamina")
    style_keywords: list[str] = Field(default_factory=list, description="Style keyword tags")
    color_palette: list[str] = Field(default_factory=list, description="Suggested hex colors")
    energy_level: float = Field(description="Energy level 0-1")


class DreaminaOutput(BaseModel):
    """Complete Dreamina prompt output for a song."""
    song_title: str = Field(default="", description="Song title if known")
    total_duration: float = Field(description="Total duration in seconds")
    sections: list[DreaminaSectionPrompt] = Field(default_factory=list)
    global_style: str = Field(default="", description="Global style descriptor")
    global_keywords: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Storyboard
# ---------------------------------------------------------------------------

class StoryboardShot(BaseModel):
    """A single shot in the storyboard."""
    shot_number: int = Field(description="Shot sequence number")
    section: str = Field(description="Song section label")
    time_range: dict = Field(description="{'start': float, 'end': float}")
    duration: float = Field(description="Shot duration in seconds")
    shot_type: str = Field(description="Shot type: wide, medium, close-up, extreme close-up, aerial")
    camera_movement: str = Field(description="Camera movement: static, pan, tilt, dolly, orbit, crane")
    visual_description_zh: str = Field(default="", description="Visual description in Chinese")
    visual_description_en: str = Field(default="", description="Visual description in English")
    mood: str = Field(default="", description="Mood descriptor for this shot")
    color_palette: list[str] = Field(default_factory=list)
    transition: str = Field(default="cut", description="Transition to next shot: cut, dissolve, fade, wipe")
    energy_level: float = Field(default=0.5, description="Energy level 0-1")


class StoryboardOutput(BaseModel):
    """Complete storyboard for a song."""
    song_title: str = Field(default="", description="Song title if known")
    total_duration: float = Field(description="Total duration in seconds")
    bpm: float = Field(description="Song BPM")
    key: str = Field(default="", description="Song key")
    shots: list[StoryboardShot] = Field(default_factory=list)
    global_mood: str = Field(default="", description="Overall mood")
    global_style: str = Field(default="", description="Overall visual style")


# ---------------------------------------------------------------------------
# Top-level result
# ---------------------------------------------------------------------------

class MusicAnalysisResult(BaseModel):
    """Top-level music analysis result containing all analysis dimensions."""
    file_path: str = Field(description="Path to the analyzed audio file")
    file_name: str = Field(default="", description="Audio file name")
    duration: float = Field(description="Total duration in seconds")
    sample_rate: int = Field(description="Sample rate used for analysis")
    dependency_tier: str = Field(default="lite", description="Dependency tier used: lite/standard/full")
    rhythm: Optional[RhythmAnalysis] = None
    emotion: Optional[EmotionAnalysis] = None
    timbre: Optional[TimbreAnalysis] = None
    tonality: Optional[TonalityAnalysis] = None
    lyrics: Optional[LyricsAnalysis] = None
    onsets: Optional[OnsetInfo] = None
    color_palette: Optional[ColorPalette] = None
