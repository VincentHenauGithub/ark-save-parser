# Drop your ARK save in this folder

Place your save here, either layout works — the first `.ark` found recursively
is used:

```
test_save/Ragnarok_WP/Ragnarok_WP.ark      <- the whole save folder
test_save/Ragnarok_WP.ark                  <- just the .ark file
```

Then run the testbench from the `testbench/` directory:

```bash
cd testbench
pytest
```

Everything in this folder (except this file) is gitignored, so your save is
never committed.
