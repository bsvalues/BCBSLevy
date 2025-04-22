# Data Dictionary

This document provides a comprehensive description of all database models and fields used in the SaaS Levy Calculation Application.

## Property

The `Property` model represents a property in the tax system with assessed value and tax code information.

| Field          | Type       | Description                                 | Constraints                   |
| -------------- | ---------- | ------------------------------------------- | ----------------------------- |
| id             | Integer    | Primary key                                 | Auto-increment                |
| property_id    | String(64) | Unique identifier for the property          | Unique, Non-null, Indexed     |
| assessed_value | Float      | Dollar value assigned to the property       | Non-null                      |
| tax_code       | String(20) | Tax code area where the property is located | Non-null, Indexed             |
| created_at     | DateTime   | Timestamp when the record was created       | Default: UTC now              |
| updated_at     | DateTime   | Timestamp when the record was last updated  | Default: UTC now, Auto-update |

## TaxCode

The `TaxCode` model represents a tax code area with levy information.

| Field                | Type       | Description                                                  | Constraints                   |
| -------------------- | ---------- | ------------------------------------------------------------ | ----------------------------- |
| id                   | Integer    | Primary key                                                  | Auto-increment                |
| code                 | String(20) | Tax code identifier                                          | Unique, Non-null, Indexed     |
| levy_amount          | Float      | Total levy amount in dollars                                 | Nullable                      |
| levy_rate            | Float      | Rate per $1,000 of assessed value                            | Nullable                      |
| previous_year_rate   | Float      | Previous year's levy rate for statutory limit calculations   | Nullable                      |
| total_assessed_value | Float      | Total assessed value of all properties in this tax code area | Nullable                      |
| created_at           | DateTime   | Timestamp when the record was created                        | Default: UTC now              |
| updated_at           | DateTime   | Timestamp when the record was last updated                   | Default: UTC now, Auto-update |

## TaxDistrict

The `TaxDistrict` model represents a tax district with levy code relationships.

| Field            | Type       | Description                                | Constraints                   |
| ---------------- | ---------- | ------------------------------------------ | ----------------------------- |
| id               | Integer    | Primary key                                | Auto-increment                |
| tax_district_id  | Integer    | Identifier for the tax district            | Non-null, Indexed             |
| year             | Integer    | Tax year                                   | Non-null, Indexed             |
| levy_code        | String(20) | Levy code                                  | Non-null, Indexed             |
| linked_levy_code | String(20) | Related levy code                          | Non-null, Indexed             |
| created_at       | DateTime   | Timestamp when the record was created      | Default: UTC now              |
| updated_at       | DateTime   | Timestamp when the record was last updated | Default: UTC now, Auto-update |

**Unique Constraint**: (`tax_district_id`, `year`, `levy_code`, `linked_levy_code`)

## ImportLog

The `ImportLog` model logs import operations for auditing and tracking.

| Field         | Type        | Description                                   | Constraints      |
| ------------- | ----------- | --------------------------------------------- | ---------------- |
| id            | Integer     | Primary key                                   | Auto-increment   |
| filename      | String(255) | Name of the imported file                     | Non-null         |
| rows_imported | Integer     | Number of rows successfully imported          | Non-null         |
| rows_skipped  | Integer     | Number of rows skipped during import          | Non-null         |
| warnings      | Text        | Warning messages from the import process      | Nullable         |
| import_date   | DateTime    | Timestamp when the import occurred            | Default: UTC now |
| import_type   | String(50)  | Type of import ('property', 'district', etc.) | Nullable         |

## ExportLog

The `ExportLog` model logs export operations for auditing and tracking.

| Field         | Type        | Description                        | Constraints      |
| ------------- | ----------- | ---------------------------------- | ---------------- |
| id            | Integer     | Primary key                        | Auto-increment   |
| filename      | String(255) | Name of the exported file          | Non-null         |
| rows_exported | Integer     | Number of rows exported            | Non-null         |
| export_date   | DateTime    | Timestamp when the export occurred | Default: UTC now |

## Relationships

### Property and TaxCode

- A `Property` belongs to a `TaxCode` via the `tax_code` field
- A `TaxCode` can have many `Property` records

### TaxDistrict and TaxCode

- A `TaxDistrict` relates `levy_code` to `linked_levy_code`
- These codes correspond to entries in the `TaxCode` table

## Data Flow

1. Property data is imported, creating `Property` records
2. Tax code totals are updated, aggregating assessed values in the `TaxCode` table
3. Tax district relationships are imported, creating `TaxDistrict` records
4. Levy amounts are entered for tax codes, updating the `TaxCode` table
5. Levy rates are calculated based on assessed values and levy amounts
6. Property taxes are calculated using levy rates and individual assessed values

## Calculation Formulas

### Levy Rate Calculation

```
levy_rate = (levy_amount / total_assessed_value) * 1000
```

### Statutory Limits

1. 101% Cap:

```
if previous_year_rate exists:
    max_rate = previous_year_rate * 1.01
    if levy_rate > max_rate:
        levy_rate = max_rate
```

2. $5.90 Maximum Rate:

```
if levy_rate > 5.90:
    levy_rate = 5.90
```

### Property Tax Calculation

```
property_tax = (assessed_value / 1000) * levy_rate
```

## Import/Export Format Specifications

### Property Import CSV Format

Required columns:

- `property_id`
- `assessed_value`
- `tax_code`

### Tax District Import Formats

#### Text Format (tab-delimited)

- Column 1: `tax_district_id`
- Column 2: `year`
- Column 3: `levy_code`
- Column 4: `linked_levy_code`

#### XML Format

```xml
<TaxDistricts>
  <District>
    <ID>123</ID>
    <Year>2023</Year>
    <LevyCode>00120</LevyCode>
    <LinkedLevyCode>00121</LinkedLevyCode>
  </District>
  <!-- More district entries -->
</TaxDistricts>
```

#### Excel Format

Sheet with columns:

- `tax_district_id`
- `year`
- `levy_code`
- `linked_levy_code`

### Tax Roll Export Format (CSV)

Columns:

- `property_id`
- `assessed_value`
- `tax_code`
- `levy_rate`
- `calculated_tax`
