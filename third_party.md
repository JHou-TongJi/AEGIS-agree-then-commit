# Third-Party Components, Data and Licences

This repository contains only the project's own code, configuration and derived data. It copies no
third-party model weights or external code repositories. Anyone reproducing the work should obtain
each component from its official channel and treat the **current licence text** published there as
authoritative.

| Component | Use in this project | Official source | Licence and boundary of use |
| --- | --- | --- | --- |
| Tesseract OCR 4.1 | Channel 1: LSTM character recogniser, called as an external program | [GitHub](https://github.com/tesseract-ocr/tesseract) | Apache-2.0. Installed as a system package; not redistributed here. |
| EasyOCR 1.7 | Channel 2: CRAFT detector and CRNN recogniser | [GitHub](https://github.com/JaidedAI/EasyOCR) | Apache-2.0. Installed with `pip`; its models are downloaded on first use and are not redistributed here. |
| SmolVLM-256M-Instruct | Channel 3: vision-language model | [Hugging Face](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) | Licence as stated on the model card (Apache-2.0 at the time of writing; re-check before use). Weights are loaded from a local copy and are not redistributed here. |
| PyTorch, Transformers | Run the vision-language model (acquisition only) | [PyTorch](https://pytorch.org/), [Transformers](https://github.com/huggingface/transformers) | Their own licences; installed as dependencies, not redistributed. |
| Poppler (`pdftoppm`) | Render PDFs to images | [poppler.freedesktop.org](https://poppler.freedesktop.org/) | GPL; used as an external program. |
| pdfplumber | Text layer and word boxes of the source PDFs (acquisition only) | [GitHub](https://github.com/jsvine/pdfplumber) | MIT. |
| NumPy, pandas, Matplotlib, OpenCV, Pillow | Analysis and figures | their official sites | BSD-style / Apache-2.0 / HPND licences; installed with `pip`. |
| Conformal risk control (Angelopoulos et al.) | Method implemented in `src/aegis/crc.py` | [arXiv:2208.02814](https://arxiv.org/abs/2208.02814) | The method is cited; no third-party code is copied. |
| Source problem sheets and issue list | The documents that were read | Plant data, not public | Used under the plant's data-use agreement; **not distributed**. Only derived readings and masked pages are released — see `docs/data-compliance.md`. |

Citing a paper, model or open-source implementation here does not constitute authorisation for its
data, weights, trademarks or commercial deployment. If the end use goes beyond research and
reproduction, complete a separate data-compliance, software-licence and model-licence review.
