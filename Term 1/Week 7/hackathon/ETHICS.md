# Ethical reflection: Flower Welfare

## Data card

| | |
|---|---|
| **What** | 317 unique photos of flowers; 4,035 Healthy and 1,421 Wilted boxes (training boxes include augmented copies) [2] |
| **How collected** | 197 photos from [iNaturalist](https://www.inaturalist.org), filtered to the Netherlands and open flowers. 120 photos from [Wikimedia Commons](https://commons.wikimedia.org) (dead, wilting and dried flower categories), because iNaturalist had few wilted flowers [2] |
| **Labelling** | We labelled 30 photos by hand. Roboflow auto-labelled the rest, then we approved, changed or discarded each auto-label |
| **Model** | Roboflow RF-DETR Object Detection [3], 2 classes (Healthy, Wilted) [2] |
| **Split** | 224 train · 65 valid · 28 test photos; training photos augmented to 432 images [2] |
| **Licences** | iNaturalist photos are CC BY-NC by default (credit required, no commercial use), but users can choose other licences, including all rights reserved [1]. We use the photos only in this non-commercial student project, and every photo can be traced back to its source: iNaturalist file names keep the observation and photo IDs, and Commons file names keep most of the original file title [2] |
| **Results** | Test set: mAP@50 59.3%, precision 66.2%, recall 53.9%, F1 57.8% [2] |

## Reflection

We built a model that labels flowers in a photo as Healthy or Wilted, so a green-space ecologist at the Gemeente Den Haag can decide which flower meadows and verges to check first [4]. The main weakness is in the data. In our dataset export, 3,617 of the 4,035 Healthy boxes (90%) are in iNaturalist photos and 933 of the 1,421 Wilted boxes (66%) are in Wikimedia Commons photos [2]. So the two classes differ in more than wilting: different photographers, cameras and backgrounds. The model may partly learn *which site a photo came from* instead of *whether a flower is wilted*, and a 59.3% mAP on only 28 test images cannot rule that out [2]. The classes are also unbalanced: Healthy boxes outnumber Wilted almost 3 to 1, and the test set has 254 Healthy against 69 Wilted boxes, so the scores mostly tell us how well it finds Healthy flowers. Recall of 53.9% means it misses almost half of the flowers. In our own tests it boxed only a few dozen flowers in a dense heath field and ignored buds, so counts and the Healthy share can be badly off exactly where there are many flowers. If someone used it for real decisions, two things could go wrong. A bed could be wrongly flagged as "mostly wilted" and mown or cleared, while seed heads and dry stems actually feed birds and shelter insects. Or a bed in real trouble could look fine because its flowers were never detected. It must stay a first screen that tells someone where to look, never a decision on its own. Before any real use, we would take our own photos for both classes, test on far more than 28 images, and check the licence of every photo.

## Sources

1. iNaturalist Help. [How do licenses work on iNaturalist?](https://help.inaturalist.org/en/support/solutions/articles/151000173511)
2. Roboflow project `hackathon-flowers`, version 1: COCO dataset export (29 Oct 2026) and test-set metrics.
3. Roboflow. [RF-DETR documentation](https://rfdetr.roboflow.com)
4. Gemeente Den Haag. [Stadsnatuur beschermen en versterken](https://www.denhaag.nl/nl/natuur-en-milieu/groen-en-bomen/stadsnatuur-beschermen-en-versterken/)
