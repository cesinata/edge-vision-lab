// Guardian: power and state logic for a camera node that runs a small image
// classifier. Pure logic: no clock, no random numbers, no hardware calls. All
// time comes from the timestamps in the input, so every run is repeatable.
//
// Nothing here is a measurement of a board. Durations are configuration values
// of this logic, not claims about any device.
#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace guardian {

enum class State { Idle, Capture, Infer, Alert, LowPower, Recovery };

const char* state_name(State s);
// Identifier used in the Mermaid diagram (state_name with '-' replaced by '_').
std::string mermaid_id(State s);

// One row of a scripted trace.
struct Input {
    uint32_t t_ms = 0;     // timestamp, must not go backwards
    float score = -1.0f;   // classifier score in [0,1] for a new frame; -1 means "no frame"
    int battery_pct = 100; // 0..100
    bool tick = false;     // the main loop fed the watchdog on this row
    bool fault = false;    // an external fault was reported on this row
};

struct Config {
    float alert_threshold = 0.85f;      // score >= this raises an alert
    uint32_t capture_ms = 40;           // time spent in Capture
    uint32_t infer_ms = 120;            // time spent in Infer
    uint32_t alert_ms = 500;            // time spent in Alert
    uint32_t watchdog_timeout_ms = 2000;// no tick for longer than this means a stall
    uint32_t recovery_ms = 1000;        // hold time in Recovery before restarting
    int low_battery_pct = 20;           // at or below this, Idle goes to LowPower
    int resume_battery_pct = 30;        // at or above this, LowPower returns to Idle
};

enum class Event { None, AlertRaised, WatchdogReset, FaultReset };

const char* event_name(Event e);

struct Step {
    State state;       // state after processing the row
    Event event;       // what happened on this row, if anything
    bool changed;      // true if the state differs from before the row
};

// Every legal transition, with a label. The tests, the Mermaid diagram and the
// CLI all read this one table.
struct Transition {
    State from;
    State to;
    const char* label;
};
const std::vector<Transition>& transitions();

// Mermaid stateDiagram-v2 text generated from transitions().
std::string mermaid_diagram();

class Controller {
public:
    explicit Controller(const Config& cfg = Config());

    // Process one row. Returns false and sets `error` if the row is invalid
    // (timestamp going backwards, battery or score out of range). The state is
    // unchanged after an invalid row.
    bool step(const Input& in, Step& out, std::string& error);

    State state() const { return state_; }
    const Config& config() const { return cfg_; }

private:
    void enter(State s, uint32_t t_ms);

    Config cfg_;
    State state_ = State::Idle;
    uint32_t entered_ms_ = 0;
    uint32_t last_tick_ms_ = 0;
    uint32_t last_t_ms_ = 0;
    bool started_ = false;
    float pending_score_ = 0.0f;
};

// Parse a trace in CSV form: t_ms,score,battery_pct,tick,fault. A header line
// starting with "t_ms" and blank lines or lines starting with '#' are skipped.
// Returns false and sets `error` (with a line number) on any malformed row.
bool parse_trace(const std::string& text, std::vector<Input>& rows, std::string& error);

}  // namespace guardian
