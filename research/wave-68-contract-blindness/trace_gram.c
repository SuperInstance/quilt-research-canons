/* trace_gram.c — R3 wave-68 instrument: per-cell exercise traces.
 *
 * Drives each quilt-c kernel through a seeded exercise schedule and emits
 * one JSON line per step: {cell, seed, i, op, call, args, state, err}.
 * The op vocabulary is the shared 5+1 (BIND/EFFECT/VIEW/TICK/LINK/FORGET);
 * `call` is the kernel-specific entry point; `args`/`state` are the honest
 * payload telemetry (states, not just events). Failed calls are recorded
 * with their error code — a failed call is part of the run's behavior.
 *
 * Build: cc -std=c99 -O2 -Iinclude trace_gram.c -o trace_gram build/libquilt-c.a src/route.c src/crdt.c src/time.c src/quf.c src/world.c src/proof.c -lm
 * (or with the lib as built by make). Usage: ./trace_gram <cell> <seed>
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
static int STEP = 0;

static void emit(const char *op, const char *call, const char *args, const char *state, int err)
{
    printf("{\"cell\":\"%s\",\"seed\":%d,\"i\":%d,\"op\":\"%s\",\"call\":\"%s\","
           "\"args\":\"%s\",\"state\":\"%s\",\"err\":%d}\n",
           CELL, SEED, STEP++, op, call, args, state, err);
}

static unsigned long rng_state;
static unsigned rnd(unsigned n) { rng_state = rng_state * 6364136223846793005UL + 1442695040888963407UL; return (unsigned)((rng_state >> 33) % n); }

/* ── route: policy selection over 5 substrates ─────────────────────── */
static void ex_route(void)
{
    quilt_route_stats_t r;
    emit("TICK", "route:init", "", "total=0", quilt_route_init(&r));
    const char *names[] = {"TEXT_LOG", "DENSE_VEC", "SPARSE_IDX", "KV_KEYVAL", "SYNTH_V2"};
    for (int i = 0; i < 12; i++) {
        int k = rnd(QUILT_ROUTE__COUNT);
        int rc = quilt_route_record(&r, (quilt_route_kind_t)k);
        char st[64]; snprintf(st, sizeof st, "total=%u count[%s]=%u", r.total, names[k], r.count[k]);
        emit("EFFECT", "route:record", names[k], st, rc < 0);
    }
    quilt_route_kind_t pk = quilt_route_pick(&r);
    emit("VIEW", "route:pick", "", quilt_route_kind_name(pk), 0);
    quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(1000);
    quilt_route_kind_t pol = quilt_route_policy(&v);
    char st[64]; snprintf(st, sizeof st, "v=%lld -> %s", (long long)v.u.i, quilt_route_kind_name(pol));
    emit("VIEW", "route:policy", "v:int", st, 0);
}

/* ── crdt: replicated state ────────────────────────────────────────── */
static void ex_crdt(void)
{
    quilt_pn_counter_t c;
    quilt_pn_counter_init(&c);
    for (int i = 0; i < 8; i++) {
        int peer = (int)rnd(4);
        if (rnd(3)) { int rc = quilt_pn_counter_inc(&c, peer);
            char st[48]; snprintf(st, sizeof st, "peers[%d]++ value=%lld", peer, (long long)quilt_pn_counter_value(&c));
            emit("EFFECT", "crdt:pn_inc", "peer", st, rc); }
        else { int rc = quilt_pn_counter_dec(&c, peer);
            char st[48]; snprintf(st, sizeof st, "peers[%d]-- value=%lld", peer, (long long)quilt_pn_counter_value(&c));
            emit("EFFECT", "crdt:pn_dec", "peer", st, rc); }
    }
    quilt_or_set_t s; quilt_or_set_init(&s);
    const char *elems[] = {"alpha", "beta", "gamma", "delta"};
    for (int i = 0; i < 4; i++) {
        int rc = quilt_or_set_add(&s, elems[i]);
        char st[48]; snprintf(st, sizeof st, "has[%s]=%d", elems[i], quilt_or_set_contains(&s, elems[i]));
        emit("BIND", "crdt:orset_add", elems[i], st, rc);
    }
    quilt_mv_register_t m; quilt_mv_register_init(&m);
    quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)(rnd(500) - 250);
    emit("BIND", "crdt:mv_set", "v:int", "replica-local", quilt_mv_register_set(&m, v, 1, 2));
}

/* ── time: temporal projection ─────────────────────────────────────── */
static void ex_time(void)
{
    quilt_time_cell_t c;
    quilt_time_cell_init(&c);
    double ctx[32];
    for (int i = 0; i < 32; i++) ctx[i] = (double)i + (double)rnd(10) / 10.0;
    emit("BIND", "time:bind_context", "ctx[32],n_variates=1", "context-bound", quilt_time_bind_context(&c, ctx, 32, 1));
    size_t hz = 3 + rnd(4);
    emit("BIND", "time:set_horizon", "horizon", "set", quilt_time_set_horizon(&c, hz));
    int rc = quilt_time_forecast(&c);
    emit("TICK", "time:forecast", "", "ran", rc);
    for (int i = 0; i < 2; i++) {
        double pts[4];
        int rc2 = quilt_time_read_quantile(&c, 0.1 + 0.4 * i, i, pts, 4);
        char st[64]; snprintf(st, sizeof st, "q%.1f p0=%.2f p3=%.2f", 0.1 + 0.4 * i, pts[0], pts[3]);
        emit("VIEW", "time:read_quantile", "q,variate", st, rc2);
    }
    quilt_time_cell_free(&c);
}

