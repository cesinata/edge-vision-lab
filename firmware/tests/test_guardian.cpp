// Plain assert-style tests, no external framework. Registered with CTest.
#include <cstdio>
#include <fstream>
#include <set>
#include <sstream>
#include <utility>

#include "guardian.hpp"

using namespace guardian;

static int g_failures = 0;
static int g_checks = 0;
#define CHECK(cond)                                                              \
    do {                                                                         \
        ++g_checks;                                                              \
        if (!(cond)) {                                                           \
            ++g_failures;                                                        \
            std::printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond);          \
        }                                                                        \
    } while (0)

// Every (from, to) pair seen while stepping, across all tests.
static std::set<std::pair<int, int>> g_seen;

static Input row(uint32_t t, float score = -1.0f, int batt = 90, bool tick = true, bool fault = false) {
    Input i;
    i.t_ms = t;
    i.score = score;
    i.battery_pct = batt;
    i.tick = tick;
    i.fault = fault;
    return i;
}

static Step go(Controller& c, const Input& in) {
    State before = c.state();
    Step s;
    std::string err;
    bool ok = c.step(in, s, err);
    CHECK(ok);
    if (s.state != before) g_seen.insert({static_cast<int>(before), static_cast<int>(s.state)});
    return s;
}

static void test_idle_without_trigger() {
    Controller c;
    for (uint32_t t = 0; t <= 1000; t += 100) CHECK(go(c, row(t)).state == State::Idle);
}

static void test_low_score_cycle_returns_to_idle_without_alert() {
    Controller c;
    go(c, row(0));
    CHECK(go(c, row(100, 0.20f)).state == State::Capture);
    CHECK(go(c, row(139)).state == State::Capture);  // capture_ms not yet reached
    CHECK(go(c, row(140)).state == State::Infer);
    CHECK(go(c, row(259)).state == State::Infer);
    Step s = go(c, row(260));
    CHECK(s.state == State::Idle);
    CHECK(s.event == Event::None);
}

static void test_high_score_raises_one_alert_then_idle() {
    Controller c;
    int alerts = 0;
    go(c, row(0));
    go(c, row(100, 0.90f));
    go(c, row(140));
    Step s = go(c, row(260));
    CHECK(s.state == State::Alert);
    CHECK(s.event == Event::AlertRaised);
    alerts += s.event == Event::AlertRaised;
    for (uint32_t t = 300; t < 760; t += 20) {
        Step x = go(c, row(t));
        alerts += x.event == Event::AlertRaised;
        CHECK(x.state == State::Alert);
    }
    CHECK(go(c, row(760)).state == State::Idle);
    CHECK(alerts == 1);
}

static void test_threshold_boundary() {
    for (int above = 0; above < 2; ++above) {
        Controller c;
        float score = above ? 0.85f : 0.8499f;
        go(c, row(0));
        go(c, row(100, score));
        go(c, row(140));
        Step s = go(c, row(260));
        CHECK((s.state == State::Alert) == (above == 1));
    }
}

static void test_watchdog_stall_enters_recovery_and_restarts() {
    Controller c;
    go(c, row(0));                       // tick at 0
    CHECK(go(c, row(1000, -1, 90, false)).state == State::Idle);
    CHECK(go(c, row(2000, -1, 90, false)).state == State::Idle);  // exactly the timeout: not yet
    Step s = go(c, row(2001, -1, 90, false));
    CHECK(s.state == State::Recovery);
    CHECK(s.event == Event::WatchdogReset);
    CHECK(go(c, row(3000, -1, 90, false)).state == State::Recovery);  // 999 ms held
    CHECK(go(c, row(3001, -1, 90, true)).state == State::Idle);       // hold done
    CHECK(go(c, row(4500, -1, 90, false)).state == State::Idle);      // watchdog restarted at 3001
}

