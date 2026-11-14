import json, os
from urllib.request import urlopen, Request

ENV = os.environ["MAKEFUN_ENV_URL"]
VAL = (0, 100, 320, 330, 500, 900, 0)
NOFF = (33, 31, 18, 14, -33, -31, -18, -14)
KOFF = (1, 17, 16, 15, -1, -17, -16, -15)
DOFF = (17, 15, -17, -15)
ROFF = (16, 1, -16, -1)
SQS = [i for i in range(128) if not i & 136]
FILES = "abcdefgh"
MATE = 32000

# Piece-square tables: material and position, from White's point of view.
TAB = [[0] * 128 for _ in range(13)]
for s in SQS:
    f, r = s & 7, s >> 4
    c = min(f, 7 - f) + min(r, 7 - r)
    TAB[1][s] = 100 + (r - 1) * 6 + (12 if f in (3, 4) else 0) + (50 if r == 6 else 0)
    TAB[2][s] = 338 - 3 * c
    TAB[3][s] = 342 - 2 * c
    TAB[4][s] = 506 - c
    TAB[5][s] = 904 - c
    TAB[6][s] = (24 if r == 0 else -22) + (18 if f in (2, 6) else 0)
for s in SQS:
    for p in 1, 2, 3, 4, 5, 6:
        TAB[-p][s] = -TAB[p][s ^ 112]

# Deterministic Zobrist position hashing.
_r = 0x2F0A31B7

def _rnd():
    global _r
    _r = (_r * 1103515245 + 12345) & 0x7FFFFFFF
    return (_r << 33) ^ (_r * 2654435761 & 0xFFFFFFFFFFFF)

Z = [[_rnd() for _ in range(128)] for _ in range(13)]
ZS, ZC, ZE = _rnd(), [_rnd() for _ in range(16)], [_rnd() for _ in range(128)]
B, W, EP, C, MAT, H, HM = [0] * 128, 1, -1, 0, 0, 0, 0

def parse(fen):
    global B, W, EP, C, MAT, H, HM
    a, B = fen.split(), [0] * 128
    r, f = 7, 0
    for ch in a[0]:
        if ch == "/": r, f = r - 1, 0
        elif ch.isdigit(): f += int(ch)
        else:
            v = "pnbrqk".index(ch.lower()) + 1
            B[r * 16 + f] = v if ch.isupper() else -v
            f += 1
    W = 1 if a[1] == "w" else -1
    C = sum(v for ch, v in (("K", 1), ("Q", 2), ("k", 4), ("q", 8)) if ch in a[2])
    EP = -1 if a[3] == "-" else (int(a[3][1]) - 1) * 16 + FILES.index(a[3][0])
    HM, MAT, H = int(a[4]) if len(a) > 4 else 0, 0, 0
    for s in SQS:
        x = B[s]
        if x: MAT, H = MAT + TAB[x][s], H ^ Z[x][s]
    H ^= ZC[C] ^ (ZS if W < 0 else 0) ^ (ZE[EP] if EP >= 0 else 0)

def attacked(s, by):
    b = B
    for o in (-15, -17):
        u = s + o * by
        if not u & 136 and b[u] == by: return 1
    for o in NOFF:
        u = s + o
        if not u & 136 and b[u] == 2 * by: return 1
    for o in KOFF:
        u = s + o
        if not u & 136 and b[u] == 6 * by: return 1
    for ds, pc in ((DOFF, 3), (ROFF, 4)):
        for o in ds:
            u = s
            while 1:
                u += o
                if u & 136: break
                x = b[u]
                if x:
                    if x == pc * by or x == 5 * by: return 1
                    break
    return 0

def moves(w, ep, c):
    b, out = B, []
    ap = out.append
    for s in SQS:
        x = b[s]
        if not x or (x > 0) != (w > 0): continue
        a, o = abs(x), x > 0
        if a == 1:
            d, t = (16 if o else -16), s + (16 if o else -16)
            if not t & 136 and not b[t]:
                if t >> 4 in (0, 7):
                    for z in (5, 4, 3, 2): ap((s, t, z))
                else:
                    ap((s, t, 0))
                    if s >> 4 == (1 if o else 6) and not b[s + 2 * d]: ap((s, s + 2 * d, 0))
            for t in (s + d - 1, s + d + 1):
                if t & 136: continue
                z = b[t]
                if z and (z > 0) != o:
                    if t >> 4 in (0, 7):
                        for p in (5, 4, 3, 2): ap((s, t, p))
                    else: ap((s, t, 0))
                elif t == ep: ap((s, t, 0))
        elif a < 3 or a == 6:
            for d in (NOFF if a == 2 else KOFF):
                t = s + d
                if not t & 136 and (not b[t] or (b[t] > 0) != o): ap((s, t, 0))
            if a == 6:
                if o and s == 4:
                    if c & 1 and b[7] == 4 and not b[5] and not b[6] and not attacked(4, -1) and not attacked(5, -1) and not attacked(6, -1): ap((4, 6, 0))
                    if c & 2 and b[0] == 4 and not b[3] and not b[2] and not b[1] and not attacked(4, -1) and not attacked(3, -1) and not attacked(2, -1): ap((4, 2, 0))
                elif not o and s == 116:
                    if c & 4 and b[119] == -4 and not b[117] and not b[118] and not attacked(116, 1) and not attacked(117, 1) and not attacked(118, 1): ap((116, 118, 0))
                    if c & 8 and b[112] == -4 and not b[115] and not b[114] and not b[113] and not attacked(116, 1) and not attacked(115, 1) and not attacked(114, 1): ap((116, 114, 0))
        else:
            ds = (DOFF if a == 3 else ROFF) if a < 5 else DOFF + ROFF
            for d in ds:
                t = s
                while 1:
                    t += d
                    if t & 136: break
                    if not b[t]: ap((s, t, 0))
                    else:
                        if (b[t] > 0) != o: ap((s, t, 0))
                        break
    return out

