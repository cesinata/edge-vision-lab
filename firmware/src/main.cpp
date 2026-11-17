// guardian_cli: run the state logic over a scripted trace.
//   guardian_cli trace.csv                 print the state after every row (CSV)
//   guardian_cli trace.csv --json [path]   also write the timeline as JSON
//                                          (default path web/public/trace.json)
//   guardian_cli --mermaid                 print the state diagram (Mermaid)
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>

#include "guardian.hpp"

using namespace guardian;

static int usage() {
    std::cerr << "usage: guardian_cli <trace.csv> [--json [path]]\n       guardian_cli --mermaid\n";
    return 2;
}

int main(int argc, char** argv) {
    if (argc < 2) return usage();
    std::string first = argv[1];
    if (first == "--mermaid") {
        std::cout << mermaid_diagram();
        return 0;
    }
    std::string trace_path = first;
    bool want_json = false;
    std::string json_path = "web/public/trace.json";
    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--json") {
            want_json = true;
            if (i + 1 < argc && argv[i + 1][0] != '-') json_path = argv[++i];
        } else {
            return usage();
        }
    }

    std::ifstream f(trace_path);
    if (!f) {
        std::cerr << "cannot open " << trace_path << "\n";
        return 2;
    }
    std::stringstream buf;
    buf << f.rdbuf();
    std::vector<Input> rows;
    std::string err;
    if (!parse_trace(buf.str(), rows, err)) {
        std::cerr << trace_path << ": " << err << "\n";
        return 2;
    }

    Controller c;
    std::ostringstream json;
    const Config& k = c.config();
    json << "{\n  \"label\": \"simulated\",\n"
         << "  \"note\": \"State logic run on a scripted trace. Not measured on hardware.\",\n"
         << "  \"trace\": \"" << trace_path << "\",\n"
         << "  \"config\": {\"alert_threshold\": " << k.alert_threshold << ", \"capture_ms\": " << k.capture_ms
         << ", \"infer_ms\": " << k.infer_ms << ", \"alert_ms\": " << k.alert_ms
         << ", \"watchdog_timeout_ms\": " << k.watchdog_timeout_ms << ", \"recovery_ms\": " << k.recovery_ms
         << ", \"low_battery_pct\": " << k.low_battery_pct << ", \"resume_battery_pct\": " << k.resume_battery_pct
         << "},\n  \"transitions\": [";
    {
        const auto& ts = transitions();
        for (size_t i = 0; i < ts.size(); ++i)
            json << "{\"from\": \"" << state_name(ts[i].from) << "\", \"to\": \"" << state_name(ts[i].to)
                 << "\", \"label\": \"" << ts[i].label << "\"}" << (i + 1 < ts.size() ? ", " : "");
    }
    json << "],\n  \"timeline\": [\n";
    std::cout << "t_ms,state,event\n";
    for (size_t i = 0; i < rows.size(); ++i) {
        Step s;
        if (!c.step(rows[i], s, err)) {
            std::cerr << trace_path << ": row " << (i + 1) << ": " << err << "\n";
            return 2;
        }
        std::cout << rows[i].t_ms << "," << state_name(s.state) << "," << event_name(s.event) << "\n";
        json << "    {\"t_ms\": " << rows[i].t_ms << ", \"state\": \"" << state_name(s.state)
             << "\", \"event\": \"" << event_name(s.event) << "\", \"score\": " << rows[i].score
             << ", \"battery_pct\": " << rows[i].battery_pct << ", \"tick\": " << rows[i].tick
             << ", \"fault\": " << rows[i].fault << "}" << (i + 1 < rows.size() ? "," : "") << "\n";
    }
    json << "  ]\n}\n";
    if (want_json) {
        std::ofstream o(json_path);
        if (!o) {
            std::cerr << "cannot write " << json_path << "\n";
            return 2;
        }
        o << json.str();
    }
    return 0;
}
