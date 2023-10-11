# rssClassifier_Microservice
Classify SQLite article titles using transformer embeddings from the Transformers library. Features dynamic SQLite updates, customizable thresholds, and option to save embeddings.

# SQLite Title Classifier with Transformers

An automated tool for classifying article titles stored in an SQLite database using transformer-based embeddings. Utilizes the Transformers library to generate embeddings for each title and performs similarity comparisons to classify them based on pre-defined classes.

Features:

Uses embeddings from the transformer model "thenlper/gte-small".
Classifies titles based on cosine similarity with predefined class embeddings.
Supports dynamic SQLite table structure with automatic schema updates for classification.
Provides flexibility with a threshold parameter to control the classification confidence.
Option to store the generated embeddings back in the SQLite database.
Incremental update functionality to track progress.
Usage:

Setup your environment with the necessary libraries.
Define your classes and the SQLite database path.
Run the classify_titles_from_db() function to classify titles and store results in the database.
