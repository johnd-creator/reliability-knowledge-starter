# FIX-03 isolated evidence

[Memory comparison](profile-summary.json) contains sanitized numeric measurements from temporary loopback Node22 probes, not the live HTTPS3000 frontend. Heap samples: five seconds; cgroup intervals are recorded because compilation delays sampling. The baseline internally restarted; its lower final memory follows that restart. FS resource counts include transient requests and do not identify retained watcher allocations.

Browser screenshot evidence, when listed here, comes from temporary candidate copies with all backend addresses redirected to closed loopback port9. It shows real rendered candidate UI with UNAVAILABLE/UNKNOWN state, not operational values or live QA session acceptance. Original design PNGs remain unchanged. Raw evidence is privately retained and contains no committed session material.

| Isolated responsive rendering | SHA256 |
|---|---|
| [1440px](isolated-empty-1440.png) | `b1e765110d321262b126430ec0b7de1aabf1a4b83aaf707b5d65ac3b29cbae73` |
| [768px](isolated-empty-768.png) | `b8fab59c63352c5d2216543b08b7a743127165e5f777db74e47b5733cadc35fa` |
| [390px](isolated-empty-390.png) | `3b8b27de3e4feb7354aa27ff73e430c9836524e1ac5711540257f213b6e386ac` |

[Cold start / HMR summary](cold-hmr-summary.json): three temporary candidate process starts, 42 route navigations, nine HMR changes observed without reload plus exact restoration. Backends are intentionally unavailable; no live auth/session acceptance is claimed.
