/* trace_gram_sched.c — wave-69 P1 instrument: SCHEDULE-VARYING trace-gram.
 *
 * Adapted from wave-68 trace_gram.c (same 7 cells, same 5+1 opcode contract,
 * same honest telemetry). Structural change, pre-registered in README.md:
 *
 *   - Each cell's exercise script is split into SELF-CONTAINED PHASES. Each
 *     phase consumes a per-(cell, seed, phase) seeded sub-RNG, so its emitted
 *     bytes are a pure function of (cell, seed, phase). Cross-phase
 *     accumulation is removed ON PURPOSE: schedule reordering then provably
 *     preserves the payload multiset and the op multiset — only emission
 *     ORDER varies. (wave-68's accumulating instrument remains in
 *     trace_gram.c; this is the order-isolating sibling.)
 *   - Four schedules over the same contract:
 *       A linear, B reverse, C interleave(front/back), D split-swap(rotate n/2)
 *   - reseed mode: sub-RNGs keyed by (cell, seed, phase, sched) so payloads
 *     co-vary with schedule (law predicts embeddings STILL cannot name it).
 *
 * Build: cc -std=c99 -O2 -I<quilt-c>/include trace_gram_sched.c -o \
 *            trace_gram_sched <quilt-c>/build/libquilt-c.a -lm
 * Usage: ./trace_gram_sched <cell> <seed> <A|B|C|D> [reseed]
 * Emits one JSON line per step:
 *   {"cell","seed","sched","i","op","call","args","state","err"}
 */
#include "quilt/cell.h"
#include "quilt/route.h"
#include "quilt/crdt.h"
#include "quilt/time.h"
#include "quilt/quf.h"
#include "quilt/world.h"
#include "quilt/proof.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *CELL = "?";
static int SEED = 0;
static const char *SCHED = "A";
static int STEP = 0;
static unsigned long rng_state;

static void set_rng(int phase, int reseed)
{
    unsigned long h = (unsigned long)SEED * 2654435761UL + 12345UL;
    h += (unsigned long)phase * 97UL + 7UL;
    if (reseed) h += (unsigned long)(SCHED[0] - 'A') * 1000003UL;
    rng_state = h;
}

static void emit(const char *op, const char *call, const char *args, const char *state, int err)
{
    printf("{\"cell\":\"%s\",\"seed\":%d,\"sched\":\"%s\",\"i\":%d,\"op\":\"%s\",\"call\":\"%s\","
           "\"args\":\"%s\",\"state\":\"%s\",\"err\":%d}\n",
           CELL, SEED, SCHED, STEP++, op, call, args, state, err);
}

static unsigned rnd(unsigned n) { rng_state = rng_state * 6364136223846793005UL + 1442695040888963407UL; return (unsigned)((rng_state >> 33) % n); }

/* ── route: 6 phases ───────────────────────────────────────────────── */
static void ph_route0(void) { quilt_route_stats_t r; emit("TICK", "route:init", "", "total=0", quilt_route_init(&r)); }
static void ph_route_rec(int n)
{
    quilt_route_stats_t r; quilt_route_init(&r);
    static const char *names[] = {"TEXT_LOG", "DENSE_VEC", "SPARSE_IDX", "KV_KEYVAL", "SYNTH_V2"};
    for (int j = 0; j < n; j++) {
        int k = rnd(QUILT_ROUTE__COUNT);
        int rc = quilt_route_record(&r, (quilt_route_kind_t)k);
        char st[64]; snprintf(st, sizeof st, "total=%u count[%s]=%u", r.total, names[k], r.count[k]);
        emit("EFFECT", "route:record", names[k], st, rc < 0);
    }
}
static void ph_route1(void) { ph_route_rec(4); }
static void ph_route2(void) { ph_route_rec(4); }
static void ph_route3(void) { ph_route_rec(4); }
static void ph_route4(void)
{
    quilt_route_stats_t r; quilt_route_init(&r);
    for (int j = 0; j < 5; j++) quilt_route_record(&r, (quilt_route_kind_t)j);
    quilt_route_kind_t pk = quilt_route_pick(&r);
    emit("VIEW", "route:pick", "", quilt_route_kind_name(pk), 0);
}
static void ph_route5(void)
{
    quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(1000);
    quilt_route_kind_t pol = quilt_route_policy(&v);
    char st[64]; snprintf(st, sizeof st, "v=%lld -> %s", (long long)v.u.i, quilt_route_kind_name(pol));
    emit("VIEW", "route:policy", "v:int", st, 0);
}

