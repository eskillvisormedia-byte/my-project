# Scene list for the ESkillVisor Walmart partnership reel (1:35). Times follow the script at a natural pace.
from engine import Text, Stroke, Pause, Scene, chain, INK, BLUE, YELLOW, GREY, W
import icons as I

CX = W / 2


def hl(text, pad=10, color=YELLOW, alpha=0.5):
    """Yellow highlighter swipe behind a text element."""
    y = text.y - text.size * 0.28
    s = Stroke(I.underline(text.x0 + text.w + pad, text.x0 - pad, y, 3), color, text.size * 0.62, cap='butt', alpha=alpha, speed=1100)
    s.z = -1
    return s


def ul(text, color=BLUE, width=5, off=16):
    return Stroke(I.underline(text.x0 + text.w, text.x0, text.y + off, 5), color, width, speed=1100)


def option_scene(t0, t1, n, l1, l2, amount, icon_items, b1, b2):
    pill = Stroke(I.pill(CX, 255, 125, 44), BLUE, 5, speed=1000)
    lab = Text(f'OPTION {n}', CX, 278, 60, BLUE)
    a = Text(l1, CX, 430, 100)
    b = Text(l2, CX, 535, 100)
    amt = Text(amount, CX, 760, 190, BLUE)
    sub = Text('PARTICIPATION AMOUNT', CX, 850, 54, GREY)
    c1 = Stroke(I.check(150, 1438, 40), BLUE, 8)
    t1_ = Text(b1, 200, 1455, 58, align='left', maxw=820)
    c2 = Stroke(I.check(150, 1548, 40), BLUE, 8)
    t2_ = Text(b2, 200, 1565, 58, align='left', maxw=820)
    return Scene(t0, t1, [pill, lab, a, b, amt, hl(amt, 14), sub] + icon_items + [c1, t1_, c2, t2_])


