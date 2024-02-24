# Dream Writer

## Deploy

Install the package:

```
pip install .
```

If you want to self-host the embedding service, you should install the package with the `emb_server` extra:

```
pip install ".[emb_server]"
```

Now you can start the self-host embedding service:

```
python src/emb_server.py
```

Then import the environment variable:

```
export EMBEDDING_SERVICE_BASE="http://localhost:8000"
export EMBEDDING_SERVICE_MODEL="intfloat/multilingual-e5-large"
export GOOGLE_API_KEY="your-google-api-key"
```

> Without self-host embedding service, the code will use OpenAI embedding API. No need to set the `EMBEDDING_SERVICE_BASE` and `EMBEDDING_SERVICE_MODEL` environment variables, but:
>
> ```
> export OPENAI_API_KEY="your-openai-api-key"
> ```

Finally, run the app:

```
streamlit run src/webui/main.py
```