/* ── crdt: 5 phases ────────────────────────────────────────────────── */
static void ph_crdt_pn(int n)
{
    quilt_pn_counter_t c; quilt_pn_counter_init(&c);
    for (int j = 0; j < n; j++) {
        int peer = (int)rnd(4);
        if (rnd(3)) { int rc = quilt_pn_counter_inc(&c, peer);
            char st[48]; snprintf(st, sizeof st, "peers[%d]++ value=%lld", peer, (long long)quilt_pn_counter_value(&c));
            emit("EFFECT", "crdt:pn_inc", "peer", st, rc); }
        else { int rc = quilt_pn_counter_dec(&c, peer);
            char st[48]; snprintf(st, sizeof st, "peers[%d]-- value=%lld", peer, (long long)quilt_pn_counter_value(&c));
            emit("EFFECT", "crdt:pn_dec", "peer", st, rc); }
    }
}
static void ph_crdt0(void) { ph_crdt_pn(3); }
static void ph_crdt1(void) { ph_crdt_pn(3); }
static void ph_crdt2(void) { ph_crdt_pn(2); }
static void ph_crdt3(void)
{
    quilt_or_set_t s; quilt_or_set_init(&s);
    const char *elems[] = {"alpha", "beta", "gamma", "delta"};
    for (int i = 0; i < 4; i++) {
        int rc = quilt_or_set_add(&s, elems[i]);
        char st[48]; snprintf(st, sizeof st, "has[%s]=%d", elems[i], quilt_or_set_contains(&s, elems[i]));
        emit("BIND", "crdt:orset_add", elems[i], st, rc);
    }
}
static void ph_crdt4(void)
{
    quilt_mv_register_t m; quilt_mv_register_init(&m);
    quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)(rnd(500) - 250);
    emit("BIND", "crdt:mv_set", "v:int", "replica-local", quilt_mv_register_set(&m, v, 1, 2));
}

/* ── time: 5 phases ────────────────────────────────────────────────── */
static void bind_full(quilt_time_cell_t *c)
{
    double ctx[32];
    for (int i = 0; i < 32; i++) ctx[i] = (double)i + (double)rnd(10) / 10.0;
    quilt_time_bind_context(c, ctx, 32, 1);
    quilt_time_set_horizon(c, 3 + rnd(4));
}
static void ph_time0(void)
{
    quilt_time_cell_t c; quilt_time_cell_init(&c);
    double ctx[32];
    for (int i = 0; i < 32; i++) ctx[i] = (double)i + (double)rnd(10) / 10.0;
    emit("BIND", "time:bind_context", "ctx[32],n_variates=1", "context-bound", quilt_time_bind_context(&c, ctx, 32, 1));
    quilt_time_cell_free(&c);
}
static void ph_time1(void)
{
    quilt_time_cell_t c; quilt_time_cell_init(&c);
    size_t hz = 3 + rnd(4);
    emit("BIND", "time:set_horizon", "horizon", "set", quilt_time_set_horizon(&c, hz));
    quilt_time_cell_free(&c);
}
static void ph_time2(void)
{
    quilt_time_cell_t c; quilt_time_cell_init(&c); bind_full(&c);
    int rc = quilt_time_forecast(&c);
    emit("TICK", "time:forecast", "", "ran", rc);
    quilt_time_cell_free(&c);
}
static void ph_timeq(double q, int vi)
{
    quilt_time_cell_t c; quilt_time_cell_init(&c); bind_full(&c);
    quilt_time_forecast(&c);
    double pts[4] = {0, 0, 0, 0};   /* deterministic even if the read fails */
    int rc2 = quilt_time_read_quantile(&c, q, vi, pts, 4);
    char st[64]; snprintf(st, sizeof st, "q%.1f p0=%.2f p3=%.2f", q, pts[0], pts[3]);
    emit("VIEW", "time:read_quantile", "q,variate", st, rc2);
    quilt_time_cell_free(&c);
}
static void ph_time3(void) { ph_timeq(0.1, 0); }
static void ph_time4(void) { ph_timeq(0.5, 1); }