def play(m):
    global W, EP, C, MAT, H, HM
    b, (s, t, z) = B, m
    x, y, a = b[s], b[t], abs(b[s])
    u = [x, y, EP, C, s, t, -1, 0, 0, MAT, H, HM]
    h = H ^ ZS ^ (ZE[EP] if EP >= 0 else 0)
    if a == 1 and (s & 7) != (t & 7) and not y and t == EP:
        p = t - 16 * W
        h ^= Z[-W][p]
        b[p], u[6], MAT = 0, p, MAT + TAB[-W][p]
    h ^= Z[x][s]
    if y: h ^= Z[y][t]; MAT -= TAB[y][t]
    if z:
        x2 = z * W
        b[t], h, MAT = x2, h ^ Z[x2][t], MAT + TAB[x2][t] - TAB[x][s]
    else:
        b[t], h, MAT = x, h ^ Z[x][t], MAT + TAB[x][t] - TAB[x][s]
    b[s] = 0
    if a == 6 and abs(t - s) == 2:
        r0, r1 = (s + 3, s + 1) if t > s else (s - 4, s - 1)
        rp = b[r0]
        b[r1], b[r0] = rp, 0
        h ^= Z[rp][r0] ^ Z[rp][r1]
        MAT += TAB[rp][r1] - TAB[rp][r0]
        u[7], u[8] = r0, r1
    if C:
        c0 = C
        for sq, keep in ((0, 13), (7, 14), (112, 7), (119, 11)):
            if s == sq or t == sq: C &= keep
        if a == 6: C &= 12 if W > 0 else 3
        if C != c0: h ^= ZC[c0] ^ ZC[C]
    if a == 1 and abs(t - s) == 32: EP = (s + t) >> 1; h ^= ZE[EP]
    else: EP = -1
    HM, H, W = (0 if a == 1 or y or u[6] >= 0 else HM + 1), h, -W
    return u

def mk(m, k):
    u = play(m)
    if attacked(m[1] if abs(u[0]) == 6 else k, W): undo(u); return None
    return u

def undo(u):
    global W, EP, C, MAT, H, HM
    b = B
    x, y, ep, c, s, t, epc, r0, r1, m0, h0, hm0 = u
    W, EP, C = -W, ep, c
    if r1: b[r0], b[r1] = b[r1], 0
    b[s], b[t] = x, y
    if epc >= 0: b[epc] = -W
    MAT, H, HM = m0, h0, hm0

Cut = IndexError
NODES, LIM, HISTORY, TT = [0], [0], [], {}
KIL, HIST = [[None, None] for _ in range(64)], {}

def rep():
    n, stop = len(HISTORY), max(0, len(HISTORY) - 1 - HM)
    for i in range(n - 3, stop - 1, -2):
        if HISTORY[i] == H: return 1
    return 0

def qsearch(alpha, beta, ply):
    NODES[0] += 1
    if NODES[0] > LIM[0]: raise Cut
    w, k = W, B.index(W * 6)
    chk, best = attacked(k, -W), -MATE
    if not chk:
        st = MAT * w
        if st >= beta: return st
        if st > alpha: alpha = st
        best = st
    cap = []
    for m in moves(w, EP, C):
        y = B[m[1]]
        if y: cap.append((VAL[abs(y)] * 8 - VAL[abs(B[m[0]])], m))
        elif m[2]: cap.append((m[2] * 10, m))
        elif chk: cap.append((0, m))
    if not cap: return -MATE + ply if chk else best
    cap.sort(reverse=True)
    n = 0
    for _, m in cap:
        u = mk(m, k)
        if not u: continue
        n += 1
        v = -qsearch(-beta, -alpha, ply + 1)
        undo(u)
        if v > best:
            best = v
            if v > alpha:
                alpha = v
                if alpha >= beta: return alpha
    return -MATE + ply if chk and not n else best

