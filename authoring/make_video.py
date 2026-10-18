"""Assemble a captioned, condensed walkthrough from actual browser captures."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
SCENES = [
    ("01-c3-home.jpg", 6, "Byte Club Studio\nA short demo with Gemini. All contact details are fictional."),
    ("02-c3-price.jpg", 8, "Prices and policies\nThe answer uses the business summary and the PDF."),
    ("03-c3-missing-email.jpg", 8, "Contact requests\nThe assistant asks for the missing email."),
    ("04-c3-lead.jpg", 8, "Remembering details\nIt combines the email with the name and request from the previous message."),
    ("05-c3-tool-trace.jpg", 10, "Tool result\nThe contact request was saved. The activity panel shows the receipt."),
    ("06-c3-feedback.jpg", 8, "Feedback\nThe feedback tool saves the customer's comment."),
    ("07-c3-unknown.jpg", 8, "Unanswered questions\nThe assistant records a question that the documents cannot answer."),
    ("08-c4-configuration.jpg", 8, "ReAct version\nThe LangGraph app has controls for examples and instruction placement."),
    ("09-c4-sampling.jpg", 7, "Model settings\nTemperature, top-p, top-k, and the output limit can be changed."),
]


def stamp(seconds):
    seconds = int(seconds)
    return f"{seconds//3600:02}:{seconds%3600//60:02}:{seconds%60:02},000"


if __name__ == "__main__":
    manifest, subtitles, elapsed = [], [], 0
    for index, (filename, duration, caption) in enumerate(SCENES, start=1):
        if not (DEMO / filename).exists():
            raise FileNotFoundError(filename)
        manifest.extend(["file '" + filename + "'", "duration " + str(duration)])
        subtitles.append(str(index) + "\n" + stamp(elapsed) + " --> " + stamp(elapsed + duration) + "\n" + caption)
        elapsed += duration
    manifest.append("file '" + SCENES[-1][0] + "'")
    (DEMO / "scenes.txt").write_text("\n".join(manifest) + "\n")
    (DEMO / "demo.srt").write_text("\n\n".join(subtitles) + "\n")
    filters = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,subtitles=demo.srt:force_style='FontName=DejaVu Sans,FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=2,MarginV=16'"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", "scenes.txt", "-vf", filters,
                    "-t", str(elapsed), "-r", "12", "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "byte_club_demo.mp4"], cwd=DEMO, check=True)
    print("Created", DEMO / "byte_club_demo.mp4", "duration", elapsed, "seconds")