/* ── quf: 4 phases ─────────────────────────────────────────────────── */
static void ph_quf0(void)
{
    quilt_quf_t q; int rc = quilt_quf_init(&q, 4, 3, 1, 8);
    emit("TICK", "quf:init", "cells=4,edges=3", "init", rc);
    quilt_quf_free(&q);
}
static void ph_quf1(void)
{
    quilt_quf_t q; quilt_quf_init(&q, 4, 3, 1, 8);
    quilt_quf_dial_row_t row; memset(&row, 0, sizeof row);
    quilt_value_t v; v.t = QUILT_V_FLOAT; v.u.f = (rnd(2000) - 1000) / 100.0;
    quilt_quf_dial_from_value(&row, &v);
    quilt_value_t back; quilt_quf_dial_to_value(&row, &back);
    char st[64]; snprintf(st, sizeof st, "%.3f -> q115 -> %.3f", v.u.f, back.u.f);
    emit("EFFECT", "quf:dial_roundtrip", "v:float", st, 0);
    quilt_quf_free(&q);
}
static void ph_quf2(void)
{
    uint64_t h = quilt_quf_hash((const uint8_t *)"alpha-beta", 10);
    char st2[48]; snprintf(st2, sizeof st2, "hash=%016llx", (unsigned long long)h);
    emit("VIEW", "quf:hash", "buf[10]", st2, 0);
}
static void ph_quf3(void)
{
    quilt_quf_t q; quilt_quf_init(&q, 4, 3, 1, 8);
    int rs = quilt_quf_serialize(&q);
    emit("TICK", "quf:serialize", "", rs == 0 ? "ok" : "err", rs < 0);
    quilt_quf_free(&q);
}

/* ── world: 3 phases ───────────────────────────────────────────────── */
static void ph_world0(void)
{
    quilt_world_program_t p; quilt_world_program_init(&p);
    const char *code = "1 2 + 3 *";
    emit("BIND", "world:program_set", code, "loaded", quilt_world_program_set(&p, code));
    quilt_world_program_free(&p);
}
static void ph_world1(void)
{
    quilt_world_program_t p; quilt_world_program_init(&p);
    quilt_world_program_set(&p, "1 2 + 3 *");
    quilt_quantity_t q = {0};
    int rc = quilt_world_execute(&p, NULL, 0, &q);
    char st[64]; snprintf(st, sizeof st, "quantity=%.3f", q.value);
    emit("TICK", "world:execute", "env=NULL", st, rc);
    quilt_world_program_free(&p);
}
static void ph_world2(void)
{
    quilt_world_program_t p; quilt_world_program_init(&p);
    quilt_world_program_set(&p, "1 2 + 3 *");
    double obs = (double)rnd(200) / 10.0 - 10.0;
    int rv = quilt_world_verify(&p, obs, 5.0);
    char st[64]; snprintf(st, sizeof st, "observed=%.2f tol=5", obs);
    emit("VIEW", "world:verify", "observed,tol", st, rv);
    quilt_world_program_free(&p);
}

