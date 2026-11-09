# Data Compliance Statement

## 1. Source of the data and preconditions for use

The documents behind this work are production quality documents of a battery-electric vehicle
plant: seven problem sheets (the plant's standard corrective-action form) and one issue master
list. They are confidential, belong to the plant, and were read inside the authorised environment
under a data-use agreement. This statement does not replace that agreement; where the two differ,
the agreement governs.

## 2. Key constraints observed

1. The source documents, their page renders and any text copied from them stay inside the
   authorised environment and are never published.
2. Anything released was derived, and prepared so that the source cannot be reconstructed from it
   (section 3).
3. No attempt is made — and none is permitted — to recover masked content, or to identify the
   plant, its products or projects, or any person named on the documents.
4. The released material is for research and reproduction of the paper's results only.

## 3. What is in the repository and what is not

| Data category | In the repository | Handling |
|---|---|---|
| Source problem sheets (PDF), issue list (spreadsheet) | No | Read only inside the authorised environment |
| Page renders and crops of the source pages | No, except the eight crops of the paper's figures | Eight small crops of numeric callouts only |
| Recognised text of the 344-token second set | No (`local/`, git-ignored) | It contains the documents' wording; only aggregate results derived from it are released |
| Per-read canonical values of the 54 numeric callouts (3 channels × 16 renderings) | Yes (`data/callouts/`) | Numbers only: a measured deviation in millimetres carries no wording and no identifier |
| Reference values and callout geometry | Yes | Numbers and rectangles |
| Structural columns of the 122-row issue list | Yes (`data/masterlist/`) | Lengths, presence flags, calendar week, traffic light, status, zone; no free text, no names |
| Four page images | Yes (`data/masked/`) | Plant mark, project and product names, person names, department codes and part numbers covered before export |
| Code, aggregate results, figure scripts | Yes | Contain no document content |

## 4. Disclosure boundary for the masked images

The masked pages exist to show what the documents look like and what the test bed is. They are
licensed CC BY-NC 4.0 for research and reproduction ([`LICENSE-DATA`](../LICENSE-DATA)). Do not:

- republish them as a dataset, or present them as a recording from any particular plant or
  vehicle programme;
- try to read, reconstruct or infer the content under the masks;
- use them, or anything in `data/`, to identify a person, a supplier, a product or a project.

## 5. Privacy

The work processes numeric measurement callouts and page structure. It performs no person
identification, no biometric processing and no tracking of individuals. Photographs on the source
sheets (defect and assembly close-ups) appear only inside the four masked page images, at page
resolution; no photograph is released separately.

## 6. Veracity boundary

The released readings are the outputs of three engines on renderings of one measurement page, and
a second set of tokens from seven sheets. They are suitable for studying how reading channels fail
and how agreement and conformal risk control behave. They are **not**:

- a benchmark of OCR engines in general (the channels are configured by the authors);
- measurements of any vehicle, usable for quality, safety or compliance decisions;
- evidence about the correctness of the plant's own records (the reference is the document's text
  layer and a hand transcription, which establish transcription fidelity only).

## 7. Third-party components

Licences and sources of the software and models used are listed in
[`third_party.md`](../third_party.md). None of their code or weights is redistributed here.
