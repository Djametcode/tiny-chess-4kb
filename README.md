# Tiny Chess 4 KB

[make.fun entry](https://make.fun/bounty/tiny-chess-01)

This repository contains a deterministic Python chess engine packed into `main.py` for the `tiny-chess-01` competition. The readable implementation is kept as `engine_source.py`; the official kit compressor produces the entrypoint.

## Engine

- Compact 0x88 board representation and legal move generation.
- Material and piece-square evaluation with deterministic Zobrist hashing.
- Iterative deepening with negamax, alpha-beta and principal-variation search.
- Transposition-table bounds and hash-move ordering.
- Capture ordering, killer moves and history scores.
- Null-move pruning, late-move reduction and quiescence search.
- Pawn promotions, castling, en passant, repetition and fifty-move draws.
- Fixed node budget per move and a legal fallback if search is interrupted.
- Python standard library only; no model calls or external packages.

## Runtime

Run with Python 3.13. The competition provides `MAKEFUN_ENV_URL`; the program requests game state, selects a UCI move, submits it through the environment route, and exits when all games are complete.

## Reproducibility and checks

After editing `engine_source.py`, run the kit's `makefun compress engine_source.py --out main.py` as a separate command and commit `main.py`. Bundle the readable source with the agent session. The entry limit is 4,096 bytes and the complete committed snapshot limit is 8,192 bytes.

Move generation passed perft checks:

- Start position: 20, 400, 8,902 nodes at depths 1–3.
- Kiwipete: 48, 2,039, 97,862 nodes at depths 1–3.
