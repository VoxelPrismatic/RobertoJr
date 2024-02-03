import argparse
import time
import os

parser = argparse.ArgumentParser()
parser.add_argument("id", type = int, help = "The user ID to generate the card")
parser.add_argument("level", type = int, help = "Current level of the user")
parser.add_argument("xp", type = int, help = "Current XP of the user")
parser.add_argument("rank", type = int, help = "Current rank of the user")
parser.add_argument("name", type = str, help = "Username")
parser.add_argument("elite", type = int, help = "Is the user elite?")
args = parser.parse_args()

ROOT_IMG = os.environ["PWD"]
if "/data/levels/" not in ROOT_IMG:
    ROOT_IMG += "/data/levels/"
try:
    open(f"{ROOT_IMG}saved/{args.id}/{args.level}-{args.xp}-{args.rank}-{args.elite}.webp")
    exit()
except FileNotFoundError:
    pass # File exists

def xp_equation(lvl):
    return 5 * (lvl ** 2) + (50 * lvl) + 100


SPACING = 8

from PIL import Image, ImageDraw, ImageFont
import os

t = time.time()

try:
    for item in os.listdir(f"{ROOT_IMG}pfp/{args.id}"):
        pfp_img = Image.open(f"{ROOT_IMG}pfp/{args.id}/{item}")
        break
except:
    pfp_img = Image.open(f"{ROOT_IMG}pfp/default.webp")

try:
    card_bg = Image.open(f"{ROOT_IMG}bg/{args.id}.webp")
except FileNotFoundError:
    card_bg = Image.open(f"{ROOT_IMG}bg/default.webp")

chip_img = Image.open(f"{ROOT_IMG}chip_24.webp")

print("Time to load images:", time.time() - t)
t = time.time()

COLOR = 0x0E7FAA if args.elite else 0xECB300

def create_border_radius(img, radius):
    width, height = img.size
    alpha_mask = Image.new('L', img.size, "black")
    alpha_draw = ImageDraw.Draw(alpha_mask)
    alpha_draw.rounded_rectangle((0, 0, width, height), radius = radius, fill = 255)
    return alpha_mask

def readable_num(n):
    suffix = ["", "k", "M", "B"]
    while n >= 1000:
        n /= 1000
        suffix.pop(0)
    if n >= 100:
        return f"{int(n)}{suffix[0]}"
    elif n >= 10:
        return f"{round(n, 1)}{suffix[0]}"
    return f"{round(n, 2)}{suffix[0]}"

margin = int((card_bg.height - pfp_img.height) / 2)


ttl_xp = xp_equation(args.level + 1)
card_bg.paste(pfp_img, box = (margin, margin), mask = create_border_radius(pfp_img, 12))

bar_w = card_bg.width - pfp_img.width - margin * 3
bar_h = int(card_bg.height / 8)
progress_bar = Image.new('RGBA', (bar_w, bar_h), "black")
progress_draw = ImageDraw.Draw(progress_bar)
progress_draw.rounded_rectangle((0, 0, int(bar_w * args.xp / ttl_xp), bar_h), fill = COLOR, radius = 8)

bar_left = margin * 2 + pfp_img.width
bar_top = card_bg.height - margin - bar_h
card_bg.paste(progress_bar, box = (bar_left, bar_top), mask = create_border_radius(progress_bar, 8))

print("Time to draw images:", time.time() - t)
t = time.time()

name_font_64px = ImageFont.truetype(ROOT_IMG + "font/BebasNeue-Regular.ttf", 64)
name_font_48px = ImageFont.truetype(ROOT_IMG + "font/BebasNeue-Regular.ttf", 48)
name_font_24px = ImageFont.truetype(ROOT_IMG + "font/BebasNeue-Regular.ttf", 24)

print("Time to load fonts:", time.time() - t)
t = time.time()

card_draw = ImageDraw.Draw(card_bg)

items_right = card_bg.width - margin - 2

### LEFT / TTL XP

total_str = "TOTAL"
total_box = name_font_24px.getbbox(total_str)
item_total_right = items_right - total_box[2]

true_ttl_xp = args.xp + sum(xp_equation(q) for q in range(args.level))

xp_ttl_st = readable_num(true_ttl_xp)
xp_ttl_box = name_font_24px.getbbox(xp_ttl_st)
item_xp_ttl_right = item_total_right - xp_ttl_box[2] - 32
item_total_left = bar_left + xp_ttl_box[2] + 32


xp_sum_st = f" / {readable_num(ttl_xp)} CHIPS"
xp_sum_box = name_font_24px.getbbox(xp_sum_st)
items_right -= xp_sum_box[2]
item_xp_sum_right = items_right


