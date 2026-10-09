# Licence Selection Note

> **Status: no licence chosen.** This file stands in for `LICENSE` until the project owner decides (decision D-03). Until a licence file is added, the default applies: **all rights reserved** by the authors. Others may view the repository if it is published, but have no permission to copy, modify, or redistribute the code.

## Why the decision is open

The proposal suggests "a perpetual local-software license, optional upgrades, and support services" as a possible business model (P§15.10), and the project will also be presented for academic and technical review. These goals pull in different directions, so the choice needs the owner's explicit decision.

## Questions to answer first

1. Will LocalLoop be sold, open-sourced, or both (open core or dual licensing)?
2. Will outside contributors be accepted? If so, is a Contributor License Agreement (CLA) or Developer Certificate of Origin (DCO) needed to keep relicensing options open?
3. Do academic requirements (university or adviser policies) constrain ownership or licensing?
4. Should others be allowed to offer LocalLoop as a competing product?

## Options

| Option | What it allows | Fits when | Watch out for |
|---|---|---|---|
| Keep proprietary (all rights reserved) | Nothing beyond viewing | Commercial plans, not ready to decide | Discourages contributions and reuse |
| Source-available (for example Business Source License, Functional Source License, PolyForm) | Reading and limited use; commercial competition restricted | Commercial product with transparent code | Not open source by OSI definition; terms vary |
| Apache-2.0 | Broad use, modification, redistribution; explicit patent grant | Open-source project seeking adoption | Competitors may build on it commercially |
| MIT | Very broad use with minimal conditions | Maximum adoption, simple terms | No explicit patent grant |
| MPL-2.0 | File-level copyleft; modified files must stay open | Balance between openness and commercial embedding | Less familiar to some users |
| GPL-3.0 / AGPL-3.0 | Strong copyleft (AGPL also covers network use) | Keep derivatives open | Limits proprietary embedding; affects dual-licensing strategy |
| Dual licensing (copyleft + commercial) | Open use under copyleft; paid licence for proprietary use | Open project with revenue | Requires owning all copyrights (CLA) |

## Third-party licences to check before deciding

The final choice must be compatible with dependencies that ship in the product. Verify current licence terms at selection time; the list below reflects the proposed stack and may be out of date.

| Component | Commonly published under | Note |
|---|---|---|
| Tauri | MIT / Apache-2.0 | Permissive |
| React | MIT | Permissive |
| llama.cpp | MIT | Permissive |
| Playwright | Apache-2.0 | Permissive; bundled browsers have their own licences |
| Tesseract OCR | Apache-2.0 | If chosen (EV-06) |
| PDFium | BSD-3-Clause / Apache-2.0 | If chosen |
| MuPDF | AGPL-3.0 or commercial | Avoid unless the AGPL or a commercial licence is acceptable |
| SQLCipher (community) | BSD-style | If chosen (D-07) |
| Local models (GGUF) | Varies widely | Some restrict commercial use or require attribution; record each in the model registry (FR-108, AIC-09) |

## Recommendation

Decide before making the repository public. If commercial use is likely, keep the repository private or proprietary until the business model is clearer, and adopt a CLA before accepting outside contributions. If the main goal is open collaboration and academic visibility, Apache-2.0 is a common choice for its explicit patent grant.

When decided: add `LICENSE`, update the README licence section, add licence headers if required, and record the decision in an ADR.
