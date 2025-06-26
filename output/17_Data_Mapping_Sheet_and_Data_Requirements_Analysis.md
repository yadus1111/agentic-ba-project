# Data Mapping Sheet and Data Requirements Analysis

| Source Data         | Data Element             | Target Data      | Data Transformation                               | Data Type          |
|----------------------|--------------------------|-------------------|-------------------------------------------------|----------------------|
| Customer Database   | Customer ID               | Loan Application  | Direct mapping                                    | Integer             |
| Customer Database   | Income                   | Loan Application  | Direct mapping                                    | Decimal             |
| Customer Database   | Credit Score              | Loan Application  | Direct mapping                                    | Integer             |
| Transaction History | Spending Patterns         | Loan Offer        | Aggregate spending, identify loan suitability       | JSON                |
| Loan Product Catalog | Loan Product Details      | Loan Offer        | Matching customer profile with relevant products | JSON                |