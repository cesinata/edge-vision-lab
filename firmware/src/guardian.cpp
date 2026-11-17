#include "guardian.hpp"

#include <cstdlib>
#include <sstream>

namespace guardian {

const char* state_name(State s) {
    switch (s) {
        case State::Idle: return "idle";
        case State::Capture: return "capture";
        case State::Infer: return "infer";
        case State::Alert: return "alert";
        case State::LowPower: return "low-power";
        case State::Recovery: return "recovery";
    }
    return "?";
}

const char* event_name(Event e) {
    switch (e) {
        case Event::None: return "none";
        case Event::AlertRaised: return "alert";
        case Event::WatchdogReset: return "watchdog-reset";
        case Event::FaultReset: return "fault-reset";
    }
    return "?";
}

const std::vector<Transition>& transitions() {
    static const std::vector<Transition> t = {
        {State::Idle, State::Capture, "frame ready"},
        {State::Capture, State::Infer, "capture done"},
        {State::Infer, State::Idle, "score below threshold"},
        {State::Infer, State::Alert, "score at or above threshold"},
        {State::Alert, State::Idle, "alert done"},
        {State::Idle, State::LowPower, "battery low"},
        {State::LowPower, State::Idle, "battery recovered"},
        {State::Idle, State::Recovery, "fault or watchdog stall"},
        {State::Capture, State::Recovery, "fault or watchdog stall"},
        {State::Infer, State::Recovery, "fault or watchdog stall"},
        {State::Alert, State::Recovery, "fault or watchdog stall"},
        {State::LowPower, State::Recovery, "fault or watchdog stall"},
        {State::Recovery, State::Idle, "recovery done"},
        {State::Recovery, State::LowPower, "recovery done, battery low"},
    };
    return t;
}

std::string mermaid_id(State s) {
    std::string n = state_name(s);
    for (char& c : n)
        if (c == '-') c = '_';
    return n;
}

std::string mermaid_diagram() {
    std::ostringstream o;
    o << "stateDiagram-v2\n    state \"low-power\" as low_power\n    [*] --> idle\n";
    for (const auto& t : transitions())
        o << "    " << mermaid_id(t.from) << " --> " << mermaid_id(t.to) << ": " << t.label << "\n";
    return o.str();
}

Controller::Controller(const Config& cfg) : cfg_(cfg) {}

void Controller::enter(State s, uint32_t t_ms) {
    state_ = s;
    entered_ms_ = t_ms;
}

bool Controller::step(const Input& in, Step& out, std::string& error) {
    if (in.battery_pct < 0 || in.battery_pct > 100) {
        error = "battery_pct out of range 0..100";
        return false;
    }
    if (in.score != -1.0f && (in.score < 0.0f || in.score > 1.0f)) {
        error = "score must be -1 (no frame) or in [0,1]";
        return false;
    }
    if (started_ && in.t_ms < last_t_ms_) {
        error = "timestamp went backwards";
        return false;
    }
    if (!started_) {
        started_ = true;
        last_tick_ms_ = in.t_ms;  // the watchdog starts counting at the first row
        entered_ms_ = in.t_ms;
    }
    last_t_ms_ = in.t_ms;
    if (in.tick) last_tick_ms_ = in.t_ms;

    const State before = state_;
    Event ev = Event::None;
    const uint32_t in_state = in.t_ms - entered_ms_;

    if (state_ == State::Recovery) {
        // The watchdog is not evaluated while held in Recovery.
        if (in_state >= cfg_.recovery_ms) {
            last_tick_ms_ = in.t_ms;
            enter(in.battery_pct <= cfg_.low_battery_pct ? State::LowPower : State::Idle, in.t_ms);
        }
    } else if (in.fault) {
        ev = Event::FaultReset;
        enter(State::Recovery, in.t_ms);
    } else if (in.t_ms - last_tick_ms_ > cfg_.watchdog_timeout_ms) {
        ev = Event::WatchdogReset;
        enter(State::Recovery, in.t_ms);
    } else {
        switch (state_) {
            case State::Idle:
                if (in.battery_pct <= cfg_.low_battery_pct) {
                    enter(State::LowPower, in.t_ms);
                } else if (in.score >= 0.0f) {
                    pending_score_ = in.score;
                    enter(State::Capture, in.t_ms);
                }
                break;
            case State::Capture:
                if (in_state >= cfg_.capture_ms) enter(State::Infer, in.t_ms);
                break;
            case State::Infer:
                if (in_state >= cfg_.infer_ms) {
                    if (pending_score_ >= cfg_.alert_threshold) {
                        ev = Event::AlertRaised;
                        enter(State::Alert, in.t_ms);
                    } else {
                        enter(State::Idle, in.t_ms);
                    }
                }
                break;
            case State::Alert:
                if (in_state >= cfg_.alert_ms) enter(State::Idle, in.t_ms);
                break;
            case State::LowPower:
                if (in.battery_pct >= cfg_.resume_battery_pct) enter(State::Idle, in.t_ms);
                break;
            case State::Recovery:
                break;  // handled above
        }
    }
    out.state = state_;
    out.event = ev;
    out.changed = state_ != before;
    return true;
}

static bool parse_int(const std::string& s, long& v) {
    char* end = nullptr;
    v = std::strtol(s.c_str(), &end, 10);
    return !s.empty() && end && *end == '\0';
}

static bool parse_float(const std::string& s, float& v) {
    char* end = nullptr;
    v = std::strtof(s.c_str(), &end);
    return !s.empty() && end && *end == '\0';
}

bool parse_trace(const std::string& text, std::vector<Input>& rows, std::string& error) {
    std::istringstream in(text);
    std::string line;
    int lineno = 0;
    while (std::getline(in, line)) {
        ++lineno;
        while (!line.empty() && (line.back() == '\r' || line.back() == ' ')) line.pop_back();
        if (line.empty() || line[0] == '#' || line.rfind("t_ms", 0) == 0) continue;
        std::vector<std::string> f;
        std::istringstream ls(line);
        std::string cell;
        while (std::getline(ls, cell, ',')) f.push_back(cell);
        auto fail = [&](const char* why) {
            error = "line " + std::to_string(lineno) + ": " + why;
            return false;
        };
        if (f.size() != 5) return fail("expected 5 comma-separated fields");
        long t, b, tick, fault;
        float score;
        if (!parse_int(f[0], t) || t < 0) return fail("t_ms must be a non-negative integer");
        if (!parse_float(f[1], score)) return fail("score must be a number");
        if (!parse_int(f[2], b)) return fail("battery_pct must be an integer");
        if (!parse_int(f[3], tick) || (tick != 0 && tick != 1)) return fail("tick must be 0 or 1");
        if (!parse_int(f[4], fault) || (fault != 0 && fault != 1)) return fail("fault must be 0 or 1");
        Input r;
        r.t_ms = static_cast<uint32_t>(t);
        r.score = score;
        r.battery_pct = static_cast<int>(b);
        r.tick = tick == 1;
        r.fault = fault == 1;
        rows.push_back(r);
    }
    return true;
}

}  // namespace guardian
