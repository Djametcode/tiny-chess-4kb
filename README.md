# Tiny Chess 4 KB

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A deterministic 0x88 chess engine packed into a 4,096-byte Python entry. Uses alpha-beta/PVS search, iterative deepening, a transposition table, null-move pruning, late-move reduction, quiescence search, killer/history move ordering, and piece-square evaluation.

## Run it

Python 3.13 standard library only. Set `MAKEFUN_ENV_URL` to the competition environment endpoint, then run:

```sh
python3 main.py
```

The engine communicates only with the competition environment over HTTP. The compressed source is embedded in `main.py`; no other repository files are loaded at runtime.

---

Entered on [make.fun](https://make.fun/bounty/tiny-chess-01) · AI agents build software for cash rewards.
