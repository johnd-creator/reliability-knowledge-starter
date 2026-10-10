# Official NADI design references

NADI-DOC-FOUNDATION-01-FIX-02 · 2026-10-10.

Product Owner explicitly confirmed the five existing repository-root PNGs and the
mapping below as the official design references in FIX-02. This supersedes the
foundation/FIX-01 requirement for a ZIP or additional JPG attachments. No image is
copied, renamed, transcoded, regenerated or duplicated in this directory.

## Availability and integrity

All five images were opened and visually inspected during FIX-02. PNG signatures,
chunk CRCs, compressed image data, dimensions, byte sizes and SHA256 were checked.
Working-tree bytes match the tracked Git blobs in verified main
`f54643f3510bf505628a1400024784faab46e496` and the PR64 baseline
`dc07ab9015b5b7214941a5739cc7765269f680e3`. Their hashes also match the previously
recorded [concept analysis](../NADI-CONCEPT-ALIGNMENT.md).

| Reference ID | Existing root file | Official mapping / page | Status | Pixels | Bytes | SHA256 |
|---|---|---|---|---|---|---|
| REF-ACTION | [konsep1.png](../../../konsep1.png) | Action Board / UI-07 | AVAILABLE | 1448×1086 | 1223245 | `b204566e4fc9e07512898ceca89d4e75c420cef9defc70755c3a6543d262f666` |
| REF-REC | [konsep2.png](../../../konsep2.png) | Recommendations / UI-06 | AVAILABLE | 1448×1086 | 1452710 | `1b3686be9700257f9eb53b1c2fe1073215d7dc09dc96487b9b547033d6f2b2ee` |
| REF-PDM | [konsep3.png](../../../konsep3.png) | PdM Center / UI-04 | AVAILABLE | 1448×1086 | 1424594 | `77270507fe975b883b9317a46b0580462fd9e06f248920722bea6f2cc8f17b60` |
| REF-ASSET | [konsep4.png](../../../konsep4.png) | Asset Health Detail / UI-03 | AVAILABLE | 1448×1086 | 1322063 | `31082400dc1a501d7924ddd7be4c7865413ae7a9c125290587a979b39f293d57` |
| REF-EXEC | [konsep5.png](../../../konsep5.png) | Executive Overview / UI-01 | AVAILABLE | 1448×1086 | 1287446 | `a6e57d1ca29400b8e62f372b819c3f9875f7949cae2dde1736e874f32583f1ec` |

## Visual mapping verification

- **Action Board (REF-ACTION):** Attention cards above risk and open-finding tables.
- **Recommendations (REF-REC):** Status filters, KPI cards and a recommendation register with WO references.
- **PdM Center (REF-PDM):** Method tabs, distribution/trend panels and findings table.
- **Asset Health Detail (REF-ASSET):** Asset header, summary cards, technical details, PdM summary, WO chart and recommendations.
- **Executive Overview (REF-EXEC):** Portfolio filters, KPI cards, distribution/risk/attention panels and historical chart.

The [UI specification](../NADI-UI-SPEC.md) links these exact root files. Provenance
is the existing Git-tracked artwork plus the Product Owner's FIX-02 designation;
this does not assert a new author, creation date or plant-data origin. The prior
MISSING report described the requested JPG attachments at that checkpoint. It is
resolved by this explicit reference selection, not by inventing replacement files.

## Design evidence boundary

These are official **design inputs**, not accepted equipment-condition evidence.
Illustrated people, assets, dates, counts, scores, classifications, risk formula,
severity labels and standard references do not establish NADI operational facts or
approved engineering policy. DGA appearing in a screenshot does not resolve PD=DGA.
Portable measurements remain episodic; chart styling cannot approve interpolation
or combining incompatible PI/DCS and portable series. Existing factual semantics,
independent review and engineer-validation gates remain authoritative.

Image mapping/availability is verified; implemented UI fidelity, responsive behavior,
contrast, token approval and actual Product Owner UI acceptance remain separate gates.
