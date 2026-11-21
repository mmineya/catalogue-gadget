import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


S = 2
W = H = 1024
SW = SH = W * S


def font(size: int, bold: bool = False):
    name = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(name, size * S)


def rounded(draw, box, radius, fill, outline=None, width=1):
    box = tuple(int(v * S) for v in box)
    draw.rounded_rectangle(box, radius=radius * S, fill=fill, outline=outline, width=max(1, width * S))


def path_points(points, width):
    """Return a filled ribbon around a centerline."""
    out = []
    for i, (x, y) in enumerate(points):
        if i == 0:
            dx, dy = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n * width / 2, dx / n * width / 2
        out.append((int((x + nx) * S), int((y + ny) * S)))
    for i in range(len(points) - 1, -1, -1):
        x, y = points[i]
        if i == 0:
            dx, dy = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n * width / 2, dx / n * width / 2
        out.append((int((x - nx) * S), int((y - ny) * S)))
    return out


def add_shadow(base, box, blur=28, alpha=100):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(tuple(int(v * S) for v in box), fill=(35, 40, 42, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur * S))
    base.alpha_composite(layer)


def render():
    im = Image.new("RGBA", (SW, SH))
    px = im.load()
    # Smooth neutral studio sweep, with a restrained vignette.
    for y in range(SH):
        yy = y / (SH - 1)
        for x in range(SW):
            xx = x / (SW - 1)
            horizon = max(0.0, (yy - 0.55) / 0.45)
            r = int(238 - 20 * horizon + 4 * (1 - yy))
            g = int(240 - 21 * horizon + 3 * (1 - yy))
            b = int(239 - 20 * horizon + 3 * (1 - yy))
            vignette = max(0.0, math.hypot(xx - .5, yy - .46) - .27) * 13
            px[x, y] = (max(0, int(r - vignette)), max(0, int(g - vignette)), max(0, int(b - vignette)), 255)

    add_shadow(im, (184, 620, 850, 790), blur=32, alpha=95)
    add_shadow(im, (744, 658, 973, 731), blur=18, alpha=70)
    d = ImageDraw.Draw(im)

    # Main brushed aluminium body.
    rounded(d, (190, 430, 842, 690), 30, (146, 153, 157, 255), outline=(86, 92, 96, 255), width=2)
    rounded(d, (197, 437, 835, 683), 25, (181, 187, 189, 255), outline=(225, 228, 228, 210), width=2)
    # Glossy top plane and lower edge.
    rounded(d, (205, 445, 827, 510), 20, (217, 222, 222, 170))
    d.line([(224 * S, 472 * S), (810 * S, 472 * S)], fill=(246, 247, 246, 130), width=2 * S)
    d.line([(221 * S, 658 * S), (812 * S, 658 * S)], fill=(105, 112, 115, 115), width=2 * S)

    # Slot mouths, recessed black with metallic lips.
    rounded(d, (165, 501, 270, 616), 28, (51, 56, 58, 255), outline=(101, 108, 111, 255), width=4)
    rounded(d, (762, 501, 867, 616), 28, (52, 57, 59, 255), outline=(101, 108, 111, 255), width=4)
    rounded(d, (176, 513, 258, 604), 21, (20, 24, 25, 255))
    rounded(d, (774, 513, 856, 604), 21, (20, 24, 25, 255))

    # Control panel.
    rounded(d, (548, 526, 738, 650), 12, (125, 133, 136, 255), outline=(79, 86, 89, 255), width=2)
    rounded(d, (561, 539, 725, 638), 8, (178, 184, 184, 255), outline=(220, 222, 221, 180), width=1)
    d.text((577 * S, 548 * S), "STRAIGHT & CO.", font=font(11, True), fill=(48, 54, 56, 255))
    d.ellipse((583 * S, 580 * S, 600 * S, 597 * S), fill=(72, 205, 112, 255), outline=(226, 255, 225, 255), width=2 * S)
    d.ellipse((586 * S, 582 * S, 592 * S, 588 * S), fill=(220, 255, 225, 210))
    # Dial with ticks.
    d.ellipse((649 * S, 571 * S, 712 * S, 634 * S), fill=(83, 90, 93, 255), outline=(49, 55, 58, 255), width=2 * S)
    d.ellipse((657 * S, 579 * S, 704 * S, 626 * S), fill=(151, 158, 159, 255), outline=(205, 208, 208, 180), width=1 * S)
    for a in range(-130, 131, 52):
        rad = math.radians(a)
        x1, y1 = 680.5 + math.cos(rad) * 18, 602.5 + math.sin(rad) * 18
        x2, y2 = 680.5 + math.cos(rad) * 22, 602.5 + math.sin(rad) * 22
        d.line((int(x1 * S), int(y1 * S), int(x2 * S), int(y2 * S)), fill=(46, 52, 54, 255), width=2 * S)
    d.line((681 * S, 603 * S, 694 * S, 589 * S), fill=(44, 49, 51, 255), width=3 * S)

    # Curved input banana, visibly disappearing into the left slot.
    curved = [(208, 566), (195, 555), (182, 531), (177, 504), (185, 477), (207, 459), (233, 454)]
    d.polygon(path_points(curved, 43), fill=(231, 188, 48, 255), outline=(158, 117, 25, 255))
    d.line([(198 * S, 568 * S), (183 * S, 534 * S), (182 * S, 500 * S), (195 * S, 474 * S)], fill=(255, 224, 93, 230), width=7 * S)
    d.ellipse((216 * S, 438 * S, 245 * S, 468 * S), fill=(183, 132, 28, 255))

    # Straight output banana sitting just beyond the right slot.
    straight = [(814, 560), (846, 559), (879, 559), (912, 558), (944, 557)]
    d.polygon(path_points(straight, 43), fill=(235, 193, 53, 255), outline=(156, 113, 22, 255))
    d.line([(815 * S, 550 * S), (943 * S, 548 * S)], fill=(255, 226, 101, 230), width=7 * S)
    d.ellipse((940 * S, 539 * S, 967 * S, 565 * S), fill=(181, 128, 26, 255))

    # Open peel accessory near the machine.
    peel = [(759, 748), (785, 714), (805, 692), (814, 703), (797, 735), (783, 763)]
    d.polygon([(int(x * S), int(y * S)) for x, y in peel], fill=(235, 194, 54, 255), outline=(162, 118, 25, 255))
    d.polygon([(790 * S, 745 * S), (821 * S, 708 * S), (836 * S, 718 * S), (809 * S, 759 * S)], fill=(246, 205, 60, 255), outline=(160, 116, 23, 255))
    d.polygon([(772 * S, 752 * S), (748 * S, 719 * S), (758 * S, 705 * S), (789 * S, 741 * S)], fill=(224, 182, 44, 255), outline=(154, 112, 22, 255))
    d.ellipse((802 * S, 680 * S, 820 * S, 706 * S), fill=(124, 91, 24, 255))

    # Fine contact highlights keep the object photographic.
    d.line([(220 * S, 445 * S), (796 * S, 445 * S)], fill=(255, 255, 255, 95), width=2 * S)
    d.line([(235 * S, 678 * S), (798 * S, 678 * S)], fill=(255, 255, 255, 85), width=2 * S)

    im = im.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    return im


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"
    render().save(out, format="PNG", optimize=True, compress_level=9)
    print(out)


if __name__ == "__main__":
    main()
