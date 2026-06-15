# Forex Engine Local Data Folder

This folder is for manually exported local candle CSV files used by PAPER_ONLY research.

Required columns:

```text
timestamp,open,high,low,close
```

Optional columns:

```text
volume,symbol,timeframe
```

Rules:

- Do not put credentials here.
- Do not put broker API exports with tokens here.
- Do not add live order files.
- Do not add webhook payloads.
- Do not use this folder for network download automation.
- Keep private or large datasets out of commits unless separately approved.

The Forex Engine loader validates local CSV shape only. It does not download, connect, trade, or route orders.