def build():
    S = []

    # 1. Every business has its own path; the right partner makes it easier.
    a = Text('EVERY BUSINESS', CX, 360, 104)
    b = Text('HAS ITS OWN PATH', CX, 470, 104)
    st = Stroke(I.circle(I.P(), CX - 270, 1165, 14), INK, 7)
    r = Stroke(I.road(CX, 880, 300), INK, 7, speed=800)
    fl = Stroke(I.flag(CX + 135, 715, 150), BLUE, 7)
    c = Text('THE RIGHT PARTNER', CX, 1400, 100, BLUE)
    S.append(Scene(0.0, 7.6, [a, b, st, r, fl, c, ul(c)]))

    # 2. Start your e-commerce journey through an established marketplace.
    a = Text('START YOUR', CX, 340, 100)
    b = Text('E-COMMERCE JOURNEY', CX, 450, 100)
    sto = Stroke(I.store(CX, 860, 210), INK, 7, speed=1000)
    d = Text('ESTABLISHED MARKETPLACE', CX, 1300, 86, BLUE)
    S.append(Scene(7.6, 14.6, [a, b, sto, d, hl(d, 8)]))

    # 3. Walmart Marketplace + right model + experienced team = structured direction.
    a = Text('WALMART', CX - 40, 320, 120, BLUE)
    sp = Stroke(I.spark(a.x0 + a.w + 70, 280, 52), YELLOW, 12)
    b = Text('MARKETPLACE', CX, 440, 120, BLUE)
    f1 = Stroke(I.flowchart(290, 700, 110), INK, 6, speed=850)
    t1 = Text('BUSINESS MODEL', 290, 900, 60, maxw=440)
    plus = Stroke(I.line(I.P(), (CX - 26, 740), (CX + 26, 740)).moveTo(CX, 714).lineTo(CX, 766), BLUE, 8)
    f2 = Stroke(I.people(790, 710, 120, n=2), INK, 6, speed=900)
    t2 = Text('EXPERIENCED TEAM', 790, 900, 60, maxw=440)
    ar = Stroke(I.arrow_down(CX, 1110, 90), BLUE, 7)
    t3 = Text('STRUCTURED DIRECTION', CX, 1350, 86)
    S.append(Scene(14.6, 25.0, [a, b, sp, f1, t1, plus, f2, t2, ar, t3, hl(t3, 8)]))

    # 4. And that's exactly what ESkillVisor does.
    a = Text("THAT'S WHAT", CX, 700, 90)
    e = Text('ESKILLVISOR', CX, 900, 150, BLUE)
    d = Text('DOES', CX, 1040, 96)
    S.append(Scene(25.0, 29.4, [a, e, hl(e, 14), d], gap=0.1))

    # 5. Three partnership models on Walmart Marketplace, for your budget and goals.
    n3 = Text('3', 175, 420, 180, BLUE)
    b = Text('PARTNERSHIP MODELS', CX + 60, 395, 92, maxw=780)
    c = Text('ON WALMART MARKETPLACE', CX, 520, 66, GREY)
    cards = []
    for i, x in enumerate((230, 540, 850)):
        cards.append(Stroke(I.card(x, 760, 105, 115), INK, 6, speed=1200))
        cards.append(Text(str(i + 1), x, 805, 130, BLUE))
    w = Stroke(I.wallet(330, 1170, 95), INK, 7, speed=900)
    tw = Text('BUDGET', 330, 1370, 74)
    tg = Stroke(I.target(750, 1170, 95), INK, 7, speed=1000)
    tt = Text('GOALS', 750, 1370, 74)
    S.append(Scene(29.4, 40.8, [n3, b, c] + cards + [w, tw, tg, tt]))

    # 6-8. The three options
    S.append(option_scene(40.8, 54.2, 1, 'INVENTORY', 'PARTNERSHIP', '$5,000',
                          [Stroke(I.boxes(CX, 1110, 150), INK, 7, speed=900)],
                          'INVENTORY-BASED E-COMMERCE', 'TEAM SUPPORT'))
    S.append(option_scene(54.2, 67.6, 2, 'WALMART', 'WHOLESALE', '$30,000',
                          [Stroke(I.warehouse(CX, 1130, 170), INK, 7, speed=900)],
                          'STRUCTURED OPERATIONS', 'EXPERIENCED TEAM'))
    S.append(option_scene(67.6, 80.3, 3, 'WALMART', 'BRAND PARTNERS', '$100,000',
                          [Stroke(I.tag(380, 1120, 140), INK, 7), Stroke(I.star(330, 1120, 34), YELLOW, 7),
                           Stroke(I.growth(760, 1120, 130), INK, 7)],
                          'BUILD BRANDS', 'FOCUS ON GROWTH'))

    # 9. Now you have options, and the chance to choose your next step.
    a = Text('NOW YOU HAVE', CX, 380, 100)
    b = Text('OPTIONS', CX, 510, 140, BLUE)
    stp = Stroke(I.stairs(CX - 20, 950, 200), INK, 7, speed=900)
    fl = Stroke(I.flag(CX + 150, 790, 120), BLUE, 7)
    c = Text('CHOOSE YOUR NEXT STEP', CX, 1340, 88)
    S.append(Scene(80.3, 86.4, [a, b, stp, fl, c, ul(c)], gap=0.12))

    # 10. Discuss your requirements; contact ESkillVisor today; www.eskillvisor.com
    a = Text('DISCUSS YOUR', CX, 400, 96)
    b = Text('REQUIREMENTS', CX, 510, 96)
    c = Text('CONTACT ESKILLVISOR TODAY', CX, 760, 80)
    br = Stroke(I.browser(CX, 1080, 440, 120), INK, 6, speed=1700)
    url = Text('www.eskillvisor.com', CX, 1155, 104, BLUE, caps=False, maxw=820)
    cu = Stroke(I.cursor(CX + 330, 1165, 80), INK, 6)
    S.append(Scene(86.4, 95.0, [a, b, c, br, url, hl(url, 10), cu], gap=0.12, fade=False, final=True))
    return chain(S)
