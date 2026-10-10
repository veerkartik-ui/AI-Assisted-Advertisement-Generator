# AI-Assisted Advertisement Generator

A lightweight Python project that turns a product or campaign brief into a square **1080 × 1080 PNG advertisement concept**.

## Features
- Browser interface powered by Streamlit.
- Keyword-based category detection for fitness, beauty, education, food, technology, and fashion.
- Rule-based suggestions for palette, tagline, visual motif, typography, layout, and call to action.
- PNG output generated with Pillow.
- Command-line interface, automated tests, and a Google Colab notebook.

> **Implementation note:** This version is an offline, rule-based prototype. It does not call an LLM or an image-generation API. The design-strength score is a heuristic indicator, not model accuracy or a statistical probability. Product artwork is vector-style and should be reviewed before commercial use.

## Run locally

Python 3.10 or later is recommended.

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`).

## Generate an ad from the command line

```bash
python advertisement_generator.py --product "PulseFit Protein" --audience "Gym Goers" --requirements "bold, modern, energetic" --output generated_ad.png
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Run in Google Colab
Open `notebooks/colab_demo.ipynb` in [Google Colab](https://colab.research.google.com/). Run the cells from top to bottom; the notebook clones this repository, installs dependencies, generates a PNG, and offers a download.

## Project structure

```text
.
├── advertisement_generator.py
├── app.py
├── requirements.txt
├── tests/
│   └── test_generator.py
└── notebooks/
    └── colab_demo.ipynb
```

## Future improvements
Potential upgrades include LLM-based copy variations, a generative image API, brand-kit uploads, multilingual output, A/B variants, and campaign analytics.
