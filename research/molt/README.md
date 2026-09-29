# molt — soft shells

A soft shell is a starting state, not a product. It fits exactly one size. It is
supposed to be outgrown, and when you outgrow it the correct action is to shed it and
find a larger one — not to patch it into something that fits nothing.

## Three properties

**APPLIABLE.** A shell is an application on the quilt: it has a cell address, it BINDs
to the state you hand it, and it leaves a receipt. You do not read a shell to
understand it; you run it against a state and read what it did.

**REWINDABLE.** Every `apply()` can snapshot the state first and return a handle.
`rewind(handle)` puts it back *exactly*. A shell that cannot be left is a commitment,
and commitments are what molt exists to avoid.

**FITS ONE SIZE.** Each shell declares what it is for AND what it stops being good for.
A shell with no `outgrows` clause is a framework, and frameworks are the thing this
replaces. That is enforced as a test.

## The seven shells

Every one was extracted from a pattern that actually ran and did work. Nothing here
because it sounds like good practice.

| cell | shell | fits | outgrows when |
|---|---|---|---|
| `molt.method.pre-register` | pre-register | any run that could produce a number | you register hundreds nobody reads |
| `molt.test.fault-injection` | fault-injection | any suite you are about to trust | every fault is caught first time |
| `molt.test.derive-prose-from-run` | derive-prose-from-run | any demo, report or reading beside a number | you're writing narrative nobody reads |
| `molt.self.outgrew-it` | outgrew-it | deciding whether to keep what you have been using | you start shedding things still working |
| `molt.method.two-instruments` | two-instruments | any claim you are about to trust | the two share an ancestor and you didn't check |
| `molt.method.measure-first` | measure-first | any claim about your own work | you measure the unmeasurable and record a number |
| `molt.quilt.to-cells` | to-cells | turning a flat record into something addressable | your cells have no edges |

## The shed/keep decision, and why it matters

```
$ python3 shells.py --apply outgrew-it --state '{"uses": 50, "fit_for": 10}'
  applied molt.self.outgrew-it
    action:  shed
    note:    50/10 uses — a soft shell is meant to be outgrown, and a shell past
             its fit is not a success, it is a leftover
    receipt: f01c5f4568971557
    rewind:  outgrew-it#0
```

Nothing in a substrate that lives gets bigger by accretion alone. A shell that has
outgrown its fit is a liability dressed as continuity, and the expensive mistake is
never shedding.

## Self-test: 15/15, and the failures were the library's own controls

The controls here are about **shedding and rewinding**, not about each shell firing
correctly — a shell library that cannot shed its own shells is a framework.

Three legs failed on the first run and **all three were the tests being wrong**:

1. A leg asserted a rewind would be *dirty* after an in-place leak. It is not, and
   should not be: `apply_with_rewind` snapshots **before** calling `apply`, so a shell
   that mutates its argument cannot corrupt an existing snapshot. The leg was testing a
   hazard the library had already designed against.
2. The KAT leg used one fixture shaped for one shell. Several shells ignore most
   fields, so a single fixture is not coverage. Rewritten per-shell.
3. A chain leg asserted `status == "MEASURED"` while setting up `measurement=None`, which
   correctly yields `UNMEASURED`. It was asserting a different scenario than the one it
   built.

## Fault injection on the library itself

| injected | result |
|---|---|
| `outgrew-it` shedding inverted | 3 legs fail |
| `derive-prose-from-run` contradiction check removed | 1 leg fails |

The second injection initially appeared to survive. It had not — the substitution string
did not match, so the fault was never applied. **A fault injection that silently fails to
inject is indistinguishable from a fault the test cannot catch**, and the difference is
always the same: check that the injection landed before believing the result.

## Usage

```sh
python3 shells.py --list
python3 shells.py --show <name>
python3 shells.py --apply <name> --state '{"k": 1}'
python3 shells.py --self-test
```