suffix = ["", "K", "M", "B"]
cur_xp = args.xp
while cur_xp >= 1000:
    suffix.pop(0)
    cur_xp /= 1000


xp_cur_st = f"{round(cur_xp, 2)}{suffix[0]}"
xp_cur_box = name_font_24px.getbbox(xp_cur_st)
items_right -= xp_cur_box[2]
item_xp_cur_right = items_right




st = args.name.rsplit("#", 1)[0]
l1 = len(st)

name_box = name_font_64px.getbbox(st)
while name_box[2] > 480:
    st = st[:-1]
    name_box = name_font_64px.getbbox(st + "...")

if len(st) != l1:
    st += "..."
baseline = name_font_64px.getbbox("hello there")[3] - name_box[3]
card_draw.text((bar_left, bar_top - SPACING - name_box[3]), st, fill = 0xFFFFFF, font = name_font_64px)

if "#" in args.name:
    st = "#" + args.name.rsplit("#", 1)[-1]
    discrim_box = name_font_48px.getbbox(st)
    # card_draw.text((bar_left + name_box[2], bar_top - SPACING - discrim_box[3] + baseline), st, fill = 0x888888, font = name_font_48px)

    if name_box[2] + bar_left + discrim_box[2] >= items_right:
        card_draw.text((item_xp_sum_right, card_bg.height - margin), xp_sum_st, fill = 0x888888, font = name_font_24px)
        card_draw.text((item_xp_cur_right, card_bg.height - margin), xp_cur_st, fill = 0xCCCCCC, font = name_font_24px)
        card_draw.text((bar_left, card_bg.height - margin), xp_ttl_st, fill = 0xCCCCCC, font = name_font_24px)
        card_draw.text((item_total_left, card_bg.height - margin), total_str, fill = 0x888888, font = name_font_24px)
        card_bg.paste(chip_img, (item_total_left - 28, card_bg.height - margin + 2), mask = chip_img.getchannel("A"))
    else:
        card_draw.text((item_xp_sum_right, bar_top - SPACING - xp_cur_box[3]), xp_sum_st, fill = 0x888888, font = name_font_24px)
        card_draw.text((item_xp_cur_right, bar_top - SPACING - xp_cur_box[3]), xp_cur_st, fill = 0xCCCCCC, font = name_font_24px)
        card_draw.text((item_xp_ttl_right, card_bg.height - margin), xp_ttl_st, fill = 0xCCCCCC, font = name_font_24px)
        card_draw.text((item_total_right, card_bg.height - margin), total_str, fill = 0x888888, font = name_font_24px)
        card_bg.paste(chip_img, (item_total_right - 28, card_bg.height - margin + 2), mask = chip_img.getchannel("A"))

items_right = card_bg.width - margin - 2

st = str(args.level)
level_num_box = name_font_48px.getbbox(st)
items_right -= level_num_box[2]
card_draw.text((items_right, margin - 12), st, fill = COLOR, font = name_font_48px)

st = "LEVEL"
level_txt_box = name_font_24px.getbbox(st)
baseline = level_num_box[3] - level_txt_box[3]
items_right -= level_txt_box[2] + 4
card_draw.text((items_right, margin + int(baseline / 3) - 12), st, fill = 0x888888, font = name_font_24px)

st = "#" + str(args.rank)
rank_num_box = name_font_48px.getbbox(st)
items_right -= margin + rank_num_box[2]
card_draw.text((items_right, margin - 12), st, fill = 0xCCCCCC, font = name_font_48px)

st = "RANK"
rank_txt_box = name_font_24px.getbbox(st)
baseline = rank_num_box[3] - rank_txt_box[3]
items_right -= rank_txt_box[2] + 4
card_draw.text((items_right, margin + int(baseline / 3) - 12), st, fill = 0x888888, font = name_font_24px)

print("Time to draw text:", time.time() - t)
t = time.time()


if args.elite:
    crown_img = Image.open(f"{ROOT_IMG}crown.webp")
    card_bg.paste(crown_img, (116, 4), mask = crown_img.getchannel("A"))

card_bg.putalpha(create_border_radius(card_bg, 12))
save_dir = f"{ROOT_IMG}saved/{args.id}/"
if not os.path.isdir(save_dir):
    os.mkdir(save_dir)
else:
    for f in os.listdir(save_dir):
        os.remove(save_dir + f)
card_bg.save(save_dir + f"{args.level}-{args.xp}-{args.rank}-{args.elite}.webp", lossless = True)
