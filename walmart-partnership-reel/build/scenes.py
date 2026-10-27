# Scene list for the ESkillVisor Walmart partnership reel (1:35). Times follow the script at a natural pace.
from engine import Text, Stroke, Pause, Scene, chain, INK, BLUE, YELLOW, GREY, W
import icons as I
import logo as L

CX = W / 2


def at(el, t):
    """Don't start drawing `el` before t seconds (when the voiceover says it)."""
    el.at = t
    return el


def hl(text, pad=10, color=YELLOW, alpha=0.5):
    """Yellow highlighter swipe behind a text element."""
    y = text.y - text.size * 0.28
    s = Stroke(I.underline(text.x0 + text.w + pad, text.x0 - pad, y, 3), color, text.size * 0.62, cap='butt', alpha=alpha, speed=1100)
    s.z = -1
    return s


def ul(text, color=BLUE, width=5, off=16):
    return Stroke(I.underline(text.x0 + text.w, text.x0, text.y + off, 5), color, width, speed=1100)


def option_scene(t0, t1, n, l1, l2, amount, icon_items, b1, b2, cue, icon_first, post=()):
    pill = Stroke(I.pill(CX, 255, 125, 44), BLUE, 5, speed=1000)
    lab = Text(f'OPTION {n}', CX, 290, 72, BLUE)
    a = Text(l1, CX, 430, 100)
    b = Text(l2, CX, 535, 100)
    amt = Text(amount, CX, 760, 190, BLUE)
    sub = Text('PARTICIPATION AMOUNT', CX, 850, 54, GREY)
    c1 = Stroke(I.check(150, 1438, 40), BLUE, 8)
    t1_ = Text(b1, 200, 1455, 58, align='left', maxw=820)
    c2 = Stroke(I.check(150, 1548, 40), BLUE, 8)
    t2_ = Text(b2, 200, 1565, 58, align='left', maxw=820)
    at(a, cue[0]); at(amt, cue[1]); at(c1, cue[2]); at(c2, cue[3])
    money = [amt, hl(amt, 14), sub]
    body = icon_items + money if icon_first else money + icon_items
    return Scene(t0, t1, [lab, a, b] + body + [c1, t1_, c2, t2_] + list(post))


def build():
    S = []

    # 1-2. Every business has its own path; the right partner makes it easier.
    #      Start your e-commerce journey through an established marketplace.
    a = Text('EVERY BUSINESS', CX, 280, 96)
    b = Text('HAS ITS OWN PATH', CX, 385, 96)
    r = Stroke(I.road(CX, 660, 190), INK, 7, speed=850)
    fl = Stroke(I.flag(CX + 86, 555, 100), BLUE, 7)
    c = Text('THE RIGHT PARTNER', CX, 940, 90, BLUE)
    sto = Stroke(I.store(CX, 1190, 150), INK, 7, speed=1000)
    d = Text('ESTABLISHED MARKETPLACE', CX, 1450, 80)
    S.append(Scene(0.0, 10.4, [at(a, 0.4), b, r, fl, c, sto, at(d, 7.6), hl(d, 8)]))

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
    S.append(Scene(10.4, 20.9, [a, b, sp, f1, t1, plus, f2, t2, ar, t3, hl(t3, 8)]))

    # 4-5. "That's what ESkillVisor does": three partnership models on Walmart Marketplace, for your budget and goals.
    lg = L.mark(CX, 190, 2.2) + L.wordmark(CX, 500, 104)
    n3 = Text('3', 175, 840, 170, BLUE)
    b = Text('PARTNERSHIP MODELS', CX + 60, 815, 90, maxw=780)
    c = Text('ON WALMART MARKETPLACE', CX, 650, 66, GREY)
    at(c, 25.6); at(n3, 28.6)
    w = Stroke(I.wallet(330, 1140, 105), INK, 7, speed=900)
    tw = Text('BUDGET', 330, 1360, 80)
    tg = Stroke(I.target(750, 1140, 105), INK, 7, speed=1000)
    tt = Text('GOALS', 750, 1360, 80)
    S.append(Scene(20.9, 35.4, [at(lg[0], 20.9)] + lg[1:] + [c, n3, b, at(w, 31.4), tw, tg, tt]))

    # 6-8. The three options
    S.append(option_scene(35.4, 50.3, 1, 'INVENTORY', 'PARTNERSHIP', '$5,000',
                          [Stroke(I.boxes(CX, 1110, 150), INK, 7, speed=1150)],
                          'INVENTORY-BASED E-COMMERCE', 'TEAM SUPPORT', (36.7, 39.9, 42.6, 46.5), True))
    S.append(option_scene(50.3, 65.5, 2, 'WALMART', 'WHOLESALE', '$30,000',
                          [Stroke(I.warehouse(CX, 1130, 170), INK, 7, speed=900)],
                          'STRUCTURED OPERATIONS', 'EXPERIENCED TEAM', (51.7, 53.4, 60.7, 62.5), False))
    S.append(option_scene(65.5, 77.8, 3, 'WALMART', 'BRAND PARTNERS', '$100,000',
                          [Stroke(I.tag(CX, 1110, 140), INK, 7)],
                          'BUILD BRANDS', 'FOCUS ON GROWTH', (67.3, 70.6, 74.0, 75.6), True,
                          post=[Stroke(I.growth(830, 1495, 85), BLUE, 7)]))

    # 9. Now you have options, and the chance to choose your next step.
    b = Text('YOUR OPTIONS', CX, 450, 130, BLUE)
    stp = Stroke(I.stairs(CX - 20, 950, 200), INK, 7, speed=900)
    fl = Stroke(I.flag(CX + 150, 790, 120), BLUE, 7)
    c = Text('CHOOSE YOUR NEXT STEP', CX, 1340, 88)
    S.append(Scene(77.8, 82.1, [at(b, 78.3), stp, at(c, 80.6)], gap=0.12))

    # 10. Discuss your requirements; contact ESkillVisor today; www.eskillvisor.com
    a = Text('DISCUSS YOUR', CX, 400, 96)
    b = Text('REQUIREMENTS', CX, 510, 96)
    lg = L.mark(CX, 650, 1.5) + L.wordmark(CX, 930, 84)
    br = Stroke(I.browser(CX, 1170, 440, 120), INK, 6, speed=1700)
    url = Text('www.eskillvisor.com', CX, 1245, 104, BLUE, caps=False, maxw=820)
    cu = Stroke(I.cursor(CX + 330, 1255, 80), INK, 6)
    S.append(Scene(82.1, 95.0, [a, b, at(lg[0], 84.1)] + lg[1:] + [at(url, 87.2), hl(url, 10), br, cu], gap=0.12, fade=False, final=True))
    return chain(S)
