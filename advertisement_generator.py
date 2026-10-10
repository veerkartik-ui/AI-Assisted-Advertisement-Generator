"""AI-Assisted Advertisement Generator: offline design recommendations and PNG rendering."""
from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

WIDTH = HEIGHT = 1080

CATEGORY_RULES: dict[str, dict[str, Any]] = {
    "fitness": {
        "keywords": ["gym", "fitness", "protein", "muscle", "workout", "training", "health", "athlete", "supplement"],
        "palette": [(9, 22, 38), (24, 91, 113), (73, 201, 176)],
        "taglines": ["Train harder. Recover smarter.", "Fuel your next level.", "Built for the grind."],
        "cta": "SHOP NOW", "visual": "bottle",
    },
    "beauty": {
        "keywords": ["skin", "skincare", "serum", "beauty", "glow", "face", "cosmetic", "makeup", "moisturizer", "vitamin"],
        "palette": [(39, 19, 45), (110, 44, 91), (236, 144, 196)],
        "taglines": ["Glow that feels like you.", "A better routine starts here.", "Simple care. Visible glow."],
        "cta": "DISCOVER", "visual": "jar",
    },
    "education": {
        "keywords": ["course", "learning", "education", "exam", "coding", "skill", "study", "class", "tutor", "workshop"],
        "palette": [(13, 28, 64), (36, 83, 148), (244, 178, 76)],
        "taglines": ["Learn today. Lead tomorrow.", "Turn curiosity into skill.", "Your next skill starts here."],
        "cta": "START LEARNING", "visual": "laptop",
    },
    "food": {
        "keywords": ["food", "restaurant", "pizza", "burger", "cafe", "meal", "delivery", "snack", "bakery", "coffee"],
        "palette": [(70, 24, 12), (165, 59, 31), (247, 177, 80)],
        "taglines": ["Good food. Great mood.", "Your craving, upgraded.", "One bite closer to happy."],
        "cta": "ORDER NOW", "visual": "plate",
    },
    "tech": {
        "keywords": ["app", "phone", "laptop", "software", "ai", "technology", "device", "smart", "digital", "platform"],
        "palette": [(10, 15, 30), (65, 55, 155), (114, 216, 255)],
        "taglines": ["Smarter tools. Better work.", "Power up the way you create.", "Designed for what comes next."],
        "cta": "TRY IT NOW", "visual": "phone",
    },
    "fashion": {
        "keywords": ["fashion", "shoe", "shoes", "shirt", "clothing", "style", "wear", "outfit", "sneaker", "accessory"],
        "palette": [(18, 18, 18), (71, 71, 71), (223, 190, 146)],
        "taglines": ["Make your everyday iconic.", "Wear the difference.", "Style, made personal."],
        "cta": "SHOP COLLECTION", "visual": "shoe",
    },
}

AUDIENCE_MODIFIERS = {
    "students": ("education", "START LEARNING"),
    "college students": ("education", "START LEARNING"),
    "young adults": ("tech", "TRY IT NOW"),
    "professionals": ("tech", "TRY IT NOW"),
    "gym goers": ("fitness", "SHOP NOW"),
    "gym-goers": ("fitness", "SHOP NOW"),
    "fitness enthusiasts": ("fitness", "SHOP NOW"),
    "parents": ("education", "EXPLORE COURSES"),
    "food lovers": ("food", "ORDER NOW"),
    "fashion lovers": ("fashion", "SHOP COLLECTION"),
}


@dataclass(frozen=True)
class DesignPlan:
    category: str
    palette: list[tuple[int, int, int]]
    tagline: str
    cta: str
    visual: str
    typography: str
    layout: str
    confidence: int
    matched_keywords: list[str]


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def deterministic_choice(options: list[str], seed_text: str) -> str:
    if not options:
        raise ValueError("At least one option is required.")
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return options[int(digest[:8], 16) % len(options)]


def analyze_inputs(product: str, audience: str, requirements: str) -> dict[str, Any]:
    corpus = normalize(" ".join((product, audience, requirements)))
    words = set(corpus.split())
    scores = {name: 0 for name in CATEGORY_RULES}
    matched = {name: [] for name in CATEGORY_RULES}
    for category, rule in CATEGORY_RULES.items():
        for keyword in rule["keywords"]:
            if keyword in words:
                scores[category] += 1
                matched[category].append(keyword)
    audience_text = normalize(audience)
    for phrase, (category, _cta) in AUDIENCE_MODIFIERS.items():
        if phrase in audience_text:
            scores[category] += 2
            matched[category].append(phrase)
    ranked = sorted(scores.items(), key=lambda item: (-item[1], list(CATEGORY_RULES).index(item[0])))
    category, score = ranked[0]
    if score == 0:
        category, score = "tech", 1
    return {
        "category": category,
        "score": score,
        "confidence": min(96, 58 + score * 9),
        "scores": scores,
        "matched": matched[category],
    }


