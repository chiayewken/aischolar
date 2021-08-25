## AI Scholar
Aim to help AI researchers search papers more efficiently, it **only** contains the most updated AI papers from top conferences and journals.
[Website](http://aischolar.academy/)

#### Search with Alfred
This website supports alfred web search with link `https://aischolar.herokuapp.com/?query={query}`

### Hosting AI Scholar

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

### Contributing
We are open to suggestions on how to improve the website.

### Donating
If this project help you search paper easier, you can give us a cup of coffee :) 


[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://paypal.me/aischolar)