/* ── quf: quantized filter/dial ────────────────────────────────────── */
static void ex_quf(void)
{
    quilt_quf_t q;
    int rc = quilt_quf_init(&q, 4, 3, 1, 8);
    emit("TICK", "quf:init", "cells=4,edges=3", "init", rc);
    quilt_quf_dial_row_t row; memset(&row, 0, sizeof row);
    quilt_value_t v; v.t = QUILT_V_FLOAT; v.u.f = (rnd(2000) - 1000) / 100.0;
    quilt_quf_dial_from_value(&row, &v);
    quilt_value_t back; quilt_quf_dial_to_value(&row, &back);
    char st[64]; snprintf(st, sizeof st, "%.3f -> q115 -> %.3f", v.u.f, back.u.f);
    emit("EFFECT", "quf:dial_roundtrip", "v:float", st, 0);
    uint64_t h = quilt_quf_hash((const uint8_t *)"alpha-beta", 10);
    char st2[48]; snprintf(st2, sizeof st2, "hash=%016llx", (unsigned long long)h);
    emit("VIEW", "quf:hash", "buf[10]", st2, 0);
    int rs = quilt_quf_serialize(&q);
    emit("TICK", "quf:serialize", "", rs == 0 ? "ok" : "err", rs < 0);
    quilt_quf_free(&q);
}

/* ── world: world programs ─────────────────────────────────────────── */
static void ex_world(void)
{
    quilt_world_program_t p;
    quilt_world_program_init(&p);
    const char *code = "1 2 + 3 *";
    emit("BIND", "world:program_set", code, "loaded", quilt_world_program_set(&p, code));
    quilt_quantity_t q = {0};
    int rc = quilt_world_execute(&p, NULL, 0, &q);
    char st[64]; snprintf(st, sizeof st, "quantity=%.3f", q.value);
    emit("TICK", "world:execute", "env=NULL", st, rc);
    double obs = (double)rnd(200) / 10.0 - 10.0;
    int rv = quilt_world_verify(&p, obs, 5.0);
    snprintf(st, sizeof st, "observed=%.2f tol=5", obs);
    emit("VIEW", "world:verify", "observed,tol", st, rv);
    quilt_world_program_free(&p);
}

/* ── proof: hash-chain receipts ────────────────────────────────────── */
static void ex_proof(void)
{
    quilt_proof_t pr;
    quilt_proof_entry_t ring[QUILT_PROOF_RING_CAP];
    quilt_proof_init(&pr, ring);
    uint8_t sec[32]; memset(sec, 7, sizeof sec);
    emit("BIND", "proof:set_secret", "sec[32]", "set", quilt_proof_set_secret(&pr, sec));
    for (int i = 0; i < 4; i++) {
        quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(10000);
        int rc = quilt_proof_append(&pr, &v, (uint64_t)i, 1);
        char st[48]; snprintf(st, sizeof st, "head=%u count=%u", pr.head, pr.count);
        emit("EFFECT", "proof:append", "v:int", st, rc);
    }
    int rv = quilt_proof_verify(&pr);
    emit("VIEW", "proof:verify", "", rv == 0 ? "chain-ok" : "chain-bad", rv);
}

/* ── engine: the iterator over the cell graph ──────────────────────── */
static void ex_engine(void)
{
    quilt_cell_t cells[8];
    quilt_engine_t e;
    int rc = quilt_engine_init(&e, cells, 8);
    emit("TICK", "engine:init", "cap=8", "ok", rc);
    const char *ids[] = {"a", "b", "c", "d"};
    for (int i = 0; i < 4; i++) {
        quilt_value_t v; v.t = QUILT_V_INT; v.u.i = (int64_t)rnd(100);
        int rb = quilt_bind(&e, ids[i], v);
        char st[48]; snprintf(st, sizeof st, "%s=%lld", ids[i], (long long)v.u.i);
        emit("BIND", "engine:bind", ids[i], st, rb);
    }
    for (int i = 0; i < 3; i++) {
        int rl = quilt_link(&e, ids[i], ids[i + 1]);
        char st[48]; snprintf(st, sizeof st, "%s->%s", ids[i], ids[i + 1]);
        emit("LINK", "engine:link", st, st, rl);
    }
    for (int i = 0; i < 2; i++) {
        int re = quilt_effect(&e, ids[rnd(4)]);
        emit("EFFECT", "engine:effect", "id", "applied", re);
    }
    for (int i = 0; i < 2; i++) {
        quilt_value_t out; int rv = quilt_view(&e, ids[rnd(4)], &out);
        char st[48]; snprintf(st, sizeof st, "view=%s", rv == 0 ? "ok" : "missing");
        emit("VIEW", "engine:view", "id", st, rv);
    }
    uint64_t t = quilt_tick(&e);
    char st[48]; snprintf(st, sizeof st, "tick=%llu", (unsigned long long)t);
    emit("TICK", "engine:tick", "", st, 0);
    int rf = quilt_forget(&e, "d");
    emit("FORGET", "engine:forget", "d", "torn-down", rf);
    quilt_engine_free(&e);
}

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: %s <cell> <seed>\n", argv[0]); return 2; }
    CELL = argv[1];
    SEED = atoi(argv[2]);
    rng_state = (unsigned long)SEED * 2654435761UL + 12345UL;
    if      (!strcmp(CELL, "route"))  ex_route();
    else if (!strcmp(CELL, "crdt"))   ex_crdt();
    else if (!strcmp(CELL, "time"))   ex_time();
    else if (!strcmp(CELL, "quf"))    ex_quf();
    else if (!strcmp(CELL, "world"))  ex_world();
    else if (!strcmp(CELL, "proof"))  ex_proof();
    else if (!strcmp(CELL, "engine")) ex_engine();
    else { fprintf(stderr, "unknown cell\n"); return 2; }
    return 0;
}
