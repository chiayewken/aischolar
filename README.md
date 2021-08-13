## AI Scholar

### Usage

```
pip install -r requirements.txt
bash setup_data.sh
streamlit run main.py
```

### Deploying to Heroku

```
heroku container:login
heroku container:push --app <your-app-name> web
heroku container:release --app <your-app-name> web
```