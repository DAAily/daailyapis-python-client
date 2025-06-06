# Product Scoring System Documentation

## Overview

The Product Scoring System is a comprehensive evaluation framework that assesses product data quality across multiple dimensions. It combines weighted scoring of various product attributes to generate a final quality score between 0 and 1, helping identify areas for improvement in product information.

## Table of Contents

1. [Scoring Architecture](#scoring-architecture)
2. [Field Weights](#field-weights)
3. [Scoring Methods](#scoring-methods)
4. [Text Scoring](#text-scoring)
5. [Score Calculation](#score-calculation)
6. [Dependencies](#dependencies)

## Scoring Architecture

The system uses a modular approach where each product field is evaluated independently and then combined using weighted averaging. The main components are:

- **Client Base Class**: Provides core scoring functionality and text analysis tools
- **Product Scorer**: Implements specific scoring logic for each product field
- **Score Models**: Data structures for storing results and intermediate calculations

## Field Weights

The scoring system evaluates products across 15 different fields, each with a specific weight:

| Field | Weight | Description |
|-------|--------|-------------|
| **images** | 20.0% | Product images (main, gallery, dimension) |
| **text_en** | 20.31% | English product description |
| **text_de** | 20.3% | German product description |
| **attributes** | 10.0% | Product attributes (materials, dimensions, features) |
| **family_id** | 4.67% | Product family association |
| **group_ids** | 4.67% | Product group associations |
| **collection_ids** | 4.67% | Product collection associations |
| **live_link** | 4.67% | Active product link |
| **prices** | 2.33% | Product pricing information |
| **pdfs** | 2.33% | Product documentation |
| **cads** | 2.33% | CAD files |
| **internal_number** | 0.93% | Internal product identifier |
| **text_es** | 0.93% | Spanish product description |
| **text_fr** | 0.93% | French product description |
| **text_it** | 0.93% | Italian product description |

**Total**: 100% (weights sum to 1.0)

## Scoring Methods

### 1. Binary Scoring (0 or 1)

Simple presence/absence checks used for:
- `internal_number`, `article_number`, `launch_date`, `design_year`
- `family_id`, `family_name`, `category`, `master_variant_name`
- `live_link`, `3D` (pcon_config or emersya_config)

**Score**: 1 if field exists and has value, 0 otherwise

### 2. Count-Based Scoring

Uses `compute_score()` function for fields with multiple values:
- `designer_names`, `group_ids`, `collection_ids`, `collection_names`
- `materials`, `dimensions`, `prices`, `pdfs`, `cads`

**Scoring Logic**:
```python
if count > target_count: return 1.0
elif count == 0: return 0.0
else: return 0.8
```

### 3. Image Scoring

Complex evaluation based on image types, quality, and completeness:

**Image Type Weights**:
- **pro-b** (Main image): 50% - Critical product representation
- **pro-g** (Gallery images): 30% - Additional views (0.06 per image, max 5)
- **pro-d** (Dimension image): 20% - Technical specifications

**Quality Factors**:
- Penalizes low-resolution images (-0.05 per image)
- Requires online status for consideration
- Perfect score needs: 1 main image, 5+ gallery images, 1 dimension image

### 4. Attribute Scoring

Evaluates attribute diversity and completeness:

**Scoring Components**:
- **Diversity** (60%): Variety of attribute types (max 7 types)
- **Critical Types** (30%): Material, dimension, feature (0.1 each)
- **Primary Dimensions** (10%): Height, width, length/depth/breadth

**Attribute Types**:
- base, category, certification, color, dimension, feature, material

### 5. Text Scoring

Most sophisticated scoring combining multiple linguistic analyses:

**Components & Weights**:
- **Content Quality** (60%): Semantic similarity to ideal topics
- **Readability** (20%): Flesch reading ease score
- **Spelling** (10%): Percentage of correctly spelled words
- **Grammar** (10%): Grammatical correctness

#### Semantic Similarity Topics

Each language has specific topics with weights:

| Topic | Weight | Focus |
|-------|--------|-------|
| **Benefits** | 35% | Product advantages and problem-solving |
| **Design Concept** | 25% | Philosophy and designer intent |
| **Experience** | 25% | User experience and atmosphere |
| **Context** | 15% | Relation to environment and trends |

#### Language-Specific Features

**Supported Languages**: English, German, Spanish, French, Italian

**Flesch Reading Ease Formulas**:
- **English**: 206.835 - (1.015 × words/sentence) - (84.6 × syllables/word)
- **German**: 180 - (1.0 × words/sentence) - (58.5 × syllables/word)
- **Italian**: 217 - (1.3 × words/sentence) - (60.0 × syllables/word)
- **French**: 207 - (1.015 × words/sentence) - (73.6 × syllables/word)
- **Spanish**: 206.835 - (1.02 × words/sentence) - (60.0 × syllables/word)

## Score Calculation

### Final Score Formula

```python
final_score = Σ(field_score × field_weight)
```

Where:
- `field_score` is between 0 and 1
- `field_weight` is the predefined weight for that field
- Sum of all weights equals 1.0

### Score Result Structure

Each field returns a `ScoreResult` containing:
- **score**: Numerical score (0-1)
- **weight**: Field weight
- **details**: Rich scoring information (richness, completeness, etc.)
- **issues**: Identified problems (missing data, quality issues)

### Example Score Calculation

For a product with:
- Perfect images (1.0) × 20% = 0.20
- Good English text (0.8) × 20.31% = 0.1625
- Missing German text (0.0) × 20.3% = 0.00
- Some attributes (0.6) × 10% = 0.06

Partial score = 0.20 + 0.1625 + 0.00 + 0.06 = 0.4225

## Dependencies

### Required Python Packages

```python
# Core dependencies
google-cloud-language  # Grammar checking
sentence-transformers  # Semantic similarity
spellchecker          # Spelling verification
```

### External Services

- **Google Cloud Natural Language API**: Grammar analysis
- **Sentence Transformers**: Using `distiluse-base-multilingual-cased-v1` model
- **Local Spell Check Dictionaries**: JSON files for each supported language

## Usage Example

```python
from daaily.score.client import Product
from daaily.score.constants import PRODUCT_WEIGHTS

# Initialize scorer with default weights
scorer = Product(score_weights=PRODUCT_WEIGHTS)

# Score a product
product_data = {
    "images": [...],
    "text_en": "Product description...",
    "attributes": [...],
    # ... other fields
}

score_summary = scorer.score(product_data)
print(f"Total Score: {score_summary.sum_score}")

# Access individual field scores
for result in score_summary.score_results:
    print(f"{result.field_name}: {result.score}")
```

## Best Practices for High Scores

1. **Images**: Include at least 1 main image, 5 gallery images, and 1 dimension image
2. **Text**: Write comprehensive descriptions covering benefits, design, experience, and context
3. **Attributes**: Provide diverse attributes including materials, dimensions, and features
4. **Completeness**: Fill all available fields, even those with lower weights
5. **Quality**: Ensure high-resolution images and well-written, error-free text

## Score Interpretation

- **0.9-1.0**: Excellent product data quality
- **0.7-0.9**: Good quality with minor improvements needed
- **0.5-0.7**: Acceptable but significant gaps exist
- **Below 0.5**: Poor quality requiring substantial improvement