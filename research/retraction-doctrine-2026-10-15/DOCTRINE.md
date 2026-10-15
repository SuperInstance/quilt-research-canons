# §6 Doctrine — the captain's open question, written for the captain

> **Author:** Mavis (Mavis × Casey session line).
> **Date:** 2026-10-15.
> **Status:** Draft, for the captain's ruling. PR #16 (retraction spike) has shipped the mechanics; this document is the missing verdict.
> **Repo home:** `SuperInstance/quilt-research-canons/research/retraction-doctrine-2026-10-15/`

## 0. The question, stated precisely

The design duel's §6 (cited verbatim in PR #16's body, also referenced in `git.pp-ng/docs/OPEN-QUESTIONS.md` §1b and §1c):

> **May a third party's accusation, once ratified, stain a record its author still stands behind?**

Concretely: Author A writes a record `r`. Author A does not retract `r`. Author B files a `dispute` against `r`. Author C — a captain — writes a `settlement` upholding B's dispute. **Does `r`'s retraction leave a trace that distinguishes "A retracted their own work" from "B accused and C ratified, against A's standing position"?**

PR #16's mechanics implement *both* shapes (a `dispute` and a `settlement` are records; the settlement is bite only if `authoritative`; bite ⇒ effects voided, graph position preserved, descendants not orphaned, ancestry runs through). What the spike does *not* do is mark a retraction as contested when the settling author is not the target's author. The doctrine flag is open because the design of the system — *what is the difference, if any, that should be visible* — is a captain question, not an engineering one.

## 1. The shape of the existing system (so the three options are concrete)

The fold's invariants, as established by `DESIGN.md`, `docs/CHECKPOINT-V2.md`, and PR #16's spike:

- **Derivation is a pure function of the record.** The fold never reads a `dispute` or `settlement` *as state*. It reads a settlement pass (`retraction_status`) that computes the retracted set from the record set alone, and the fold runs on what stands.
- **Captain-class = author of an applied override** (in the spike's set-internal proxy; a real deployment binds this to the token layer).
- **The record is the truth.** Anything outside the record is rebuildable or receipted. Whatever the §6 verdict is, the system should not need a service in the write path to enforce it.
- **Self-disavowal is the unambiguous case.** A retracting author is the authority on their own intent. The mechanism for "A retracts A" is clean, reproducible, and requires no captain call. §6 is not about this.
- **Meta records never appear in `order`, never candidacy, never in tallies or `recordsBehind`.** This is the only path that keeps the bite-bounded-stain design honest.

The question is therefore: *given a settlement upheld by a captain (or the captain proxy) against a record whose author still stands behind it, what surface — if any — should mark the contested nature of the retraction?*

## 2. Three options

### Option I — Pure self-retraction: only the author retracts, the rest is shadow

The settlement's `authoritative` predicate reduces to *author-of-target OR captain-of-overrides-of-target*. A captain upholding a third-party dispute **does not retract** — it converts to a *warning surface* (`/api/records` gains a `contestedBy: [B, C, ...]` annotation; the record's effects still stand).

**Implications:**

- *No silent side effects.* The state never changes because of a dispute unless the disputing party is the author.
- *The captain's authority is the captain's annotation, not the captain's claw.* This is a clean, non-violent way to wield captaincy.
- *Adversarial accusations can be witnessed but not silenced.* If B and C want to mark A's record as suspect, they can — but A's effects still hold.
- *The risk: the captain cannot defend the record against a malicious author.* A captured author can poison the record; the captain's only recourse is to *add a new record* that supersedes the old (a `task` or `override`), not retract it. This is a re-statement of the existing inheritance doctrine: the captain outranks by reason, not by erasure.
- *Conformance cost.* Zero new code. The spike's `retraction_status` already handles "non-authoritative settlement" as inert.

### Option II — Captain-retract-but-no-stain: ratified accusations retract, no trace

A captain upholding a third-party dispute **does retract** the target's effects — but the surface does not distinguish self-retraction from ratified accusation. The doctrine flag in PR #16 says: the mechanics support this; the surface is silent on the difference.

**Implications:**

- *Captaincy is fully effective.* A captain can defend the record against a malicious author.
- *No new fingerprint.* The `retraction_status` set is the same shape regardless of who settled. Conformance corpus is unchanged.
- *The risk: an over-reaching captain.* If a captain routinely retracts against standing authors, the system gives no early signal. The captain's edits are not their own.
- *The risk: a captured captain.* If the captain is compromised (token, key, or social engineering), the surface is silent and the record can be retroactively voided.
- *Conformance cost.* Zero new code. The spike is built for this.

### Option III — Captain-retract-and-stain: ratified accusations mark the record as contested

A captain upholding a third-party dispute retracts the target's effects **and** adds a durable surface — the record gains a `contested: true` annotation in the witness-freshness set, the closure root includes the contestation, and the surface (e.g. `/api/records`) shows the dispute/settlement chain so a downstream consumer can verify the contested nature.

**Implications:**

