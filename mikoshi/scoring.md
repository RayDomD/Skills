# Scoring

Applies to a decision. Every number comes from the seats' cards; the Chair computes. Use the last round that ran.

## Weights

Set before Round 1, one per seat, with a one-line reason. A pricing call leans on the pricing seat.

| Weight | Meaning |
|---|---|
| 3 | The decision lives in this seat's pillar |
| 2 | The pillar is materially affected |
| 1 | The pillar is touched at the edges |

One or two seats get a 3. With two seats, give both the weight the user states, or equal weights.

## Option scores

Each card scores every option 0 to 10. For each option:

`option score = sum(weight x seat's score) / sum(weight)`, to one decimal.

The **recommended option** is the highest, unless an override removes it. Show each option's math on one line: `B (3x6 + 2x7 + 2x8) / 7 = 6.9`.

## Verdict bands, on the recommended option's score

| Option score | Verdict |
|---|---|
| 7.5 to 10 | GO |
| 6.0 to 7.4 | GO WITH CONDITIONS |
| 4.5 to 5.9 | RESHAPE |
| below 4.5 | DON'T DO IT |

Two labels replace the band when they fit better, and the report says why:

- **WAIT**: the option is good but rests on a prerequisite that is unmet (a test result, cash, a hire). Name the trigger and date that turn it into GO, and what happens if the trigger fails.
- **DON'T DO IT** also applies when "keep doing what you do now" is the top-scoring option.

## Overrides, applied after the band and stated in the report

1. **Ruin cap.** A seat ending at `RUIN RISK: likely` on the recommended option caps the verdict at RESHAPE until the resolution names a mitigation that seat endorsed. One seat at ruin risk outweighs every enthusiastic seat.
2. **One-way door cap.** When a majority of seats call the recommended option a one-way door and the spread on it is 4 or more, cap at GO WITH CONDITIONS and make the cheapest test a precondition.
3. **Unanimity check.** When every seat's top option matches and their scores for it sit within 1 point in Round 1, the Chair names the strongest unargued alternative as a crux for Round 2.

## Spread, confidence, support

- `spread` = highest minus lowest seat score on the recommended option. A 7.0 with spread 1 is a different answer from a 7.0 with spread 6.
- `confidence` = average seat confidence x 2, rounded, minus 1 when the spread is 5 or more. Scale 1 to 10.
- `support for the resolution` = the weighted average of Round 3's FINAL SCORE. It measures how well the draft captured the room.

## Pillar scorecard

One row per seat with its final PILLAR SCORE, labelled with that seat's pillar. Any pillar at 4 or below gets a named fix under "What to do next", even on a GO.
