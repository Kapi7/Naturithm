"""Compile Reel clips with branded text overlays matching still photo style."""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips


# Brand colors
SAND = (196, 149, 106)
WHITE = (255, 255, 255)
FONT_TTC = "/System/Library/Fonts/Palatino.ttc"
FONT_REGULAR_IDX = 0
FONT_ITALIC_IDX = 1
FONT_BOLD_IDX = 2
FONT_BOLD_ITALIC_IDX = 3


def create_text_overlay(width, height, lines, key_line_idx=None, font_size=38,
                         watermark=None, position="bottom"):
    """Create a transparent overlay image with styled text.

    lines: list of text lines
    key_line_idx: index of the line to highlight in sand bold italic
    position: "bottom" (default) or "center"
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_regular = ImageFont.truetype(FONT_TTC, font_size, index=FONT_REGULAR_IDX)
    font_bold_italic = ImageFont.truetype(FONT_TTC, font_size, index=FONT_BOLD_ITALIC_IDX)

    # Calculate total text block height
    line_spacing = int(font_size * 0.6)
    line_heights = []
    for i, line in enumerate(lines):
        f = font_bold_italic if i == key_line_idx else font_regular
        bbox = draw.textbbox((0, 0), line, font=f)
        line_heights.append(bbox[3] - bbox[1])

    total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)

    # Semi-transparent dark gradient band
    if position == "bottom":
        band_top = height - total_text_height - int(font_size * 4)
        band_bottom = height
    else:  # center
        center_y = height // 2
        band_top = center_y - total_text_height // 2 - int(font_size * 2)
        band_bottom = center_y + total_text_height // 2 + int(font_size * 2)

    # Draw gradient band (darker in center, fading at edges)
    band_height = band_bottom - band_top
    for y_offset in range(band_height):
        y = band_top + y_offset
        # Smooth fade: stronger in middle, softer at edges
        progress = y_offset / band_height
        if progress < 0.15:
            alpha = int(140 * (progress / 0.15))
        elif progress > 0.85:
            alpha = int(140 * ((1 - progress) / 0.15))
        else:
            alpha = 140
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    # Draw text centered in the band
    if position == "bottom":
        text_start_y = height - total_text_height - int(font_size * 2)
    else:
        text_start_y = (height - total_text_height) // 2

    current_y = text_start_y
    for i, line in enumerate(lines):
        if i == key_line_idx:
            font = font_bold_italic
            color = SAND
        else:
            font = font_regular
            color = WHITE

        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2

        # Subtle text shadow for depth
        draw.text((x + 1, current_y + 1), line, font=font, fill=(0, 0, 0, 100))
        draw.text((x, current_y), line, font=font, fill=color + (255,))

        current_y += line_heights[i] + line_spacing

    # Watermark
    if watermark:
        wm_font = ImageFont.truetype(FONT_TTC, 20, index=FONT_REGULAR_IDX)
        draw.text((24, 24), watermark, font=wm_font, fill=(255, 255, 255, 120))

    return np.array(img)


def compile_coconut_reel(output_path="output/coconut_reel/coconut_reel_final.mp4",
                          audio_path=None):
    """Compile the coconut reel with branded overlays."""

    base = "output/coconut_reel/video"

    # Clip definitions: (filename, duration, lines, key_line_index, position)
    clips_data = [
        ("01_hook.mp4", 5,
         ["A coconut falls from a tree.", "Inside it...", "perfection."],
         2, "bottom"),

        ("02_oria.mp4", 6,
         ["Most people see a drink.", "I see millions of years", "of design."],
         2, "center"),

        ("03_rain_palm.mp4", 6,
         ["Rain falls. The palm catches it.", "Filters it. Stores it."],
         1, "bottom"),

        ("04_ocean.mp4", 6,
         ["Electrolytes your cells", "recognize instantly."],
         1, "center"),

        ("05_cross.mp4", 6,
         ["We spend billions trying to replicate", "what one fruit does for free."],
         1, "bottom"),

        ("06_closing.mp4", 5,
         ["Nature didn't need a lab.", "— Oria"],
         0, "center"),
    ]

    final_clips = []

    for filename, duration, lines, key_idx, pos in clips_data:
        filepath = os.path.join(base, filename)
        print(f"Processing {filename}...")

        video = VideoFileClip(filepath)
        w, h = video.size

        # Create overlay
        overlay_array = create_text_overlay(
            w, h, lines,
            key_line_idx=key_idx,
            font_size=38,
            watermark="oria" if filename != "06_closing.mp4" else None,
            position=pos
        )

        overlay_clip = (ImageClip(overlay_array)
                       .with_duration(video.duration)
                       .with_position((0, 0)))

        composite = CompositeVideoClip([video, overlay_clip])
        final_clips.append(composite)

    print("Concatenating clips...")
    final = concatenate_videoclips(final_clips, method="compose")

    # Add audio if provided
    if audio_path:
        from moviepy import AudioFileClip
        audio = AudioFileClip(audio_path).subclipped(0, final.duration)
        final = final.with_audio(audio)

    print(f"Writing to {output_path}...")
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="8000k",
    )
    print("Done!")

    # Cleanup
    for c in final_clips:
        c.close()
    final.close()


if __name__ == "__main__":
    compile_coconut_reel()