static void test_ticks_keep_watchdog_alive() {
    Controller c;
    for (uint32_t t = 0; t <= 20000; t += 1500) CHECK(go(c, row(t)).state == State::Idle);
}

static void test_fault_enters_recovery_from_every_state() {
    for (int target = 0; target < 5; ++target) {
        Controller c;
        uint32_t t = 0;
        go(c, row(t));
        switch (target) {
            case 0: break;                                              // Idle
            case 1: go(c, row(t = 100, 0.5f)); break;                   // Capture
            case 2: go(c, row(t = 100, 0.5f)); go(c, row(t = 140)); break;  // Infer
            case 3: go(c, row(t = 100, 0.9f)); go(c, row(140)); go(c, row(t = 260)); break;  // Alert
            case 4: go(c, row(t = 100, -1, 10)); break;                 // LowPower
        }
        State expect[] = {State::Idle, State::Capture, State::Infer, State::Alert, State::LowPower};
        CHECK(c.state() == expect[target]);
        Step s = go(c, row(t + 10, -1, target == 4 ? 10 : 90, true, true));
        CHECK(s.state == State::Recovery);
        CHECK(s.event == Event::FaultReset);
    }
}

static void test_recovery_goes_to_low_power_if_battery_low() {
    Controller c;
    go(c, row(0));
    go(c, row(100, -1, 50, true, true));
    CHECK(c.state() == State::Recovery);
    CHECK(go(c, row(1100, -1, 10)).state == State::LowPower);
}

static void test_low_power_hysteresis_and_ignores_scores() {
    Controller c;
    go(c, row(0, -1, 40));
    CHECK(go(c, row(100, -1, 21)).state == State::Idle);
    CHECK(go(c, row(200, -1, 20)).state == State::LowPower);
    CHECK(go(c, row(300, 0.95f, 25)).state == State::LowPower);  // score ignored
    CHECK(go(c, row(400, -1, 29)).state == State::LowPower);
    CHECK(go(c, row(500, -1, 30)).state == State::Idle);
}

static void test_invalid_rows_are_rejected_and_leave_state_alone() {
    Controller c;
    Step s;
    std::string err;
    CHECK(c.step(row(100), s, err));
    CHECK(!c.step(row(50), s, err));
    CHECK(err.find("backwards") != std::string::npos);
    CHECK(!c.step(row(200, -1, 101), s, err));
    CHECK(!c.step(row(200, 1.5f), s, err));
    CHECK(!c.step(row(200, -0.5f), s, err));
    CHECK(c.state() == State::Idle);
    CHECK(c.step(row(200), s, err));  // a good row still works afterwards
}

static void test_parse_trace() {
    std::vector<Input> r;
    std::string err;
    CHECK(parse_trace("# note\nt_ms,score,battery_pct,tick,fault\n\n0,-1,90,1,0\n100,0.5,89,0,1\n", r, err));
    CHECK(r.size() == 2);
    CHECK(r[1].t_ms == 100 && r[1].score == 0.5f && r[1].battery_pct == 89 && !r[1].tick && r[1].fault);
    std::vector<Input> bad;
    CHECK(!parse_trace("0,-1,90,1\n", bad, err));
    CHECK(err.find("line 1") != std::string::npos);
    CHECK(!parse_trace("0,-1,90,2,0\n", bad, err));
    CHECK(!parse_trace("0,abc,90,1,0\n", bad, err));
    CHECK(!parse_trace("-5,-1,90,1,0\n", bad, err));
}

static std::vector<Input> load(const std::string& name) {
    std::ifstream f(std::string(TRACE_DIR) + "/" + name);
    CHECK(static_cast<bool>(f));
    std::stringstream b;
    b << f.rdbuf();
    std::vector<Input> rows;
    std::string err;
    CHECK(parse_trace(b.str(), rows, err));
    return rows;
}

struct Summary { int alerts = 0, wd = 0, fault = 0; bool saw_low_power = false; };

