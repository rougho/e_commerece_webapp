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

Run the development server:
```sh
python manage.py runserver
```

### Contributing
We welcome contributions to this project! Please read <a href="">CONTRIBUTING.md</a> for details on our code of conduct, and the process for submitting pull requests.

### License
This project is licensed under the MIT License - see the <a href="">LICENSE.md</a> file for details.