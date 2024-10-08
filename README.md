# AI Life Coach Assistant

<p align="center">
  <img src="images/life_coach.webp">
</p>

Staying motivated and maintaining a balanced life can be difficult, especially when juggling work, hobbies, and personal growth. Finding the right advice or activities to boost your mood isn't always easy, and professional life coaches aren't always accessible.

The **AI Life Coach Assistant** offers a conversational AI that helps users get personalized advice, recommend activities for boosting happiness, and improve productivity. By providing suggestions on work, communication, lifestyle, and hobbies, it makes life coaching more accessible and enjoyable.

This project was implemented for 
[LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) -
a free course about LLMs and RAG."


## Project overview

**AI Life Coach Assistant** is a virtual life coach designed to boost your mood, inspire productivity, and offer personalized advice across multiple areas of life. Whether you're seeking guidance in work, communication, hobbies, or lifestyle, this assistant will recommend enjoyable activities and tips to enhance your happiness and overall well-being. Through personalized suggestions, it aims to help users feel more fulfilled, motivated, and balanced.

## Dataset

The dataset used in this project is the [`DailyDialog dataset`](https://huggingface.co/datasets/li2017dailydialog/daily_dialog) from Hugging Face, which provides high-quality multi-turn dialog data for training conversational agents. The dataset includes:

- **Dialog:** A list of strings representing conversations, useful for generating personalized advice and recommendations.
- **Act:** A list of classification labels that define the type of dialog act, including:
    - **dummy (0):** Placeholder value.
    - **Inform (1):** Provides information.
    - **Question (2):** Asks a question.
    - **Directive (3):** Gives commands or suggestions.
    - **Commissive (4):** Makes promises or commitments.
- **Emotion:** A list of classification labels representing emotional tone, with possible values:
    - **No emotion (0)**
    - **Anger (1)**
    - **Disgust (2)**
    - **Fear (3)**
    - **Happiness (4)**
    - **Sadness (5)**
    - **Surprise (6)**

This dataset contains 11,118 training samples, which have been used to train the AI Life Coach Assistant in providing context-aware, emotionally responsive advice across various life scenarios.

You can find the data in [`data/daily_dialog`](data/daily_dialog).

## Technologies

   - Python 3.12: Core programming language used for the project.
   - Docker and Docker Compose: Used for containerization, ensuring a consistent environment across different systems.
   - FAISS and Rank-BM25: Employed for efficient full-text search and similarity search to retrieve relevant information.
   - Streamlit: Used for creating an interactive and user-friendly UI.
   - Grafana (not fully implemented): Planned for monitoring, with PostgreSQL as the backend database. The implementation is incomplete due to Grafana's 5-chars restriction.
   - sentence-transformers/all-MiniLM-L6-v2: Used for generating high-quality embeddings for semantic search.
   - Qwen/Qwen2.5-0.5B (via Hugging Face): Utilized for answer generation, data creation, and evaluating answers.
   - Langchain: Applied to handle LLM operations and chaining tasks for better context management in the system.

## Preparation

For dependency management, we use pipenv, so you need to install it:

```bash
pip install pipenv
```

Once installed, you can install the app dependencies:

```bash
pipenv install --dev
```

## Running the application


### Database configuration

Before the application starts for the first time, the database
needs to be initialized.

First, run `postgres`:

```bash
docker-compose up postgres
```

Then run the [`db_prep.py`](life_coach/db_prep.py) script:

```bash
pipenv shell

cd life_coach

export POSTGRES_HOST=localhost
python db_prep.py
```

### Running with Docker-Compose

The easiest way to run the application is with `docker-compose`:

```bash
docker-compose up
```

### Running locally

If you want to run the application locally,
start only postres and grafana:

```bash
docker-compose up postgres grafana
```

If you previously started all applications with
`docker-compose up`, you need to stop the `app`:

```bash
docker-compose stop app
```

Now run the app on your host machine:

```bash
pipenv shell

cd life_coach

export POSTGRES_HOST=localhost
streamlit run app.py
```

## Using the application

When the application is running, we can start using it.
make sure that postgres service is up to store likes/dislikes

```bash
docker-compose up postgres
```
```bash
pipenv run streamlit run app.py
```
## Code

The code for the application is in the [`life_coach`](life_coach/) folder:

- [`app.py`](life_coach/app.py) - the main entry point for the Streamlit application, responsible for the user interface and interaction.
- [`rag.py`](life_coach/rag.py) - contains the main logic for Retrieval-Augmented Generation (RAG), building queries, retrieving data, and constructing prompts.
- [`ingest.py`](life_coach/ingest.py) - responsible for loading data into the knowledge base, ensuring that the assistant has access to relevant information.
- [`db.py`](life_coach/db.py) - manages the logic for logging requests and responses to a PostgreSQL database.
- [`db_prep.py`](life_coach/db_prep.py) - initializes the database and sets up the necessary tables for storing interactions.

### Interface

The application is built using Streamlit, which provides a user-friendly interface for interacting with the AI Life Coach Assistant. 

In the interface, users can provide feedback by using two buttons to rate their experience. This rating is stored in the PostgreSQL database, allowing for ongoing improvements and adjustments based on user input.

Refer to the ["Using the Application" section](#using-the-application) for examples on how to interact with the application.

### Ingestion

The ingestion script is in [`ingest.py`](life_coach/ingest.py).

We load the preindexed data from our experiments, stored in the [`data/dialog_index`](life_coach/data/dialog_index) folder. This ensures that the knowledge base is already populated and ready for efficient querying. The ingestion script is executed at the startup of the application and is called within [`rag.py`](life_coach/rag.py) upon import.

Additionally, we utilize the embedding model `sentence-transformers/all-MiniLM-L6-v2` for generating embeddings, which are then indexed into our vector databases, **FAISS** and **Rank-BM25**. This setup allows for fast and accurate retrieval of relevant information.


## Experiments

For experiments, we use Jupyter notebooks, which are located in the [`notebooks`](notebooks/) folder.

To start Jupyter, run:

```bash
cd notebooks
pipenv run jupyter notebook
```

We have the following notebooks:

  - [`clean_creation_data.ipynb:`](notebooks/clean_creation_data.ipynb) This notebook includes the process of creating ground truth datasets for evaluating our RAG pipeline. We have two approaches for generating ground truth:

      1-  A naive assumption where the last two sentences of a dialog are taken as a question and its answer.

      2-  Using an LLM to extract questions and answers from dialogs, followed by cleaning the output.

    Note: Additional libraries such as matplotlib and seaborn will need to be installed to run this notebook, as they are not included in the Pipfile for a faster application build.

  - [`rag_system_llm_truth.ipynb:`](notebooks/rag_system_llm_truth.ipynb) This notebook evaluates the RAG pipeline using one of the ground truths llm created.

  - [`rag_system_main.ipynb:`](notebooks/rag_system_main.ipynb) This notebook evaluates the system using the two most recent dialogs from the ground truth.

Additionally, we perform three types of searches: vector search, keyword search, and hyper search. For each type of search, we apply hit rate and MRR (Mean Reciprocal Rank) functions. We also use cosine similarity in addition to LLM evaluation to assess the RAG flow.

### Retrieval evaluation
for rag_system_main.ipynb with the two most recent dialogs from the ground truth.
Sparse Search - using `rank-bm25` gave the following metrics:

- Hit rate: 79%
- MRR: 74%
which is better than Dense Search and Hyper Search

for rag_system_llm_truth.ipynb with the ground truths llm created.
Dense Search - using `FAISS` gave the following metrics:

- Hit rate: 55%
- MRR: 35%
which is better than Sparse Search and Hyper Search

so I used Dense Search and found his results better especially when the question was not explicitly in your data

### RAG flow evaluation

We used the LLM-as-a-Judge metric to evaluate the quality
of our RAG flow and the cosine similarity.

for  rag_system_main.ipynb notebook

For `Qwen/Qwen2.5-0.5B-Instruct`, in a sample with 100 records, we had:

- 95 (95%) `PARTLY_RELEVANT`
- 4 (4%) `RELEVANT`
- 1 (1%) `NON_RELEVANT`

with cosine similarity, in a sample with 100 records, we had:

- 0.271979  `mean` 
- 0.206015  `std`
- 0.219197  `median`

for  notebooks/rag_system_llm_truth notebook

For `Qwen/Qwen2.5-0.5B-Instruct`, in a sample with 105 records, we had:

- 98 (93%) `PARTLY_RELEVANT`
- 6 (6%) `RELEVANT`
- 1 (0.1%) `NON_RELEVANT`

with cosine similarity, in a sample with 100 records, we had:

- 0.349225  `mean` 
- 0.203658  `std`
- 0.341583  `median`

The difference is minimal, so we opted for `Qwen/Qwen2.5-0.5B`.

## Monitoring

We use Grafana for monitoring the application, and it’s set up in the Docker-Compose configuration. While the Grafana instance is up and running, the dashboard setup is not fully completed yet.

Grafana is accessible at [localhost:3000](http://localhost:3000):

- **Login:** "admin"
- **Password:** "admin"

The next steps involve completing the configuration of the dashboard to track key metrics and monitor the application's performance in real time.


## Acknowledgements

I would like to express my sincere gratitude to the creators and instructors of this amazing course. Your dedication, expertise, and passion for teaching have made learning about LLMs and Retrieval-Augmented Generation (RAG) an engaging and invaluable experience.

A special thank you to the course organizers for creating a supportive learning environment. Your efforts have empowered me to dive deep into this fascinating field, and I truly appreciate all the hard work that went into making this course possible.

Thank you for the knowledge, guidance, and inspiration throughout the journey!