def nullmove(depth, beta, ply):
    global W, EP, H, HM
    sw, se, sh, sm = W, EP, H, HM
    W, H = -W, H ^ ZS
    if EP >= 0: H ^= ZE[EP]
    EP, HM = -1, HM + 1
    HISTORY.append(H)
    try: return -search(depth - 3, -beta, -beta + 1, ply + 1, 0)
    finally:
        HISTORY.pop()
        W, EP, H, HM = sw, se, sh, sm

def search(depth, alpha, beta, ply, nullok):
    NODES[0] += 1
    if NODES[0] > LIM[0]: raise Cut
    if ply and (HM >= 100 or rep()): return 0
    if depth < 1: return qsearch(alpha, beta, ply)
    w, k = W, B.index(W * 6)
    chk = attacked(k, -w)
    if chk: depth += 1
    a0, key = alpha, H
    ent = TT.get(key)
    tt = ent and ent[3]
    if ent and ent[0] >= depth:
        if ent[1] == 1 or ent[1] == 2 and ent[2] >= beta or ent[1] == 3 and ent[2] <= alpha: return ent[2]
    if nullok and not chk and depth > 2 and MAT * w > 300:
        if nullmove(depth, beta, ply) >= beta: return beta
    kil = KIL[ply] if ply < 64 else [None, None]
    sc = []
    for m in moves(w, EP, C):
        y = B[m[1]]
        t = 1000000 if m == tt else 100000 + VAL[abs(y)] * 8 - VAL[abs(B[m[0]])] if y else 90000 + m[2] * 10 if m[2] else 80000 if kil[0] == m else 70000 if kil[1] == m else HIST.get(m, 0)
        sc.append((t, m))
    sc.sort(reverse=True)
    bs, bm, n = -MATE, None, 0
    for _, m in sc:
        u = mk(m, k)
        if not u: continue
        n += 1
        quiet = not u[1] and not m[2]
        r = 1 if n > 3 and depth > 3 and quiet and not chk else 0
        HISTORY.append(H)
        if n == 1: v = -search(depth - 1, -beta, -alpha, ply + 1, 1)
        else:
            v = -search(depth - 1 - r, -alpha - 1, -alpha, ply + 1, 1)
            if alpha < v < beta: v = -search(depth - 1, -beta, -alpha, ply + 1, 1)
        HISTORY.pop()
        undo(u)
        if v > bs:
            bs, bm = v, m
            if v > alpha:
                alpha = v
                if alpha >= beta:
                    if quiet:
                        if kil[0] != m: kil[1], kil[0] = kil[0], m
                        HIST[m] = HIST.get(m, 0) + depth * depth
                    break
    if not n: return -MATE + ply if chk else 0
    fl = 1 if bs <= a0 else 2 if bs >= beta else 3
    if not ent or ent[0] <= depth: TT[key] = (depth, fl, bs, bm)
    return bs

def root(d, pv):
    k, w, sc = B.index(W * 6), W, []
    for m in moves(w, EP, C):
        y = B[m[1]]
        t = 1000000 if m == pv else 100000 + VAL[abs(y)] * 8 if y else m[2] * 100
        sc.append((t, m))
    sc.sort(reverse=True)
    al, best = -MATE - 1, None
    for _, m in sc:
        u = mk(m, k)
        if not u: continue
        HISTORY.append(H)
        v = -search(d - 1, -MATE - 1, -al, 1, 1)
        HISTORY.pop()
        undo(u)
        if best is None or v > al: al, best = v, m
    return best

def best_move(fen, budget=200000):
    global KIL, HIST, TT, HISTORY
    parse(fen)
    NODES[0], LIM[0], TT = 0, budget, {}
    KIL, HIST, HISTORY = [[None, None] for _ in range(64)], {}, [H]
    pv = out = None
    for d in range(1, 12):
        try: m = root(d, pv)
        except Cut: break
        if m: pv = out = m
        if NODES[0] > budget: break
    if out is None:
        k = B.index(W * 6)
        for m in moves(W, EP, C):
            u = mk(m, k)
            if u: undo(u); return m
    return out

def to_uci(m):
    s, t, z = m
    return FILES[s & 7] + str((s >> 4) + 1) + FILES[t & 7] + str((t >> 4) + 1) + ("pnbrq"[z - 1] if z else "")

def post(path, body):
    return json.load(urlopen(Request(ENV + path, json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=60))

while True:
    g = post("/game", {})
    if g["status"] == "done": break
    while g["status"] == "your_move":
        m = best_move(g["fen"])
        g = post("/move", {"game": g["game"], "move": to_uci(m)})
