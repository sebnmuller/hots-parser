# hots-parser
A Heroes of the Storm replays files parser

## How to run it:

```
python main.py </path/to/replay.StormReplay>
```

You should see a sample output like this one:
```
=== MAP: Sky Temple ===
Duration: 1151 secs (18423 gl)
[Human] Hero: Lunara (0)
	Regen Globes taken: 13
[Human] Hero: Sonya (1)
	Regen Globes taken: 12
[Human] Hero: Tyrande (2)
	Regen Globes taken: 3
[Human] Hero: Azmodan (3)
	Regen Globes taken: 12
[Human] Hero: Greymane (4)
	Regen Globes taken: 10
[Human] Hero: Li Li (5)
	Regen Globes taken: 8
[Human] Hero: The Butcher (6)
	Regen Globes taken: 14
[Human] Hero: Jaina (7)
	Regen Globes taken: 6
[Human] Hero: Diablo (8)
	Regen Globes taken: 13
[Human] Hero: Greymane (9)
	Regen Globes taken: 14
Team 0 missed 71 regen globes
Team 1 missed 53 regen globes
Team 0 controlled temples 35.0 percent of the time (134 seconds)
	 North Tower: 14.0 percent (19 seconds)
	 Center Tower: 67.0 percent (97 seconds)
	 South Tower: 19.0 percent (18 seconds)
Team 1 controlled temples 65.0 percent of the time (245 seconds)
	 North Tower: 86.0 percent (121 seconds)
	 Center Tower: 33.0 percent (47 seconds)
	 South Tower: 81.0 percent (77 seconds)
```
This is just a small sample of what is being calculated, check `models/__init__.py` for a comprehensive list of metrics being calculated

## How to help
There are several ways you can help:
* Help with the [current open issues] (https://github.com/crorella/hots-parser/issues)
* Help [giving more ideas] (https://github.com/crorella/hots-parser/issues/5) on what to track and how to track it.


## Metrics currently tracked

Please refer to `tracked_metrics.md` to see what metrics are being tracked right now
