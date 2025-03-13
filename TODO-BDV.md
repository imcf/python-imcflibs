# BDV processing-options-class TODO

/!\ WARNING /!\

When the ***auto-loader*** is used, view enumeration in BigStitcher is based on
*metadata*, for example the first channel in a ligthsheet dataset might then be called
*Channel 488* instead of *Channel 1* or *Channel 0*.

-> It's actually very difficult to forsee this properly, upfront image metadata
inspection would be required to do this!

In case the ***manual loader*** is used, view enumeration follows the file naming
pattern, e.g. the file name for the first tile and first channel would read
`myimage_tile0_channel1`.

-> In that case, tile enumeration starts at **zero** while channel enumeration starts at
**one**!

## Options

### First options block: "*what to process*"

The *first options block* is selecting which parts of the h5/xml dataset will be
processed.

This block is relevant for *most* of our BDV functions:

- `resave_as_h5`
- `flip_axes`
- `phase_correlation_pairwise_shifts_calculation`
- `filter_pairwise_shifts`
- `optimize_and_apply_shifts`
- `detect_interest_points`
- `interest_points_registration`
- `duplicate_transformations`
- `fuse_dataset`

Valid choices are:

- `[All Xs]`
- `[Single X (Select from List)]`
- `[Multiple Xs (Select from List)]`
- `[Range of Xs (Specify by Name)]`

With `X` being one of `angle`, `channel`, `illumination`, `tile`, `timepoint`.

### Second options block: details for "*what to process*"

The *second options block* is **required** for each component having selected anything
other than `All Xs` in the in the first options block.

- For `Single X (Select from List)` the required option is `processing_X=[X n]`, e.g.
  `processing_channel=[channel 1]` for `[Single channel (Select from List)]`.
- For `Multiple Xs (Select from List)` the required options are `X_n X_m`, e.g.
  `channel_1 channel_3` for `[Multiple channels (Select from List)]`.
- For `Range of Xs (Specify by Name)` the required option is `process_following_X=n-m`,
  e.g. `process_following_channels=1-3` for `[Range of channels (Specify by Name)]`.

### Third options block: "*how to treat*"

The *third options block* selects how the components will be processed.

This options block is relevant for *some* of our BDV functions, for example:

- `phase_correlation_pairwise_shifts_calculation`
- `optimize_and_apply_shifts`

Valid choices are:

- `[treat individually]`
- `group`
- `compare`

### Fourth options block: details for "*how to treat*"

The *fourth option block* is ***required*** for each component that has `group` as their
setting in the *third options block*. Exceptions are when e.g. the dataset only has a
single *illumination* (then nothing illumination-related needs to be put into the fourth
block, even if `group` was selected in the third block), or if the first block already
restricted the used data to a single item (for example `Single channel (Select from
List)` was selected in block 1, then nothing channel-related is required in block 4).

Valid choices are:

- `Average Ys`
- `Use Y n`

With `Y` being one of `Angle`, `Channel`, `Illumination`, `Tile`, `Timepoint`. Note the
difference in uppercase / lowercase compared to the `X` from blocks 1 and 2!

## Examples

### Example 1

Selected options:

- First block:
  - Process angle: all angles
  - Process channel: all channels
  - Process illumination: all illuminations
  - Process tile: all tiles
  - Process timepoint: all Timepoints
- Second block:
  - (N/A)
- Third block:
  - How to treat Angles: treat individually
  - How to treat Channels: group
  - How to treat Illuminations: group
  - How to treat Tiles: compare
  - How to treat Timepoints: treat individually
- Fourth block:
  - [use Channel 1]

Resulting macro parameters:

```text
process_angle=[All angles]
process_channel=[All channels]
process_illumination=[All illuminations]
process_tile=[All tiles]
process_timepoint=[All Timepoints]
method=[Phase Correlation]
show_expert_grouping_options
how_to_treat_angles=[treat individually]
how_to_treat_channels=group
how_to_treat_illuminations=group
how_to_treat_tiles=compare
how_to_treat_timepoints=[treat individually]
channels=[use Channel 1]
```

## Example 2

Selected options:

- First block:
  - Process angle: All angles
  - Process channel: Single channel (Select from List)
  - Process illumination: all illuminations
  - Process tile: all tiles
  - Process timepoint: all Timepoints
- Second block:
  - Processing channel: channel 1
- Third block:
  - How to treat Timepoints: treat individually
  - How to treat Channels: group
  - How to treat Illuminations: group
  - How to treat Angles: treat individually
  - How to treat Tiles: group
- Fourth block:
  - [use Tile 3]

```text
process_angle=[All angles]
process_channel=[Single channel (Select from List)]
process_illumination=[All illuminations]
process_tile=[All tiles]
process_timepoint=[All Timepoints]
processing_channel=[channel 1]
method=[Phase Correlation]
show_expert_grouping_options
how_to_treat_timepoints=[treat individually]
how_to_treat_channels=group
how_to_treat_illuminations=group
how_to_treat_angles=[treat individually]
how_to_treat_tiles=group
tiles=[use Tile 3]
```

## Example 3

Selected options:

- First block:
  - Process angle: All angles
  - Process channel: Multiple channels (Select from List)
  - Process illumination: all illuminations
  - Process tile: all tiles
  - Process timepoint: all Timepoints
- Second block:
  - Processing channel: channel_n channel_m etc
- Third block:
  - How to treat Timepoints: treat individually
  - How to treat Channels: group
  - How to treat Illuminations: group
  - How to treat Angles: treat individually
  - How to treat Tiles: compare
- Fourth block:
  - Average Channels

```text
process_angle=[All angles]
process_channel=[Multiple channels (Select from List)]
process_illumination=[All illuminations]
process_tile=[All tiles]
process_timepoint=[All Timepoints]
channel_1
channel_2
method=[Phase Correlation]
show_expert_grouping_options
how_to_treat_timepoints=[treat individually]
how_to_treat_channels=group
how_to_treat_illuminations=group
how_to_treat_angles=[treat individually]
how_to_treat_tiles=compare
channels=[Average Channels]
```

## Example 4

- First block:
  - Process angle: All angles
  - Process channel: Range of channels (Specify by Name)
  - Process illumination: all illuminations
  - Process tile: all tiles
  - Process timepoint: all Timepoints
- Second block:
  - Processing following channels: n-m, e.g. 1-3
- Third block:
  - How to treat Timepoints: treat individually
  - How to treat Channels: group
  - How to treat Illuminations: group
  - How to treat Angles: treat individually
  - How to treat Tiles: compare
- Fourth block:
  - Average Channels

```text
process_angle=[All angles]
process_channel=[Range of channels (Specify by Name)]
process_illumination=[All illuminations]
process_tile=[All tiles]
process_timepoint=[All Timepoints]
process_following_channels=1-3
method=[Phase Correlation]
show_expert_grouping_options
how_to_treat_timepoints=[treat individually]
how_to_treat_channels=group
how_to_treat_illuminations=group
how_to_treat_angles=[treat individually]
how_to_treat_tiles=compare
channels=[Average Channels]
```
