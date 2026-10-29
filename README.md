# Flower Welfare

Hackathon 7, Eyes on Earth. Majed Al-Sakkaf and Sandra Wandel.

**What it does:** upload a photo of a flowerbed. A Roboflow object-detection model draws a box around each flower and labels it **Healthy** or **Wilted**, and the app shows the counts and the share of Healthy flowers.
**App:** [`app.py`](app.py) (Streamlit) · **Ethical reflection:** [`ETHICS.md`](ETHICS.md)

## Who it is for, and why SDG 15

**User:** a green-space ecologist at the **Gemeente Den Haag**, which is adding flower meadows and wants nature-friendly mowing of grass and verges [7]. In the flowering season, they use the Healthy share to decide where to **water, delay mowing or reseed first**. It is a first screen, never a reason to remove wilted flowers. **Not for:** private gardeners, plant disease or species diagnosis, or any automatic mowing or clearing decision.

**Why they need it:** Den Haag did not monitor the quality of its green maintenance before 2024, while making more than €225 million available for green since 2016 [8]. About 60% of Dutch municipalities work on ecological verge management [9]. **Why not just a site visit?** Visits stay the final check, but photos let one ecologist triage many beds first.

**SDG 15, target 15.5:** "Take urgent and significant action to reduce the degradation of natural habitats, halt the loss of biodiversity…" [3]. 181 of the 331 Dutch wild bee species (55%) are on the Red List [1], and in the EU 1 in 3 bee, butterfly and hoverfly species is disappearing [2]. Our model only checks visible flower condition, not biodiversity or pollinators.

## Data, model and results

| | |
|---|---|
| **Photos** | 317: 197 from [iNaturalist](https://www.inaturalist.org) (filtered to the Netherlands), 120 from [Wikimedia Commons](https://commons.wikimedia.org) (dead, wilting and dried flowers) [5] |
| **Labelling** | 30 photos by hand; Roboflow auto-labelled the rest, and every auto-label was approved, changed or discarded by hand |
| **Model** | Roboflow RF-DETR Object Detection [6], classes Healthy and Wilted [5] |
| **Split** | 224 train · 65 valid · 28 test photos; training photos augmented to 432 images [5] |
| **Licences** | iNaturalist photos default to CC BY-NC: credit required, no commercial use [4] |
| **Test set** | mAP@50 59.3% · precision 66.2% · recall 53.9% · F1 57.8% [5] |

It misses almost half of the flowers, and about 1 in 3 boxes is wrong. With 28 test images these numbers are rough. In our tests it missed most flowers in a dense heath field and skipped buds.

## How to run

1. `pip install -r requirements.txt`
2. `streamlit run app.py`
3. In the sidebar, enter your Roboflow **private API key** and model ID `hackathon-flowers/1`.
4. Upload a photo and press **Analyze flower image** (needs internet).

## Who did what

Together we thought of the project idea. We selected the best available datasets.  Sandra trained the model and Majed built the app. Sandra Made live demo and wrote the ethical refection while Majed wrote the readme and created thepresentation. 


## Sources

1. Reemer, M. (2018). *Basisrapport voor de Rode Lijst Bijen*, EIS2018-06, via [review on natuurtijdschriften.nl](https://natuurtijdschriften.nl/pub/1025031/HYM2018016001030.pdf)
2. European Commission (24 Jan 2023). [Commission boosts action on pollinators](https://ireland.representation.ec.europa.eu/news-and-events/news/food-security-and-ecosystem-resilience-european-commission-boosts-action-pollinators-2023-01-24_en)
3. United Nations. [SDG target 15.5](https://metadata.un.org/sdg/15.5?lang=ar)
4. iNaturalist Help. [How do licenses work on iNaturalist?](https://help.inaturalist.org/en/support/solutions/articles/151000173511)
5. Roboflow project `hackathon-flowers` v1: COCO dataset export (29 Oct 2026) and test-set metrics
6. Roboflow. [RF-DETR documentation](https://rfdetr.roboflow.com)
7. Gemeente Den Haag. [Stadsnatuur beschermen en versterken](https://www.denhaag.nl/nl/natuur-en-milieu/groen-en-bomen/stadsnatuur-beschermen-en-versterken/)
8. Rekenkamer Den Haag (2025). [Koers op Groen](https://www.rekenkamerdenhaag.nl/wp-content/uploads/2025/09/RIS323316-Raadsvoorstel-rekenkameronderzoek-Koers-op-Groen.pdf)
9. VNG (2025). [Factsheet ecologisch bermbeheer](https://vng.nl/sites/default/files/2025-01/factsheet-ecologisch-bermbeheer.pdf), citing Vlinderstichting 2024
