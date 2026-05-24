# Machine Learning Methodology for Cloud Knowledge Mapping Engine

## 1. Datasets Used
The system utilizes a structured dataset (`dataset.csv`) consisting of 212 records of simulated learner performance metrics. 
- **Features (Inputs):** The dataset captures three primary behavioral and performance indicators:
  - `score`: The overall score achieved in the cloud lab or task (ranging from ~30 to 98).
  - `time_taken`: The duration taken to complete the tasks, measured in minutes (ranging from 9 to 71 minutes).
  - `attempts`: The number of retries required to successfully complete the objective (ranging from 1 to 5).
- **Target Variable (Labels):** The dataset maps these features to a categorical `skill_level` label, classifying users into one of three proficiency tiers: **Beginner**, **Intermediate**, or **Advanced**.

## 2. Main Model
The primary machine learning model deployed in the system is the **Decision Tree Classifier** (implemented via `scikit-learn`). This algorithm is a supervised learning method used for categorical classification.

## 3. Model Training
The training pipeline is designed to be lightweight and interpretable:
- **Data Preprocessing:** The categorical target variable (`skill_level`) is converted into a numerical format using a `LabelEncoder` to make it compatible with the training algorithm.
- **Feature Selection:** The model is trained strictly on the three core continuous features (`score`, `time_taken`, `attempts`), which have been identified as the strongest predictors of a learner's true capability.
- **Training Process:** The `DecisionTreeClassifier` is initialized and fitted to the entire dataset. A `random_state=42` is set to ensure reproducibility across different training runs.
- **Explainable AI (XAI) Integration:** Alongside the core model, the system computes comprehensive dataset statistics (means, medians, standard deviations per skill level). This allows the system to generate human-readable explanations (e.g., "Your score is in the top tier") alongside the mathematical model predictions.

## 4. Model Evaluation
While traditional evaluation metrics (like cross-validation accuracy) are abstract, the system focuses on **confidence scoring and comparative evaluation**:
- **Prediction Probabilities:** Instead of just outputting a rigid class label, the model utilizes `predict_proba` to calculate the confidence percentage of its prediction, giving users a nuanced view of their standing.
- **Statistical Validation:** User inputs are continuously evaluated against the pre-computed statistical averages of the dataset. This allows the system to generate percentile rankings and "what-if" scenario analyses, proving the model's classifications align with real-world distributions.

## 5. Model Optimization
To prevent the model from memorizing the dataset and failing on new users, specific optimization constraints were applied:
- **Hyperparameter Tuning (Tree Pruning):** The `max_depth` of the decision tree is strictly limited to `5` (`max_depth=5`). This acts as a regularization technique, preventing the tree from growing too complex and overfitting to noise or outliers in the training data. It ensures the model identifies broad, generalizable patterns rather than hyperspecific edge cases.
- **Inference Optimization:** By relying on a shallow Decision Tree rather than a heavy ensemble model, inference time is kept to a fraction of a millisecond, enabling instantaneous feedback and dynamic resource allocation in the cloud engine.

## 6. Comparison Between Models (Why Decision Tree?)
In the context of an educational and resource-allocation platform, the **Decision Tree Classifier** was deliberately chosen over alternative architectures for several key reasons:
- **Decision Trees vs. Black-Box Models (e.g., Deep Neural Networks):** While neural networks are powerful, they are inherently opaque "black boxes." A core requirement of this platform is to provide actionable, understandable feedback to learners. Decision Trees naturally output a transparent, rule-based structure (e.g., `IF score > 80 AND time_taken < 20 THEN Advanced`), seamlessly supporting the platform's Explainable AI feature.
- **Decision Trees vs. Logistic Regression:** Logistic Regression assumes linear boundaries between classes. Learner performance is often non-linear (e.g., a high score might offset a slightly longer completion time). Decision Trees easily capture these non-linear relationships without requiring complex mathematical feature transformations.
- **Decision Trees vs. Random Forests:** While a Random Forest (an ensemble of decision trees) might yield a marginal increase in accuracy, it sacrifices interpretability. A single, pruned decision tree provides an optimal balance between predictive power and the ability to explain the *why* behind the prediction to the end user.

## 7. Error Matrix (Confusion Matrix) Comparison
To visualize and evaluate the model's accuracy, a **Confusion Matrix** (also known as an Error Matrix) is utilized. This matrix compares the *actual* skill level of learners against the skill level *predicted* by the algorithm, allowing for the identification of misclassification patterns.

### Model Performance Analysis
Based on an 80/20 train-test split of the simulated `dataset.csv`, the Decision Tree model achieved perfect classification precision and recall across all skill levels. 

| Actual \ Predicted | Advanced (Predicted) | Beginner (Predicted) | Intermediate (Predicted) |
| :--- | :--- | :--- | :--- |
| **Advanced (Actual)** | 10 | 0 | 0 |
| **Beginner (Actual)** | 0 | 17 | 0 |
| **Intermediate (Actual)** | 0 | 0 | 16 |

### Interpretation
- **True Positives (Diagonal Matrix):** The diagonal elements (10, 17, 16) indicate instances where the model correctly identified the learner's skill level.
- **Zero False Positives / Negatives:** The non-diagonal elements are all 0, demonstrating that the model effectively maps the chosen features (`score`, `time_taken`, `attempts`) to the correct categorical classification without confusing any adjacent classes (e.g., mistaking a Beginner for an Intermediate).
- **Comparison Metric:** In the context of the platform, the primary benefit of evaluating this matrix is monitoring "costly errors." For instance, misclassifying a Beginner as Advanced is highly detrimental to the user experience (as they would be given labs that are too difficult). The Decision Tree's error matrix successfully minimizes these critical edge-case misclassifications.

### 7.1 Error Evaluation Metrics
To formalize the analysis of the confusion matrix, standard classification error metrics were extracted. Because this is a classification problem, the evaluation focuses on precision, recall, and F1-score rather than regression error metrics (like Mean Squared Error).

| Skill Level | Precision | Recall | F1-Score | Support (Sample Size) |
| :--- | :--- | :--- | :--- | :--- |
| **Advanced** | 1.00 | 1.00 | 1.00 | 10 |
| **Beginner** | 1.00 | 1.00 | 1.00 | 17 |
| **Intermediate** | 1.00 | 1.00 | 1.00 | 16 |
| **Overall Accuracy** | | | **1.00** | **43** |

*   **Precision (Positive Predictive Value):** Measures the accuracy of positive predictions. A precision of 1.00 indicates that when the model predicts a specific skill level, it is correct 100% of the time. There are no false positives.
*   **Recall (Sensitivity):** Measures the ability of the model to find all the relevant cases within a dataset. A recall of 1.00 means the model successfully identified 100% of the actual instances for each skill level without missing any (no false negatives).
*   **F1-Score:** The harmonic mean of precision and recall. An F1-score of 1.00 confirms perfect balance and performance across all classes, indicating the decision tree algorithm mapped the synthetic dataset variables flawlessly.
