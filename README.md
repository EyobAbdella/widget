# Contact Us Widget API
## setup

Clone the repository:

    git clone git@github.com:se61-ireg/Contact-us-widget-Backend-by-kalkidan.git

    cd Contact-us-widget-Backend-by-kalkidan

Install the dependencies:

    python3 -m venv venv

    source venv/bin/activate

    pip install -r requirements.txt


Set up Google OAuth credentials:

    Add your OAuth credentials in the .env
    GOOGLE_OAUTH2_CLIENT_ID
    GOOGLE_OAUTH2_CLIENT_SECRET
    GOOGLE_OAUTH2_PROJECT_ID
    
Set Up RECAPTCHA:

    Add your key in the .env
    RECAPTCHA_SITE_KEY
    RECAPTCHA_SECRET_KEY

Run the Django server:

    python manage.py migrate 

    python manage.py runserver
    
### Endpoints

## Auth Endpoints

  Sign UP
    http://127.0.0.1:8000/auth/users/
    
  Login 
    http://127.0.0.1:8000/auth/jwt/create

## Create Widget
  - **URL**: `127.0.0.1:8000/contact-form/widget/`
  - **Method**: `POST`
  - **Example**: 
      POST 127.0.0.1:8000/contact-form/widget/
    
      Body:
      ```
      {
          "html": "<div><h1>Welcome to our Widget!</h1></div>",
          "widget_fields": [
                            {"id": "134", "type": "text", "label": "Name", “required”: true, “placeholder”: “John”},
                          ],
          "success_msg": "Your submission was successful!",
          "redirect_url": "https://google.com",
          "hide_form": false,
          "post_submit_action": "REDIRECT_URL",
          "pre_fill": [
                        {"field_id": "134", "parameter_name": "name"},
                      ]
          “Spam_protection”: “true”
    }
    ```

      