/* ── proof: 4 phases ───────────────────────────────────────────────── */
static void ph_proof0(void)
{
    quilt_proof_t pr; quilt_proof_entry_t ring[QUILT_PROOF_RING_CAP];
    quilt_proof_init(&pr, ring);
    uint8_t sec[32]; memset(sec, 7, sizeof sec);
    emit("BIND", "proof:set_secret", "sec[32]", "set", quilt_proof_set_secret(&pr, sec));
}
static void ph_proof_app(int n)
{
    quilt_proof_t pr; quilt_proof_entry_t ring[QUILT_PROOF_RING_CAP];
    quilt_proof_init(&pr, ring);
    uint8_t sec[32]; memset(sec, 7, sizeof sec);
    quilt_proof_set_secret(&pr, sec);
    for (int j = 0; j < n; j++) {
        quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(10000);
        int rc = quilt_proof_append(&pr, &v, (uint64_t)j, 1);
        char st[48]; snprintf(st, sizeof st, "head=%u count=%u", pr.head, pr.count);
        emit("EFFECT", "proof:append", "v:int", st, rc);
    }
}
static void ph_proof1(void) { ph_proof_app(2); }
static void ph_proof2(void) { ph_proof_app(2); }
static void ph_proof3(void)
{
    quilt_proof_t pr; quilt_proof_entry_t ring[QUILT_PROOF_RING_CAP];
    quilt_proof_init(&pr, ring);
    uint8_t sec[32]; memset(sec, 7, sizeof sec);
    quilt_proof_set_secret(&pr, sec);
    quilt_value_t v; v.t = QUILT_V_INT; v.u.i = 42;
    quilt_proof_append(&pr, &v, 0, 1);
    int rv = quilt_proof_verify(&pr);
    emit("VIEW", "proof:verify", "", rv == 0 ? "chain-ok" : "chain-bad", rv);
}

/* ── engine: 7 phases ──────────────────────────────────────────────── */
static void ph_engine0(void)
{
    quilt_cell_t cells[8]; quilt_engine_t e;
    int rc = quilt_engine_init(&e, cells, 8);
    emit("TICK", "engine:init", "cap=8", "ok", rc);
    quilt_engine_free(&e);
}
static void ph_engine_bind(int n)
{
    quilt_cell_t cells[8]; quilt_engine_t e; quilt_engine_init(&e, cells, 8);
    const char *ids[] = {"a", "b", "c", "d"};
    for (int j = 0; j < n; j++) {
        quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(100);
        int rb = quilt_bind(&e, ids[j], v);
        char st[48]; snprintf(st, sizeof st, "%s=%lld", ids[j], (long long)v.u.i);
        emit("BIND", "engine:bind", ids[j], st, rb);
    }
    quilt_engine_free(&e);
}
static void ph_engine1(void) { ph_engine_bind(4); }
static void ph_engine2(void)
{
    quilt_cell_t cells[8]; quilt_engine_t e; quilt_engine_init(&e, cells, 8);
    const char *ids[] = {"a", "b", "c", "d"};
    for (int j = 0; j < 4; j++) { quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(100); quilt_bind(&e, ids[j], v); }
    for (int j = 0; j < 3; j++) {
        int rl = quilt_link(&e, ids[j], ids[j + 1]);
        char st[48]; snprintf(st, sizeof st, "%s->%s", ids[j], ids[j + 1]);
        emit("LINK", "engine:link", st, st, rl);
    }
    quilt_engine_free(&e);
}
static void ph_engine3(void)
{
    quilt_cell_t cells[8]; quilt_engine_t e; quilt_engine_init(&e, cells, 8);
    const char *ids[] = {"a", "b", "c", "d"};
    for (int j = 0; j < 4; j++) { quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(100); quilt_bind(&e, ids[j], v); }
    for (int j = 0; j < 2; j++) {
        int re = quilt_effect(&e, ids[rnd(4)]);
        emit("EFFECT", "engine:effect", "id", "applied", re);
    }
    quilt_engine_free(&e);
}
static void ph_engine4(void)
{
    quilt_cell_t cells[8]; quilt_engine_t e; quilt_engine_init(&e, cells, 8);
    const char *ids[] = {"a", "b", "c", "d"};
    for (int j = 0; j < 4; j++) { quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(100); quilt_bind(&e, ids[j], v); }
    for (int j = 0; j < 2; j++) {
        quilt_value_t out; int rv = quilt_view(&e, ids[rnd(4)], &out);
        char st[48]; snprintf(st, sizeof st, "view=%s", rv == 0 ? "ok" : "missing");
        emit("VIEW", "engine:view", "id", st, rv);
    }
    quilt_engine_free(&e);
}
static void ph_engine5(void)
{
    quilt_cell_t cells[8]; quilt_engine_t e; quilt_engine_init(&e, cells, 8);
    for (int j = 0; j < 4; j++) { quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(100); quilt_bind(&e, "a", v); }
    uint64_t t = quilt_tick(&e);
    char st[48]; snprintf(st, sizeof st, "tick=%llu", (unsigned long long)t);
    emit("TICK", "engine:tick", "", st, 0);
    quilt_engine_free(&e);
}
static void ph_engine6(void)
{
    quilt_cell_t cells[8]; quilt_engine_t e; quilt_engine_init(&e, cells, 8);
    quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(100);
    quilt_bind(&e, "d", v);
    int rf = quilt_forget(&e, "d");
    emit("FORGET", "engine:forget", "d", "torn-down", rf);
    quilt_engine_free(&e);
}

