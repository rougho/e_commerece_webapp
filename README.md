# E-Commerce Web Application

### For End-Users

If you're looking to shop with us, here's how you can get started:

- **Visit Our Website**: Access our e-commerce platform by navigating to [our website](#). (Note: Replace `#` with the actual URL of your deployed application.)
- **Browse Products**: Explore our wide range of products across different categories.
- **Add to Cart**: Found something you like? Add it to your cart with just one click.
- **Checkout**: Follow the simple checkout process to place your order.
- **Track Your Order**: Keep tabs on your order with real-time updates on its status.

### For Developers

If you're interested in setting up the project locally for development or testing purposes, follow these steps:

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or higher
- Pipenv

If you don't have Pipenv installed, you can install it by running:

```sh
pip install pipenv
```

#### Setting Up the Project
Clone the repository to your local machine:

```sh
git clone https://github.com/rougho/e_commerce_webapp.git
```
Navigate into the project directory:
```sh
cd e_commerce_webapp
```

Use Pipenv to create a virtual environment and install the dependencies:
```sh
pipenv install
```

Install the required dependencies:

```sh
pip install -r requirements.txt
```

Navigate into the app directory:
```sh
cd Alimama
```

Apply the migrations to create the database schema:
```sh
python manage.py migrate
```




# Setting Up Environment Variables

To run this e-commerce web application correctly, you need to set up several environment variables that are crucial for the application's configuration, including settings for security, email services, and payment processing. These variables should never be hardcoded into your project files for security reasons. Instead, we use an `.env` file to define these variables.

## Steps to Set Up Your `.env` File

1. **Create a `.env` file** in the root directory of the project, if it doesn't already exist.

2. **Open your `.env` file** and add the following environment variables:

    ```
    SECRET_KEY='your_django_secret_key'
    EMAIL_HOST_USER='your_email@example.com'
    EMAIL_HOST_PASSWORD='your_email_password'
    STRIPE_PUBLISHABLE_KEY='your_stripe_publishable_key'
    STRIPE_SECRET_KEY='your_stripe_secret_key'
    ```

    Replace the placeholder values with your actual data:
    - `your_django_secret_key`: A new, secure key for Django. You can generate one using online tools or Django itself by running `django.core.management.utils.get_random_secret_key()`.
    - `your_email@example.com` and `your_email_password`: Credentials for the email service you'll use for sending emails from the application.
    - `your_stripe_publishable_key` and `your_stripe_secret_key`: Your Stripe API keys for handling payments. Obtain them from your Stripe dashboard.

3. **Save the `.env` file** with your changes.

## Integrating Environment Variables in Django

Make sure your Django settings are configured to use the environment variables from the `.env` file. You can use libraries such as `django-environ` to easily manage and use environment variables in your project. Here's how to integrate it:

1. Install `django-environ` by adding it to your `requirements.txt` file or by running:

    ```sh
    pip install django-environ
    ```

2. At the top of your `settings.py`, import `environ` and load the `.env` file's environment variables:

    ```python
    import environ

    env = environ.Env()
    # Reading .env file
    environ.Env.read_env()
    ```

3. Replace your current settings with environment variables. For example:

    ```python
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your_email@example.com')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_email_password')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'your_stripe_publishable_key')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'your_stripe_secret_key')
    ```

By following these steps, you can securely configure your application without exposing sensitive information in your codebase. Remember to add `.env` to your `.gitignore` file to prevent it from being tracked by Git and potentially exposed publicly.


## Run the app
Run the development server:
```sh
python manage.py runserver
```
Access the Application:
Open your browser and go to http://127.0.0.1:8000 to see the application running locally.



### Contributing
We welcome contributions to this project! Please read <a href="https://github.com/rougho/e_commerece_webapp/blob/rohi/CONTRIBUTING.md">CONTRIBUTING.md</a> for details on our code of conduct, and the process for submitting pull requests.

### License
This project is licensed under the MIT License - see the <a href="https://github.com/rougho/e_commerece_webapp/blob/rohi/LICENSE">LICENSE.md</a> file for details.