- *Captaincy is fully effective and fully visible.* A captain retracts and the system remembers that the captain did so against a standing author.
- *A captured captain is detectable in the substrate.* Future readers can audit which records were contested, by whom, and when.
- *The cost: a new field in the record set, in the closure root, in the conformance corpus.* Every new record kind adds a leaf domain. The withdrawal mechanics in PR #16 already have a leaf (id, parents, kind, effects, reason) — the `dispute` and `settlement` records need a target field, an `author` field, and the existing format-v2 leaf would need to broaden to cover them (PR #16's "closure-root leaf blind spot" is exactly this).
- *The cost: every consumer must handle the contestation surface.* The desk, the grid, the worker, the runner — all need to read and render the annotation.
- *The cost: the captain's authority is now a permanent artefact in the record.* A captain's retraction is a fact in the project's history forever, not just an event. This is the *constitutional* cost.
- *Conformance cost.* Substantial. 28 pinned answers already assert bite/captain-classes; the new leaf domain requires new cases (target-stain-through-upheld, target-no-stain-through-rejected, etc.) and a new "I-look-like-the-other-but-am-not" corpus family.

## 3. The recommendation

**Option II** is the right default for the current state of the project.

Rationale:

1. **The fold is mechanical and pure; this matches.** A captain's authority is a reasoned record (a settlement) that lives in the substrate, not a force that violates the substrate. Option II says: the captain's reasoned settlement stands as a record; the record's content is its bite. No magic. The conformance harness can adjudicate every case without knowing about captaincy as a separate concept.
2. **Option I under-specifies the captain's role.** The system already grants the captain the power to author an `override`. A captain who can author an `override` can already supersede any record's effect. Refusing to let the captain uphold a third-party retraction means the captain's authority is *narrower* than the existing inheritance doctrine — the captain is told "you can only act on your own work." That is a captain with one hand tied.
3. **Option III is the most defensible long-term but pays its cost now.** "Captain actions are permanently in the substrate" is the right principle. But the cost — broadening the leaf, retraining consumers, retesting the conformance corpus, and a permanent constitutional record of every captain action — is the right cost only when the project has at least one real, contested, captain-upheld dispute in production. Until then, the captaincy model is the spike's set-internal proxy, and tying the substrate to a record of every captain action against a still-standing author is paying a long-term cost for a short-term abstraction.
4. **The settlement's author is already a fact in the record.** Option II is not "no accountability" — every settlement carries its `author` field. The system already has the audit trail. What it does not have is a *doctrinal* mark that says "this retraction was contested." The captain's signature on the settlement is the existing accountability. Adding more is an engineering decision, not a doctrine decision, and the engineering decision is "defer until the second contested case."

A note on what this *does* change: Option II is the spike's "do nothing else" path. PR #16's mechanics already support it. The doctrine doc's job is to *commit to the verdict* so the spike can graduate from "spike, do not merge" to "merge as §6 doctrine: Option II." The recommendation is to ship the spike with that verdict recorded in `docs/RETRACTION-SPIKE.md` and to revisit the question if a contested case appears in production.

## 4. The conformance test the answer must pass

Whichever option is chosen, the system must satisfy this. It is not part of any of the three options; it is a load-bearing invariant that the chosen option must not violate.

**The retract-then-supersede cycle.** Given a record `r` and a captain-class settlement `s` upholding a third-party dispute against `r`, the following must hold:

- `derive(records \ { r })` produces state `S'`.
- `derive(records)` produces state `S''` where `S''` and `S'` differ **only on keys `r` would have set** (the bite).
- For any descendant `d` of `r` that does not itself dispute `r`, `d`'s effects still apply, with `r` lending graph position (descendants are not orphaned) but not cleanliness.
- A new record `r2` that sets a key `r` would have set, with parents that include `r`'s id, applies and wins by the existing class+ancestry rule — i.e. the captain's retraction does not make `r` "un-disputable." The captain retracts `r` once; a future record that explicitly chooses to build on `r` is a different act.

This invariant is the floor. Options I, II, III all *can* satisfy it (Option I trivially, by not retracting; Options II and III by including the settlement in the set and computing the retracted-set as PR #16 does). What the options disagree on is what surface marks the difference.

## 5. What "the captain" is, in this argument

For the spike, "captain" is the author of an applied override. For a real deployment, the captain is bound to the token layer — the project owner, the org steward, the maintainer. The doc is agnostic to *which* mechanism names the captain; it commits only to the doctrine that **the captain is identified in the record**, and any change to the captain-mechanism is itself a record.

## 6. A note on the lossy case the spike doesn't yet model

PR #16 implements effect-voiding; the design duel's brief was effect-voiding; the design duel's §5.2 spine (GLM's winning design) was cleanliness-stain. The spike says this divergence is deliberate. Option II is consistent with the brief-specified effect-voiding. **If a future regression to cleanliness-stain is contemplated, it is a new spike, a new doc, a new captain call.** This document does not pre-commit.

## 7. What to do now

1. **The captain reads this doc.** Casey, Muse, or whoever is on the desk this week.
2. **Pick an option.** My recommendation is II; the other two are real, defensible, and would be respected.
3. **Record the verdict in `docs/RETRACTION-SPIKE.md`** (in `patchwork-quilt/git.pp-ng`). One paragraph: "§6 doctrine, Option {I,II,III}. Rationale: this doc."
4. **PR #16 graduates from spike to merge.** With the verdict, the spike is no longer a "do not merge" branch. The merge commits to §6 doctrine as chosen; the conformance corpus does not change (Option I and II are zero-diff against the spike as shipped; Option III is a new leaf domain and new corpus family).
5. **Add the "retract-then-supersede" test to the conformance corpus** (see §4). The chosen option should not change the test, but the test should exist for the next time the doctrine is challenged.

## 8. Why this doc exists

PR #16 says "doctrine flag open, awaiting the captain's ruling." This doc is the ruling being offered, written so the captain can sign or counter-sign. If counter-signed, the doc becomes a paper trail for the next review; if signed, it becomes the canonical reference for §6.