static Summary run_file(const std::string& name) {
    Controller c;
    Summary s;
    for (const auto& r : load(name)) {
        Step st = go(c, r);
        s.alerts += st.event == Event::AlertRaised;
        s.wd += st.event == Event::WatchdogReset;
        s.fault += st.event == Event::FaultReset;
        s.saw_low_power |= st.state == State::LowPower;
    }
    return s;
}

static void test_trace_files() {
    Summary a = run_file("normal_alert.csv");
    CHECK(a.alerts == 1 && a.wd == 0 && a.fault == 0);
    Summary w = run_file("watchdog_stall.csv");
    CHECK(w.wd == 1 && w.alerts == 0);
    Summary l = run_file("low_battery.csv");
    CHECK(l.saw_low_power && l.alerts == 0);
    Summary f = run_file("fault_in_alert.csv");
    CHECK(f.fault == 1 && f.alerts == 1);
    Summary d = run_file("demo.csv");
    CHECK(d.alerts == 1 && d.wd == 1 && d.saw_low_power);
}

// Every transition in the table must have been exercised, and nothing outside
// the table may have happened.
static void test_transition_table_coverage() {
    std::set<std::pair<int, int>> table;
    for (const auto& t : transitions()) table.insert({static_cast<int>(t.from), static_cast<int>(t.to)});
    for (const auto& p : g_seen) CHECK(table.count(p) == 1);  // nothing illegal happened
    for (const auto& p : table) {
        bool seen = g_seen.count(p) == 1;
        if (!seen)
            std::printf("transition not exercised: %s -> %s\n", state_name(static_cast<State>(p.first)),
                        state_name(static_cast<State>(p.second)));
        CHECK(seen);
    }
}

static void test_mermaid_lists_every_transition() {
    std::string m = mermaid_diagram();
    CHECK(m.rfind("stateDiagram-v2", 0) == 0);
    for (const auto& t : transitions()) {
        std::string line = mermaid_id(t.from) + " --> " + mermaid_id(t.to);
        CHECK(m.find(line) != std::string::npos);
    }
}

static void test_score_arriving_while_busy_is_dropped() {
    Controller c;
    go(c, row(0));
    go(c, row(100, 0.20f));          // Capture with a low score
    go(c, row(110, 0.99f));          // a high score during Capture must not replace it
    go(c, row(140));
    Step s = go(c, row(260));
    CHECK(s.state == State::Idle);   // decided on 0.20, so no alert
    CHECK(s.event == Event::None);
}

static void test_names_are_distinct_and_known() {
    std::set<std::string> states, events;
    for (State st : {State::Idle, State::Capture, State::Infer, State::Alert, State::LowPower, State::Recovery}) {
        std::string n = state_name(st);
        CHECK(n != "?");
        states.insert(n);
    }
    for (Event e : {Event::None, Event::AlertRaised, Event::WatchdogReset, Event::FaultReset}) {
        std::string n = event_name(e);
        CHECK(n != "?");
        events.insert(n);
    }
    CHECK(states.size() == 6);
    CHECK(events.size() == 4);
}

int main() {
    test_idle_without_trigger();
    test_low_score_cycle_returns_to_idle_without_alert();
    test_high_score_raises_one_alert_then_idle();
    test_threshold_boundary();
    test_watchdog_stall_enters_recovery_and_restarts();
    test_ticks_keep_watchdog_alive();
    test_fault_enters_recovery_from_every_state();
    test_recovery_goes_to_low_power_if_battery_low();
    test_low_power_hysteresis_and_ignores_scores();
    test_invalid_rows_are_rejected_and_leave_state_alone();
    test_parse_trace();
    test_trace_files();
    test_transition_table_coverage();
    test_mermaid_lists_every_transition();
    test_score_arriving_while_busy_is_dropped();
    test_names_are_distinct_and_known();
    std::printf("%d checks, %d failures\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