def build_design_plan(product: str, audience: str, requirements: str = "") -> DesignPlan:
    if not product.strip():
        raise ValueError("Please enter a product or campaign name.")
    if not audience.strip():
        raise ValueError("Please enter a target audience.")
    analysis = analyze_inputs(product, audience, requirements)
    category = analysis["category"]
    rule = CATEGORY_RULES[category]
    seed = f"{product}|{audience}|{requirements}|{category}"
    req = normalize(requirements)
    if "premium" in req or "minimal" in req or "clean" in req:
        typography = "Bold display heading + clean regular body"
        layout = "Minimal split layout with strong product focus"
    elif any(word in req for word in ("sale", "discount", "offer")):
        typography = "Heavy bold heading + high-contrast offer"
        layout = "Asymmetric promotional layout"
    else:
        typography = "Bold display heading + compact supporting text"
        layout = "Diagonal hero layout with CTA anchor"
    cta = rule["cta"]
    audience_text = normalize(audience)
    for hint, (hint_category, hint_cta) in AUDIENCE_MODIFIERS.items():
        if hint_category == category and hint in audience_text:
            cta = hint_cta
            break
    return DesignPlan(category, list(rule["palette"]), deterministic_choice(rule["taglines"], seed),
                      cta, rule["visual"], typography, layout, int(analysis["confidence"]), list(analysis["matched"]))


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        (["C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
         ["C:/Windows/Fonts/arial.ttf", "/Library/Fonts/Arial.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if current and _text_width(draw, trial, font) > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def _rounded(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], radius: int, fill: Any) -> None:
    draw.rounded_rectangle(bounds, radius=radius, fill=fill)


def _draw_visual(draw: ImageDraw.ImageDraw, plan: DesignPlan, center: tuple[int, int] = (805, 530)) -> None:
    cx, cy = center
    _base, main, accent = plan.palette
    dark = (18, 23, 32)
    if plan.visual == "bottle":
        x1, y1, x2, y2 = cx-82, cy-185, cx+82, cy+185
        _rounded(draw, (x1, y1, x2, y2), 28, main)
        draw.rectangle((cx-43, y1-27, cx+43, y1+4), fill=main)
        _rounded(draw, (cx-68, y1-45, cx+68, y1-24), 7, accent)
        _rounded(draw, (cx-64, cy-35, cx+64, cy+69), 14, accent)
        f = _font(22, True)
        draw.text((cx-_text_width(draw, "ACTIVE", f)//2, cy-3), "ACTIVE", font=f, fill=plan.palette[0])
    elif plan.visual == "jar":
        _rounded(draw, (cx-150, cy-100, cx+150, cy+105), 36, main)
        _rounded(draw, (cx-130, cy-130, cx+130, cy-91), 8, accent)
        label, f = "GLOWLEAF", _font(21, True)
        draw.text((cx-_text_width(draw, label, f)//2, cy-10), label, font=f, fill=(43, 18, 43))
    elif plan.visual == "laptop":
        _rounded(draw, (cx-190, cy-125, cx+190, cy+120), 22, dark)
        _rounded(draw, (cx-172, cy-107, cx+172, cy+101), 13, main)
        draw.ellipse((cx-30, cy-30, cx+30, cy+30), fill=accent)
        draw.polygon([(cx-218, cy+120), (cx+218, cy+120), (cx+185, cy+147), (cx-185, cy+147)], fill=(40, 44, 54))
    elif plan.visual == "phone":
        _rounded(draw, (cx-100, cy-190, cx+100, cy+190), 35, dark)
        _rounded(draw, (cx-87, cy-174, cx+87, cy+174), 26, main)
        draw.ellipse((cx-26, cy-113, cx+26, cy-61), fill=accent)
        _rounded(draw, (cx-58, cy-24, cx+58, cy), 7, (241, 243, 246))
        _rounded(draw, (cx-58, cy+18, cx+35, cy+42), 7, (218, 224, 234))
    elif plan.visual == "plate":
        r = 160
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(246, 239, 225))
        draw.ellipse((cx-r+22, cy-r+22, cx+r-22, cy+r-22), fill=(80, 37, 22))
        for dx, dy, rr in [(-48, -28, 34), (38, -40, 30), (-6, 42, 40), (58, 42, 27)]:
            draw.ellipse((cx+dx-rr, cy+dy-rr, cx+dx+rr, cy+dy+rr), fill=accent)
    elif plan.visual == "shoe":
        points = [(cx-180, cy+48), (cx-58, cy-56), (cx+15, cy-42), (cx+105, cy+25),
                  (cx+165, cy+45), (cx+175, cy+91), (cx-110, cy+91)]
        draw.polygon(points, fill=main)
        draw.line(points[:5], fill=accent, width=7, joint="curve")
        draw.rectangle((cx-128, cy+82, cx+151, cy+108), fill=(238, 238, 238))


def render_ad(product: str, audience: str, requirements: str = "bold, modern, energetic",
              out_path: str | Path = "generated_ad.png") -> DesignPlan:
    plan = build_design_plan(product, audience, requirements)
    img = Image.new("RGB", (WIDTH, HEIGHT), plan.palette[0])
    draw = ImageDraw.Draw(img)
    top, bottom = plan.palette[0], tuple(max(0, c-18) for c in plan.palette[0])
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")
    for radius, alpha in ((420, 15), (300, 18), (180, 22)):
        od.ellipse((560-radius, 20-radius, 560+radius, 20+radius), fill=(*plan.palette[2], alpha))
    od.polygon([(610, 0), (WIDTH, 0), (WIDTH, HEIGHT), (390, HEIGHT)], fill=(*plan.palette[1], 58))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    _rounded(draw, (64, 58, 354, 108), 22, plan.palette[2])
    badge_font = _font(19, True)
    draw.text((82, 72), "AI-ASSISTED CONCEPT", font=badge_font, fill=plan.palette[0])

    title = re.sub(r"\s+", " ", product.strip()).upper()
    title_y = 152
    for line in _wrap(draw, title, _font(68, True), 515)[:3]:
        f = _font(68 if _text_width(draw, line, _font(68, True)) <= 515 else 48, True)
        draw.text((66, title_y), line, font=f, fill=(248, 249, 251))
        title_y += 78
    copy_y = max(390, title_y + 5)
    for line in _wrap(draw, plan.tagline, _font(32, True), 485)[:3]:
        draw.text((68, copy_y), line, font=_font(32, True), fill=plan.palette[2])
        copy_y += 42
    copy_y += 12
    for line in _wrap(draw, f"DESIGNED FOR {audience.strip().upper()}", _font(21), 490)[:2]:
        draw.text((68, copy_y), line, font=_font(21), fill=(220, 226, 233))
        copy_y += 30

    tokens = [x.strip() for x in re.split(r"[,;\n]", requirements) if x.strip()][:3]
    chip_x, chip_y = 66, max(copy_y + 22, 690)
    for token in tokens:
        f = _font(16, True)
        text = token.upper()[:24]
        width = min(265, max(125, _text_width(draw, text, f) + 30))
        if chip_x + width > 565:
            chip_x, chip_y = 66, chip_y + 52
        _rounded(draw, (chip_x, chip_y, chip_x+width, chip_y+40), 14, (55, 64, 78))
        draw.text((chip_x+14, chip_y+10), text, font=f, fill=(246, 248, 250))
        chip_x += width + 10

    _draw_visual(draw, plan)
    cta_font = _font(26, True)
    cta_width = _text_width(draw, plan.cta, cta_font) + 66
    _rounded(draw, (66, 875, 66+cta_width, 943), 23, plan.palette[2])
    draw.text((99, 894), plan.cta, font=cta_font, fill=plan.palette[0])
    footer = _font(16)
    draw.text((66, 1010), f"DESIGN STRENGTH: {plan.confidence}%  |  CATEGORY: {plan.category.upper()}",
              font=footer, fill=(205, 211, 220))
    draw.text((66, 1040), "Generated concept - review copy and brand details before publishing",
              font=_font(13), fill=(170, 179, 191))

    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, format="PNG", optimize=True)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a digital advertisement PNG concept.")
    parser.add_argument("--product", default="PulseFit Protein")
    parser.add_argument("--audience", default="Gym Goers")
    parser.add_argument("--requirements", default="bold, modern, energetic")
    parser.add_argument("--output", default="generated_ad.png")
    args = parser.parse_args()
    plan = render_ad(args.product, args.audience, args.requirements, args.output)
    print(f"Category: {plan.category}\nTagline: {plan.tagline}\nCTA: {plan.cta}")
    print(f"Design-strength score: {plan.confidence}% (heuristic score)")
    print(f"Output: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