/* ── schedules ─────────────────────────────────────────────────────── */
typedef void (*phase_fn)(void);
static void run_cell(const char *cell, int nph, const phase_fn *ph, int reseed)
{
    int n = nph, order[8];
    for (int i = 0; i < n; i++) order[i] = i;
    int tmp[8];
    switch (SCHED[0]) {
    case 'A': break;
    case 'B': for (int i = 0; i < n; i++) order[i] = n - 1 - i; break;
    case 'C': { int f = 0, b = n - 1, k = 0;
                while (f <= b) { tmp[k++] = order[f++]; if (f <= b) tmp[k++] = order[b--]; }
                for (int i = 0; i < n; i++) order[i] = tmp[i]; break; }
    case 'D': { int h = (n + 1) / 2, k = 0;
                for (int i = h; i < n; i++) tmp[k++] = order[i];
                for (int i = 0; i < h; i++) tmp[k++] = order[i];
                for (int i = 0; i < n; i++) order[i] = tmp[i]; break; }
    default: fprintf(stderr, "bad schedule\n"); exit(2);
    }
    for (int i = 0; i < n; i++) { set_rng(order[i], reseed); ph[order[i]](); }
}

int main(int argc, char **argv)
{
    if (argc < 4) { fprintf(stderr, "usage: %s <cell> <seed> <A|B|C|D> [reseed]\n", argv[0]); return 2; }
    CELL = argv[1]; SEED = atoi(argv[2]); SCHED = argv[3];
    int reseed = (argc > 4 && !strcmp(argv[4], "reseed"));
    static const phase_fn route_ph[] = {ph_route0, ph_route1, ph_route2, ph_route3, ph_route4, ph_route5};
    static const phase_fn crdt_ph[]  = {ph_crdt0, ph_crdt1, ph_crdt2, ph_crdt3, ph_crdt4};
    static const phase_fn time_ph[]  = {ph_time0, ph_time1, ph_time2, ph_time3, ph_time4};
    static const phase_fn quf_ph[]   = {ph_quf0, ph_quf1, ph_quf2, ph_quf3};
    static const phase_fn world_ph[] = {ph_world0, ph_world1, ph_world2};
    static const phase_fn proof_ph[] = {ph_proof0, ph_proof1, ph_proof2, ph_proof3};
    static const phase_fn engine_ph[] = {ph_engine0, ph_engine1, ph_engine2, ph_engine3, ph_engine4, ph_engine5, ph_engine6};
    if      (!strcmp(CELL, "route"))  run_cell(CELL, 6, route_ph, reseed);
    else if (!strcmp(CELL, "crdt"))   run_cell(CELL, 5, crdt_ph, reseed);
    else if (!strcmp(CELL, "time"))   run_cell(CELL, 5, time_ph, reseed);
    else if (!strcmp(CELL, "quf"))    run_cell(CELL, 4, quf_ph, reseed);
    else if (!strcmp(CELL, "world"))  run_cell(CELL, 3, world_ph, reseed);
    else if (!strcmp(CELL, "proof"))  run_cell(CELL, 4, proof_ph, reseed);
    else if (!strcmp(CELL, "engine")) run_cell(CELL, 7, engine_ph, reseed);
    else { fprintf(stderr, "unknown cell\n"); return 2; }
    return 0;
}
