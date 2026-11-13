# tiny-chess engine

A compact chess engine in a single Python file: 0x88 board, negamax with
alpha-beta, transposition table, quiescence search, and a fixed 40,000-node
budget per move (deterministic: no clock, no randomness).

It plays the make.fun tiny-chess-01 gauntlet through the env HTTP API.

MIT license, see LICENSE.
